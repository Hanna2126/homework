"""作业 01 的命令行演示：按小节打印字符田字格。

用法：
    python demo.py textbook   # 教材图 5.16 复现
    python demo.py sizes      # 1×1、2×2、3×3 三组小尺寸
    python demo.py big        # 5×5 的大图
    python demo.py heights    # 格高对比：height=1 与 height=3
    python demo.py errors     # 非法参数
    python demo.py all        # 全部
"""

from __future__ import annotations

import argparse

from src.tian_grid import draw_tian, grid_size

INDENT = "  "


def emit(text: object = "") -> None:
    """逐行输出，统一留两个空格边距（截图时不会贴住窗口边缘）。"""
    if text == "":
        print()
        return
    for line in str(text).split("\n"):
        print(f"{INDENT}{line}" if line else "")


def _title(text: str) -> None:
    emit()
    emit("=" * 52)
    emit(text)
    emit("=" * 52)


def show_textbook() -> None:
    _title("教材图 5.16 复现：cells=4, width=10, height=4")
    rows, cols = grid_size(4, 10, 4)
    emit(f"规格：{rows} 行 × {cols} 字符")
    emit()
    emit(draw_tian(4, 10, 4))


def show_sizes() -> None:
    _title("同一函数，改参数就能缩放")
    for cells, width, height in [(1, 6, 1), (2, 4, 2), (3, 3, 1)]:
        rows, cols = grid_size(cells, width, height)
        emit()
        emit(f"cells={cells}, width={width}, height={height} -> {rows} 行 × {cols} 字符")
        emit(draw_tian(cells, width, height))


def show_big() -> None:
    _title("大一点的：5×5 格，每格 5 个短横、2 行高")
    rows, cols = grid_size(5, 5, 2)
    emit(f"规格：{rows} 行 × {cols} 字符")
    emit()
    emit(draw_tian(5, 5, 2))


def show_heights() -> None:
    _title("height 决定格子有多“高”")
    for height in (1, 3):
        rows, cols = grid_size(2, 6, height)
        emit()
        emit(f"height={height} -> {rows} 行 × {cols} 字符")
        emit(draw_tian(2, 6, height))


def show_errors() -> None:
    _title("参数校验：画不出来的参数要当场拒绝")
    cases = [
        ("cells=0", lambda: draw_tian(0, 10, 4)),
        ("width=-2", lambda: draw_tian(4, -2, 4)),
        ("cells=2.5", lambda: draw_tian(2.5, 10, 4)),
        ("width='5'", lambda: draw_tian(4, "5", 4)),
        ("height=True", lambda: draw_tian(4, 10, True)),
    ]
    for label, call in cases:
        try:
            call()
        except Exception as exc:  # noqa: BLE001 - 演示就是要抓异常
            emit(f"{label:<12} -> {type(exc).__name__}: {exc}")
        else:
            emit(f"{label:<12} -> 没有报错（不应该）")


SECTIONS = {
    "textbook": show_textbook,
    "sizes": show_sizes,
    "big": show_big,
    "heights": show_heights,
    "errors": show_errors,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="字符田字格演示")
    parser.add_argument("section", nargs="?", default="all", choices=[*SECTIONS, "all"])
    args = parser.parse_args()

    names = list(SECTIONS) if args.section == "all" else [args.section]
    for name in names:
        SECTIONS[name]()


if __name__ == "__main__":
    main()
