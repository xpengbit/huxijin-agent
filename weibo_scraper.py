#!/usr/bin/env python3
"""
微博爬虫 - 抓取指定用户的帖子
用法: python weibo_scraper.py
"""

import requests
import json
import time
import csv
from pathlib import Path

# ============================================================
# 配置区 - 填你的信息
# ============================================================

# 从浏览器 F12 → Network → 任意请求 → 复制 Cookie header
COOKIE = "YOUR_COOKIE_HERE"
# 胡锡进的微博 UID（登录后访问他主页 URL 里的数字）
# 例如 https://weibo.com/u/1974576991 → UID = 1974576991
UID = "1989660417"

# 抓取页数（每页约 10 条）
MAX_PAGES = 20

# 输出文件
OUTPUT_FILE = "huxijin_weibo.json"

# ============================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
    "Referer": "https://m.weibo.cn/",
    "Cookie": COOKIE,
}


def get_uid_from_profile():
    """如果不知道 UID，通过用户名搜索"""
    url = f"https://m.weibo.cn/n/胡锡进"
    r = requests.get(url, headers=HEADERS, allow_redirects=True)
    print(f"Profile URL: {r.url}")
    # UID 在重定向 URL 里


def fetch_posts(uid: str, max_pages: int = 20) -> list[dict]:
    """抓取用户帖子"""
    container_id = f"107603{uid}"
    all_posts = []

    for page in range(1, max_pages + 1):
        url = "https://m.weibo.cn/api/container/getIndex"
        params = {
            "containerid": container_id,
            "page": page,
        }

        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=10)
            data = r.json()
        except Exception as e:
            print(f"第 {page} 页请求失败: {e}")
            break

        if data.get("ok") != 1:
            print(f"第 {page} 页返回异常: {data.get('msg', '未知错误')}")
            break

        cards = data.get("data", {}).get("cards", [])
        if not cards:
            print(f"第 {page} 页无数据，停止")
            break

        page_posts = []
        for card in cards:
            if card.get("card_type") != 9:  # type 9 = 微博正文
                continue
            mblog = card.get("mblog", {})
            post = {
                "id": mblog.get("id"),
                "created_at": mblog.get("created_at"),
                "text": clean_text(mblog.get("text", "")),
                "reposts_count": mblog.get("reposts_count", 0),
                "comments_count": mblog.get("comments_count", 0),
                "attitudes_count": mblog.get("attitudes_count", 0),
            }
            page_posts.append(post)

        print(f"第 {page} 页: 获取 {len(page_posts)} 条")
        all_posts.extend(page_posts)

        time.sleep(1.5)  # 礼貌性延迟

    return all_posts


def clean_text(html: str) -> str:
    """简单去除 HTML 标签"""
    import re
    text = re.sub(r'<[^>]+>', '', html)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return text.strip()


def save_posts(posts: list[dict], output_file: str):
    """保存为 JSON"""
    Path(output_file).write_text(
        json.dumps(posts, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\n共保存 {len(posts)} 条帖子 → {output_file}")


def main():
    if COOKIE == "YOUR_COOKIE_HERE":
        print("请先填写 COOKIE！")
        print("\n获取方式:")
        print("1. 浏览器登录 weibo.com")
        print("2. F12 → Network → 刷新页面")
        print("3. 点任意请求 → Headers → 复制 Cookie 的值")
        print("4. 粘贴到脚本顶部 COOKIE = '...'")
        return

    print(f"开始抓取 UID={UID} 的微博，共 {MAX_PAGES} 页...")
    posts = fetch_posts(UID, MAX_PAGES)
    save_posts(posts, OUTPUT_FILE)


if __name__ == "__main__":
    main()
