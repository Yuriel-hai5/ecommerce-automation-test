"""
电商系统Mock服务（Flask）
用于本地独立运行测试，不依赖外部真实系统
面试时说明：本Mock基于真实业务规则设计，实际工作中可直接替换为公司测试环境地址
"""
from flask import Flask, request, jsonify
import uuid
import time
from datetime import datetime

app = Flask(__name__)

# 内存数据库（模拟）
db = {
    "users": {},
    "products": {
        "1001": {"id": "1001", "name": "iPhone 15 Pro", "price": 7999.00, "stock": 50, "category": "手机"},
        "1002": {"id": "1002", "name": "MacBook Air M3", "price": 8999.00, "stock": 30, "category": "电脑"},
        "1003": {"id": "1003", "name": "AirPods Pro 2", "price": 1899.00, "stock": 100, "category": "配件"},
        "1004": {"id": "1004", "name": "iPad Air", "price": 4799.00, "stock": 0, "category": "平板"},   # 库存为0，测试缺货场景
    },
    "carts": {},
    "orders": {},
    "coupons": {
        "C001": {"id": "C001", "code": "SAVE100", "type": "fixed", "value": 100, "min_order": 500},
        "C002": {"id": "C002", "code": "DISCOUNT20", "type": "percent", "value": 0.20, "min_order": 1000},
    }
}

# ========== 辅助函数 ==========
def generate_id():
    return str(uuid.uuid4()).replace("-", "")[:16]

def get_auth_user():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        for uid, user in db["users"].items():
            if user.get("token") == token:
                return user
    return None

# ========== 用户模块 ==========
@app.route("/api/user/register", methods=["POST"])
def user_register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"code": 400, "message": "用户名和密码不能为空"}), 400
    if username in [u["username"] for u in db["users"].values()]:
        return jsonify({"code": 409, "message": "用户名已存在"}), 409

    uid = generate_id()
    db["users"][uid] = {"id": uid, "username": username, "password": password, "token": None}
    return jsonify({"code": 200, "message": "注册成功", "data": {"userId": uid, "username": username}}), 200

@app.route("/api/user/login", methods=["POST"])
def user_login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    user = next((u for u in db["users"].values() if u["username"] == username and u["password"] == password), None)
    if not user:
        return jsonify({"code": 401, "message": "用户名或密码错误"}), 401
    token = generate_id() + generate_id()
    user["token"] = token
    return jsonify({"code": 200, "message": "登录成功", "data": {"token": token, "userId": user["id"]}}), 200

@app.route("/api/user/info", methods=["GET"])
def user_info():
    user = get_auth_user()
    if not user:
        return jsonify({"code": 401, "message": "未登录或token无效"}), 401
    return jsonify({"code": 200, "data": {"userId": user["id"], "username": user["username"]}}), 200

# ========== 商品模块 ==========
@app.route("/api/product/list", methods=["GET"])
def product_list():
    category = request.args.get("category")
    keyword = request.args.get("keyword")
    products = list(db["products"].values())
    if category:
        products = [p for p in products if p["category"] == category]
    if keyword:
        products = [p for p in products if keyword.lower() in p["name"].lower()]
    return jsonify({"code": 200, "data": products}), 200

@app.route("/api/product/<product_id>", methods=["GET"])
def product_detail(product_id):
    product = db["products"].get(product_id)
    if not product:
        return jsonify({"code": 404, "message": "商品不存在"}), 404
    return jsonify({"code": 200, "data": product}), 200

# ========== 购物车模块 ==========
@app.route("/api/cart/add", methods=["POST"])
def cart_add():
    user = get_auth_user()
    if not user:
        return jsonify({"code": 401, "message": "未登录"}), 401
    data = request.get_json() or {}
    product_id = data.get("productId")
    quantity = data.get("quantity", 1)
    product = db["products"].get(product_id)
    if not product:
        return jsonify({"code": 404, "message": "商品不存在"}), 404
    if product["stock"] < quantity:
        return jsonify({"code": 400, "message": "库存不足"}), 400

    uid = user["id"]
    if uid not in db["carts"]:
        db["carts"][uid] = []
    # 检查是否已存在
    for item in db["carts"][uid]:
        if item["productId"] == product_id:
            item["quantity"] += quantity
            break
    else:
        db["carts"][uid].append({"productId": product_id, "name": product["name"], "price": product["price"], "quantity": quantity})
    return jsonify({"code": 200, "message": "添加成功", "data": db["carts"][uid]}), 200

@app.route("/api/cart/list", methods=["GET"])
def cart_list():
    user = get_auth_user()
    if not user:
        return jsonify({"code": 401, "message": "未登录"}), 401
    items = db["carts"].get(user["id"], [])
    total = sum(item["price"] * item["quantity"] for item in items)
    return jsonify({"code": 200, "data": {"items": items, "totalAmount": round(total, 2)}}), 200

@app.route("/api/cart/clear", methods=["POST"])
def cart_clear():
    user = get_auth_user()
    if not user:
        return jsonify({"code": 401, "message": "未登录"}), 401
    db["carts"][user["id"]] = []
    return jsonify({"code": 200, "message": "购物车已清空"}), 200

