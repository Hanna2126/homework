"""中文分词与词频统计。"""

from __future__ import annotations

import logging
import re
from collections import Counter
from pathlib import Path

import jieba
import jieba.posseg as pseg

jieba.setLogLevel(logging.WARNING)

ROOT = Path(__file__).resolve().parent.parent
STOPWORDS_FILE = ROOT / "data" / "stopwords.txt"

WORD_RE = re.compile(r"[\u4e00-\u9fff]{2,}")
NOUN_FLAGS = {"n", "nr", "ns", "nt", "nz", "vn", "an", "ng"}

__all__ = [
    "load_stopwords",
    "tokenize",
    "tag",
    "count_words",
    "top_words",
    "per_1000",
    "noun_words",
]


def load_stopwords(path: Path = STOPWORDS_FILE) -> set[str]:
    return {ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()}


def tokenize(text: str, stopwords: set[str] | None = None) -> list[str]:
    """jieba 精确模式分词：只保留 2 字以上的纯汉字词，并去掉停用词。"""
    stops = load_stopwords() if stopwords is None else stopwords
    return [w for w in jieba.cut(text) if WORD_RE.fullmatch(w) and w not in stops]


def tag(text: str, stopwords: set[str] | None = None) -> list[tuple[str, str]]:
    """带词性的分词，返回 (词, 词性)。"""
    stops = load_stopwords() if stopwords is None else stopwords
    return [(w.word, w.flag) for w in pseg.cut(text) if WORD_RE.fullmatch(w.word) and w.word not in stops]


def count_words(tokens: list[str]) -> Counter[str]:
    return Counter(tokens)


def top_words(counter: Counter[str], n: int = 20) -> list[tuple[str, int]]:
    # 频次降序，同频按字典序，保证结果稳定
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def per_1000(count: int, total: int) -> float:
    return count / total * 1000 if total else 0.0


def noun_words(pairs: list[tuple[str, str]]) -> list[str]:
    """从带词性的结果里挑名词类（含 vn/an），用于“名词榜”。"""
    return [w for w, flag in pairs if flag in NOUN_FLAGS]
