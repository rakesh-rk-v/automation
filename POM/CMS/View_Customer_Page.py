from selenium.webdriver.common.by import By

from POM.Common.Raptr_Base_Page import RpBasePage
from Utils.selenium_wrapper import find_element


class Search_Customer_Page(RpBasePage):
    def __init__(self, driver):
        super().__init__(driver)

    @find_element(By.ID,"billingAccountID")
    def __search_by_billing_acc_id(self):pass

    def enter_billing_acc_id(self ,billing_acc_id):
        self.__search_by_billing_acc_id().send_keys(billing_acc_id)

    def check_if_customer_is_unavailable(self):
        self.__alert_dialog_div()