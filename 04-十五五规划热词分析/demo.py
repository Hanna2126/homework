"""命令行演示：语料统计、热词榜、出图。

用法：
    python demo.py corpus     # 语料规模
    python demo.py table      # 总榜 TOP20
    python demo.py nouns      # 名词榜 TOP12
    python demo.py sections   # 每个部分的门面词
    python demo.py render     # 生成三张图到 截图/
    python demo.py all        # 上面全做
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter

from src.corpus import han_chars, load_text, paragraphs, split_sections
from src.hotwords import count_words, per_1000, tag, noun_words, tokenize, top_words
from src.render import SHOT_DIR, plot_bar, plot_heatmap, plot_wordcloud

W = 74


def dwidth(s: str) -> int:
    return sum(2 if ord(ch) > 0x2E7F else 1 for ch in s)


def pad(s: str, width: int) -> str:
    return s + " " * max(0, width - dwidth(s))


def rule(ch: str = "-") -> str:
    return ch * W


def show_corpus(text: str, sections: list, tokens: list[str], counter: Counter[str]) -> None:
    print(rule("="))
    print("《十五五规划建议》热词统计")
    print(rule("="))
    print(f"  段落数：{len(paragraphs(text))}    汉字数：{han_chars(text):,}    一级部分：{len(sections)}")
    print(f"  分词后词数：{len(tokens):,}    去重词数：{len(counter):,}")
    print("  语料来源：data/十五五规划建议.txt（2025-10-28 发布，约 2 万字）")
    print(rule("="))
    print()


def show_table(sections: list, tokens: list[str], counter: Counter[str], start: int = 1, end: int = 20) -> None:
    if start == 1:
        print("【总榜 TOP 20】")
    print(f"  {pad('名次', 4)}  {pad('词语', 10)}{pad('词频', 5)}  {pad('每千词', 8)}{pad('出现部分', 6)}".rstrip())
    print(rule())
    total = len(tokens)
    ranked = top_words(counter, end)
    for i, (w, c) in enumerate(ranked[start - 1:end], start):
        cover = sum(1 for s in sections if w in tokenize(s.body))
        print(f"  {pad(str(i), 4)}  {pad(w, 10)}{pad(str(c), 5)}  {pad(f'{per_1000(c, total):.2f}', 8)}{cover}/15".rstrip())
    print(rule())
    if end >= 20:
        print("  说明：已过滤单字与停用词；每千词 = 词频 / 总词数 × 1000。")
    print()


def show_nouns(text: str) -> None:
    pairs = tag(text)
    ncounter = count_words(noun_words(pairs))
    print("【名词榜 TOP 12】（只保留名词类词性：n / vn / an）")
    print(rule())
    print(f"  {pad('名次', 4)}  {pad('词语', 10)}{pad('词频', 5)}".rstrip())
    print(rule())
    for i, (w, c) in enumerate(top_words(ncounter, 12), 1):
        print(f"  {pad(str(i), 4)}  {pad(w, 10)}{pad(str(c), 5)}".rstrip())
    print(rule())
    print()


def show_sections(sections: list) -> None:
    print("【各部分的“门面词”】每部分取词频最高的 2 个词")
    print(rule())
    for sec in sections:
        toks = tokenize(sec.body)
        c = Counter(toks)
        head = "、".join(f"{w}({n})" for w, n in top_words(c, 2))
        disp = sec.title[:16] + ("…" if len(sec.title) > 16 else "")
        print(f"  {pad(sec.label, 4)} {pad(disp, 37)} {head}".rstrip())
    print(rule())
    print(f"  语料共 {han_chars(load_text()):,} 汉字，最大部分 {max(s.chars for s in sections)} 字，最小部分 {min(s.chars for s in sections)} 字。")
    print()


def do_render(text: str, sections: list, counter: Counter[str]) -> None:
    total = sum(counter.values())
    p1 = plot_bar(counter, SHOT_DIR / "04-TOP20柱状图.png", total=total)
    p2 = plot_wordcloud(counter, SHOT_DIR / "05-热词云.png")
    p3 = plot_heatmap(sections, counter, SHOT_DIR / "06-分部分热力图.png")
    for p in (p1, p2, p3):
        print(f"  已生成 {p.relative_to(SHOT_DIR.parent)}")


def main() -> int:
    ap = argparse.ArgumentParser(description="十五五规划建议热词统计")
    ap.add_argument("cmd", nargs="?", default="all",
                    choices=["corpus", "table", "nouns", "sections", "render", "all"])
    ap.add_argument("--start", type=int, default=1, help="总榜起始名次")
    ap.add_argument("--end", type=int, default=20, help="总榜结束名次")
    args = ap.parse_args()

    text = load_text()
    sections = split_sections(text)
    if len(sections) != 15:
        print(f"[警告] 只切出 {len(sections)} 个部分，预期 15 个。", file=sys.stderr)

    tokens = tokenize(text)
    counter = count_words(tokens)

    if args.cmd in ("corpus", "all"):
        show_corpus(text, sections, tokens, counter)
    if args.cmd in ("table", "all"):
        show_table(sections, tokens, counter, args.start, args.end)
    if args.cmd in ("nouns", "all"):
        show_nouns(text)
    if args.cmd in ("sections", "all"):
        show_sections(sections)
    if args.cmd in ("render", "all"):
        print("【出图】")
        do_render(text, sections, counter)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
