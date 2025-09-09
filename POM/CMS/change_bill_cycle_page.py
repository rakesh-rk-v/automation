from selenium.webdriver.common.by import By

from POM.Common.Raptr_Base_Page import RpBasePage
from Utils.selenium_wrapper import find_element


class Change_Bill_Cycle(RpBasePage):
    @find_element(By.XPATH,"//span[text()='New Bill Cycle']")
    def __new_bill_cycle_dropdown(self):pass

    def select_new_bill_cycle(self,new_bill_cycle):
        self.wait_for_page_to_load()
        self.select_mat_option(self.__new_bill_cycle_dropdown(),new_bill_cycle)