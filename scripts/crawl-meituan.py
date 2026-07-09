#!/usr/bin/env python3
"""美团开放平台 API 封装 — 搜索附近外卖商家

支持两种模式：
  1. 真实 API 模式 — 通过美团开发者平台 (developer.meituan.com) 调用
  2. Mock 模式 — 使用高质量模拟数据，无需真实 API 密钥

认证方式：DeveloperId + SignKey (SHA1 签名)
API 网关：https://api-open-cater.meituan.com
"""

import hashlib
import json
import os
import sys
import time
from typing import Any

import requests  # type: ignore

# ============================================================
# 配置
# ============================================================

MEITUAN_DEVELOPER_ID = os.getenv("MEITUAN_DEVELOPER_ID", "")
MEITUAN_SIGN_KEY = os.getenv("MEITUAN_SIGN_KEY", "")
MEITUAN_GATEWAY = "https://api-open-cater.meituan.com"
MOCK_MODE = os.getenv("GRILL_MOCK_MODE", "true").lower() == "true"


# ============================================================
# 签名工具
# ============================================================

def sha1_sign(params: dict[str, str], sign_key: str) -> str:
    """美团开放平台 SHA1 签名算法

    1. 所有请求参数（sign 除外）按 key 字典序排列
    2. 拼接所有 value → param_str
    3. sign_str = SignKey + param_str + SignKey
    4. sign = SHA1(sign_str)
    """
    sorted_keys = sorted(k for k in params if k != "sign")
    param_str = "".join(str(params[k]) for k in sorted_keys)
    sign_str = f"{sign_key}{param_str}{sign_key}"
    return hashlib.sha1(sign_str.encode("utf-8")).hexdigest()


def make_request(path: str, biz_params: dict[str, Any], business_id: int = 2) -> dict:
    """向美团开放平台发送请求

    Args:
        path: API 路径，如 /waimai/poi/search
        biz_params: 业务参数
        business_id: 业务线 ID (2=外卖, 1=到店)
    """
    timestamp = str(int(time.time()))
    biz_json = json.dumps(biz_params, ensure_ascii=False, separators=(",", ":"))

    sys_params = {
        "developerId": MEITUAN_DEVELOPER_ID,
        "timestamp": timestamp,
        "version": "2",
        "businessId": str(business_id),
        "charset": "utf-8",
        "biz": biz_json,
    }
    sys_params["sign"] = sha1_sign(sys_params, MEITUAN_SIGN_KEY)

    try:
        resp = requests.post(
            f"{MEITUAN_GATEWAY}{path}",
            data=sys_params,
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"⚠️ 美团 API 请求失败：{e}", file=sys.stderr)
        return {"error": str(e)}
    except ValueError:
        print("⚠️ 美团 API 返回数据解析失败", file=sys.stderr)
        return {"error": "JSON 解析失败"}


# ============================================================
# Mock 数据 (高仿真)
# ============================================================

