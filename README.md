# 电商全链路自动化测试项目

> 基于 Python + Pytest + Selenium + JMeter/Locust 构建的电商系统全链路测试框架，覆盖接口、UI、性能三大测试维度。

## 一、项目概述

本项目针对电商核心业务流程（用户、商品、购物车、订单、支付）进行全链路自动化测试建设，重点验证：

- **订单状态流转**：待支付 -> 已支付 / 已取消 / 支付失败
- **支付回调模拟**：第三方回调签名校验、成功/失败场景
- **库存超卖并发测试**：高并发下库存扣减的准确性
- **优惠券叠加计算**：固定金额券、百分比折扣券的抵扣逻辑
- **多端兼容性**：Web端UI自动化流程验证

## 二、技术栈

| 层级 | 技术/工具 | 用途 |
|------|----------|------|
| 编程语言 | Python 3.9+ | 测试脚本开发 |
| 接口测试 | Pytest + Requests + Allure | 接口自动化与报告生成 |
| UI测试 | Selenium WebDriver + POM | Web端功能验证 |
| 性能测试 | JMeter / Locust | 并发压测与超卖检测 |
| Mock服务 | Flask | 被测系统模拟（可替换为真实环境） |
| 报告 | pytest-html / Allure / JMeter聚合报告 | 测试可视化输出 |

## 三、项目结构

```
.
├── api_tests/              # 接口自动化测试
│   ├── conftest.py         # Fixture配置（登录态、数据清理）
│   ├── test_user.py        # 用户模块（注册/登录/信息）
│   ├── test_product.py     # 商品模块（列表/详情/搜索）
│   ├── test_cart.py        # 购物车模块（加购/查询/清空）
│   ├── test_order.py       # 订单模块（创建/详情/取消/优惠券/库存）
│   └── test_pay.py         # 支付模块（支付/回调/签名）
├── ui_tests/               # UI自动化测试
│   ├── conftest.py         # WebDriver配置
│   ├── pages/              # Page Object页面对象
│   │   ├── base_page.py    # 基础封装（查找/点击/等待/截图）
│   │   ├── login_page.py
│   │   ├── product_page.py
│   │   ├── cart_page.py
│   │   └── order_page.py
│   └── test_ui_flow.py     # 核心业务流程E2E测试
├── performance/            # 性能测试
│   ├── jmeter/
│   │   └── ecommerce_test.jmx    # JMeter混合场景压测脚本
│   └── locust/
│       └── locustfile.py         # Locust秒杀超卖专项测试
├── utils/
│   ├── api_client.py       # HTTP请求统一封装（日志/断言/Token管理）
│   └── mock_server.py      # 电商系统Mock服务（Flask）
├── reports/                # 测试报告输出目录
├── requirements.txt
└── pytest.ini              # Pytest全局配置与Markers
```

## 四、核心测试点

### 4.1 订单状态流转
```
[创建订单] --> 待支付 --> [支付成功] --> 已支付
                      --> [支付失败] --> 支付失败（库存回滚）
                      --> [用户取消] --> 已取消（库存回滚）
```
- 已支付订单不可取消
- 支付失败/取消后库存必须回滚

### 4.2 支付回调模拟
- **成功回调**：签名校验通过后更新订单为已支付
- **失败回调**：更新订单为支付失败，回滚库存
- **异常场景**：缺少签名直接拒绝，防止伪造回调

### 4.3 库存超卖并发测试
- **测试方法**：Locust/JMeter模拟50+并发用户同时抢购低库存商品
- **验证标准**：最终成交订单总量 <= 初始库存量
- **发现Bug示例**：若系统未做乐观锁/悲观锁，可能出现超卖

### 4.4 优惠券计算
| 优惠券类型 | 规则 | 示例 |
|-----------|------|------|
| 固定金额券 | 满X减Y | SAVE100：满500减100 |
| 百分比券 | 满X打Y折 | DISCOUNT20：满1000减20% |
- 验证门槛判断：不满足门槛时不抵扣
- 验证叠加规则：本项目暂不支持多张叠加（可扩展测试）

### 4.5 UI全链路E2E
覆盖：`登录 -> 商品搜索 -> 加购 -> 下单 -> 支付 -> 取消`
- 采用 **Page Object 模式** 降低维护成本
- Allure步骤拆解，方便定位失败环节

## 五、快速运行

### 5.1 环境准备
```bash
pip install -r requirements.txt
```

### 5.2 启动Mock服务
```bash
python -m utils.mock_server
```
服务启动后访问：`http://127.0.0.1:5000`

### 5.3 运行接口测试
```bash
# 全部接口测试
pytest api_tests/ -v --html=reports/api_report.html

# 仅冒烟测试
pytest api_tests/ -m smoke -v

# 仅订单模块
pytest api_tests/ -m order -v

# 生成Allure报告
pytest api_tests/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

### 5.4 运行UI测试
```bash
pytest ui_tests/ -v --html=reports/ui_report.html
```

### 5.5 运行性能测试

**Locust（推荐用于超卖测试）**：
```bash
cd performance/locust
locust -f locustfile.py --host=http://127.0.0.1:5000 -u 100 -r 10 --run-time 60s
```

**JMeter**：
```bash
jmeter -n -t performance/jmeter/ecommerce_test.jmx -l reports/jmeter_result.jtl -e -o reports/jmeter_dashboard
```

## 六、扩展方向

- **接入CI/CD**：将 pytest 和 JMeter 接入 Jenkins/GitHub Actions，每次代码提交自动触发
- **数据驱动**：用 JSON/Excel/YAML 管理测试数据，实现参数化
- **数据库断言**：增加订单表、库存表的直接查询断言，避免接口返回200但数据未落库
- **App/小程序**：基于 Appium 扩展移动端UI测试