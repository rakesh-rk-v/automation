from POM.Common.Raptr_Base_Page import RpBasePage
from Utils.selenium_wrapper import *


class PrepaidToPostpaid(RpBasePage):
    def __init__(self, driver):
        super().__init__(driver)

    # region locators
    @find_element(By.XPATH, "//span[text()='Customer Sub Type']")
    def __customer_sub_type_dropdown(self): pass

    @find_element(By.XPATH, "//span[text()='Segments']")
    def __segments_dropdown(self):pass

    @find_element(By.XPATH,"//input[@data-placeholder='Address Line1']")
    def __address_line_one_textbox(self): pass

    @find_element(By.XPATH, "//input[@data-placeholder='City']")
    def __city_textbox(self): pass

    @find_element(By.XPATH, "//input[@data-placeholder='State']")
    def __state_textbox(self): pass

    @find_element(By.XPATH, "//input[@data-placeholder='Country']")
    def __country_textbox(self): pass

    @find_element(By.XPATH, "//button[text()='Get Plans']")
    def __get_plans_button(self): pass

    @find_element(By.XPATH, "(//span[@class='mat-checkbox-inner-container mat-checkbox-inner-container-no-side-margin'])[1]")
    def __rate_plan_button(self):pass

    # endregion

    # region methods

    def select_customer_sub_type_dropdown(self,sub_type):
        self.select_mat_option(self.__customer_sub_type_dropdown(),sub_type)

    def select_segment_dropdown(self,segment):
        self.select_mat_option(self.__segments_dropdown(),segment)
        self.escape()

    def enter_in_address_line_one_textbox(self,add):
        self.__address_line_one_textbox().send_keys(add)

    def enter_in_city_textbox(self,city):
        self.__city_textbox().send_keys(city)

    def enter_in_state_textbox(self,state):
        self.__state_textbox().send_keys(state)

    def enter_in_country_textbox(self,country):
        self.__country_textbox().send_keys(country)

    def click_on_get_plans_button(self):
        self.__get_plans_button().click()

    def click_on_rate_plan_button(self):
        self.__rate_plan_button().click()

    def click_on_rp_checkbox(self, plan_name):
        xpath_checkbox = f"//div[b[normalize-space(text())='{plan_name}']]/ancestor::div[@class='row'][1]//input[@type='checkbox']"
        wait = WebDriverWait(self.driver, 15)

        checkbox = wait.until(EC.presence_of_element_located((By.XPATH, xpath_checkbox)))

        #Scrolling
        self.driver.execute_script("""
            var el = arguments[0], offset = 70;
            var pos = el.getBoundingClientRect().top + window.pageYOffset - offset;
            window.scrollTo({top: pos, behavior: 'smooth'});
        """, checkbox)

        time.sleep(0.5)

        xpath_label = f"//div[b[normalize-space(text())='{plan_name}']]/ancestor::div[@class='row'][1]//mat-checkbox//label"
        label = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_label)))

        try:
            label.click()
        except:
            self.driver.execute_script("arguments[0].click();", label)