MOCK_RESTAURANTS: dict[str, list[dict[str, Any]]] = {
    "泰式": [
        {
            "name": "泰谣·冬阴功海鲜面",
            "rating": 4.7,
            "avg_price": 38,
            "delivery_time": 30,
            "deeplink": "meituanwaimai://shop/10001",
            "tags": ["酸辣", "海鲜", "冬阴功"],
            "top_comment": "冬阴功汤底绝了，酸辣度刚刚好，海鲜也很新鲜！",
        },
        {
            "name": "曼谷食堂",
            "rating": 4.5,
            "avg_price": 35,
            "delivery_time": 25,
            "deeplink": "meituanwaimai://shop/10002",
            "tags": ["泰式简餐", "凉面", "春卷"],
            "top_comment": "凉面夏天吃太爽了，分量足还不油腻",
        },
        {
            "name": "柠檬草泰式料理",
            "rating": 4.3,
            "avg_price": 42,
            "delivery_time": 40,
            "deeplink": "meituanwaimai://shop/10003",
            "tags": ["正宗泰味", "绿咖喱", "芒果糯米饭"],
        },
    ],
    "日料": [
        {
            "name": "丸龟制面",
            "rating": 4.6,
            "avg_price": 35,
            "delivery_time": 20,
            "deeplink": "meituanwaimai://shop/20001",
            "tags": ["乌冬面", "天妇罗", "日式简餐"],
            "top_comment": "乌冬面Q弹，天妇罗炸得恰到好处",
        },
        {
            "name": "争鲜回转寿司",
            "rating": 4.4,
            "avg_price": 30,
            "delivery_time": 35,
            "deeplink": "meituanwaimai://shop/20002",
            "tags": ["寿司", "刺身", "性价比高"],
        },
        {
            "name": "食其家",
            "rating": 4.2,
            "avg_price": 28,
            "delivery_time": 25,
            "deeplink": "meituanwaimai://shop/20003",
            "tags": ["牛丼", "咖喱", "快餐"],
        },
    ],
    "中餐": [
        {
            "name": "老王黄焖鸡米饭",
            "rating": 4.6,
            "avg_price": 28,
            "delivery_time": 20,
            "deeplink": "meituanwaimai://shop/30001",
            "tags": ["黄焖鸡", "米饭", "性价比"],
            "top_comment": "黄焖鸡味道正宗，汤汁拌饭一绝！",
        },
        {
            "name": "湘味小炒",
            "rating": 4.4,
            "avg_price": 32,
            "delivery_time": 25,
            "deeplink": "meituanwaimai://shop/30002",
            "tags": ["湘菜", "小炒肉", "下饭"],
        },
        {
            "name": "沙县小吃",
            "rating": 3.8,
            "avg_price": 12,
            "delivery_time": 15,
            "deeplink": "meituanwaimai://shop/30003",
            "tags": ["超值", "蒸饺", "拌面"],
        },
    ],
    "沙拉": [
        {
            "name": "Wagas 沃歌斯",
            "rating": 4.5,
            "avg_price": 45,
            "delivery_time": 30,
            "deeplink": "meituanwaimai://shop/40001",
            "tags": ["轻食", "沙拉", "果汁"],
        },
        {
            "name": "大开沙界",
            "rating": 4.3,
            "avg_price": 38,
            "delivery_time": 25,
            "deeplink": "meituanwaimai://shop/40002",
            "tags": ["自选沙拉", "低卡", "高蛋白"],
        },
    ],
    "凉面": [
        {
            "name": "凉面大王",
            "rating": 4.5,
            "avg_price": 22,
            "delivery_time": 20,
            "deeplink": "meituanwaimai://shop/50001",
            "tags": ["凉面", "拌面", "夏天必点"],
            "top_comment": "夏天吃这个太合适了，面不坨，酱汁很够味",
        },
        {
            "name": "四川凉面馆",
            "rating": 4.3,
            "avg_price": 18,
            "delivery_time": 25,
            "deeplink": "meituanwaimai://shop/50002",
            "tags": ["川味凉面", "酸辣", "鸡丝"],
        },
    ],
}


def mock_search(keyword: str) -> list[dict[str, Any]]:
    """使用 Mock 数据模拟搜索"""
    results: list[dict[str, Any]] = []
    kw_lower = keyword.lower()

    for category, restaurants in MOCK_RESTAURANTS.items():
        if category in kw_lower or any(
            kw_lower in r["name"].lower() for r in restaurants
        ):
            results.extend(restaurants)
            continue
        # 也检查 tags
        for r in restaurants:
            if any(kw_lower in t.lower() for t in r.get("tags", [])):
                if r not in results:
                    results.append(r)

    # 如果没有匹配，返回综合推荐
    if not results:
        results = [
            MOCK_RESTAURANTS["中餐"][0],
            MOCK_RESTAURANTS["日料"][0],
            MOCK_RESTAURANTS["泰式"][0],
        ]

    return results[:3]


# ============================================================
# 核心搜索函数
# ============================================================

