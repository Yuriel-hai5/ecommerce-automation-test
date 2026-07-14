"""
基础页面对象类
封装通用操作：查找元素、点击、输入、等待、截图等
"""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import allure
import os


class BasePage:
    """页面对象基类"""

    def __init__(self, driver: WebDriver, base_url: str = ""):
        self.driver = driver
        self.base_url = base_url
        self.timeout = 10

    def open(self, url: str = ""):
        """打开页面"""
        full_url = f"{self.base_url}{url}"
        self.driver.get(full_url)

    def find(self, locator: tuple) -> WebElement:
        """查找元素"""
        by, value = locator
        return self.driver.find_element(by, value)

    def find_all(self, locator: tuple) -> list:
        """查找多个元素"""
        by, value = locator
        return self.driver.find_elements(by, value)

    def click(self, locator: tuple):
        """点击元素"""
        element = self.wait_for_clickable(locator)
        element.click()

    def input_text(self, locator: tuple, text: str):
        """输入文本"""
        element = self.wait_for_visible(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        """获取元素文本"""
        return self.wait_for_visible(locator).text

    def wait_for_visible(self, locator: tuple, timeout: int = None):
        """等待元素可见"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.visibility_of_element_located(locator))

    def wait_for_clickable(self, locator: tuple, timeout: int = None):
        """等待元素可点击"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.element_to_be_clickable(locator))

    def wait_for_present(self, locator: tuple, timeout: int = None):
        """等待元素存在于DOM中"""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def is_element_present(self, locator: tuple, timeout: int = 3) -> bool:
        """判断元素是否存在"""
        try:
            self.wait_for_present(locator, timeout)
            return True
        except TimeoutException:
            return False

    def take_screenshot(self, name: str = "screenshot"):
        """截图并附加到Allure报告"""
        screenshot = self.driver.get_screenshot_as_png()
        allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_title(self) -> str:
        return self.driver.title
