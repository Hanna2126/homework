"""作业 02 的命令行演示。

    python demo.py metrics   # 0~4 阶的线段数、周长、面积
    python demo.py render    # 生成 5 张单图 + 1 张对比图
    python demo.py all
"""

from __future__ import annotations

import argparse
import unicodedata
from math import sqrt

from src.koch import perimeter, polygon_area, snowflake
from src.render import render_all

INDENT = "  "
INITIAL_AREA = sqrt(3) / 4  # 边长 1 的等边三角形面积
GAP = " | "


def emit(text: object = "") -> None:
    if text == "":
        print()
        return
    for line in str(text).split("\n"):
        print(f"{INDENT}{line}" if line else "")


def display_width(text: str) -> int:
    """按等宽字体的占位宽度计数：中文/全角算 2 格，ASCII 算 1 格。"""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def pad(text: str, width: int, align: str = ">") -> str:
    fill = " " * max(0, width - display_width(text))
    return fill + text if align == ">" else text + fill


def table_row(cells: list[str], widths: list[int], aligns: list[str]) -> str:
    return GAP.join(pad(c, w, a) for c, w, a in zip(cells, widths, aligns))


def show_metrics() -> None:
    headers = ["n", "每边线段", "总线段", "周长", "面积", "面积/初始"]
    aligns = ["^", ">", ">", ">", ">", ">"]
    widths = [display_width(h) for h in headers]
    rows: list[list[str]] = []
    for order in range(5):
        area = polygon_area(snowflake(order, 1.0))
        rows.append(
            [
                str(order),
                str(4 ** order),
                str(3 * 4 ** order),
                f"{perimeter(order):.4f}",
                f"{area:.5f}",
                f"{area / INITIAL_AREA:.3f}",
            ]
        )
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], display_width(cell))

    rule = "-" * (sum(widths) + len(GAP) * (len(widths) - 1))
    emit()
    emit("=" * len(rule))
    emit("科赫雪花：0~4 阶的线段数、周长与面积（初始边长 = 1）")
    emit("=" * len(rule))
    emit(table_row(headers, widths, ["^"] * len(headers)))
    emit(rule)
    for row in rows:
        emit(table_row(row, widths, aligns))
    emit(rule)
    emit(f"极限：周长 → ∞，面积 → 8/5 初始三角形 = {INITIAL_AREA * 8 / 5:.5f}")
    emit("4 阶一共 3 × 4^4 = 768 条线段，点列 769 个。")


def do_render() -> None:
    for path in render_all():
        emit(f"生成 {path.name}")


SECTIONS = {
    "metrics": show_metrics,
    "render": do_render,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="科赫雪花演示")
    parser.add_argument("section", nargs="?", default="all", choices=[*SECTIONS, "all"])
    args = parser.parse_args()
    names = list(SECTIONS) if args.section == "all" else [args.section]
    for name in names:
        SECTIONS[name]()


if __name__ == "__main__":
    main()
