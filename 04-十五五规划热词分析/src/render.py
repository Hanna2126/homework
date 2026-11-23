"""把词频结果画成图：柱状图、词云、分部分热力图。"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

from .corpus import Section
from .hotwords import per_1000, tokenize, top_words

ROOT = Path(__file__).resolve().parent.parent
SHOT_DIR = ROOT / "截图"
FONT_FILE = Path("C:/Windows/Fonts/msyh.ttc")


def _font(size: int = 12) -> FontProperties:
    return FontProperties(fname=str(FONT_FILE), size=size)


def plot_bar(counter: Counter[str], out: Path, n: int = 20, total: int | None = None) -> Path:
    items = top_words(counter, n)[::-1]
    words = [w for w, _ in items]
    counts = [c for _, c in items]
    total = total or sum(counter.values())

    fig, ax = plt.subplots(figsize=(9.2, 7.2), dpi=200)
    colors = plt.cm.YlOrRd(np.linspace(0.28, 0.92, len(counts)))
    bars = ax.barh(words, counts, color=colors, edgecolor="#7a3b12", linewidth=0.6)

    for bar, c in zip(bars, counts):
        ax.text(bar.get_width() + max(counts) * 0.012, bar.get_y() + bar.get_height() / 2,
                f"{c}  ({per_1000(c, total):.1f}‰)", va="center", fontproperties=_font(9), color="#333")

    ax.set_xlim(0, max(counts) * 1.22)
    ax.set_title(f"《十五五规划建议》高频词 TOP {n}", fontproperties=_font(17), pad=14)
    ax.set_xlabel("出现次数（括号内为每千词频次）", fontproperties=_font(10))
    ax.tick_params(axis="y", labelsize=10)
    for lbl in ax.get_yticklabels():
        lbl.set_fontproperties(_font(10))
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def plot_wordcloud(counter: Counter[str], out: Path, max_words: int = 180) -> Path:
    from wordcloud import WordCloud

    wc = WordCloud(
        font_path=str(FONT_FILE),
        width=1800, height=1100,
        background_color="white",
        max_words=max_words,
        colormap="viridis",
        prefer_horizontal=0.92,
        relative_scaling=0.55,
        margin=6,
    )
    wc.generate_from_frequencies(dict(counter))
    fig, ax = plt.subplots(figsize=(11, 6.8), dpi=200)
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.tight_layout(pad=0)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def section_rates(sections: list[Section], words: list[str], stops: set[str] | None = None) -> np.ndarray:
    """每个部分里，每个目标词的每千词频次。"""
    rows = []
    for sec in sections:
        toks = tokenize(sec.body, stops)
        c = Counter(toks)
        rows.append([per_1000(c[w], len(toks)) for w in words])
    return np.array(rows)


def plot_heatmap(sections: list[Section], counter: Counter[str], out: Path, n: int = 12) -> Path:
    words = [w for w, _ in top_words(counter, n)]
    data = section_rates(sections, words)

    fig, ax = plt.subplots(figsize=(12.4, 6.4), dpi=200)
    im = ax.imshow(data, cmap="YlGnBu", aspect="auto")
    ax.set_xticks(range(len(words)), labels=words)
    for lbl in ax.get_xticklabels():
        lbl.set_fontproperties(_font(9.5))
    short = [f"{s.label}、{s.title[:13]}{'…' if len(s.title) > 13 else ''}" for s in sections]
    ax.set_yticks(range(len(sections)), labels=short)
    for lbl in ax.get_yticklabels():
        lbl.set_fontproperties(_font(9))

    for i in range(len(sections)):
        for j in range(len(words)):
            v = data[i, j]
            if v >= 1:
                ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                        fontproperties=_font(7.5), color="white" if v > data.max() * 0.62 else "#1b3a4b")

    ax.set_title("TOP 12 热词在 15 个部分中的分布（每千词频次）", fontproperties=_font(15), pad=12)
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.ax.tick_params(labelsize=8)
    ax.set_xlabel("热词", fontproperties=_font(10))
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out
