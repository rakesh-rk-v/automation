from selenium.webdriver.common.by import By

from POM.Common.Raptr_Base_Page import RpBasePage
from Utils.selenium_wrapper import find_element


class ChangeBillingAddressPage(RpBasePage):
    @find_element(By.XPATH,"(//button[text()='Yes'])[2]")
    def __yes_button(self):pass

    @find_element(By.ID, "addresstype")
    def __address_type_input(self): pass

    @find_element(By.ID, "addressline1")
    def __address_line1_input(self): pass

    @find_element(By.ID, "addressline2")
    def __address_line2_input(self): pass

    @find_element(By.ID, "Cities")
    def __city_input(self): pass

    @find_element(By.ID, "addressstate")
    def __state_input(self): pass

    @find_element(By.ID, "addresscountry")
    def __country_input(self): pass

    @find_element(By.XPATH, "//button[contains(@class,'submitButton') and text()='Create Request']")
    def __create_request_button(self): pass

    def click_on_yes_button(self):
        self.wait_for_page_to_load()
        self.__yes_button().click()

    def enter_address_type(self, address_type):
        self.__address_type_input().send_keys(address_type)

    def enter_address_line1(self, address):
        self.__address_line1_input().send_keys(address)

    def enter_address_line2(self, address):
        self.__address_line2_input().send_keys(address)

    def enter_city(self, city):
        self.__city_input().send_keys(city)

    def enter_state(self, state):
        self.__state_input().send_keys(state)

    def enter_country(self, country):
        self.__country_input().send_keys(country)

    def click_create_request(self):
        self.__create_request_button().click()
