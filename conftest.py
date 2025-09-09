import codecs
import sys

import pytest
import os
import logging
import allure
import pyautogui
import cv2
import numpy as np
import time
import threading
import platform

from POM.Common.login_page import LoginPage
from Utils.config_manager import ConfigManager
from Utils.data_reader import DataReader
from Utils.screenshot_manager import ScreenshotManager

# 1️ Add custom CLI options
def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="sit")
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--app", action="store", default="oms")


# 2️ Configure logging before session
def pytest_configure(config):
    # Ensure logs folder exists (optional)
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler('logs/test_log.log', mode='a')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    # Write two newlines before each test run for separation
    with open('logs/test_log.log', 'a') as f:
        f.write('\n\n')

    logger.info("Test session is starting.")


# 3️ Session start
def pytest_sessionstart(session):
    print(" Session started")
    logging.info("Session started.")


# 4️ Session finish
def pytest_sessionfinish(session, exitstatus):
    print("Session finished")
    logging.info("Session finished with exit status: %s", exitstatus)
    """
    Create allure environment.properties after all tests
    """
    results_dir = os.path.join(os.getcwd(), "allure-results")
    os.makedirs(results_dir, exist_ok=True)
    env_file = os.path.join(results_dir, "environment.properties")

    # Get CLI input
    app_name = session.config.getoption("--app") or "DefaultApp"
    env_name = session.config.getoption("--env") or "DEV"

    browser_name = session.config.getoption("--browser")
    browser_version = " "
    # Try to get driver info if browser is not provided
    driver = getattr(session.config, "driver_instance", None)
    if driver:
        browser_name = driver.capabilities.get("browserName", " ")
        browser_version = driver.capabilities.get("browserVersion", " ")
    else:
        browser_name = browser_name or " "
        browser_version = " "

    # OS info programmatically
    os_name = platform.system()
    os_release = platform.release()
    os_version = platform.version()

    # Write environment.properties for Allure
    with open(env_file, "w") as f:
        f.write(f"App={app_name.upper()}\n")
        f.write(f"Environment={env_name.upper()}\n")
        f.write(f"Browser={browser_name.upper()} {browser_version.upper()}\n")
        f.write(f"OS={os_name.upper()} {os_release.upper()} ({os_version.upper()})\n")


# 5️ Runtest setup (before each test)
def pytest_runtest_setup(item):
    print(f"\n Setup for {item.name}")
    logging.info("Setting up: %s", item.name)


# 6️ Runtest call (actual test execution)
def pytest_runtest_call(item):
    print(f" Running test: {item.name}")
    logging.info("Running: %s", item.name)


# 7️ Runtest teardown (after each test)
def pytest_runtest_teardown(item):
    print(f" Teardown for {item.name}")
    logging.info("Teardown: %s", item.name)


# 8️ Make report hook - detect failures
@pytest.fixture
def screenshot_manager(request):
    app = request.config.getoption("--app")

    # Generate a unique and safe test name
    raw_name = request.node.nodeid.replace("/", "_").replace("::", "_")
    test_name = os.path.splitext(raw_name)[0]

    manager = ScreenshotManager(test_name=test_name, app_name=app)

    yield manager

    try:
        outcome = request.node.rep_call
        if outcome.failed:
            driver = request.node.funcargs.get("driver", None)
            if driver:
                manager.add_screenshot(driver, "Final state before failure")
    except Exception as e:
        print(f"⚠️ Error capturing screenshot: {e}")

    try:
        manager.generate_doc()
    except Exception as e:
        print(f"⚠️ Error generating Word doc: {e}")


# Hook to get test outcome info
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# 9️ Exception interaction (e.g. print custom messages)
def pytest_exception_interact(node, call, report):
    print(f" Exception in {node.name}: {call.excinfo.value}")
    logging.error("Exception in %s: %s", node.name, call.excinfo.value)


# 10 Add to summary at the end
def pytest_terminal_summary(terminalreporter, exitstatus):
    print("\n Custom Summary:")
    logging.info(f"Total tests run: {terminalreporter._numcollected}")
    logging.info(f"Passed: {len(terminalreporter.stats.get('passed', []))}")
    logging.info(f"Failed: {len(terminalreporter.stats.get('failed', []))}")
    logging.info(f"Skipped: {len(terminalreporter.stats.get('skipped', []))}")
    logging.info("Terminal summary written.")


