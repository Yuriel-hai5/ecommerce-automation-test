"""
接口测试Fixture配置
- 提供APIClient实例
- 提供已登录的用户session
- 测试数据初始化与清理
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.api_client import APIClient
from utils.mock_server import db


@pytest.fixture(scope="session")
def api_client():
    """全局API客户端"""
    client = APIClient(base_url="http://127.0.0.1:5000")
    yield client


@pytest.fixture(scope="function")
def registered_user(api_client):
    """注册一个新用户，测试结束后清理"""
    import time
    username = f"testuser_{int(time.time() * 1000)}"
    password = "Test1234"
    resp = api_client.post("/api/user/register", json_data={"username": username, "password": password})
    assert resp.status_code == 200
    user_id = resp.json()["data"]["userId"]
    yield {"username": username, "password": password, "userId": user_id}
    # 清理
    if user_id in db["users"]:
        del db["users"][user_id]


@pytest.fixture(scope="function")
def auth_client(api_client, registered_user):
    """已登录认证的客户端"""
    resp = api_client.post("/api/user/login", json_data={
        "username": registered_user["username"],
        "password": registered_user["password"]
    })
    assert resp.status_code == 200
    token = resp.json()["data"]["token"]
    api_client.set_token(token)
    yield api_client
    # 登出后清理token
    api_client.headers.pop("Authorization", None)
    api_client.token = None


@pytest.fixture(scope="function")
def sample_cart(auth_client):
    """预设购物车数据"""
    # 添加商品到购物车
    auth_client.post("/api/cart/add", json_data={"productId": "1001", "quantity": 1})
    auth_client.post("/api/cart/add", json_data={"productId": "1003", "quantity": 2})
    yield auth_client
    # 清空购物车
    auth_client.post("/api/cart/clear")
