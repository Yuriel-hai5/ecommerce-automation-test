"""
商品模块接口测试
覆盖：商品列表、商品详情、搜索、分类筛选、异常场景
"""
import pytest
import allure


@allure.feature("商品模块")
@allure.story("商品列表")
class TestProductList:

    @allure.title("获取全部商品列表")
    @pytest.mark.smoke
    @pytest.mark.product
    def test_product_list_all(self, api_client):
        resp = api_client.get("/api/product/list")
        api_client.assert_response(resp, expected_status=200, expected_keys=["data"])
        products = resp.json()["data"]
        assert len(products) >= 3
        for p in products:
            assert all(k in p for k in ["id", "name", "price", "stock", "category"])

    @allure.title("按分类筛选")
    @pytest.mark.product
    def test_product_list_by_category(self, api_client):
        resp = api_client.get("/api/product/list", params={"category": "手机"})
        api_client.assert_response(resp, expected_status=200)
        products = resp.json()["data"]
        assert len(products) > 0
        assert all(p["category"] == "手机" for p in products)

    @allure.title("按关键词搜索")
    @pytest.mark.product
    def test_product_list_search(self, api_client):
        resp = api_client.get("/api/product/list", params={"keyword": "iPhone"})
        api_client.assert_response(resp, expected_status=200)
        products = resp.json()["data"]
        assert len(products) > 0
        assert all("iphone" in p["name"].lower() for p in products)

    @allure.title("搜索无结果")
    @pytest.mark.product
    def test_product_list_no_result(self, api_client):
        resp = api_client.get("/api/product/list", params={"keyword": "不存在的商品XYZ"})
        api_client.assert_response(resp, expected_status=200)
        assert resp.json()["data"] == []


@allure.feature("商品模块")
@allure.story("商品详情")
class TestProductDetail:

    @allure.title("正常获取商品详情")
    @pytest.mark.smoke
    @pytest.mark.product
    def test_product_detail_success(self, api_client):
        resp = api_client.get("/api/product/1001")
        api_client.assert_response(resp, expected_status=200, expected_keys=["data"])
        data = resp.json()["data"]
        assert data["id"] == "1001"
        assert data["name"] == "iPhone 15 Pro"
        assert data["price"] > 0

    @allure.title("商品不存在")
    @pytest.mark.product
    def test_product_detail_not_found(self, api_client):
        resp = api_client.get("/api/product/99999")
        api_client.assert_response(resp, expected_status=404)
