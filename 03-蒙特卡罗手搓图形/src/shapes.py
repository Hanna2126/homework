"""作业 03：用蒙特卡罗方法“手搓”图形。

思路：不给图形描边，而是在一个矩形框里均匀撒随机点，
落在图形内部的点保留下来，几万个点自然堆出图形的轮廓；
命中率 × 矩形面积就是图形面积的估计值。

四个图形：
- 圆：面积 π，命中率 π/4；
- 心形：隐函数 (x²+y²−1)³ − x²y³ ≤ 0；
- 五角星、科赫雪花：多边形，面积用鞋带公式精确算。
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sin, sqrt
from typing import Callable

import numpy as np
from matplotlib.path import Path

__all__ = [
    "Shape",
    "circle",
    "heart",
    "star",
    "snowflake",
    "grid_area",
    "polygon_area",
]


@dataclass(frozen=True)
class Shape:
    name: str
    bbox: tuple[float, float, float, float]  # xmin, xmax, ymin, ymax
    contains: Callable[[np.ndarray, np.ndarray], np.ndarray]
    ref_area: float | None = None  # 解析值；None 表示只能网格参考
    name_en: str = ""
    slug: str = ""

    @property
    def bbox_area(self) -> float:
        xmin, xmax, ymin, ymax = self.bbox
        return (xmax - xmin) * (ymax - ymin)


def circle(radius: float = 1.0) -> Shape:
    def contains(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return x * x + y * y <= radius * radius

    r = radius
    return Shape("圆", (-r, r, -r, r), contains, pi * r * r, "circle", "circle")


def heart() -> Shape:
    """经典心形曲线 (x²+y²−1)³ − x²y³ = 0 围成的区域。"""

    def contains(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return (x * x + y * y - 1) ** 3 - x * x * y**3 <= 0

    return Shape("心形", (-1.15, 1.15, -1.02, 1.26), contains, None, "heart", "heart")


def _polygon(vertices: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    pad = 0.02 * max(max(xs) - min(xs), max(ys) - min(ys))
    return (min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad)


def _contains_polygon(vertices: list[tuple[float, float]]):
    path = Path(vertices + [vertices[0]])

    def contains(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return path.contains_points(np.column_stack([x, y]))

    return contains


def polygon_area(vertices: list[tuple[float, float]]) -> float:
    """鞋带公式，顶点按逆时针排列。"""
    total = 0.0
    for (x1, y1), (x2, y2) in zip(vertices, vertices[1:] + vertices[:1]):
        total += x1 * y2 - x2 * y1
    return abs(total) / 2


def star(points: int = 5, outer: float = 1.0, inner: float = 0.382) -> Shape:
    vertices = []
    for k in range(2 * points):
        angle = pi / 2 + k * pi / points
        r = outer if k % 2 == 0 else inner
        vertices.append((r * cos(angle), r * sin(angle)))

    def contains(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return _contains_polygon(vertices)(x, y)

    return Shape(f"{points} 角星", _polygon(vertices), contains, polygon_area(vertices), "star", "star")


def _koch_curve(order: int, start: complex, end: complex) -> list[complex]:
    if order == 0:
        return [start, end]
    third = (end - start) / 3
    p1 = start + third
    p2 = p1 + third * complex(cos(-pi / 3), sin(-pi / 3))
    p3 = start + 2 * third
    return (
        _koch_curve(order - 1, start, p1)[:-1]
        + _koch_curve(order - 1, p1, p2)[:-1]
        + _koch_curve(order - 1, p2, p3)[:-1]
        + _koch_curve(order - 1, p3, end)
    )


def snowflake(order: int = 3, size: float = 2.0) -> Shape:
    radius = size / sqrt(3)
    corners = [complex(radius * cos(pi / 2 + 2 * pi * k / 3), radius * sin(pi / 2 + 2 * pi * k / 3)) for k in range(3)]
    points: list[complex] = []
    for k in range(3):
        seg = _koch_curve(order, corners[k], corners[(k + 1) % 3])
        points.extend(seg[:-1])
    points.append(points[0])
    vertices = [(p.real, p.imag) for p in points]

    def contains(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return _contains_polygon(vertices)(x, y)

    return Shape(f"雪花（{order} 阶）", _polygon(vertices), contains, polygon_area(vertices), "snowflake", "snowflake")


def grid_area(shape: Shape, n: int = 1200) -> float:
    """高密度网格积分，给没有解析式的图形当参考值。"""
    xmin, xmax, ymin, ymax = shape.bbox
    xs = np.linspace(xmin, xmax, n)
    ys = np.linspace(ymin, ymax, n)
    X, Y = np.meshgrid(xs, ys)
    return float(shape.bbox_area * shape.contains(X, Y).mean())
