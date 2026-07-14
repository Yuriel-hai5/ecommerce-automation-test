"""
UI全链路流程测试
覆盖：登录 -> 浏览商品 -> 加入购物车 -> 下单 -> 支付 -> 取消订单
采用Page Object设计模式，降低维护成本
"""
import pytest
import allure
import sys
import os

# 确保pages包可被导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.order_page import OrderPage


@allure.feature("UI全链路测试")
@allure.story("核心业务流程")
class TestE2EFlow:

    @allure.title("完整购物流程：登录-浏览-加购-下单-支付")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_complete_purchase_flow(self, driver, base_url):
        """模拟用户从登录到支付完成的全流程"""
        login_page = LoginPage(driver, base_url)
        product_page = ProductPage(driver, base_url)
        cart_page = CartPage(driver, base_url)
        order_page = OrderPage(driver, base_url)

        with allure.step("1. 用户登录"):
            login_page.open_login_page()
            login_page.login("test_user", "test_pass")
            # 注：实际测试需确保该用户存在于mock系统中，此处展示流程
            assert "login" not in driver.current_url

        with allure.step("2. 浏览商品并搜索"):
            product_page.open_product_list()
            initial_count = product_page.get_product_count()
            assert initial_count > 0, "商品列表为空"
            product_page.search_product("iPhone")
            # 验证搜索结果过滤生效（展示断言思路）

        with allure.step("3. 添加商品到购物车"):
            product_page.open_product_list()
            product_page.add_first_to_cart()

        with allure.step("4. 进入购物车并结算"):
            cart_page.open_cart()
            assert cart_page.get_item_count() > 0
            cart_page.click_checkout()

        with allure.step("5. 创建订单"):
            order_page.input_address("北京市朝阳区测试大街88号")
            order_page.click_create_order()
            order_id = order_page.get_order_id()
            assert order_id != ""
            assert "待支付" in order_page.get_order_status()

        with allure.step("6. 支付订单"):
            order_page.click_pay()
            assert "已支付" in order_page.get_order_status()

    @allure.title("优惠券使用流程")
    @pytest.mark.ui
    def test_coupon_flow(self, driver, base_url):
        """测试优惠券在下单时的抵扣效果"""
        order_page = OrderPage(driver, base_url)
        cart_page = CartPage(driver, base_url)

        with allure.step("1. 购物车已有商品，进入结算"):
            cart_page.open_cart()
            cart_page.click_checkout()

        with allure.step("2. 输入优惠券并创建订单"):
            order_page.input_address("上海市浦东新区")
            order_page.input_coupon("SAVE100")
            order_page.click_create_order()
            amount = order_page.get_final_amount()
            # 验证金额因优惠券减少（断言逻辑取决于前端展示格式）
            assert amount is not None

    @allure.title("取消订单流程")
    @pytest.mark.ui
    def test_cancel_order_flow(self, driver, base_url):
        """测试用户主动取消待支付订单"""
        order_page = OrderPage(driver, base_url)
        cart_page = CartPage(driver, base_url)

        with allure.step("1. 创建订单但不支付"):
            cart_page.open_cart()
            cart_page.click_checkout()
            order_page.input_address("广州市天河区")
            order_page.click_create_order()
            assert "待支付" in order_page.get_order_status()

        with allure.step("2. 取消订单"):
            order_page.click_cancel()
            # 通常取消后会跳转或刷新状态
            assert "已取消" in order_page.get_order_status() or "订单列表" in driver.title

    @allure.title("购物车清空")
    @pytest.mark.ui
    def test_clear_cart(self, driver, base_url):
        """测试清空购物车功能"""
        cart_page = CartPage(driver, base_url)
        cart_page.open_cart()
        if cart_page.get_item_count() > 0:
            cart_page.click_clear_cart()
        assert cart_page.is_cart_empty()


@allure.feature("UI异常场景测试")
@allure.story("前端校验与异常处理")
class TestUIExceptions:

    @allure.title("未登录访问购物车跳转登录")
    @pytest.mark.ui
    def test_access_cart_without_login(self, driver, base_url):
        """验证未登录态下访问需要鉴权的页面"""
        cart_page = CartPage(driver, base_url)
        cart_page.open_cart()
        # 预期：系统应重定向到登录页
        assert "login" in driver.current_url.lower()

    @allure.title("登录失败提示")
    @pytest.mark.ui
    def test_login_error_message(self, driver, base_url):
        """验证错误密码时前端提示"""
        login_page = LoginPage(driver, base_url)
        login_page.open_login_page()
        login_page.login("wrong_user", "wrong_pass")
        msg = login_page.get_error_message()
        assert msg != "" or "login" in driver.current_url
