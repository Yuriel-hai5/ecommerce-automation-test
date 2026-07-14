"""
订单模块接口测试
覆盖：创建订单、订单详情、取消订单、订单状态流转、优惠券计算、库存扣减与回滚
"""
import pytest
import allure


@allure.feature("订单模块")
@allure.story("创建订单")
class TestOrderCreate:

    @allure.title("正常创建订单（无优惠券）")
    @pytest.mark.smoke
    @pytest.mark.order
    def test_order_create_success(self, auth_client, sample_cart):
        resp = auth_client.post("/api/order/create", json_data={"address": "北京市海淀区测试路1号"})
        auth_client.assert_response(resp, expected_status=200, expected_keys=["data"])
        data = resp.json()["data"]
        assert "orderId" in data
        assert data["status"] == "待支付"
        assert data["finalAmount"] > 0

    @allure.title("创建订单（使用固定金额优惠券）")
    @pytest.mark.order
    def test_order_create_with_fixed_coupon(self, auth_client, sample_cart):
        resp = auth_client.post("/api/order/create", json_data={"address": "上海", "couponCode": "SAVE100"})
        auth_client.assert_response(resp, expected_status=200)
        data = resp.json()["data"]
        # 优惠券减100
        assert data["finalAmount"] < sum(i["price"] * i["quantity"] for i in sample_cart.get("/api/cart/list").json()["data"]["items"])

    @allure.title("创建订单（使用百分比优惠券）")
    @pytest.mark.order
    def test_order_create_with_percent_coupon(self, auth_client, sample_cart):
        # 添加高价商品确保满足门槛
        auth_client.post("/api/cart/add", json_data={"productId": "1002", "quantity": 1})
        resp = auth_client.post("/api/order/create", json_data={"couponCode": "DISCOUNT20"})
        auth_client.assert_response(resp, expected_status=200)

    @allure.title("购物车为空时创建订单")
    @pytest.mark.order
    def test_order_create_empty_cart(self, auth_client):
        auth_client.post("/api/cart/clear")
        resp = auth_client.post("/api/order/create")
        auth_client.assert_response(resp, expected_status=400)
        assert "购物车为空" in resp.json()["message"]

    @allure.title("未登录创建订单")
    @pytest.mark.order
    def test_order_create_no_auth(self, api_client):
        resp = api_client.post("/api/order/create")
        api_client.assert_response(resp, expected_status=401)

    @allure.title("创建订单后购物车被清空")
    @pytest.mark.smoke
    @pytest.mark.order
    def test_order_create_cart_cleared(self, auth_client, sample_cart):
        auth_client.post("/api/order/create")
        resp = auth_client.get("/api/cart/list")
        assert resp.json()["data"]["items"] == []

    @allure.title("库存不足时创建订单失败")
    @pytest.mark.order
    def test_order_create_stock_insufficient(self, auth_client):
        # 先把库存占完（1003库存100，1004库存0）
        auth_client.post("/api/cart/add", json_data={"productId": "1004", "quantity": 1})
        resp = auth_client.post("/api/order/create")
        auth_client.assert_response(resp, expected_status=400)
        assert "库存不足" in resp.json()["message"]


@allure.feature("订单模块")
@allure.story("订单详情")
class TestOrderDetail:

    @allure.title("获取订单详情")
    @pytest.mark.smoke
    @pytest.mark.order
    def test_order_detail_success(self, auth_client, sample_cart):
        create_resp = auth_client.post("/api/order/create").json()["data"]
        order_id = create_resp["orderId"]
        resp = auth_client.get(f"/api/order/{order_id}")
        auth_client.assert_response(resp, expected_status=200, expected_keys=["data"])
        data = resp.json()["data"]
        assert data["id"] == order_id
        assert data["status"] in ["待支付", "已支付", "已取消"]

    @allure.title("获取不存在的订单")
    @pytest.mark.order
    def test_order_detail_not_found(self, auth_client):
        resp = auth_client.get("/api/order/NOTEXIST999")
        auth_client.assert_response(resp, expected_status=404)


@allure.feature("订单模块")
@allure.story("取消订单")
class TestOrderCancel:

    @allure.title("取消待支付订单")
    @pytest.mark.smoke
    @pytest.mark.order
    def test_order_cancel_success(self, auth_client, sample_cart):
        create_resp = auth_client.post("/api/order/create").json()["data"]
        order_id = create_resp["orderId"]
        # 记录取消前库存
        product = auth_client.get("/api/product/1001").json()["data"]
        stock_before = product["stock"]

        resp = auth_client.post(f"/api/order/{order_id}/cancel")
        auth_client.assert_response(resp, expected_status=200)

        # 验证状态变更
        detail = auth_client.get(f"/api/order/{order_id}").json()["data"]
        assert detail["status"] == "已取消"

        # 验证库存回滚
        product_after = auth_client.get("/api/product/1001").json()["data"]
        assert product_after["stock"] == stock_before + 1

    @allure.title("取消已支付订单失败")
    @pytest.mark.order
    def test_order_cancel_paid_order(self, auth_client, sample_cart):
        create_resp = auth_client.post("/api/order/create").json()["data"]
        order_id = create_resp["orderId"]
        # 先支付
        auth_client.post("/api/pay", json_data={"orderId": order_id, "payMethod": "wechat"})
        # 再取消
        resp = auth_client.post(f"/api/order/{order_id}/cancel")
        auth_client.assert_response(resp, expected_status=400)
        assert "只有待支付订单可取消" in resp.json()["message"]

    @allure.title("取消不存在的订单")
    @pytest.mark.order
    def test_order_cancel_not_found(self, auth_client):
        resp = auth_client.post("/api/order/FAKE123/cancel")
        auth_client.assert_response(resp, expected_status=404)
