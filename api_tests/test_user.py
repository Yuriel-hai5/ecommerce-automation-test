"""
用户模块接口测试
覆盖：注册、登录、获取用户信息、参数校验、异常场景
"""
import pytest
import allure


@allure.feature("用户模块")
@allure.story("用户注册")
class TestUserRegister:

    @allure.title("正常注册")
    @pytest.mark.smoke
    @pytest.mark.user
    def test_register_success(self, api_client):
        import time
        username = f"newuser_{int(time.time() * 1000)}"
        resp = api_client.post("/api/user/register", json_data={
            "username": username,
            "password": "ValidPass123"
        })
        api_client.assert_response(resp, expected_status=200, expected_keys=["code", "message", "data"])
        assert resp.json()["data"]["username"] == username

    @allure.title("重复注册")
    @pytest.mark.user
    def test_register_duplicate(self, api_client, registered_user):
        resp = api_client.post("/api/user/register", json_data={
            "username": registered_user["username"],
            "password": "AnyPass123"
        })
        api_client.assert_response(resp, expected_status=409)
        assert "已存在" in resp.json()["message"]

    @allure.title("用户名或密码为空")
    @pytest.mark.user
    @pytest.mark.parametrize("payload, missing", [
        ({"username": "user1"}, "密码"),
        ({"password": "pass1"}, "用户名"),
        ({}, "用户名"),
    ])
    def test_register_missing_fields(self, api_client, payload, missing):
        resp = api_client.post("/api/user/register", json_data=payload)
        api_client.assert_response(resp, expected_status=400)
        assert "不能为空" in resp.json()["message"]


@allure.feature("用户模块")
@allure.story("用户登录")
class TestUserLogin:

    @allure.title("正常登录")
    @pytest.mark.smoke
    @pytest.mark.user
    def test_login_success(self, api_client, registered_user):
        resp = api_client.post("/api/user/login", json_data={
            "username": registered_user["username"],
            "password": registered_user["password"]
        })
        api_client.assert_response(resp, expected_status=200, expected_keys=["data"])
        assert "token" in resp.json()["data"]

    @allure.title("密码错误")
    @pytest.mark.user
    def test_login_wrong_password(self, api_client, registered_user):
        resp = api_client.post("/api/user/login", json_data={
            "username": registered_user["username"],
            "password": "WrongPassword"
        })
        api_client.assert_response(resp, expected_status=401)

    @allure.title("不存在的用户")
    @pytest.mark.user
    def test_login_nonexist_user(self, api_client):
        resp = api_client.post("/api/user/login", json_data={
            "username": "not_exist_user_99999",
            "password": "somepass"
        })
        api_client.assert_response(resp, expected_status=401)


@allure.feature("用户模块")
@allure.story("获取用户信息")
class TestUserInfo:

    @allure.title("已登录获取信息")
    @pytest.mark.smoke
    @pytest.mark.user
    def test_user_info_authenticated(self, auth_client, registered_user):
        resp = auth_client.get("/api/user/info")
        auth_client.assert_response(resp, expected_status=200, expected_keys=["data"])
        assert resp.json()["data"]["username"] == registered_user["username"]

    @allure.title("未登录获取信息")
    @pytest.mark.user
    def test_user_info_no_auth(self, api_client):
        resp = api_client.get("/api/user/info")
        api_client.assert_response(resp, expected_status=401)
