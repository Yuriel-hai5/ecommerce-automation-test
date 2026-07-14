"""
商品列表/详情页面对象
"""
from selenium.webdriver.common.by import By
from .base_page import BasePage


class ProductPage(BasePage):
    """商品页面"""

    SEARCH_INPUT = (By.ID, "search-keyword")
    SEARCH_BUTTON = (By.ID, "search-btn")
    PRODUCT_CARDS = (By.CLASS_NAME, "product-card")
    PRODUCT_NAME = (By.CLASS_NAME, "product-name")
    PRODUCT_PRICE = (By.CLASS_NAME, "product-price")
    ADD_TO_CART_BUTTON = (By.CLASS_NAME, "add-cart-btn")
    CATEGORY_FILTER = (By.ID, "category-select")

    def open_product_list(self):
        self.open("/products")
        return self

    def search_product(self, keyword: str):
        self.input_text(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BUTTON)
        return self

    def select_category(self, category: str):
        from selenium.webdriver.support.ui import Select
        select = Select(self.find(self.CATEGORY_FILTER))
        select.select_by_visible_text(category)
        return self

    def get_product_count(self) -> int:
        return len(self.find_all(self.PRODUCT_CARDS))

    def add_first_to_cart(self):
        buttons = self.find_all(self.ADD_TO_CART_BUTTON)
        if buttons:
            buttons[0].click()
        return self

    def get_first_product_name(self) -> str:
        return self.get_text(self.PRODUCT_NAME)
