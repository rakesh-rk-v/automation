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
from POM.CMS.change_billing_address_page import ChangeBillingAddressPage
from POM.Common.Raptr_Base_Page import RpBasePage
from POM.Common.yopmail_page import Mail
from Utils.config_manager import ConfigManager
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
@pytest.mark.datafile("change_billing_addr.xlsx")
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
    pom = ChangeBillingAddressPage(driver)
    mail = Mail(driver)

    # Test Data
    customer_id = data.get("customer_id")
    search_by = data.get("search_by")
    request_type = data.get("request_type")
    request_name = data.get("request_name")
    req_alt_msg = data.get("req_alt_msg")
    remarks = FakeDataUtil.fake_last_name()
    address_line1 = data.get("address_line1")
    address_line2 = data.get("address_line2")
    city = data.get("city")
    state = data.get("state")
    country = data.get("country")
    request_id = None

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

        # allure.attach({"TESTING Customer ID = " : customer_id}, name="TEST Customer ID", attachment_type=allure.attachment_type.TEXT)
        with allure.step("Updating the Test Data "):
            update = ProcessingDbUtil().update_test_customer_status_in_db(customer_id)
            logging.info("Updating the test data . [{}]".format(update))

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
            logging.info("Clicked on CMS Module.")
            screenshot_manager.add_screenshot(driver, "CMS Base Page")
            allure.attach(driver.get_screenshot_as_png(), name="CMS Base Page", attachment_type=allure.attachment_type.PNG)


        # Step 4: Go to Customer Request section
        with allure.step("Navigating to Customer Request Section"):
            cb.wait_for_page_to_load()
            cb.click_on_customer_request_dropdown()
            cb.click_on_create_request_button()
            cb.wait_for_page_to_load()
            logging.info("Clicked on Customer Request Section.")
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

            with allure.step("Clicking on the Yes button"):
                cb.wait_for_page_to_load()
                pom.click_on_yes_button()
                screenshot_manager.add_screenshot(driver, "Clicking Yes Button")
                allure.attach(driver.get_screenshot_as_png(), name="Clicking Yes Button",
                               attachment_type=allure.attachment_type.PNG)

        # Step 9: Enter form details
        with allure.step("Entering form details"):
            pom.enter_address_line1(address_line1)
            pom.enter_address_line2(address_line2)
            pom.enter_city(city)
            pom.enter_state(state)
            pom.enter_country(country)
            screenshot_manager.add_screenshot(driver, "Form Details")
            allure.attach(driver.get_screenshot_as_png(), name="Form Details",
                          attachment_type=allure.attachment_type.PNG)

        with allure.step("Clicking on Create Request Button"):
            pom.click_create_request()
            logging.info("Clicking on Create Request Button")

            with allure.step("Validating the alert box content"):
                # Retrieve the actual alert message from the dialog
                alt_msg = cb.get_alert_dialog_text()
                # Normalize both the expected and actual messages for comparison
                if alt_msg.lower().strip() == req_alt_msg.lower().strip():
                    logging.info("Proper Alert as Expected.")
                    cb.click_on_alert_dialog_ok_button_two()
                else:
                    # Log the expected and actual messages for debugging
                    logging.error("Expected Alert Box content = [{}]".format(req_alt_msg))
                    logging.error("Actual Alert Box content = [{}]".format(alt_msg))
                    # Close the alert dialog
                    cb.click_on_alert_dialog_ok_button_two()
                    # Raise an assertion error with detailed information
                    raise AssertionError("Expected = [{}] but got = [{}]".format(req_alt_msg, alt_msg))

        with allure.step("Getting Request ID from Database"):
            request_id = db.get_request_id_from_db(customer_id)
            logging.info("Request ID = {}".format(request_id))
            # allure.attach(request_id, name="Request ID", attachment_type=allure.attachment_type.TEXT)

            # Updating the Customer Request After the Request Got Created
        with allure.step("Click on Customer Request Drop Down"):
            cb.click_on_customer_request_dropdown()
            screenshot_manager.add_screenshot(driver, "Customer Request Drop Down")
            allure.attach(driver.get_screenshot_as_png(), name="Customer Request Drop Down",
                              attachment_type=allure.attachment_type.PNG)
            cb.click_on_request_search_button()
            cb.click_on_search_filter_button()
            time.sleep(3)
            cb.click_on_reset_button()
            if request_id:
                logging.info("Searching with REQUEST_ID: {}".format(request_id))
                cr.enter_request_id(request_id)
                cb.click_on_search_icon()
            else:
                cb.search_by_activity_area(data.get("activity_area"))
                cb.search_by_acc_name(customer_name)
                cb.click_on_search_icon()
            with allure.step("Click on Search Request"):
                screenshot_manager.add_screenshot(driver, "Search Request")
                allure.attach(driver.get_screenshot_as_png(), name="Search Request",
                              attachment_type=allure.attachment_type.PNG)
            cr.click_update_request_by_customer(customer_name)
            cr.select_action_check_box()
            time.sleep(3)
            cr.click_on_process_now_button()
            screenshot_manager.add_screenshot(driver,"Clicked on Process")
            allure.attach(driver.get_screenshot_as_png(), name="Clicked On Process Now Button",
                          attachment_type=allure.attachment_type.PNG)
            cr.click_on_alert_dialog_ok_button_two()

         # Verification of EMAIL NOTIFICATION Change of Billing Address for a Customer
        with allure.step("Verify the email Notification"):
            contact_id = db.get_contact_id_from_customer_contacts_mapping(cust_id=customer_id)[0][
                "CONTACT_ID"]
            cust_mail = db.get_email_from_customer_contacts(contact_id)[0]["PRIMARY_EMAIL"]
            cust_req_id = db.get_customer_request_id(cust_id=customer_id)[0]["REQUEST_ID"]
            logging.info("Customer mailId :{}\nCustomer Request Id :{}".format(cust_mail, cust_req_id))
            allure.attach("Customer mailId :{}\nCustomer Request Id :{}".format(cust_mail, cust_req_id),
                          name="Customer mail id",
                          attachment_type=allure.attachment_type.TEXT)
            cb.navigate_to_url(ConfigManager.get_config().get_value('yopmail_url'))
            cb.wait_for_page_to_load()
            cb.enter_yopmail_in_textbox(cust_mail)
            logging.info("Entering the Email ID : {}".format(cust_mail))
            cb.click_on_inbox_arrow()
            cb.wait_for_page_to_load(sleep_delay=10)
            cb.hard_refresh()
            screenshot_manager.add_screenshot(driver, "Customer Recived mail with Request id")
            allure.attach(driver.get_screenshot_as_png(),
                          name="Customer Recived mail with Request id",
                          attachment_type=allure.attachment_type.PNG)
            mail.click_on_mails(2)
            cb.wait_for_page_to_load()
            screenshot_manager.add_screenshot(driver, "Customer Recived Request Processed mail")
            allure.attach(driver.get_screenshot_as_png(),
                          name="Customer Recived mail with Request id",
                          attachment_type=allure.attachment_type.PNG)
        logging.info("Successfully Received Notification.")
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
