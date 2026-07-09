#!/usr/bin/env python3
"""大众点评开放平台 API 封装 — 搜索高分餐厅

大众点评开放平台：https://open.dianping.com
需申请「商户搜索」API 权限
"""

import os
import sys
from typing import Any

import requests  # type: ignore

DIANPING_API_KEY = os.getenv("DIANPING_API_KEY", "your_api_key")


def search_restaurant(
    keyword: str,
    city: str = "上海",
    min_rating: float = 4.5,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """搜索大众点评高分餐厅，带真实用户评价摘要

    Args:
        keyword: 搜索关键词
        city: 城市
        min_rating: 最低评分
        limit: 返回结果数上限

    Returns:
        Top N 餐厅列表，含名称、评分、人均价格、评价摘要、标签
    """
    try:
        resp = requests.get(
            "https://openapi.dianping.com/v1/business/search",
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
        print(f"⚠️ 大众点评 API 请求失败：{e}", file=sys.stderr)
        return []
    except ValueError:
        print("⚠️ 大众点评 API 返回数据解析失败", file=sys.stderr)
        return []

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

        emoji = ["🥇", "🥈", "🥉"][count - 1]
        tags_str = " · ".join(result["tags"][:3]) if result["tags"] else ""
        print(
            f"  {emoji} {result['name']} | "
            f"⭐{result['rating']} | "
            f"¥{result['avg_price']} | "
            f"{tags_str}"
        )
        if result["top_comment"]:
            print(f"     💬「{result['top_comment'][:60]}」")
        print(f"     👉 {result['url']}")

    return results


def main() -> None:
    """CLI 入口：从命令行参数读取搜索条件"""
    if len(sys.argv) < 2:
        print(
            "用法: crawl-dianping.py <keyword> [city] [min_rating]",
            file=sys.stderr,
        )
        sys.exit(1)

    keyword = sys.argv[1]
    city = sys.argv[2] if len(sys.argv) > 2 else "上海"
    min_rating = float(sys.argv[3]) if len(sys.argv) > 3 else 4.5

    search_restaurant(keyword=keyword, city=city, min_rating=min_rating)


if __name__ == "__main__":
    main()
