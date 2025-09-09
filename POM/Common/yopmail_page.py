from selenium.webdriver.common.by import By

from POM.Common.Raptr_Base_Page import RpBasePage


class Mail(RpBasePage):
    def click_on_mails(self, num):
        iframe = self.driver.find_element(By.XPATH, "//iframe[@name='ifinbox']")
        self.driver.switch_to.frame(iframe)
        self.driver.find_element(By.XPATH, "(//button[@class='lm'])[" + str(num) + "]").click()