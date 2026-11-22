"""教材 P196 程序练习题 5.1：字符田字格绘制。

题目：用字符方式打印输出一个简单的田字格，效果如图 5.16；要求采用函数方式，
以田字格宽度为参数，能够根据参数绘制任意大小的田字格。

教材图 5.16 的样例可以量出来：每边 4 个格子，每格 10 个短横，格高 4 行（不含边框），
整块图形 45 个字符宽、21 行。

本模块只做两件事：
1. draw_tian —— 按参数生成整块字符画，返回字符串，不直接打印；
2. grid_size —— 事先算出这块字符画的（行数, 每行字符数），方便核对和测试。
"""

from __future__ import annotations

__all__ = ["draw_tian", "grid_size"]

# 教材图 5.16 的默认规格
CELLS_DEFAULT = 4    # 每边格子数
WIDTH_DEFAULT = 10   # 每格横向短横个数，也就是题目说的“田字格宽度”
HEIGHT_DEFAULT = 4   # 每格纵向内容行数（不含上下两条边框）


def _check_int(name: str, value: int) -> None:
    """参数必须是真正的 int，且为正数。bool 是 int 的子类，要单独拦掉。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} 必须是整数，收到 {type(value).__name__}: {value!r}")
    if value <= 0:
        raise ValueError(f"{name} 必须是正整数，收到 {value}")


def grid_size(cells: int, width: int, height: int) -> tuple[int, int]:
    """返回田字格的 (总行数, 每行字符数)。"""
    _check_int("cells", cells)
    _check_int("width", width)
    _check_int("height", height)
    rows = cells * (height + 1) + 1
    cols = cells * (width + 1) + 1
    return rows, cols


def draw_tian(
    cells: int = CELLS_DEFAULT,
    width: int = WIDTH_DEFAULT,
    height: int = HEIGHT_DEFAULT,
) -> str:
    """生成一个字符田字格，返回不带末尾换行的字符串。

    cells  —— 每边格子数，默认 4
    width  —— 每格短横个数，默认 10
    height —— 每格竖线行数，默认 4
    """
    _check_int("cells", cells)
    _check_int("width", width)
    _check_int("height", height)

    # 一条边框行：+---------+---------+---------+---------+
    border = "+" + ("-" * width + "+") * cells
    # 一条格身行：|         |         |         |         |
    body = "|" + (" " * width + "|") * cells

    lines = [border]
    for _ in range(cells):
        lines.extend([body] * height)
        lines.append(border)
    return "\n".join(lines)
