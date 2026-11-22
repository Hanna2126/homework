"""作业 02：科赫雪花（纯几何实现，不依赖 turtle / GUI）。

做法：用复数表示平面上的点，60° 旋转直接乘一个单位复数，
这样递归的时候不用三角函数、不用手写坐标矩阵。

约定：三角形顶点按逆时针排列，每条边向外“长”出一个等边三角形的尖角，
所以旋转角是 -60°（顺时针）。
"""

from __future__ import annotations

from cmath import exp, pi, sqrt

__all__ = [
    "koch_curve",
    "snowflake",
    "perimeter",
    "polygon_area",
    "segment_count",
]

# 逆时针方向的外凸旋转：-60°
OUTWARD = exp(-1j * pi / 3)


def _check_order(order: int) -> None:
    if isinstance(order, bool) or not isinstance(order, int):
        raise TypeError(f"order 必须是整数，收到 {type(order).__name__}: {order!r}")
    if order < 0:
        raise ValueError(f"order 必须是非负整数，收到 {order}")


def koch_curve(order: int, start: complex, end: complex) -> list[complex]:
    """返回从 start 到 end 的 order 阶科赫折线的所有顶点（含两端）。"""
    _check_order(order)
    if order == 0:
        return [start, end]

    third = (end - start) / 3
    p1 = start + third
    p2 = p1 + third * OUTWARD
    p3 = start + 2 * third

    return (
        koch_curve(order - 1, start, p1)[:-1]
        + koch_curve(order - 1, p1, p2)[:-1]
        + koch_curve(order - 1, p2, p3)[:-1]
        + koch_curve(order - 1, p3, end)
    )


def snowflake(order: int, size: float = 1.0, center: complex = 0j) -> list[complex]:
    """返回 order 阶科赫雪花的闭合折线顶点（最后一个点等于第一个点）。

    size 是初始等边三角形的边长。
    """
    _check_order(order)
    if size <= 0:
        raise ValueError(f"size 必须为正数，收到 {size}")

    radius = size / sqrt(3)  # 外接圆半径
    # 顶点放在 90°、210°、330°，逆时针排列，上方是尖的
    vertices = [center + radius * exp(1j * (pi / 2 + 2 * pi * k / 3)) for k in range(3)]

    points: list[complex] = []
    for k in range(3):
        segment = koch_curve(order, vertices[k], vertices[(k + 1) % 3])
        points.extend(segment[:-1])
    points.append(points[0])
    return points


def segment_count(order: int) -> int:
    """雪花的总线段数：3 × 4^order。"""
    _check_order(order)
    return 3 * 4**order


def perimeter(order: int, size: float = 1.0) -> float:
    """周长：3 × size × (4/3)^order。"""
    _check_order(order)
    return 3 * size * (4 / 3) ** order


def polygon_area(points: list[complex]) -> float:
    """用鞋带公式算闭合多边形的面积。"""
    if len(points) < 3:
        raise ValueError("至少需要 3 个点")
    total = 0j
    for a, b in zip(points, points[1:]):
        total += a.conjugate() * b
    # imag(conj(a) * b) = x_a·y_b - y_a·x_b，即鞋带公式里的叉积项
    return abs(total.imag) / 2
