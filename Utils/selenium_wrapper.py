import datetime
import random
import string
from typing import List


import os
import time

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pywinauto.application import Application


from DataFiles.Common.enum.Browser_Type_enum import BrowserType


def find_element(locator : By, locator_value=None, ec=None, wait_time=10, suppress_errors=False, skip_wait=False,
                 android_locator=None, ios_locator=None, android_locator_value=None, ios_locator_value=None):
    def decorator(func):
        def wrapper(*args) -> WebElement:
            try:
                driver = args[0].driver
                # browser = args[0].context.environment.browser
                final_locator, final_locator_value = locator, locator_value
                if not skip_wait: __wait(driver, final_locator,final_locator_value,ec,wait_time)
                return driver.find_element(final_locator, final_locator_value)
            except Exception as ex:
                if suppress_errors:
                    return None
                else:
                    raise ex
        return wrapper

    return decorator


def __get_locator( locator=None, locator_value=None, android_locator=None,android_locator_value=None,
                  ios_locator=None, ios_locator_value=None):
    # if __is_mobile(browser):
    #     if browser == BrowserType.ANDROID.value:
    #         locator = android_locator
    #         locator_value = android_locator_value
    #     else:
    #         locator = ios_locator
    #         locator_value = ios_locator_value

    return locator, locator_value


def find_elements(locator: By, locator_value: str, ec=None, wait_time=10, suppress_errors=False):
    def decorator(func):
        def wrapper(*args) -> List[WebElement]:
            try:
                driver = args[0].driver
                __wait(driver, locator, locator_value, ec
                if wait_time is None else wait_time)
                return driver.find_elements(locator, locator_value)
            except Exception as ex:
                if suppress_errors:
                    return []
                else:
                    raise ex
        return wrapper

    return decorator


def __is_mobile(browser):
    return True if browser in (BrowserType.ANDROID.value, BrowserType.IOS.value) else False


def __wait(driver, locator, locator_value, user_ec,wait_time):
    wait = WebDriverWait(driver, wait_time)
    exp_wait_fail_message = str(locator) + " " + locator_value + ' explicit wait failed ' + str(user_ec)
    if user_ec is not None:
        wait.until(user_ec((locator, locator_value)), exp_wait_fail_message if not None else "")
    wait.until(EC.presence_of_element_located((locator, locator_value)), exp_wait_fail_message)


