"""
API请求封装类
- 统一封装HTTP请求
- 自动处理token、签名等鉴权逻辑
- 支持请求/响应日志记录
"""
import requests
import json
import time
from typing import Dict, Any, Optional


class APIClient:
    """电商系统接口测试客户端"""

    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "EcommerceTest/1.0"
        }
        self.token: Optional[str] = None
        self.request_log: list = []

    def set_token(self, token: str):
        """设置认证token"""
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """统一请求方法"""
        url = f"{self.base_url}{endpoint}"
        headers = {**self.headers, **kwargs.pop("headers", {})}

        start_time = time.time()
        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
            elapsed = time.time() - start_time

            # 记录请求日志
            log_entry = {
                "method": method.upper(),
                "url": url,
                "status_code": response.status_code,
                "elapsed_ms": round(elapsed * 1000, 2),
                "request_body": kwargs.get("json"),
                "response_body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            }
            self.request_log.append(log_entry)
            return response

        except requests.RequestException as e:
            elapsed = time.time() - start_time
            self.request_log.append({
                "method": method.upper(),
                "url": url,
                "error": str(e),
                "elapsed_ms": round(elapsed * 1000, 2)
            })
            raise

    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        return self._request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, json_data: Optional[Dict] = None, **kwargs) -> requests.Response:
        return self._request("POST", endpoint, json=json_data, **kwargs)

    def put(self, endpoint: str, json_data: Optional[Dict] = None, **kwargs) -> requests.Response:
        return self._request("PUT", endpoint, json=json_data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("DELETE", endpoint, **kwargs)

    def get_logs(self) -> list:
        """获取请求日志"""
        return self.request_log

    def assert_response(self, response: requests.Response, expected_status: int = 200, expected_keys: Optional[list] = None):
        """通用响应断言"""
        assert response.status_code == expected_status, f"期望状态码 {expected_status}, 实际 {response.status_code}, 响应: {response.text}"
        if expected_keys and response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            if isinstance(data, dict):
                for key in expected_keys:
                    assert key in data, f"响应中缺少关键字段: {key}"
        return response
