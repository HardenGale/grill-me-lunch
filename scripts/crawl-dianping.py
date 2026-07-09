#!/usr/bin/env python3
"""大众点评开放平台 API 封装 — 搜索高分餐厅

支持两种模式：
  1. 真实 API 模式 — 大众点评开放平台 open.dianping.com
  2. Mock 模式 — 使用高质量模拟数据

认证方式：Bearer Token
"""

import os
import sys
from typing import Any

import requests  # type: ignore

# ============================================================
# 配置
# ============================================================

DIANPING_API_KEY = os.getenv("DIANPING_API_KEY", "")
DIANPING_GATEWAY = "https://openapi.dianping.com/v1/business"
MOCK_MODE = os.getenv("GRILL_MOCK_MODE", "true").lower() == "true"


# ============================================================
# Mock 数据
# ============================================================

MOCK_DATA: dict[str, list[dict[str, Any]]] = {
    "泰式": [
        {
            "name": "Home Thai·泰谣",
            "rating": 4.7,
            "avg_price": 98,
            "top_comment": "冬阴功汤是上海最好喝的！海鲜非常新鲜，酸辣度完美",
            "url": "https://www.dianping.com/shop/H1pQzE8m3xK",
            "tags": ["徐汇区", "东南亚菜", "必吃榜"],
        },
        {
            "name": "Lian尚莲·越泰料理",
            "rating": 4.5,
            "avg_price": 120,
            "top_comment": "环境很好，适合约会，碳烤猪颈肉必点",
            "url": "https://www.dianping.com/shop/k9M2nR5vL7",
            "tags": ["静安区", "泰式料理", "约会餐厅"],
        },
        {
            "name": "帕塔东南亚料理",
            "rating": 4.4,
            "avg_price": 85,
            "top_comment": "性价比很高的泰餐，绿咖喱很正宗",
            "url": "https://www.dianping.com/shop/tR3wF4jN9",
            "tags": ["长宁区", "泰式小馆", "性价比"],
        },
    ],
    "日料": [
        {
            "name": "鮨一",
            "rating": 4.8,
            "avg_price": 880,
            "top_comment": "板前寿司体验极佳，师傅很用心，每一贯都是享受",
            "url": "https://www.dianping.com/shop/sushi1",
            "tags": ["黄浦区", "高端日料", "黑珍珠"],
        },
        {
            "name": "Maki House",
            "rating": 4.4,
            "avg_price": 60,
            "top_comment": "性价比超高的日料简餐，三文鱼很新鲜",
            "url": "https://www.dianping.com/shop/makihouse",
            "tags": ["静安区", "日式简餐", "性价比"],
        },
    ],
    "中餐": [
        {
            "name": "新荣记",
            "rating": 4.8,
            "avg_price": 500,
            "top_comment": "台州菜天花板，黄鱼和沙蒜豆面必点",
            "url": "https://www.dianping.com/shop/xinrongji",
            "tags": ["黄浦区", "台州菜", "米其林三星"],
        },
        {
            "name": "兰心餐厅",
            "rating": 4.6,
            "avg_price": 80,
            "top_comment": "地道的本帮菜，红烧肉一绝，排队也要吃",
            "url": "https://www.dianping.com/shop/lanxin",
            "tags": ["黄浦区", "本帮菜", "必吃榜"],
        },
    ],
    "沙拉": [
        {
            "name": "Wagas 沃歌斯",
            "rating": 4.3,
            "avg_price": 68,
            "top_comment": "轻食界的星巴克，沙拉新鲜，果汁好喝",
            "url": "https://www.dianping.com/shop/wagas",
            "tags": ["连锁", "轻食", "健康餐"],
        },
    ],
    "凉面": [
        {
            "name": "味香斋",
            "rating": 4.5,
            "avg_price": 30,
            "top_comment": "老字号麻酱拌面，夏天来一碗太舒服了",
            "url": "https://www.dianping.com/shop/weixiangzhai",
            "tags": ["黄浦区", "老字号", "面馆"],
        },
    ],
}


def mock_search(keyword: str) -> list[dict[str, Any]]:
    """使用 Mock 数据模拟搜索"""
    results: list[dict[str, Any]] = []
    kw_lower = keyword.lower()

    for category, restaurants in MOCK_DATA.items():
        if category in kw_lower:
            results.extend(restaurants)
            continue
        for r in restaurants:
            if kw_lower in r["name"].lower() or any(
                kw_lower in t.lower() for t in r.get("tags", [])
            ):
                if r not in results:
                    results.append(r)

    if not results:
        # 综合推荐
        results = [
            MOCK_DATA["中餐"][1],   # 兰心
            MOCK_DATA["泰式"][0],   # Home Thai
            MOCK_DATA["日料"][1],   # Maki House
        ]

    return results[:3]