class SeleniumWrapper:
    def __init__(self, driver):
        self.driver = driver


    def wait_for_page_to_load(self, sleep_delay=2, wait_timeout=15, wait_loading_screen_duration=7, loading_element=None):
        time.sleep(sleep_delay)
        wait = WebDriverWait(self.driver, wait_timeout)
        try:
            wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        except Exception as e:
            pass

        if loading_element:
            if loading_element():
                threshold = 20  # threshold will be set to 20, meaning loading screen can go on and off 20 times
                counter = 0
                loading_screen_present = True
                while loading_screen_present:
                    try:
                        WebDriverWait(self.driver, wait_loading_screen_duration).until(EC.visibility_of(loading_element()))
                        WebDriverWait(self.driver, wait_timeout).until(EC.invisibility_of_element(loading_element()))
                        counter += 1
                    except:
                        loading_screen_present = False
                    if counter >= threshold:
                        break

    def move_to_element_e(self, element):
        """
        Move to element for given base element
        :param element:
        :return:
        """
        ActionChains(self.driver) \
            .move_to_element(element) \
            .perform()

    def __apply_style(self, style, element):
        self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                   element, style)

    def highlight_element_and_log_screenshot(self, element):
        self.move_to_element_e(element)
        original_style = element.get_attribute('style'),
        self.__apply_style("background: yellow; border: 2px solid red;", element)
        self.__apply_style(original_style, element)

    def scroll_element_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def horizontal_scroll(self, width, element):
        self.driver.execute_script("arguments[0].scrollLeft = " + str(width), element)

    def scroll_to_up_of_the_page(self):
        script = "window.scrollTo(0, 0);"
        self.driver.execute_script(script)

    def scroll_element_to_center(self, element):
        script = "var viewPortHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);" \
                 "var elementTop = arguments[0].getBoundingClientRect().top;" \
                 "window.scrollBy(0, elementTop-(viewPortHeight/2));"

        self.driver.execute_script(script, element)

    def scroll_to_bottom_of_page(self):
        script = "window.scrollBy(0, document.body.scrollHeight);"
        self.driver.execute_script(script)

    def open_new_tab(self):
        self.driver.execute_script('window.open();')

    def switch_to_tab(self, tab_name, index=0, wait_time=15):
        counter = 0

        WebDriverWait(self.driver, wait_time).until(lambda _: len(self.driver.window_handles) > 1)
        for tab in self.driver.window_handles:
            self.driver.switch_to.window(tab)
            if self.driver.title == tab_name:
                if counter == index:
                    return

                counter += 1

    def switch_to_frame(self, frame_element, wait=20):
        try:
            WebDriverWait(self.driver, wait).until(EC.frame_to_be_available_and_switch_to_it(frame_element), 'no frame found')
        except Exception as ex:
            raise ex

    def switch_to_default_content(self):
        self.driver.switch_to.parent_frame()

    def select_option(self, dropdown_element, dropdown_options, text: str, load_delay=3):
        dropdown_element.click()
        self.wait_for_page_to_load(sleep_delay=load_delay)
        for option in dropdown_options():
            if option.text == text:
                option.click()
                return

        raise Exception(f"{text} is not a valid option for the dropdown.")

    def select_mat_option(self, mat_select_element, mat_option_text):
        mat_select_element.click()
        self.wait_for_page_to_load(.5)
        element = WebDriverWait(self.driver, 20) \
                                .until(EC.presence_of_element_located(
                                (By.XPATH, "//mat-option/span[normalize-space(text()) = '" + mat_option_text + "']")))
        element.click()

    def select_mat_checkbox(self, mat_select_element, checkboxes=[]):
        mat_select_element.click()
        self.wait_for_page_to_load(.5)
        for checkbox in checkboxes:
            element = WebDriverWait(self.driver, 20)\
                .until(EC.presence_of_element_located
                ((By.XPATH, "//mat-option/span[normalize-space(text()) = '" + checkbox + "']")))
            element.click()

        overlay_element = WebDriverWait(self.driver, 20) \
             .until(EC.presence_of_element_located((By.XPATH, "//div[@class='cdk-overlay-container']")))
        overlay_element.click()

    def select_list_item_by_text(self, dropdown_element, dropdown_textbox, dropdown_list, value: str):
        dropdown_element().click()
        dropdown_textbox().send_keys(value)
        self.wait_for_page_to_load()

        for option in dropdown_list():
            if option.text.strip() == value:
                option.click()
                self.wait_for_page_to_load()
                return

    def double_click_element(self, element):
        """
        Move to element for given base element
        and double click
        :param element:
        :return:
        """
        ActionChains(self.driver) \
            .move_to_element(element) \
            .double_click(element)  \
            .perform()

    def keyboard_action(self, key):
        ActionChains(self.driver) \
            .send_keys(key) \
            .perform()

    def upload_file_using_windows_dialog(self, file_path):
        app = Application().connect(title_re="Open")
        app["Dialog"]["Edit1"].type_keys(os.path.join(os.getcwd(), file_path), with_spaces=True, pause=.1)
        time.sleep(5)
        app["Dialog"]["Button1"].click()

    def open_url_in_new_tab(self, url, window_handle=1):
        # Open a new window
        self.driver.execute_script("window.open('');")

        # Switch to the new window and open new URL
        self.driver.switch_to.window(self.driver.window_handles[window_handle])
        self.driver.get(url)

    def hard_refresh(self):
        self.driver.execute_script("location.reload()")

    def wait_for_element_visibility(self, element):
        locator_type = element['method']
        locator_value = element['value']
        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((self.get_locator_method(locator_type), locator_value)))

    def wait_for_element_invisibility(self, element):
        locator_type = element['method']
        locator_value = element['value']
        WebDriverWait(self.driver, 20).until(
            EC.invisibility_of_element_located((self.get_locator_method(locator_type), locator_value)))

    def date_picker(self, date, element):
        self.driver.execute_script("arguments[0].value='" + date + "';", element)

    def escape(self):
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    def email_with_knot(self, limit=6):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(limit))
        return result_str+"@knotsolutions.com"

    def email_with_yop(self, limit=7):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(limit))
        return result_str+"@yopmail.com"

    def select_current_date(self):
        calender = self.driver.find_element(By.XPATH, "//button[@class='mat-focus-indicator mat-icon-button mat-button-base _mat-animation-noopable']")
        calender.click()
        date = self.driver.find_element(By.XPATH, "//td[@tabindex='0']")
        date.click()
        self.escape()

    def right_click(self, element):
        ActionChains(self.driver).context_click(on_element=element).perform()

    def enter_action(self):
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()

    def clear_the_text(self,element):
        self.driver.execute_script("arguments[0].value='';", element)

    def enter(self):
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()

    def current_date(self):
        date=datetime.date.strftime(datetime.date.today(), "%d-%m-%Y")
        return date