@pytest.fixture(scope="session", autouse=True)
def config(request):
    env = request.config.getoption("--env")
    app = request.config.getoption("--app")
    ConfigManager.initialize(env, app)


@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser")
    from selenium import webdriver

    if browser == "chrome":
        driver = webdriver.Chrome()
    elif browser == "firefox":
        driver = webdriver.Firefox()
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    driver.get(ConfigManager.get_config().get_value('base_url'))
    driver.maximize_window()
    driver.implicitly_wait(10)
    lp=LoginPage(driver)
    lp.enter_username(ConfigManager.get_config().get_value('ap_username'))
    lp.enter_password(ConfigManager.get_config().get_value('ap_password'))
    lp.click_login()

    # Attach test context
    driver.context = type("Context", (), {})()

    marker = request.node.get_closest_marker("datafile")
    if marker:
        excel_file = marker.args[0]
        app = request.config.getoption("--app").upper()
        excel_path = os.path.join("DataFiles", app, "Excel", excel_file)

        if os.path.exists(excel_path):
            data = DataReader.read_excel(excel_path)
            if "_data_index" in request.fixturenames:
                idx = request.getfixturevalue("_data_index")
                driver.context.data = data[idx] if idx is not None and idx < len(data) else {}
            else:
                driver.context.data = {}
        else:
            driver.context.data = {}
    else:
        driver.context.data = {}

    yield driver
    driver.quit()


def pytest_generate_tests(metafunc):
    marker = metafunc.definition.get_closest_marker("datafile")
    if marker and "driver" in metafunc.fixturenames:
        excel_file = marker.args[0]
        app = metafunc.config.getoption("--app").upper()
        excel_path = os.path.join("DataFiles", app, "Excel", excel_file)

        if os.path.exists(excel_path):
            test_data = DataReader.read_excel(excel_path)

            # ➤ Check if this is file-level or test-level run
            collected_tests = metafunc.config.args  # like ['tests/oms/'] or ['tests/oms/test_login_ui.py']
            current_file = metafunc.module.__file__

            # If entire module/folder run, parametrize only 1 row
            if any(os.path.abspath(f) == os.path.abspath(current_file) for f in collected_tests):
                metafunc.parametrize("_data_index", range(len(test_data)))
            else:
                metafunc.parametrize("_data_index", [0])  # Only 1st row
        else:
            metafunc.parametrize("_data_index", [None])


# -------------------------
# Video Recorder Class (WebM)
# -------------------------
class VideoRecorder:
    def __init__(self, filepath, fps=5):
        self.filepath = filepath
        self.fps = fps
        self.screen_size = pyautogui.size()
        # Use VP8 codec for WebM
        self.out = cv2.VideoWriter(
            filepath,
            cv2.VideoWriter_fourcc(*"VP80"),  # VP8 codec for WebM
            fps,
            self.screen_size
        )
        self.recording = False
        self.thread = None

    def _record(self):
        while self.recording:
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            self.out.write(frame)
            time.sleep(1 / self.fps)

    def start(self):
        self.recording = True
        self.thread = threading.Thread(target=self._record)
        self.thread.start()

    def stop(self):
        self.recording = False
        if self.thread:
            self.thread.join()
        self.out.release()


# -------------------------
# Fixture to record video
# -------------------------
@pytest.fixture(scope="function", autouse=True)
def record_video(request):
    test_name = request.node.name
    os.makedirs("videos", exist_ok=True)
    filepath = os.path.join("videos", f"{test_name}.webm")

    recorder = VideoRecorder(filepath)
    recorder.start()

    yield  # Run the test

    recorder.stop()

    # Attach WebM file to Allure as downloadable
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            allure.attach(f.read(),
                          name=f"{test_name}_video",
                          attachment_type=allure.attachment_type.WEBM)


# -------------------------
# Hook to capture screenshot for every test
# -------------------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        driver = item.funcargs.get("driver")  # Your Selenium driver fixture
        if driver:
            status = "PASSED" if rep.passed else "FAILED"
            screenshot_name = f"{item.name}_{status}"
            try:
                allure.attach(driver.get_screenshot_as_png(),
                              name=screenshot_name,
                              attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                logging.warning(f"Failed to capture screenshot: {e}")

