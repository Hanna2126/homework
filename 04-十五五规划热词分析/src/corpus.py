"""语料读取与按“部分”切分。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "十五五规划建议.txt"

CN_NUM = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    "十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15,
}
SECTION_RE = re.compile(r"^([一二三四五六七八九十]{1,3})、(.+)$")


@dataclass(frozen=True)
class Section:
    index: int
    label: str
    title: str
    body: str

    @property
    def chars(self) -> int:
        return len(self.body)


def load_text(path: Path = DATA_FILE) -> str:
    return path.read_text(encoding="utf-8")


def paragraphs(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def split_sections(text: str) -> list[Section]:
    """按“一、……”“二、……”这类一级标题切分，共 15 个部分。"""
    sections: list[Section] = []
    label = title = ""
    buf: list[str] = []

    def flush() -> None:
        if label and buf:
            sections.append(Section(CN_NUM[label], label, title, "\n".join(buf)))

    for line in paragraphs(text):
        m = SECTION_RE.match(line)
        if m and m.group(1) in CN_NUM:
            flush()
            label, title = m.group(1), m.group(2)
            buf = []
        elif label:
            buf.append(line)
    flush()
    return sections


def han_chars(text: str) -> int:
    return sum("\u4e00" <= ch <= "\u9fff" for ch in text)