# ========== 订单模块 ==========
@app.route("/api/order/create", methods=["POST"])
def order_create():
    user = get_auth_user()
    if not user:
        return jsonify({"code": 401, "message": "未登录"}), 401

    data = request.get_json() or {}
    address = data.get("address", "默认地址")
    coupon_code = data.get("couponCode")

    cart_items = db["carts"].get(user["id"], [])
    if not cart_items:
        return jsonify({"code": 400, "message": "购物车为空"}), 400

    # 计算金额
    total = sum(item["price"] * item["quantity"] for item in cart_items)
    discount = 0
    if coupon_code:
        coupon = next((c for c in db["coupons"].values() if c["code"] == coupon_code), None)
        if coupon and total >= coupon["min_order"]:
            if coupon["type"] == "fixed":
                discount = coupon["value"]
            else:
                discount = round(total * coupon["value"], 2)

    final_amount = round(total - discount, 2)
    if final_amount < 0:
        final_amount = 0

    # 扣减库存
    for item in cart_items:
        product = db["products"][item["productId"]]
        if product["stock"] < item["quantity"]:
            return jsonify({"code": 400, "message": f"商品 {product['name']} 库存不足"}), 400
        product["stock"] -= item["quantity"]

    order_id = generate_id()
    order = {
        "id": order_id,
        "userId": user["id"],
        "items": cart_items.copy(),
        "totalAmount": total,
        "discount": discount,
        "finalAmount": final_amount,
        "status": "待支付",
        "address": address,
        "createTime": datetime.now().isoformat(),
        "payTime": None
    }
    db["orders"][order_id] = order
    db["carts"][user["id"]] = []  # 清空购物车
    return jsonify({"code": 200, "message": "订单创建成功", "data": {"orderId": order_id, "finalAmount": final_amount, "status": "待支付"}}), 200

@app.route("/api/order/<order_id>", methods=["GET"])
def order_detail(order_id):
    user = get_auth_user()
    if not user:
        return jsonify({"code": 401, "message": "未登录"}), 401
    order = db["orders"].get(order_id)
    if not order or order["userId"] != user["id"]:
        return jsonify({"code": 404, "message": "订单不存在"}), 404
    return jsonify({"code": 200, "data": order}), 200

@app.route("/api/order/<order_id>/cancel", methods=["POST"])
def order_cancel(order_id):
    user = get_auth_user()
    if not user:
        return jsonify({"code": 401, "message": "未登录"}), 401
    order = db["orders"].get(order_id)
    if not order or order["userId"] != user["id"]:
        return jsonify({"code": 404, "message": "订单不存在"}), 404
    if order["status"] != "待支付":
        return jsonify({"code": 400, "message": "只有待支付订单可取消"}), 400
    # 回滚库存
    for item in order["items"]:
        db["products"][item["productId"]]["stock"] += item["quantity"]
    order["status"] = "已取消"
    return jsonify({"code": 200, "message": "订单已取消"}), 200

# ========== 支付模块 ==========
@app.route("/api/pay", methods=["POST"])
def pay_order():
    user = get_auth_user()
    if not user:
        return jsonify({"code": 401, "message": "未登录"}), 401
    data = request.get_json() or {}
    order_id = data.get("orderId")
    pay_method = data.get("payMethod", "alipay")
    order = db["orders"].get(order_id)
    if not order or order["userId"] != user["id"]:
        return jsonify({"code": 404, "message": "订单不存在"}), 404
    if order["status"] != "待支付":
        return jsonify({"code": 400, "message": "订单状态不允许支付"}), 400

    # 模拟支付处理
    time.sleep(0.1)
    order["status"] = "已支付"
    order["payTime"] = datetime.now().isoformat()
    order["payMethod"] = pay_method
    return jsonify({"code": 200, "message": "支付成功", "data": {"orderId": order_id, "status": "已支付", "payTime": order["payTime"]}}), 200

@app.route("/api/pay/callback", methods=["POST"])
def pay_callback():
    """第三方支付回调接口（模拟）"""
    data = request.get_json() or {}
    order_id = data.get("orderId")
    status = data.get("status")  # success / fail
    sign = data.get("sign")

    # 模拟签名校验
    if not sign:
        return jsonify({"code": 400, "message": "签名校验失败"}), 400

    order = db["orders"].get(order_id)
    if not order:
        return jsonify({"code": 404, "message": "订单不存在"}), 404

    if status == "success":
        if order["status"] == "待支付":
            order["status"] = "已支付"
            order["payTime"] = datetime.now().isoformat()
        return jsonify({"code": 200, "message": "回调处理成功"}), 200
    else:
        order["status"] = "支付失败"
        # 回滚库存
        for item in order["items"]:
            db["products"][item["productId"]]["stock"] += item["quantity"]
        return jsonify({"code": 200, "message": "回调处理成功（支付失败）"}), 200

# ========== 优惠券模块 ==========
@app.route("/api/coupon/list", methods=["GET"])
def coupon_list():
    return jsonify({"code": 200, "data": list(db["coupons"].values())}), 200


# ========== 测试辅助接口（仅限测试环境） ==========
@app.route("/api/test/set-stock", methods=["POST"])
def test_set_stock():
    """测试专用：修改商品库存"""
    data = request.get_json() or {}
    product_id = data.get("productId")
    stock = data.get("stock")
    if product_id not in db["products"]:
        return jsonify({"code": 404, "message": "商品不存在"}), 404
    db["products"][product_id]["stock"] = stock
    return jsonify({"code": 200, "message": "库存已更新", "data": {"productId": product_id, "stock": stock}}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
