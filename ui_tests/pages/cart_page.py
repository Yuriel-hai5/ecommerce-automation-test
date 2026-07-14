"""
购物车页面对象
"""
from selenium.webdriver.common.by import By
from .base_page import BasePage


class CartPage(BasePage):
    """购物车页面"""

    CART_ITEMS = (By.CLASS_NAME, "cart-item")
    ITEM_QUANTITY_INPUT = (By.CLASS_NAME, "quantity-input")
    ITEM_REMOVE_BUTTON = (By.CLASS_NAME, "remove-btn")
    TOTAL_AMOUNT = (By.ID, "total-amount")
    CHECKOUT_BUTTON = (By.ID, "checkout-btn")
    CLEAR_CART_BUTTON = (By.ID, "clear-cart-btn")
    EMPTY_MESSAGE = (By.CLASS_NAME, "empty-cart-msg")

    def open_cart(self):
        self.open("/cart")
        return self

    def get_item_count(self) -> int:
        return len(self.find_all(self.CART_ITEMS))

    def remove_first_item(self):
        buttons = self.find_all(self.ITEM_REMOVE_BUTTON)
        if buttons:
            buttons[0].click()
        return self

    def click_checkout(self):
        self.click(self.CHECKOUT_BUTTON)
        return self

    def click_clear_cart(self):
        self.click(self.CLEAR_CART_BUTTON)
        return self

    def get_total_amount(self) -> str:
        return self.get_text(self.TOTAL_AMOUNT)

    def is_cart_empty(self) -> bool:
        return self.is_element_present(self.EMPTY_MESSAGE)
