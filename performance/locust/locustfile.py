"""
Locust性能测试脚本
场景：模拟高并发下库存扣减，验证是否存在超卖问题
"""
from locust import HttpUser, task, between
import random


class EcommerceUser(HttpUser):
    """电商用户行为模拟"""
    wait_time = between(1, 3)
    token: str = None
    user_id: str = None

    def on_start(self):
        """每个用户启动时注册并登录"""
        username = f"perf_user_{self.user_id}_{random.randint(1000, 9999)}"
        # 注册
        self.client.post("/api/user/register", json={"username": username, "password": "perf123"})
        # 登录
        resp = self.client.post("/api/user/login", json={"username": username, "password": "perf123"})
        if resp.status_code == 200:
            self.token = resp.json()["data"]["token"]

    @task(3)
    def browse_products(self):
        """浏览商品列表"""
        self.client.get("/api/product/list")

    @task(2)
    def search_product(self):
        """搜索商品"""
        self.client.get("/api/product/list", params={"keyword": "iPhone"})

    @task(5)
    def add_to_cart(self):
        """加购（核心：高频操作）"""
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        self.client.post("/api/cart/add", json={"productId": "1001", "quantity": 1}, headers=headers)

    @task(3)
    def view_cart(self):
        """查看购物车"""
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        self.client.get("/api/cart/list", headers=headers)

    @task(2)
    def create_order(self):
        """创建订单"""
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        self.client.post("/api/order/create", json={"address": "性能测试地址"}, headers=headers)

    @task(1)
    def pay_order(self):
        """支付订单"""
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        # 先创建订单
        resp = self.client.post("/api/order/create", json={"address": "性能测试地址"}, headers=headers)
        if resp.status_code == 200:
            order_id = resp.json()["data"]["orderId"]
            self.client.post("/api/pay", json={"orderId": order_id, "payMethod": "alipay"}, headers=headers)


class SpikeTestUser(HttpUser):
    """秒杀/库存超卖专项测试"""
    wait_time = between(0.1, 0.5)
    token: str = None

    def on_start(self):
        username = f"spike_{random.randint(100000, 999999)}"
        self.client.post("/api/user/register", json={"username": username, "password": "spike123"})
        resp = self.client.post("/api/user/login", json={"username": username, "password": "spike123"})
        if resp.status_code == 200:
            self.token = resp.json()["data"]["token"]

    @task(1)
    def spike_buy(self):
        """
        模拟秒杀场景：大量用户同时抢购同一低库存商品
        预期：最终销量不应超过初始库存，否则存在超卖bug
        """
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        # 1002初始库存30，用于测试超卖
        self.client.post("/api/cart/add", json={"productId": "1002", "quantity": 1}, headers=headers)
        self.client.post("/api/order/create", json={"address": "秒杀地址"}, headers=headers)


# 使用方法：
# locust -f locustfile.py --host=http://127.0.0.1:5000 -u 100 -r 10 --run-time 60s
# -u: 并发用户数  -r: 每秒启动用户数  --run-time: 运行时长
