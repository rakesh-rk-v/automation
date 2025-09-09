import allure
import pytest


@allure.title("Post-Pre-Movement Request")
@allure.description_html("""
Test Description:create request by Filtering request type as "service change",<br>
request subtype as "service change requesTC" <br>
 and request name as "Post-Pre-Movement"
""")
@allure.epic("CMS Project")
@allure.feature("Customer Requests")
@allure.story("Positive Customer Request Flow")
@allure.severity(allure.severity_level.CRITICAL)
@allure.id("TC_3467")
@pytest.mark.datafile("post-pre-migration.xlsx")
def test_customer_requests(driver, screenshot_manager, _data_index):pass