# ============================================================
# 核心搜索函数
# ============================================================

def search_restaurant(
    keyword: str, city: str = "上海", min_rating: float = 4.5, limit: int = 5
) -> list[dict[str, Any]]:
    """搜索大众点评高分餐厅

    优先使用真实 API，未配置密钥时自动降级为 Mock 模式。
    """
    print(f"🔍 大众点评搜索：「{keyword}」({city})", file=sys.stderr)
    print(f"   最低评分 ≥{min_rating}", file=sys.stderr)
    print("", file=sys.stderr)

    # --- Mock 模式 ---
    if MOCK_MODE or not DIANPING_API_KEY or DIANPING_API_KEY.startswith("your_"):
        print("   ℹ️  Mock 模式（未配置真实 API 密钥）", file=sys.stderr)
        all_results = mock_search(keyword)
        results = [r for r in all_results if r["rating"] >= min_rating]
        if not results:
            results = sorted(all_results, key=lambda r: r["rating"], reverse=True)[:3]
        return _format_output(results[:3])

    # --- 真实 API 模式 ---
    try:
        resp = requests.get(
            f"{DIANPING_GATEWAY}/search",
            headers={"Authorization": f"Bearer {DIANPING_API_KEY}"},
            params={
                "keyword": keyword,
                "city": city,
                "sort": "rating",
                "limit": limit,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"   ⚠️ 大众点评 API 不可用：{e}，降级为 Mock", file=sys.stderr)
        all_results = mock_search(keyword)
        results = [r for r in all_results if r["rating"] >= min_rating]
        return _format_output(results[:3])
    except ValueError:
        print("   ⚠️ API 返回解析失败，降级为 Mock", file=sys.stderr)
        all_results = mock_search(keyword)
        results = [r for r in all_results if r["rating"] >= min_rating]
        return _format_output(results[:3])

    businesses = data.get("businesses", [])
    results: list[dict[str, Any]] = []
    count = 0
    for b in businesses:
        if b.get("avg_rating", 0) < min_rating:
            continue
        count += 1
        if count > 3:
            break
        top_review = b.get("top_review", {})
        result = {
            "rank": count,
            "source": "大众点评",
            "name": b.get("name", "未知"),
            "rating": b.get("avg_rating", 0),
            "avg_price": b.get("avg_price", 0),
            "top_comment": top_review.get("text", ""),
            "url": b.get("business_url", ""),
            "tags": b.get("tags", []),
        }
        results.append(result)

    return _format_output(results)


def _format_output(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """格式化并打印搜索结果"""
    if not results:
        print("   😞 没有找到匹配的餐厅", file=sys.stderr)
        return []

    # 确保结果有 rank / source 字段
    for i, r in enumerate(results):
        if "rank" not in r:
            r["rank"] = i + 1
        if "source" not in r:
            r["source"] = "大众点评"

    print("", file=sys.stderr)
    for r in results:
        emoji = ["🥇", "🥈", "🥉"][r["rank"] - 1]
        tags_str = " · ".join(r.get("tags", [])[:3]) if r.get("tags") else ""
        print(
            f"  {emoji} {r['name']} | ⭐{r['rating']} | ¥{r['avg_price']}",
            file=sys.stderr,
        )
        if tags_str:
            print(f"     🏷️  {tags_str}", file=sys.stderr)
        if r.get("top_comment"):
            print(f"     💬「{r['top_comment'][:60]}」", file=sys.stderr)
        print(f"     👉 {r['url']}", file=sys.stderr)
        print("", file=sys.stderr)

    return results


# ============================================================
# CLI
# ============================================================

def main() -> None:
    if len(sys.argv) < 2:
        print("用法: crawl-dianping.py <keyword> [city] [min_rating]", file=sys.stderr)
        sys.exit(1)

    keyword = sys.argv[1]
    city = sys.argv[2] if len(sys.argv) > 2 else "上海"
    min_rating = float(sys.argv[3]) if len(sys.argv) > 3 else 4.5

    search_restaurant(keyword=keyword, city=city, min_rating=min_rating)


if __name__ == "__main__":
    main()
