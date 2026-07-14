"""
登录页面对象
"""
from selenium.webdriver.common.by import By
from .base_page import BasePage


class LoginPage(BasePage):
    """登录页面"""

    # 页面元素定位器
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-btn")
    ERROR_MSG = (By.CLASS_NAME, "error-message")
    REGISTER_LINK = (By.LINK_TEXT, "立即注册")

    def open_login_page(self):
        self.open("/login")
        return self

    def input_username(self, username: str):
        self.input_text(self.USERNAME_INPUT, username)
        return self

    def input_password(self, password: str):
        self.input_text(self.PASSWORD_INPUT, password)
        return self

    def click_login(self):
        self.click(self.LOGIN_BUTTON)
        return self

    def login(self, username: str, password: str):
        """完整登录流程"""
        self.input_username(username).input_password(password).click_login()
        return self

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MSG)

    def is_login_success(self) -> bool:
        return "login" not in self.get_current_url()
