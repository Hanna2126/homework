"""作业 03 的命令行演示。

    python demo.py metrics   # 四个图形的面积估计 + π 的收敛表
    python demo.py render    # 点画与曲线
    python demo.py all
"""

from __future__ import annotations

import argparse
import unicodedata

from src.montecarlo import estimate_area, estimate_pi, sample
from src.render import render_all
from src.shapes import Shape, circle, grid_area, heart, snowflake, star

INDENT = "  "
GAP = " | "


def emit(text: object = "") -> None:
    if text == "":
        print()
        return
    for line in str(text).split("\n"):
        print(f"{INDENT}{line}" if line else "")


def display_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def pad(text: str, width: int, align: str = ">") -> str:
    fill = " " * max(0, width - display_width(text))
    return fill + text if align == ">" else text + fill


def render_table(title: str, headers: list[str], rows: list[list[str]], aligns: list[str]) -> None:
    widths = [display_width(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], display_width(cell))
    rule = "-" * (sum(widths) + len(GAP) * (len(widths) - 1))
    emit("=" * len(rule))
    emit(title)
    emit("=" * len(rule))
    emit(GAP.join(pad(h, w, "^") for h, w in zip(headers, widths)))
    emit(rule)
    for row in rows:
        emit(GAP.join(pad(c, w, a) for c, w, a in zip(row, widths, aligns)))
    emit(rule)


def reference_of(shape: Shape) -> tuple[float, str]:
    if shape.ref_area is not None:
        return shape.ref_area, "解析"
    return grid_area(shape), "网格 1200×1200"


def show_metrics() -> None:
    ns_area = 200_000
    shapes = [circle(), heart(), star(), snowflake()]
    rows = []
    for shape in shapes:
        x, y, inside = sample(shape, ns_area, seed=3)
        est = shape.bbox_area * inside.mean()
        ref, source = reference_of(shape)
        rows.append(
            [
                shape.name,
                f"{shape.bbox_area:.4f}",
                f"{ns_area:,}",
                f"{inside.mean():.4f}",
                f"{est:.5f}",
                f"{ref:.5f}",
                f"{abs(est - ref) / ref * 100:.2f}%",
                source,
            ]
        )

    emit()
    emit()
    emit()
    render_table(
        f"蒙特卡罗估面积（每个图形撒 {ns_area:,} 个点，seed = 3）",
        ["图形", "bbox 面积", "采样数", "命中率", "MC 面积", "参考面积", "相对误差", "参考来源"],
        rows,
        ["<", ">", ">", ">", ">", ">", ">", "<"],
    )

    ns_pi = [10**k for k in range(1, 7)]
    pi_rows = []
    for n in ns_pi:
        ests = [estimate_pi(n, seed=9 + s) for s in range(5)]
        est = sum(ests) / len(ests)
        err = sum(abs(e - 3.1415926535) for e in ests) / len(ests)
        pi_rows.append([f"{n:,}", f"{est:.6f}", f"{err:.6f}"])
    emit()
    render_table(
        "用随机点估 π（单位正方形 + 1/4 圆，每个 n 跑 5 个 seed 取平均）",
        ["采样数 n", "π 估计值（5 次均值）", "平均绝对误差"],
        pi_rows,
        [">", ">", ">"],
    )
    emit(f"误差按 1/√n 收敛：n 放大 100 倍，误差大约降到 1/10。")


def do_render() -> None:
    for path in render_all():
        emit(f"生成 {path.name}")


SECTIONS = {"metrics": show_metrics, "render": do_render}


def main() -> None:
    parser = argparse.ArgumentParser(description="蒙特卡罗手搓图形")
    parser.add_argument("section", nargs="?", default="all", choices=[*SECTIONS, "all"])
    args = parser.parse_args()
    for name in list(SECTIONS) if args.section == "all" else [args.section]:
        SECTIONS[name]()


if __name__ == "__main__":
    main()
