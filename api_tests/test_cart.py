"""
购物车模块接口测试
覆盖：添加商品、查询购物车、清空购物车、库存校验、重复添加
"""
import pytest
import allure


@allure.feature("购物车模块")
@allure.story("添加商品到购物车")
class TestCartAdd:

    @allure.title("正常添加商品")
    @pytest.mark.smoke
    @pytest.mark.cart
    def test_cart_add_success(self, auth_client):
        resp = auth_client.post("/api/cart/add", json_data={"productId": "1001", "quantity": 1})
        auth_client.assert_response(resp, expected_status=200, expected_keys=["data"])
        items = resp.json()["data"]
        assert any(i["productId"] == "1001" and i["quantity"] == 1 for i in items)

    @allure.title("添加多个同商品（数量累加）")
    @pytest.mark.cart
    def test_cart_add_same_product_accumulate(self, auth_client):
        auth_client.post("/api/cart/add", json_data={"productId": "1003", "quantity": 1})
        resp = auth_client.post("/api/cart/add", json_data={"productId": "1003", "quantity": 2})
        auth_client.assert_response(resp, expected_status=200)
        items = resp.json()["data"]
        item = next(i for i in items if i["productId"] == "1003")
        assert item["quantity"] == 3

    @allure.title("库存不足")
    @pytest.mark.cart
    def test_cart_add_out_of_stock(self, auth_client):
        # 1004库存为0
        resp = auth_client.post("/api/cart/add", json_data={"productId": "1004", "quantity": 1})
        auth_client.assert_response(resp, expected_status=400)
        assert "库存不足" in resp.json()["message"]

    @allure.title("未登录添加购物车")
    @pytest.mark.cart
    def test_cart_add_no_auth(self, api_client):
        resp = api_client.post("/api/cart/add", json_data={"productId": "1001", "quantity": 1})
        api_client.assert_response(resp, expected_status=401)


@allure.feature("购物车模块")
@allure.story("查询购物车")
class TestCartList:

    @allure.title("查询已登录用户的购物车")
    @pytest.mark.smoke
    @pytest.mark.cart
    def test_cart_list_success(self, auth_client, sample_cart):
        resp = auth_client.get("/api/cart/list")
        auth_client.assert_response(resp, expected_status=200, expected_keys=["data"])
        data = resp.json()["data"]
        assert "items" in data
        assert "totalAmount" in data
        assert len(data["items"]) > 0
        assert data["totalAmount"] > 0

    @allure.title("未登录查询购物车")
    @pytest.mark.cart
    def test_cart_list_no_auth(self, api_client):
        resp = api_client.get("/api/cart/list")
        api_client.assert_response(resp, expected_status=401)


@allure.feature("购物车模块")
@allure.story("清空购物车")
class TestCartClear:

    @allure.title("清空购物车")
    @pytest.mark.smoke
    @pytest.mark.cart
    def test_cart_clear_success(self, auth_client, sample_cart):
        resp = auth_client.post("/api/cart/clear")
        auth_client.assert_response(resp, expected_status=200)
        # 验证已清空
        resp2 = auth_client.get("/api/cart/list")
        assert resp2.json()["data"]["items"] == []
