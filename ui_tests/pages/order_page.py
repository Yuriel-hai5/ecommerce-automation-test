"""
订单页面对象
"""
from selenium.webdriver.common.by import By
from .base_page import BasePage


class OrderPage(BasePage):
    """订单页面"""

    ADDRESS_INPUT = (By.ID, "address")
    COUPON_INPUT = (By.ID, "coupon-code")
    CREATE_ORDER_BUTTON = (By.ID, "create-order-btn")
    ORDER_ID_DISPLAY = (By.ID, "order-id")
    ORDER_STATUS = (By.ID, "order-status")
    PAY_BUTTON = (By.ID, "pay-btn")
    CANCEL_BUTTON = (By.ID, "cancel-btn")
    FINAL_AMOUNT = (By.ID, "final-amount")

    def input_address(self, address: str):
        self.input_text(self.ADDRESS_INPUT, address)
        return self

    def input_coupon(self, coupon: str):
        self.input_text(self.COUPON_INPUT, coupon)
        return self

    def click_create_order(self):
        self.click(self.CREATE_ORDER_BUTTON)
        return self

    def click_pay(self):
        self.click(self.PAY_BUTTON)
        return self

    def click_cancel(self):
        self.click(self.CANCEL_BUTTON)
        return self

    def get_order_id(self) -> str:
        return self.get_text(self.ORDER_ID_DISPLAY)

    def get_order_status(self) -> str:
        return self.get_text(self.ORDER_STATUS)

    def get_final_amount(self) -> str:
        return self.get_text(self.FINAL_AMOUNT)
