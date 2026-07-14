"""
一键运行脚本
快速执行接口测试、生成报告
"""
import subprocess
import sys
import os


def run_api_tests():
    """运行接口测试"""
    print("=" * 50)
    print("开始运行 接口自动化测试")
    print("=" * 50)
    cmd = [
        sys.executable, "-m", "pytest", "api_tests/",
        "-v", "--tb=short",
        "--html=reports/api_report.html", "--self-contained-html",
        "--alluredir=reports/allure-results"
    ]
    subprocess.run(cmd)


def run_ui_tests():
    """运行UI测试"""
    print("=" * 50)
    print("开始运行 UI自动化测试")
    print("=" * 50)
    cmd = [
        sys.executable, "-m", "pytest", "ui_tests/",
        "-v", "--tb=short",
        "--html=reports/ui_report.html", "--self-contained-html"
    ]
    subprocess.run(cmd)


def run_smoke():
    """运行冒烟测试"""
    print("=" * 50)
    print("开始运行 冒烟测试")
    print("=" * 50)
    cmd = [
        sys.executable, "-m", "pytest", "-m", "smoke",
        "-v", "--tb=short"
    ]
    subprocess.run(cmd)


def serve_allure():
    """启动Allure报告服务"""
    print("=" * 50)
    print("启动 Allure 报告服务 (http://localhost:8080)")
    print("=" * 50)
    cmd = ["allure", "serve", "reports/allure-results", "-p", "8080"]
    subprocess.run(cmd)


def main():
    os.makedirs("reports", exist_ok=True)
    if len(sys.argv) < 2:
        print("用法: python run_tests.py [api|ui|smoke|allure|all]")
        print("  api    - 运行接口测试")
        print("  ui     - 运行UI测试")
        print("  smoke  - 运行冒烟测试")
        print("  allure - 查看Allure报告")
        print("  all    - 运行全部测试")
        return

    action = sys.argv[1]
    if action == "api":
        run_api_tests()
    elif action == "ui":
        run_ui_tests()
    elif action == "smoke":
        run_smoke()
    elif action == "allure":
        serve_allure()
    elif action == "all":
        run_api_tests()
        run_ui_tests()
    else:
        print(f"未知命令: {action}")


if __name__ == "__main__":
    main()
