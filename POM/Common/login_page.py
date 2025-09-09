from POM.Common.Raptr_Base_Page import RpBasePage
from Utils.selenium_wrapper import *


class LoginPage(RpBasePage):
    def __init__(self, driver):
        super().__init__(driver)
        # self.driver = driver

    # region locators
    @find_element(By.ID,"userID")
    def __username_input(self):pass

    @find_element(By.ID, "userpassword")
    def __password_input(self): pass

    @find_element(By.XPATH, "//button[text()='Login']")
    def __login_button(self): pass

    # endregion

    # region methods

    def enter_username(self, username):
        self.__username_input().send_keys(username)

    def enter_password(self, password):
        self.__password_input().send_keys(password)

    def click_login(self):
        self.__login_button().click()


