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
from POM.CMS.change_bill_cycle_page import Change_Bill_Cycle
from POM.Common.Raptr_Base_Page import RpBasePage
from Utils.faker_util import FakeDataUtil


@allure.title("Create Request Postpaid-Prepaid Migration.")
@allure.description_html("""
Test Description:create request by Filtering request type as "service change",<br>
request subtype as "service change requesTC" <br>
 and request name as "Change Bill Cycle"
""")
@allure.epic("CMS Project")
@allure.feature("Customer Requests")
@allure.story("Positive Customer Request Flow")
@allure.severity(allure.severity_level.CRITICAL)
@allure.id("10003")
@pytest.mark.datafile("change_bill_cycle.xlsx")
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
    pom = Change_Bill_Cycle(driver)
    db = CmsDataUtil(app="cms")

    # Test Data
    customer_id = data.get("customer_id")
    search_by = data.get("search_by")
    request_type = data.get("request_type")
    request_name = data.get("request_name")
    req_alt_msg = data.get("req_alt_msg")
    remarks = FakeDataUtil.fake_last_name()
    request_id = None
    customer_name = None
    new_bill_cycle_id = data.get("new_bill_cycle")

    try:
        # Step: Prepare test data from Databse If Not Exists in Data File
        with allure.step("Prepare test data from Databse If Not Exists in Data File"):
            if customer_id is None:
                logging.info("Fetching customer ID from database...")
                result = ProcessingDbUtil().get_customer_id(acc_type="Postpaid")
                if not result:
                    raise AssertionError("No customers of accType=Prepaid and status=Available found in DB.")
                else:
                    customer_id = result[0]["Cust_Id"]
        logging.info("CUSTOMER ID TESTING IS = {}".format(customer_id))

        # Pre REQUEST CHECK
        with allure.step("Checking the new billcycle exists in Database."):
            check_bill_cycle = db.check_bill_cycle_exists_in_db_or_not(new_bill_cycle_id)
            if check_bill_cycle == False:
                logging.error("Bill Cycle : [{}] doesn't exists in Database.".format(new_bill_cycle_id))
                raise AssertionError ("Bill Cycle : [{}] doesn't exists in Database.".format(new_bill_cycle_id))

        # Comparing the Old Bill Cycle with new bill cycle
        with allure.step("Getting Previous Bill Cycle From Database"):
            old_bill_cycle = db.get_bill_cycle(customer_id)
            logging.info("Old bill cycle details = {}".format(old_bill_cycle))
            allure.attach(old_bill_cycle, name="OLD BILL CYCLE DETAILS", attachment_type=allure.attachment_type.TEXT)
            old_bill_cycle_id = old_bill_cycle[0]["BILL_CYCLE_ID"]
            if new_bill_cycle_id == old_bill_cycle_id:
                allure.attach("The old_bill_cycle_id = [{}] and  new_bill_cycle_id [{}] are same.".format(old_bill_cycle_id,new_bill_cycle_id), name="BILLL CYCLES ARE SAME",
                              attachment_type=allure.attachment_type.TEXT)
                logging.warn("The old_bill_cycle_id = [{}] and  new_bill_cycle_id [{}] are same.".format(old_bill_cycle_id,new_bill_cycle_id))
                raise AssertionError ("The old_bill_cycle_id = [{}] and  new_bill_cycle_id [{}] are same.".format(old_bill_cycle_id,new_bill_cycle_id))


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


        with allure.step("Selecting the New Bill Cycle"):
            cb.wait_for_page_to_load()
            cb.click_on_customer_account_radio_button()
            cr.click_on_acc_radio_button()
            pom.select_new_bill_cycle(new_bill_cycle_id)

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

            with allure.step("Getting Request ID from Database."):
                # Step for getting the request id from DB
                if request_id is None:
                    logging.info("Collecting the Request ID From DB")
                    request_id = db.get_request_id_from_db(customer_id)
                else:
                    logging.info("Request ID = {}, already collected ".format(request_id))
                logging.info("Request_ID = {}".format(request_id))

        # Step 14: Navigating to Request Search Page.
        with allure.step("Navigating to Request Search Page."):
            cb.click_on_customer_request_dropdown()
            screenshot_manager.add_screenshot(driver, "Navigating to Request Search Page.")
            allure.attach(driver.get_screenshot_as_png(), name="Navigating to Request Search Page.",
                          attachment_type=allure.attachment_type.PNG)
        cb.click_on_request_search_button()
        cb.click_on_search_filter_button()
        time.sleep(3)
        cb.click_on_reset_button()
        if request_id :
            logging.info("Searching with REQUEST_ID: {}".format(request_id))
            cr.enter_request_id(request_id)
            cb.click_on_search_icon()

        with allure.step("Click on Search Request"):
            screenshot_manager.add_screenshot(driver, "Search Request")
            allure.attach(driver.get_screenshot_as_png(), name="Search Request",
                          attachment_type=allure.attachment_type.PNG)
        cr.click_update_request_by_customer(customer_name)
        cr.select_action_check_box()
        logging.info("Clicked on action chain button")
        time.sleep(3)
        cr.click_on_process_now_button()
        logging.info("Clicked on Process Now button")
        with allure.step("Click on Process Request"):
            screenshot_manager.add_screenshot(driver, "Process Request")
            allure.attach(driver.get_screenshot_as_png(), name="Process Request",
                          attachment_type=allure.attachment_type.PNG)
        cb.click_on_alert_dialog_ok_button_two()
        screenshot_manager.add_screenshot(driver, "Successfully Processed")
        allure.attach(driver.get_screenshot_as_png(), name="Successfully Processed",
                      attachment_type=allure.attachment_type.PNG)

        # Step: Checking Whether the Billing Cycle Got Updated or Not
        with allure.step("Checking Whether the Billing Cycle Got Updated or Not"):
            after_change= db.get_bill_deleivery_mode(customer_id)
            if old_bill_cycle_id == after_change:
                logging.error("Bill Cycle Did Not Changed")
                assert  "Bill Cycle is Not Changed."
            else:
                logging.info("Bill Cycle is Updated ")


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