def search_nearby(
    keyword: str,
    lat: float,
    lng: float,
    max_price: float = 40,
    min_rating: float = 4.0,
    max_delivery_time: int = 45,
    page_size: int = 10,
) -> list[dict[str, Any]]:
    """搜索附近外卖商家

    优先使用真实 API，未配置密钥时自动降级为 Mock 模式。
    """
    print(f"🔍 美团外卖搜索：「{keyword}」", file=sys.stderr)
    print(f"   坐标: ({lat:.4f}, {lng:.4f}) | 预算 ≤¥{max_price} | 评分 ≥{min_rating} | 配送 ≤{max_delivery_time}min", file=sys.stderr)
    print("", file=sys.stderr)

    # --- Mock 模式 ---
    if MOCK_MODE or not MEITUAN_DEVELOPER_ID or MEITUAN_DEVELOPER_ID.startswith("your_"):
        print("   ℹ️  Mock 模式（未配置真实 API 密钥）", file=sys.stderr)
        all_results = mock_search(keyword)
        # 过滤
        results = [
            r for r in all_results
            if r["avg_price"] <= max_price
            and r["rating"] >= min_rating
            and r["delivery_time"] <= max_delivery_time
        ]
        if not results:
            # 放宽过滤条件
            results = sorted(all_results, key=lambda r: r["rating"], reverse=True)[:3]
        return _format_output(results[:3])

    # --- 真实 API 模式 ---
    biz_params = {
        "keyword": keyword,
        "latitude": lat,
        "longitude": lng,
        "maxPrice": max_price,
        "minRating": min_rating,
        "maxDeliveryTime": max_delivery_time,
        "pageSize": page_size,
    }

    # 尝试门店查询 API（外卖）
    data = make_request("/waimai/poi/query/nearby", biz_params, business_id=2)

    # 如果上面路径不可用，尝试备选路径
    if data.get("error") or data.get("code") != 0:
        data = make_request("/gw/cater/poi/search", biz_params, business_id=2)

    if data.get("error"):
        print(f"   ⚠️ 真实 API 不可用，降级为 Mock", file=sys.stderr)
        all_results = mock_search(keyword)
        results = [
            r for r in all_results
            if r["avg_price"] <= max_price
            and r["rating"] >= min_rating
            and r["delivery_time"] <= max_delivery_time
        ]
        return _format_output(results[:3])

    # 解析真实 API 响应
    shops = data.get("data", {}).get("poiList", data.get("data", []))
    if not shops:
        print("   ℹ️  未找到匹配商家，降级为 Mock", file=sys.stderr)
        all_results = mock_search(keyword)
        results = [
            r for r in all_results
            if r["avg_price"] <= max_price
            and r["rating"] >= min_rating
        ]
        return _format_output(results[:3])

    formatted: list[dict[str, Any]] = []
    for i, shop in enumerate(shops[:3]):
        result = {
            "rank": i + 1,
            "source": "美团外卖",
            "name": shop.get("poiName", shop.get("name", "未知")),
            "rating": float(shop.get("score", shop.get("rating", 0))),
            "avg_price": float(shop.get("avgPrice", shop.get("avg_price", 0))),
            "delivery_time": int(shop.get("deliveryTime", shop.get("delivery_time", 0))),
            "deeplink": f"meituanwaimai://shop/{shop.get('poiId', shop.get('id', ''))}",
            "tags": shop.get("tags", []),
        }
        formatted.append(result)

    return _format_output(formatted[:3])


def _format_output(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """格式化并打印搜索结果"""
    if not results:
        print("   😞 没有找到匹配的商家", file=sys.stderr)
        return []

    # 确保结果有 rank 字段
    for i, r in enumerate(results):
        if "rank" not in r:
            r["rank"] = i + 1
        if "source" not in r:
            r["source"] = "美团外卖"

    print("", file=sys.stderr)
    for r in results:
        emoji = ["🥇", "🥈", "🥉"][r["rank"] - 1]
        tags_str = " · ".join(r.get("tags", [])[:3]) if r.get("tags") else ""
        print(
            f"  {emoji} {r['name']} | ⭐{r['rating']} | ¥{r['avg_price']} | 配送 {r['delivery_time']}min",
            file=sys.stderr,
        )
        if tags_str:
            print(f"     🏷️  {tags_str}", file=sys.stderr)
        if r.get("top_comment"):
            print(f"     💬「{r['top_comment'][:60]}」", file=sys.stderr)
        print(f"     👉 {r['deeplink']}", file=sys.stderr)
        print("", file=sys.stderr)

    return results


# ============================================================
# CLI
# ============================================================

def main() -> None:
    if len(sys.argv) < 4:
        print("用法: crawl-meituan.py <keyword> <lat> <lng> [max_price] [min_rating] [max_delivery_time]", file=sys.stderr)
        sys.exit(1)

    keyword = sys.argv[1]
    lat = float(sys.argv[2])
    lng = float(sys.argv[3])
    max_price = float(sys.argv[4]) if len(sys.argv) > 4 else 40
    min_rating = float(sys.argv[5]) if len(sys.argv) > 5 else 4.0
    max_delivery_time = int(sys.argv[6]) if len(sys.argv) > 6 else 45

    search_nearby(
        keyword=keyword,
        lat=lat,
        lng=lng,
        max_price=max_price,
        min_rating=min_rating,
        max_delivery_time=max_delivery_time,
    )


if __name__ == "__main__":
    main()
