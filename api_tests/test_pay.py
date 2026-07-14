"""
支付模块接口测试
覆盖：正常支付、支付回调、重复支付、异常状态支付、签名验证
"""
import pytest
import allure


@allure.feature("支付模块")
@allure.story("订单支付")
class TestPayOrder:

    @allure.title("正常支付订单")
    @pytest.mark.smoke
    @pytest.mark.pay
    def test_pay_success(self, auth_client, sample_cart):
        order = auth_client.post("/api/order/create").json()["data"]
        resp = auth_client.post("/api/pay", json_data={
            "orderId": order["orderId"],
            "payMethod": "alipay"
        })
        auth_client.assert_response(resp, expected_status=200, expected_keys=["data"])
        assert resp.json()["data"]["status"] == "已支付"
        assert "payTime" in resp.json()["data"]

    @allure.title("微信支付")
    @pytest.mark.pay
    def test_pay_wechat(self, auth_client, sample_cart):
        order = auth_client.post("/api/order/create").json()["data"]
        resp = auth_client.post("/api/pay", json_data={
            "orderId": order["orderId"],
            "payMethod": "wechat"
        })
        auth_client.assert_response(resp, expected_status=200)
        assert resp.json()["data"]["status"] == "已支付"

    @allure.title("重复支付")
    @pytest.mark.pay
    def test_pay_duplicate(self, auth_client, sample_cart):
        order = auth_client.post("/api/order/create").json()["data"]
        auth_client.post("/api/pay", json_data={"orderId": order["orderId"]})
        resp = auth_client.post("/api/pay", json_data={"orderId": order["orderId"]})
        auth_client.assert_response(resp, expected_status=400)
        assert "不允许支付" in resp.json()["message"]

    @allure.title("支付不存在的订单")
    @pytest.mark.pay
    def test_pay_nonexist_order(self, auth_client):
        resp = auth_client.post("/api/pay", json_data={"orderId": "FAKE999"})
        auth_client.assert_response(resp, expected_status=404)

    @allure.title("未登录支付")
    @pytest.mark.pay
    def test_pay_no_auth(self, api_client):
        resp = api_client.post("/api/pay", json_data={"orderId": "ORDER123"})
        api_client.assert_response(resp, expected_status=401)


@allure.feature("支付模块")
@allure.story("支付回调")
class TestPayCallback:

    @allure.title("支付成功回调")
    @pytest.mark.smoke
    @pytest.mark.pay
    def test_callback_success(self, auth_client, sample_cart):
        order = auth_client.post("/api/order/create").json()["data"]
        resp = auth_client.post("/api/pay/callback", json_data={
            "orderId": order["orderId"],
            "status": "success",
            "sign": "mock_sign_valid"
        })
        auth_client.assert_response(resp, expected_status=200)
        # 验证订单状态
        detail = auth_client.get(f"/api/order/{order['orderId']}").json()["data"]
        assert detail["status"] == "已支付"

    @allure.title("支付失败回调")
    @pytest.mark.pay
    def test_callback_fail(self, auth_client, sample_cart):
        order = auth_client.post("/api/order/create").json()["data"]
        # 记录库存
        stock_before = auth_client.get("/api/product/1001").json()["data"]["stock"]

        resp = auth_client.post("/api/pay/callback", json_data={
            "orderId": order["orderId"],
            "status": "fail",
            "sign": "mock_sign_valid"
        })
        auth_client.assert_response(resp, expected_status=200)
        # 验证订单状态及库存回滚
        detail = auth_client.get(f"/api/order/{order['orderId']}").json()["data"]
        assert detail["status"] == "支付失败"
        stock_after = auth_client.get("/api/product/1001").json()["data"]["stock"]
        assert stock_after == stock_before + 1

    @allure.title("回调签名校验失败")
    @pytest.mark.pay
    def test_callback_invalid_sign(self, auth_client, sample_cart):
        order = auth_client.post("/api/order/create").json()["data"]
        resp = auth_client.post("/api/pay/callback", json_data={
            "orderId": order["orderId"],
            "status": "success"
            # 缺少sign
        })
        auth_client.assert_response(resp, expected_status=400)
        assert "签名校验失败" in resp.json()["message"]

    @allure.title("回调订单不存在")
    @pytest.mark.pay
    def test_callback_order_not_found(self, auth_client):
        resp = auth_client.post("/api/pay/callback", json_data={
            "orderId": "NOTEXIST",
            "status": "success",
            "sign": "sign"
        })
        auth_client.assert_response(resp, expected_status=404)
