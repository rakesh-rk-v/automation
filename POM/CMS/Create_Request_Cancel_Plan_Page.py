from POM.Common.Raptr_Base_Page import RpBasePage
from Utils.selenium_wrapper import *


class CancelPlan(RpBasePage):
    def __init__(self, driver):
        super().__init__(driver)

    # region locators
    @find_element(By.XPATH, "(//span[@class='mat-checkbox-inner-container mat-checkbox-inner-container-no-side-margin'])[2]")
    def __action_checkbox(self):pass

    @find_element(By.XPATH, "(//span[@class='mat-radio-container'])[1]")
    def __account_radio_button(self):pass

    # endregion

    # region methods
    def click_on_action_checkbox(self):
        self.__action_checkbox().click()

    def click_on_account_radio_button(self):
        self.__account_radio_button().click()
