from Utils.selenium_wrapper import *


class RpBasePage(SeleniumWrapper):
    def __init__(self, driver):
        super().__init__(driver)

    # region locators
    @find_element(By.XPATH, '//h1[text()="PCS"]')
    def __pcs_link(self): pass

    @find_element(By.XPATH, "//h1[text()='PMS']")
    def __pms_link(self): pass

    @find_element(By.XPATH, "//h1[text()='CMS']")
    def __cms_link(self): pass

    @find_element(By.XPATH, "//h1[text()='Configurator']")
    def __rms_configurator_link(self): pass

    @find_element(By.XPATH, "//h1[text()='UMS']")
    def __ums_link(self): pass

    @find_element(By.XPATH, "//h1[text()='VMS']")
    def __vms_link(self): pass

    @find_element(By.XPATH, "(//div[@class='mat-dialog-content alert-content']/p)[2]", wait_time=30)
    def __alert_dialog_div(self): pass

    @find_element(By.XPATH, "(//span[contains(text(),'OK')])[1]")
    def __alert_dialog_ok_button_one(self): pass

    @find_element(By.XPATH, "(//span[contains(text(),'OK')])[2]")
    def __alert_dialog_ok_button_two(self): pass

    # Yopmail Locators
    @find_element(By.XPATH, "//input[@id='login']")
    def __yopmail_login_textbox(self): pass

    @find_element(By.XPATH, "//div[@id='refreshbut']/button")
    def __check_inbox_arrow(self): pass

    # endregion

    # region methods

    def click_pcs_link(self):
        self.__pcs_link().click()
        self.wait_for_page_to_load()
        self.driver.switch_to.window(self.driver.window_handles[1])

    def click_on_pms_link(self):
        self.__pms_link().click()
        self.wait_for_page_to_load()
        self.driver.switch_to.window(self.driver.window_handles[1])

    def click_on_cms_module(self):
        self.__cms_link().click()
        self.wait_for_page_to_load()
        self.driver.switch_to.window(self.driver.window_handles[1])

    def click_on_rms_link(self):
        self.__rms_configurator_link().click()
        self.wait_for_page_to_load()
        self.driver.switch_to.window(self.driver.window_handles[1])

    def click_on_ums_link(self):
        self.__ums_link().click()
        self.wait_for_page_to_load()
        self.driver.switch_to.window(self.driver.window_handles[1])

    def click_on_vms_link(self):
        self.__vms_link().click()
        self.wait_for_page_to_load()
        self.driver.switch_to.window(self.driver.window_handles[1])

    def get_alert_dialog_text(self):
        return self.__alert_dialog_div().text

    def click_on_alert_dialog_ok_button_one(self):
        self.__alert_dialog_ok_button_one().click()

    def click_on_alert_dialog_ok_button_two(self):
        self.__alert_dialog_ok_button_two().click()

    def navigate_to_url(self,url):
        self.driver.get(url)
    def enter_yopmail_in_textbox(self,mail):
        self.__yopmail_login_textbox().clear()
        self.wait_for_page_to_load()
        self.__yopmail_login_textbox().send_keys(mail)

    def click_on_inbox_arrow(self):
        self.__check_inbox_arrow().click()
        self.wait_for_page_to_load()
