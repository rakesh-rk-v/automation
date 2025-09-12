import logging
import platform
import sys
import time
import traceback

import allure
import pytest
from selenium.common import TimeoutException

from DButils.CMS.cms_db_util import CmsDataUtil
from DButils.Common.processing_db_util import ProcessingDbUtil
from POM.CMS.Cms_Base_Page import CmsBasePage
from POM.CMS.Create_Request_Page import Customer_Request_Page
from POM.CMS.change_bill_delivery_mode_Page import Change_Bill_Delivery_Mode
from POM.Common.Raptr_Base_Page import RpBasePage
from Utils.faker_util import FakeDataUtil


@allure.title("Change Bill Delivery Mode")
@allure.description_html("""
Test Description:Verify the order is creating for a Change Bill delivery mode.<br>
""")
@allure.epic("CMS Project")
@allure.feature("Customer Requests")
@allure.story("Positive Customer Request Flow")
@allure.severity(allure.severity_level.CRITICAL)
@allure.id("10003")
@pytest.mark.datafile("change_bill_delivery_mode.xlsx")
def test_customer_requests(driver, screenshot_manager, _data_index):
    # Attach environment info dynamically for Allure report
    browser_name = driver.capabilities.get('browserName', 'unknown')
    browser_version = driver.capabilities.get('browserVersion', 'unknown')
    os_name = platform.system()
    os_release = platform.release()
    os_version = platform.version()
    allure.attach(
        f"Browser: {browser_name} {browser_version}\nOS: {os_name} {os_release} ({os_version})",
        name="Environment Info",
        attachment_type=allure.attachment_type.TEXT
    )

    # Initialize page objects and test data
    data = driver.context.data
    rp = RpBasePage(driver)
    cr = Customer_Request_Page(driver)
    cb = CmsBasePage(driver)
    change_bill = Change_Bill_Delivery_Mode(driver)
    db = CmsDataUtil(app="cms")

    # Test Data
    customer_id = data.get("customer_id")
    search_by = data.get("search_by")
    request_type = data.get("request_type")
    request_name = data.get("request_name")
    req_alt_msg = data.get("req_alt_msg")
    remarks = FakeDataUtil.fake_last_name()
    change_mode= None
    request_id = None
    customer_name = None
    try:
        # Step 3: Prepare test data from Databse If Not Exists in Data File
        with allure.step("Prepare test data from Databse If Not Exists in Data File"):
            if customer_id is None:
                logging.info("Fetching customer ID from database...")
                result = ProcessingDbUtil().get_customer_id(acc_type="Postpaid")
                if not result:
                    raise AssertionError("No customers of accType=Prepaid and status=Available found in DB.")
                else:
                    customer_id = result[0]["Cust_Id"]
        logging.info("CUSTOMER ID TESTING IS = {}".format(customer_id))
        with allure.step("Updating the Test Data "):
            update = ProcessingDbUtil().update_test_customer_status_in_db(customer_id)
            logging.info("Updating the test data . [{}]".format(update))

        # Step 1: Wait for login page to load
        with allure.step("Wait for login page to load"):
            rp.wait_for_page_to_load(sleep_delay=3)
            screenshot_manager.add_screenshot(driver, "Base Page")
            allure.attach(driver.get_screenshot_as_png(), name="Login_Page", attachment_type=allure.attachment_type.PNG)

        # Step 2: Navigate to CMS module
        with allure.step("Navigating to CMS Module"):
            rp.click_on_cms_module()
            rp.wait_for_page_to_load()
            screenshot_manager.add_screenshot(driver, "CMS Base Page")
            allure.attach(driver.get_screenshot_as_png(), name="CMS Base Page", attachment_type=allure.attachment_type.PNG)

        # Step 4: Go to Customer Request section
        with allure.step("Navigating to Customer Request Section"):
            cb.click_on_customer_request_dropdown()
            cb.click_on_create_request_button()
            cb.wait_for_page_to_load()
            cb.click_on_search_filter_button()
            logging.info("Search By: %s", search_by)
            cb.wait_for_page_to_load()
            cb.select_search_by_dropdown(search_by)

        # Step 5: Search for customer and fetch page
        with allure.step("Entering the Customer ID"):
            cb.enter_in_customer_id_textbox(customer_id)
            cb.click_on_search_icon()
            logging.info("Clicked on Search icon.")
            cb.wait_for_page_to_load()
            time.sleep(3)  # Consider using explicit waits

        # Step 6: Checking Customer Details
        with allure.step("Customer Details"):
            if cr.check_if_customer_details_present():
                logging.info("Customer Details Found")
            else:
                logging.info("Customer Details are not found")
                assert "NO CUSTOMER DETAILS FOUND"
            screenshot_manager.add_screenshot(driver, "Customer Details")
            allure.attach(driver.get_screenshot_as_png(), name="Customer Details", attachment_type=allure.attachment_type.PNG)
            with allure.step("Getting the Customer Name From Front End."):
                customer_name = cr.get_customer_name()
                logging.info("Customer Name: %s", customer_name)
        # Step 7: Create request
        with allure.step("Clicking on Create Request and entering the request types and request names"):
            cb.click_on_create_request_icon()
            cb.wait_for_page_to_load()
            if request_type:
                logging.info(f"Request Type {request_type}")
                cb.select_request_type_dropdown(request_type)
            else:
                logging.error(f"Request Type = {request_type} . Not Configured Properly")
                raise AssertionError(f"Request Name ={request_name}. Which is Empty or not Available")
            cb.wait_for_page_to_load()
            if request_name:
                logging.info(f"Request Name: {request_name}")
                cb.select_request_name_dropdown(request_name)
            else:
                logging.error(f"Request Name is not configured {request_name}")
                raise AssertionError(f"Request Name is  Empty.{request_name}")

            screenshot_manager.add_screenshot(driver, "Request TYPE")
            allure.attach(driver.get_screenshot_as_png(), name="Request Type", attachment_type=allure.attachment_type.PNG)

        # Step 8: Enter remarks
        with allure.step("Adding the Remarks"):
            cb.enter_in_remarks_textbox(remarks)
            cb.wait_for_page_to_load(sleep_delay=3)
            screenshot_manager.add_screenshot(driver, "Adding the Remarks")
            allure.attach(driver.get_screenshot_as_png(), name="Adding the Remarks", attachment_type=allure.attachment_type.PNG)

        # Step 9: Clicking on Customer Radio Button.
        with allure.step("Clicking on Customer  Radio Button."):
            cb.click_on_customer_radio_button()
            cb.wait_for_page_to_load()
            allure.attach(driver.get_screenshot_as_png(), name="After Clicking the Customer Radio Button", attachment_type=allure.attachment_type.PNG)
            screenshot_manager.add_screenshot(driver, "After Clicking the Customer Radio Button")

        # Step 10: Selecting the Billing Account
        with allure.step("Selecting the billing account."):
            logging.info("Selecting the Billing Account")
            change_bill.select_billing_acc_id()
            screenshot_manager.add_screenshot(driver, "Selecting the Billing Account")
            allure.attach(driver.get_screenshot_as_png(), name="Selecting the Billing Account", attachment_type=allure.attachment_type.PNG)

        # Step 11: Getting the Customer Billing Account From DB
        with allure.step("Getting the Customer Billing Account From DB"):
            logging.info("Getting the Customer Billing Account From DB")
            previous_mode = db.get_bill_deleivery_mode(customer_id)
            if previous_mode == 1:
                change_mode = "Soft Copy"
            else:
                change_mode = "Hard/Physical Copy"
            logging.info("Change Mode = {}".format(change_mode))

        # Step 12: Selecting the Delivery Mode
        with allure.step("Selecting the Delivery Mode"):
            change_bill.select_delivery_mode(change_mode)
            screenshot_manager.add_screenshot(driver, "Selecting the Delivery Mode")
            allure.attach(driver.get_screenshot_as_png(), name="Selecting the Delivery Mode", attachment_type=allure.attachment_type.PNG)

        # Step 13: Clicking on Create Request
        with allure.step("Clicking on Create Request"):
            cr.click_on_create_request_button()
            screenshot_manager.add_screenshot(driver, "After Clicking on Create Request")
            allure.attach(driver.get_screenshot_as_png(), name="After Clicking on Create Request", attachment_type=allure.attachment_type.PNG)
            alt_msg = cb.get_alert_dialog_text()
            if alt_msg.lower().strip() == req_alt_msg.lower().strip():
                logging.info("Proper Alert as Expected.")
                cb.click_on_alert_dialog_ok_button_two()
            else:
                logging.error("Expected Alert Box content = {}".format(req_alt_msg))
                cb.click_on_alert_dialog_ok_button_two()
                raise AssertionError("Expect = [{}] Actual = [{}]".format(req_alt_msg,alt_msg))


    except TimeoutException as te:
        exc_type, exc_obj, tb = sys.exc_info()
        fname = tb.tb_frame.f_code.co_filename
        line_no = tb.tb_lineno
        logging.error(f"TimeoutException: {te} (File: {fname}, Line: {line_no})")
        allure.attach(f"TimeoutException: {te}\n(File: {fname}, Line: {line_no})", name="TimeoutException", attachment_type=allure.attachment_type.TEXT)
        traceback.print_exc()
        raise

    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        fname = tb.tb_frame.f_code.co_filename
        line_no = tb.tb_lineno
        logging.error(f"Exception: {exc_type.__name__}: {e} (File: {fname}, Line: {line_no})")
        allure.attach(f"Exception: {exc_type.__name__}: {e}\n(File: {fname}, Line: {line_no})", name="Exception", attachment_type=allure.attachment_type.TEXT)
        traceback.print_exc()
        raise