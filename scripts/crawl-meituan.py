#!/usr/bin/env python3
"""美团开放平台 API 封装 — 搜索附近外卖商家

美团开放平台：https://open.meituan.com
需申请「外卖配送」或「到店餐饮」API 权限
"""

import hashlib
import os
import sys
import time
from typing import Any

import requests  # type: ignore

# 从环境变量读取密钥，避免硬编码
MEITUAN_APP_KEY = os.getenv("MEITUAN_APP_KEY", "your_app_key")
MEITUAN_APP_SECRET = os.getenv("MEITUAN_APP_SECRET", "your_app_secret")


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

    Args:
        keyword: 搜索关键词，如「泰式凉面」
        lat: 纬度
        lng: 经度
        max_price: 最高人均价格
        min_rating: 最低评分
        max_delivery_time: 最长配送时间（分钟）
        page_size: 返回结果数

    Returns:
        Top N 商家列表，含名称、评分、价格、配送时间、deep link
    """
    timestamp = int(time.time())
    sign = hashlib.md5(
        f"{MEITUAN_APP_KEY}{timestamp}{MEITUAN_APP_SECRET}".encode()
    ).hexdigest()

    try:
        resp = requests.get(
            "https://waimai-open.meituan.com/api/v1/poi/search",
            params={
                "app_key": MEITUAN_APP_KEY,
                "timestamp": timestamp,
                "sign": sign,
                "keyword": keyword,
                "latitude": lat,
                "longitude": lng,
                "max_price": max_price,
                "min_rating": min_rating,
                "max_delivery_time": max_delivery_time,
                "page_size": page_size,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"⚠️ 美团 API 请求失败：{e}", file=sys.stderr)
        return []
    except ValueError:
        print("⚠️ 美团 API 返回数据解析失败", file=sys.stderr)
        return []

    if data.get("code") != 0:
        print(f"⚠️ 美团 API 错误：{data.get('msg', '未知错误')}", file=sys.stderr)
        return []

    shops = data.get("data", [])
    results: list[dict[str, Any]] = []
    for i, shop in enumerate(shops[:3]):
        result = {
            "rank": i + 1,
            "source": "美团外卖",
            "name": shop.get("poi_name", "未知"),
            "rating": shop.get("wm_poi_score", 0),
            "avg_price": shop.get("avg_price", 0),
            "delivery_time": shop.get("delivery_time", 0),
            "deeplink": f"meituanwaimai://shop/{shop.get('wm_poi_id', '')}",
        }
        results.append(result)
        emoji = ["🥇", "🥈", "🥉"][i]
        print(
            f"  {emoji} {result['name']} | "
            f"⭐{result['rating']} | "
            f"¥{result['avg_price']} | "
            f"配送 {result['delivery_time']}min"
        )
        print(f"     👉 {result['deeplink']}")

    return results


def main() -> None:
    """CLI 入口：从命令行参数读取搜索条件"""
    if len(sys.argv) < 4:
        print(
            "用法: crawl-meituan.py <keyword> <lat> <lng> [max_price] [min_rating] [max_delivery_time]",
            file=sys.stderr,
        )
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
