"""热词统计的单元测试：语料、分词、排名、出图。"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.corpus import (  # noqa: E402
    CN_NUM,
    DATA_FILE,
    Section,
    han_chars,
    load_text,
    paragraphs,
    split_sections,
)
from src.hotwords import (  # noqa: E402
    count_words,
    load_stopwords,
    noun_words,
    per_1000,
    tag,
    tokenize,
    top_words,
)
from src.render import section_rates  # noqa: E402

TEXT = load_text()
SECTIONS = split_sections(TEXT)
TOKENS = tokenize(TEXT)
COUNTS = count_words(TOKENS)


# ---------- 语料 ----------

def test_corpus_file_exists():
    assert DATA_FILE.exists(), "语料文件缺失"


def test_fifteen_sections():
    assert len(SECTIONS) == 15


def test_section_labels_are_ordered():
    assert [s.label for s in SECTIONS] == [k for k, v in sorted(CN_NUM.items(), key=lambda kv: kv[1])]


def test_section_index_matches_label():
    for sec in SECTIONS:
        assert sec.index == CN_NUM[sec.label]


def test_cn_num_has_fifteen_entries():
    assert len(CN_NUM) == 15 and CN_NUM["十五"] == 15


def test_paragraph_count():
    assert len(paragraphs(TEXT)) == 114


def test_han_char_count():
    assert han_chars(TEXT) == 18240


def test_section_chars_property():
    for sec in SECTIONS:
        assert sec.chars == len(sec.body)
        assert sec.chars > 0


def test_every_han_char_is_covered_by_a_section():
    """除开篇那段引言外，正文的每个汉字都应落在某个部分里。"""
    from src.corpus import SECTION_RE

    lines = paragraphs(TEXT)
    first = next(i for i, ln in enumerate(lines) if SECTION_RE.match(ln))
    preamble = "".join(lines[:first])
    covered = sum(han_chars(s.label + s.title + s.body) for s in SECTIONS)
    assert han_chars(TEXT) - covered == han_chars(preamble) == 54


def test_first_and_last_section_titles():
    assert SECTIONS[0].title.startswith("“十五五”时期是基本实现社会主义现代化")
    assert "全党全国各族人民团结起来" in SECTIONS[-1].title


def test_section_boundaries_reset_body():
    # 每个部分的正文都不应包含下一个部分的一级标题
    for sec in SECTIONS[:-1]:
        assert "十五、" not in sec.body


# ---------- 停用词与分词 ----------

def test_stopwords_not_empty():
    stops = load_stopwords()
    assert len(stops) >= 60


def test_stopwords_are_plain_words():
    for w in load_stopwords():
        assert w == w.strip()
        assert w and not w.startswith(('"', "“"))


def test_tokenize_drops_single_chars():
    got = tokenize("发展 的 经济 人 民", load_stopwords())
    assert got == ["发展", "经济"]


def test_tokenize_drops_stopwords():
    got = tokenize("我们 推进 建设 工作", load_stopwords())
    assert got == ["推进", "建设"]


def test_tokenize_keeps_long_terms():
    got = tokenize("现代化 社会主义 新质生产力", load_stopwords())
    assert "现代化" in got and "社会主义" in got
    # jieba 会把“新质生产力”切成“新质 / 生产力”，这里只保证能切出多字词
    assert all(len(w) >= 2 for w in got)


def test_count_words_basic():
    assert count_words(["发展", "发展", "建设"]) == Counter({"发展": 2, "建设": 1})


def test_top_words_order_and_limit():
    c = Counter({"发展": 5, "建设": 3, "创新": 3, "安全": 1})
    assert top_words(c, 2) == [("发展", 5), ("创新", 3)]
    assert len(top_words(c, 10)) == 4


def test_top_words_tie_breaks_by_text():
    c = Counter({"体系": 3, "安全": 3, "经济": 3})
    # 同频按 Unicode 码位排序：体(4F53) < 安(5B89) < 经(7ECF)
    assert [w for w, _ in top_words(c)] == ["体系", "安全", "经济"]


def test_per_1000():
    assert per_1000(0, 100) == 0
    assert per_1000(5, 0) == 0
    assert per_1000(10, 1000) == pytest.approx(10.0)


def test_tag_returns_pos():
    pairs = tag("发展 体系 安全", load_stopwords())
    flags = dict(pairs)
    assert flags["发展"] == "vn"
    assert flags["体系"] == "n"


def test_noun_words_keeps_noun_flags():
    pairs = [("发展", "vn"), ("推进", "v"), ("体系", "n"), ("安全", "an"), ("的", "uj")]
    assert noun_words(pairs) == ["发展", "体系", "安全"]


# ---------- 真实语料上的结论 ----------

def test_top_word_is_development():
    assert top_words(COUNTS, 1) == [("发展", 173)]


def test_second_word_is_construction():
    assert top_words(COUNTS, 2)[1] == ("建设", 129)


def test_token_stats():
    assert len(TOKENS) == 7331
    assert len(COUNTS) == 2159


def test_development_covers_all_sections():
    covers = sum(1 for s in SECTIONS if "发展" in tokenize(s.body, load_stopwords()))
    assert covers == 15


def test_section_rates_shape_and_range():
    rates = section_rates(SECTIONS, ["发展", "安全"])
    assert rates.shape == (15, 2)
    assert rates.min() >= 0 and rates.max() < 100


def test_security_is_hottest_in_section_thirteen():
    rates = section_rates(SECTIONS, ["安全"])
    assert int(rates.argmax()) == 12  # 下标 12 即第十三个部分


# ---------- 出图 ----------

@pytest.fixture(scope="module")
def small_counter():
    return Counter({"发展": 173, "建设": 129, "推进": 106, "加强": 100, "完善": 81, "体系": 68})


def test_plot_bar(tmp_path, small_counter):
    from src.render import plot_bar
    out = plot_bar(small_counter, tmp_path / "bar.png", n=5)
    assert out.exists() and out.stat().st_size > 5000


def test_plot_wordcloud(tmp_path, small_counter):
    from src.render import plot_wordcloud
    out = plot_wordcloud(small_counter, tmp_path / "wc.png")
    assert out.exists() and out.stat().st_size > 5000


def test_plot_heatmap(tmp_path, small_counter):
    from src.render import plot_heatmap
    out = plot_heatmap(SECTIONS, small_counter, tmp_path / "heat.png", n=4)
    assert out.exists() and out.stat().st_size > 5000


def test_section_is_frozen_dataclass():
    sec = SECTIONS[0]
    with pytest.raises(Exception):
        sec.title = "改标题"  # type: ignore[misc]
