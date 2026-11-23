"""抓取《十五五规划建议》全文并清洗成一行一段的纯文本。

来源：维基文库收录的《中共中央关于制定国民经济和社会发展第十五个五年规划的建议》全文
（原文由中国政府网 2025-10-28 受权发布）。gov.cn 页面有反爬壳，正文抓不到，
所以脚本用维基文库的同文备份，正文与官方发布一致。

    python tools/fetch_text.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

TITLE = "中共中央关于制定国民经济和社会发展第十五个五年规划的建议"
API = "https://zh.wikisource.org/w/api.php"

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "十五五规划建议.txt"


def fetch_wikitext() -> str:
    params = {
        "action": "parse",
        "page": TITLE,
        "prop": "text",
        "format": "json",
        "formatversion": "2",
        "disableeditsection": "1",
    }
    r = requests.get(API, params=params, timeout=30, headers={"User-Agent": "homework-bot/1.0"})
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise SystemExit(data["error"])
    return data["parse"]["text"]


def clean(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["sup", "style", "script", "table"]):
        tag.decompose()
    lines: list[str] = []
    for node in soup.find_all(["h2", "h3", "p"]):
        text = node.get_text(" ", strip=True)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        # 维基的版权模板尾巴从这里开始，后面全部丢掉
        if text.startswith("中国共产党的领导人讲话") or "维基文库社群" in text:
            break
        # 跳过维基的导航/版权尾巴
        if text.startswith(("导航", "检索", "分类", "本作品", "Public domain")):
            continue
        lines.append(text)
    return lines


def main() -> None:
    html = fetch_wikitext()
    lines = clean(html)
    body = [ln for ln in lines if len(ln) >= 8]
    text = "\n".join(body)
    cn = sum("\u4e00" <= c <= "\u9fff" for c in text)
    if cn < 15000:
        raise SystemExit(f"正文太短（{cn} 个汉字），抓取可能失败")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text + "\n", encoding="utf-8")
    print(f"写入 {OUT}：{len(body)} 段，{cn} 个汉字")
    print("开头：", body[0][:60])
    print("结尾：", body[-1][:60])


if __name__ == "__main__":
    sys.exit(main())
