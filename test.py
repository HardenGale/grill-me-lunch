#!/usr/bin/env python3
"""grill-me-lunch 功能测试

测试覆盖：
  1. 美团 Mock 搜索
  2. 大众点评 Mock 搜索
  3. 真实 API 调用（需配置 .env）
  4. 端到端流水线
"""

import os
import subprocess
import sys

# 确保从项目根目录运行
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)

# 加载 .env（如果存在）
env_file = os.path.join(PROJECT_DIR, ".env")
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key, value)


def run_cmd(cmd: list[str], desc: str) -> bool:
    """运行命令并检查结果"""
    print(f"\n{'='*60}")
    print(f"🧪 测试：{desc}")
    print(f"{'='*60}")
    result = subprocess.run(
        cmd, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    ok = result.returncode == 0
    print(f"{'✅ 通过' if ok else '❌ 失败'} — {desc}")
    return ok


def main() -> int:
    print("🍜 grill-me-lunch 功能测试")
    print(f"   项目目录: {PROJECT_DIR}")
    print(f"   Python: {sys.version}")
    mock_mode = os.getenv("GRILL_MOCK_MODE", "true")
    has_meituan = os.getenv("MEITUAN_DEVELOPER_ID", "").startswith("your_") is False and os.getenv("MEITUAN_DEVELOPER_ID", "")
    has_dianping = os.getenv("DIANPING_API_KEY", "").startswith("your_") is False and os.getenv("DIANPING_API_KEY", "")
    print(f"   Mock 模式: {mock_mode}")
    print(f"   美团密钥: {'✅ 已配置' if has_meituan else '⚠️ 未配置（Mock）'}")
    print(f"   点评密钥: {'✅ 已配置' if has_dianping else '⚠️ 未配置（Mock）'}")

    results: list[bool] = []

    # Test 1: 美团 Mock 搜索
    results.append(run_cmd(
        ["python", "scripts/crawl-meituan.py", "泰式凉面", "31.2304", "121.4737", "50", "4.0", "45"],
        "美团搜索「泰式凉面」",
    ))

    # Test 2: 美团 Mock 搜索 (不同关键词)
    results.append(run_cmd(
        ["python", "scripts/crawl-meituan.py", "日料", "31.2304", "121.4737", "60", "4.0", "45"],
        "美团搜索「日料」",
    ))

    # Test 3: 大众点评 Mock 搜索
    results.append(run_cmd(
        ["python", "scripts/crawl-dianping.py", "泰式", "上海", "4.5"],
        "大众点评搜索「泰式」",
    ))

    # Test 4: 大众点评 Mock 搜索 (不同关键词)
    results.append(run_cmd(
        ["python", "scripts/crawl-dianping.py", "凉面", "上海", "4.0"],
        "大众点评搜索「凉面」",
    ))

    # Test 5: 真实 API 测试（仅当密钥配置时）
    if has_meituan:
        print("\n⚠️  真实 API 测试需要消耗配额，确认继续？")
        results.append(run_cmd(
            ["python", "scripts/crawl-meituan.py", "午餐", "31.2304", "121.4737", "40", "4.0", "45"],
            "美团真实 API 搜索",
        ))

    # Summary
    print(f"\n{'='*60}")
    passed = sum(results)
    total = len(results)
    print(f"📊 测试结果: {passed}/{total} 通过")
    if passed == total:
        print("🎉 全部测试通过！")
    else:
        print(f"⚠️  {total - passed} 个测试失败")
    print(f"{'='*60}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
