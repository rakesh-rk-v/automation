import logging
from datetime import datetime

import pytest
from selenium.common import TimeoutException
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from POM.Common.Raptr_Base_Page import RpBasePage
from Utils.selenium_wrapper import find_element
from conftest import driver


class Customer_Request_Page(RpBasePage):

    @find_element(By.ID, "mat-input-3")
    def __account_search_input(self):pass

    @find_element(By.XPATH,"//ul/li[1]//mat-checkbox")
    def __account_check_box(self):pass

    @find_element(By.XPATH,"//button[text()='Fetch']")
    def __fetch_button(self):pass

    @find_element(By.XPATH,"//button[@aria-label='Open calendar']")
    def __deactivation_date(self):pass

    @find_element(By.XPATH,"//button[text()='Create Request']")
    def __create_request_button(self):pass

    @find_element(By.XPATH, "//table/tbody/tr/td[3]")
    def __customer_name_cell(self): pass

    @find_element(By.XPATH,"//mat-checkbox/label/span[1]")
    def __get_action_checkbox(self):pass

    @find_element(By.XPATH,"//app-process-now//button[text()='Process Now ']")
    def __process_now_button(self):pass

    @find_element(By.XPATH,"//span[contains(text(),'Resume Account')]")
    def __resume_acc_radio_button(self):pass

    @find_element(By.XPATH, "(//div[@class='mat-dialog-content alert-content']/p)[2]", wait_time=30)
    def __alert_dialog_div(self):pass

    @find_element(By.XPATH,"//span[contains(text(),'Resume Contract')]")
    def __resume_contract_radio_button(self):pass

    @find_element(By.ID, "mat-radio-4")
    def __account_radio_button(self):
        pass

    def click_on_account_search(self, acc_num):
        """Enter account number and select account via checkbox or radio button."""

        input_box = self.__account_search_input()
        input_box.clear()
        input_box.send_keys(str(acc_num))

        # Attempt to find checkbox
        try:
            check_box = self.__account_check_box()
            # Check if checkbox is displayed and selectable
            logging.info("Checking the account Check Box.")
            if check_box.is_displayed() and not check_box.is_selected():
                check_box.click()
                return
        except Exception:
            pass  # If not found, proceed to radio button

        # Attempt to find radio button
        try:
            radio_button = self.__account_radio_button()
            logging.info("Checking the account Radio Button.")
            if radio_button.is_displayed():
                radio_button.click()
                logging.info("Clicked on Account Radio Button")
                return
        except Exception:
            pass  # If not found, handle as needed

        # If neither found, raise an explicit error
        raise TimeoutException("Neither checkbox nor radio button found for account selection.")
    @find_element(By.ID,"requestid")
    def __request_id_input(self):pass

    @find_element(By.XPATH, "//span[text()='Customer Sub Type']")
    def __customer_sub_type_dropdown(self):
        pass
    def select_customer_sub_type_dropdown(self,customer_sub_type):
        logging.info("Selecting the Customer Sub Type= {}".format(customer_sub_type))
        self.select_mat_option(self.__customer_sub_type_dropdown(),customer_sub_type)
    @find_element(By.XPATH, "//span[text()='Segments']")
    def __customer_segments(self):pass

    def select_customer_segments(self,segments):
        self.select_mat_checkbox(self.__customer_segments(),segments)
    def click_on_fetch_button(self):
        self.__fetch_button().click()
    def click_on_deactivation_date(self):
        # Click calendar icon
        self.__deactivation_date().click()

        # Get today's date as number (day)
        today_day = datetime.now().day

        # Wait for calendar to be visible
        wait = WebDriverWait(self.driver, 10)

        # Build XPATH specifically matching today's day in enabled state
        today_locator = (
            By.XPATH, f"//mat-calendar//td[not(contains(@class,'mat-calendar-body-disabled'))]"
                      f"/div[normalize-space(text())='{today_day}']"
        )

        # Wait for today's cell to be clickable
        today_date = wait.until(EC.element_to_be_clickable(today_locator))

        # Click it
        today_date.click()
    def click_on_create_request_button(self):
        self.__create_request_button().click()
    def get_customer_name(self) -> str:
        customer_name_element = self.__customer_name_cell()
        return customer_name_element.text.strip()
    def click_update_request_by_customer(self, customer_name: str):
        """
        Find the row matching the given customer name and click the Update Request (eye) icon.
        :param customer_name: str - name of the customer (e.g. "Raj Behera")
        """
        wait = WebDriverWait(self.driver, 10)

        # Dynamic row locator based on Customer Name column
        row_locator = (
            By.XPATH,
            f"//table//tr[td[contains(normalize-space(.), '{customer_name}')]]"
        )

        # Wait for row to exist
        row_elem = wait.until(EC.presence_of_element_located(row_locator))

        # Inside that row, locate the Update Request (eye icon)
        update_icon_locator = (
            By.XPATH,
            f".//td//em[contains(@class,'fa-eye')]"
        )

        update_icon_elem = row_elem.find_element(*update_icon_locator)

        # Click the update request icon
        update_icon_elem.click()
    def select_action_check_box(self):
        self.__get_action_checkbox().click()
    def click_on_process_now_button(self):
        self.__process_now_button().click()
    def click_on_resume_acc_radio_button(self):
        self.__resume_acc_radio_button().click()
    def check_if_alert_box_displayed(self):
        try:
            self.wait_for_page_to_load()
            self.__alert_dialog_div().is_displayed()
            logging.info("Alert Box is  Displayed")
            return True
        except TimeoutException:
            logging.info("AlertBox is Not Displayed")
            return False
        except Exception :
            return False
    def check_if_customer_details_present(self):
        try:
            self.__customer_name_cell().is_displayed()
            return True
        except TimeoutException:
            logging.error("Customer Details are not fount after searching")
            self.__customer_name_cell().is_displayed()
        except Exception:
            logging.error("Customer Details are not fount after searching")
            return False

    def select_request_level_radio_button(self,request_level):
        logging.info("Request Level = {}".format(request_level))
        self.__select_resume_account_radio_button().click()

    def enter_request_id(self,request_id):
        logging.info("Entering the Request ID = {} , in Request Search Page.")
        self.__request_id_input().send_keys(request_id)

    @find_element(By.XPATH, "//tr[td[contains(normalize-space(.), 'Suspended')]]//mat-radio-button/label")
    def __suspended_contract_radio_label(self):
        pass

    def click_suspended_contract_radio_button(self):
        self.wait_for_page_to_load()
        logging.info("Locating the Suspended Contract Radio Button.")
        self.__suspended_contract_radio_label().click()

    def click_on_resume_contract_button(self):
        logging.info("Clicking on Resume Contract Radio Button")
        self.wait_for_page_to_load()
        self.__resume_contract_radio_button().click()

    def click_on_acc_check_box(self):
        # Attempt to find checkbox
        try:
            check_box = self.__account_check_box()
            # Check if checkbox is displayed and selectable
            logging.info("Checking the account Check Box.")
            if check_box.is_displayed() and not check_box.is_selected():
                check_box.click()
                logging.info("Clicked on check Box")
                return
        except Exception as e:
            logging.error("Account Not Found. {}".format(e))
            pass  # If not found, proceed to radio button

    def click_on_prepaid_acc_radio_button(self):
        # Attempt to find radio button
        try:
            radio_button = self.__account_radio_button()
            logging.info("Checking the account Radio Button.")
            if radio_button.is_displayed():
                radio_button.click()
                logging.info("Clicked on Account Radio Button")
                return
        except Exception as e:
            logging.error("Prepaid Account Radio Button is not found. {}".format(e))

    def click_on_acc_radio_button(self):
        # Attempt to find radio button
        try:
            radio_button = self.__account_radio_button()
            logging.info("Checking the account Radio Button.")
            if radio_button.is_displayed():
                radio_button.click()
                logging.info("Clicked on Account Radio Button")
                return
        except Exception as e:
            logging.error(" Account Radio Button is not found. {}".format(e))