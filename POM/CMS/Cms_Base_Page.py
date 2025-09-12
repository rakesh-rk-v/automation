from POM.Common.Raptr_Base_Page import RpBasePage
from Utils.selenium_wrapper import *


class CmsBasePage(RpBasePage):
    def __init__(self, driver):
        super().__init__(driver)

    # region locators

    @find_element(By.XPATH, "//button[text()=' Customer Management ']")
    def __customer_management_dropdown(self):pass

    @find_element(By.XPATH, "//button[text()='View Customers']")
    def __view_customer_button(self):pass

    @find_element(By.XPATH, "//button[text()=' Customer Requests ']")
    def __customer_requests_dropdown(self):pass

    @find_element(By.XPATH, "//button[text()='Create Request']")
    def __create_request_button(self):pass

    @find_element(By.XPATH, "//button[text()='Request Search']")
    def __request_search_button(self):pass

    @find_element(By.XPATH, "//button[text()='Search ']")
    def __search_filter_button(self):pass

    @find_element(By.XPATH, "//span[text()='Search By']")
    def __search_by_dropdown(self):pass

    @find_element(By.XPATH, "//input[@data-placeholder='Account ID']")
    def __account_id_textbox(self):pass

    @find_element(By.XPATH, "//input[@data-placeholder='Account Name']")
    def __account_name_textbox(self):pass

    @find_element(By.XPATH, "//input[@data-placeholder='Customer ID']")
    def __customer_id_textbox(self):pass

    @find_element(By.XPATH, "//input[@id='firstName']")
    def __customer_name_dropdown(self):pass

    @find_element(By.XPATH, "//em[@class='fa fa-search']")
    def __search_icon(self):pass

    @find_element(By.XPATH, "//em[@mattooltip='Create Request']")
    def __create_request_icon(self):pass

    @find_element(By.XPATH, "//span[text()='Request Type']")
    def __request_type_dropdown(self):pass

    @find_element(By.XPATH, "//span[text()='Request Name']")
    def __request_name_dropdown(self):pass

    @find_element(By.XPATH, "//textarea[@data-placeholder='Remarks']")
    def __remarks_textbox(self):pass

    @find_element(By.XPATH, "//span[text()='Customer ']",EC.presence_of_element_located)
    def __customer_radio_button(self):pass

    @find_element(By.XPATH, "//span[text()='Customer Account ']",EC.presence_of_element_located)
    def __customer_account_radio_button(self):pass

    @find_element(By.XPATH, "//input[@data-placeholder='Filter']")
    def __filter_textbox(self):pass

    @find_element(By.XPATH, "//em[@mattooltip='Update Request']")
    def __update_request_icon(self):pass

    @find_element(By.XPATH, "//span[@class='mat-checkbox-inner-container mat-checkbox-inner-container-no-side-margin']")
    def __request_action_checkbox(self):pass

    @find_element(By.XPATH, "//button[text()='Process Now ']")
    def __process_now_button(self):pass

    @find_element(By.XPATH, "//em[@class='mat-tooltip-trigger fa fa-info-circle ng-star-inserted']")
    def __customer_360_view_icon(self):pass

    @find_element(By.XPATH, "//div[@class='col']")
    def __billing_account_name_button(self):pass

    @find_element(By.XPATH, "//div[text()='Contracts']")
    def __contracts_button(self):pass

    @find_element(By.ID,"activityAreaID")
    def __search_by_activity_area(self):pass

    @find_element(By.XPATH,"//button[text()='Reset']")
    def __reset_button(self):pass

    @find_element(By.ID,"customerCode")
    def __search_by_acc_name(self):pass


    def click_on_customer_management_dropdown(self):
        self.__customer_management_dropdown().click()

    def click_on_view_customer_button(self):
        self.__view_customer_button().click()

    def click_on_customer_request_dropdown(self):
        self.__customer_requests_dropdown().click()

    def click_on_create_request_button(self):
        self.__create_request_button().click()
    def click_on_request_search_button(self):
        self.__request_search_button().click()

    def click_on_search_filter_button(self):
        self.__search_filter_button().click()

    def select_search_by_dropdown(self,search_by):
        self.wait_for_page_to_load()
        self.select_mat_option(self.__search_by_dropdown(), search_by)

    def enter_in_account_id_textbox(self,ac_id):
        self.__account_id_textbox().send_keys(ac_id)

    def enter_in_account_name_textbox(self,name):
        self.__account_name_textbox().send_keys(name)

    def enter_in_customer_id_textbox(self,cu_id):
        self.__customer_id_textbox().send_keys(cu_id)

    def enter_in_customer_name_dropdown(self,cu_name):
        self.__customer_name_dropdown().send_keys(cu_name)

    def click_on_search_icon(self):
        self.__search_icon().click()

    def click_on_create_request_icon(self):
        self.__create_request_icon().click()

    def select_request_type_dropdown(self,req_type):
        self.select_mat_option(self.__request_type_dropdown(),req_type)

    def select_request_name_dropdown(self,req_name):
        self.select_mat_option(self.__request_name_dropdown(),req_name)

    def enter_in_remarks_textbox(self,remarks):
        self.__remarks_textbox().send_keys(remarks)

    def click_on_customer_radio_button(self):
        self.__customer_radio_button().click()

    def click_on_customer_account_radio_button(self):
        self.wait_for_page_to_load()
        self.__customer_account_radio_button().click()

    def enter_in_filter_textbox(self,re_id):
        self.__filter_textbox().send_keys(re_id)

    def click_on_update_request_button(self):
        self.__update_request_icon().click()

    def click_on_request_action_checkbox(self):
        self.__request_action_checkbox().click()

    def click_on_process_now_button(self):
        self.__process_now_button().click()

    def click_on_360_view_button(self):
        self.__customer_360_view_icon().click()

    def click_on_billing_account_dropdown_arrow(self):
        for i in range(1,3):
            self.driver.find_element(By.XPATH, "(//mat-icon[@class='mat-icon notranslate mat-icon-rtl-mirror material-icons mat-icon-no-color'])["+str(i)+"]").click()
            self.wait_for_page_to_load()

    def click_on_billing_account_name_button(self):
        self.__billing_account_name_button().click()

    def click_on_contracts_button(self):
        self.__contracts_button().click()

    def verify_the_status_of_contract(self,contract_id):
       return self.driver.find_element(By.XPATH, "//b[text()='"+contract_id+"']/parent::div/following-sibling::div[3]/b").text

    def search_by_activity_area(self,activty_area):
        self.select_mat_option(self.__search_by_activity_area(),activty_area)

    def search_by_acc_name(self,acc_name):
        self.__search_by_acc_name().send_keys(acc_name)

    def click_on_reset_button(self):
        self.__reset_button().click()


