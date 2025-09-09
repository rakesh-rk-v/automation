from POM.CMS.Cms_Base_Page import CmsBasePage
from Utils.selenium_wrapper import *


class SuspendService(CmsBasePage):
    def __init__(self, driver):
        super().__init__(driver)

    @find_element(By.XPATH, "//span[@class='mat-checkbox-inner-container']")
    def __account_checkbox(self): pass

    @find_element(By.XPATH, "//button[text()='Fetch']")
    def __fetch_button(self):pass

    @find_element(By.XPATH, "//span[contains(text(),'Suspend Account')]")
    def __suspend_account_radio_button(self):pass

    @find_element(By.XPATH, "//span[contains(text(),'Suspend Contract')]")
    def __suspend_contract_radio_button(self): pass

    def click_on_account_checkbox(self):
        self.__account_checkbox().click()

    def click_on_fetch_button(self):
        self.__fetch_button().click()

    def click_on_suspend_account_radio_button(self):
        self.__suspend_account_radio_button().click()

    def click_on_suspend_contract_raio_button(self):
        self.__suspend_contract_radio_button().click()