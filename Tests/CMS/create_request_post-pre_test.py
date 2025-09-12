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
from POM.CMS.Prepaid_To_Postpaid_Movement_Page import PrepaidToPostpaid
from POM.Common.Raptr_Base_Page import RpBasePage
from Utils.faker_util import FakeDataUtil


@allure.title("Post-Pre-Movement Request")
@allure.description_html("""
Test Description:create request by Filtering request type as "service change",<br>
request subtype as "service change requesTC" <br>
 and request name as "Post-Pre-Movement"
""")
@allure.epic("CMS Project")
@allure.feature("Customer Requests")
@allure.story("Positive Customer Request Flow")
@allure.severity(allure.severity_level.CRITICAL)
@allure.id("TC_3467")
@pytest.mark.datafile("post_pre_migration.xlsx")
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
    db = CmsDataUtil(app="cms")
    pom = PrepaidToPostpaid(driver)

    # Test Data
    customer_id = data.get("customer_id")
    search_by = data.get("search_by")
    request_type = data.get("request_type")
    request_name = data.get("request_name")
    req_alt_msg = data.get("req_alt_msg")
    remarks = FakeDataUtil.fake_last_name()
    plan = data.get("prepaid_plan_name")

    try:
        # Step: Prepare test data from Databse If Not Exists in Data File
        with allure.step("Prepare test data from Databse If Not Exists in Data File"):
            if customer_id is None:
                logging.info("Fetching customer ID from database...")
                result = ProcessingDbUtil().get_customer_id(acc_type="Postpaid")
                if not result:
                    raise AssertionError("No customers of accType=Postpaid and status=Available found in DB.")
                else:
                    customer_id = result[0]["Cust_Id"]
        logging.info("CUSTOMER ID TESTING IS = {}".format(customer_id))
        # allure.attach(customer_id, name="TEST Customer ID", attachment_type=allure.attachment_type.TEXT)
        with allure.step("Updating the Test Data "):
            update = ProcessingDbUtil().update_test_customer_status_in_db(customer_id)
            logging.info("Updating the test data . [{}]".format(update))
        #Step: TEST DATA Mandatory Check
        with allure.step("Checking the Mandatory Test Data"):
            if plan is not None:
                logging.info("Prepaid Plan Name for Movement is [{}]".format(plan))
            else:
                logging.error("Prepaid Plan Name is Mandatory Please Fill the Column [prepaid_plan_name] in Excel")
                assert None,"Prepaid Plan Name is Mandatory Please Fill the Column [prepaid_plan_name] in Excel"

        # Pre REQUEST CHECK
        with allure.step("Checking the Customer is Having a Active Postpaid Account"):
            logging.info("Checking the Customer is Having a Active Postpaid Account")
            check_post_paid =  db.check_customer_acc_type(customer_id,acc_type=12)
            if check_post_paid:
                logging.info("Customer = [{}] is Having a Valid Postpaid Account.".format(customer_id))
            else:
                logging.warn("Customer = [{}] is Not Having a Valid Postpaid Account.".format(customer_id))
                assert  "Customer = [{}] is not having a valid Postpaid Account."

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
            cb.wait_for_page_to_load()
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

        #Selecting the Account
        with allure.step("Clicking on Customer Account Radio Button"):
            cb.wait_for_page_to_load()
            cb.click_on_customer_account_radio_button()
            cr.click_on_acc_radio_button()
            screenshot_manager.add_screenshot(driver, "Clicking on Customer Account Radio Button")
            allure.attach(driver.get_screenshot_as_png(), name="Clicking on Customer Account Radio Button", attachment_type=allure.attachment_type.PNG)

        #Selecting the Rateplan:
        with allure.step("Selecting the Rateplan"):
            cb.wait_for_page_to_load()
            pom.click_on_rp_checkbox(plan)
            screenshot_manager.add_screenshot(driver, "Selecting the Rateplan")
            allure.attach(driver.get_screenshot_as_png(), name="Selecting the Rateplan", attachment_type=allure.attachment_type.PNG)

        #Clicking on Create Request Button
        with allure.step("Click on Create Request"):
            cr.click_on_create_request_button()
            time.sleep(2)
            cr.click_on_alert_dialog_ok_button_two()
            screenshot_manager.add_screenshot(driver, "Click on Create Request")
            allure.attach(driver.get_screenshot_as_png(), name="Click on Create Request", attachment_type=allure.attachment_type.PNG)

        # Verify Contract Details In the Customer 360 View
        with allure.step("Verify Contract Details In the Customer 360 View"):
            logging.info("Verify Contract Details In the Customer 360 View")
            cb.wait_for_page_to_load()
            cb.click_on_customer_management_dropdown()
            cb.click_on_view_customer_button()
            cb.click_on_search_filter_button()
            cb.select_search_by_dropdown(data.get('search_by'))
            cb.enter_in_customer_id_textbox(customer_id)
            cb.wait_for_page_to_load()
            screenshot_manager.add_screenshot(driver, "Customer Details In View Customer Tab")
            allure.attach(driver.get_screenshot_as_png(),
                          name="Customer Details In View Customer Tab",
                          attachment_type=allure.attachment_type.PNG)
            cb.click_on_search_icon()
            cb.click_on_360_view_button()
            logging.info("Clicking on Customer 360 Button.")
            cb.wait_for_page_to_load()
            cb.click_on_billing_account_dropdown_arrow()
            screenshot_manager.add_screenshot(driver, "Customer Contract Status")
            allure.attach(driver.get_screenshot_as_png(),
                          name="Customer Contract Status",
                          attachment_type=allure.attachment_type.PNG)
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





