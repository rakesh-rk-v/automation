import logging

from selenium.webdriver.common.by import By

from POM.Common.Raptr_Base_Page import RpBasePage
from Utils.selenium_wrapper import find_elements, find_element


class Change_Bill_Delivery_Mode(RpBasePage):

    @find_element(By.XPATH,"//span[text()='Delivery Mode']")
    def __delivery_mode(self):pass

    @find_element(By.XPATH,"//span[text()='Billing AccountID']")
    def __billing_acc_id(self):pass

    @find_element(By.XPATH,"//mat-option/span")
    def __select_billing_acc(self):pass

    def select_delivery_mode(self,delivery_mode):
        self.select_mat_option(self.__delivery_mode(),delivery_mode)

    def select_billing_acc_id(self):
        self.__billing_acc_id().click()
        self.__select_billing_acc().click()
        logging.info("Clicked on the Billing Account ID")