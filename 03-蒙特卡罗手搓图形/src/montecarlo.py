"""蒙特卡罗采样与积分：撒点、判定、估面积、估 π。"""

from __future__ import annotations

import numpy as np

from src.shapes import Shape

__all__ = ["sample", "estimate_area", "estimate_pi", "pi_series", "area_series"]


def _rng(seed: int | None) -> np.random.Generator:
    return np.random.default_rng(seed)


def _check_n(n: int) -> None:
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError(f"n 必须是整数，收到 {type(n).__name__}: {n!r}")
    if n <= 0:
        raise ValueError(f"n 必须是正整数，收到 {n}")


def sample(shape: Shape, n: int, seed: int | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """在 bbox 内均匀撒 n 个点，返回 (x, y, 是否命中)。"""
    _check_n(n)
    xmin, xmax, ymin, ymax = shape.bbox
    rng = _rng(seed)
    x = rng.uniform(xmin, xmax, n)
    y = rng.uniform(ymin, ymax, n)
    return x, y, np.asarray(shape.contains(x, y), dtype=bool)


def estimate_area(shape: Shape, n: int, seed: int | None = None) -> float:
    """命中率 × bbox 面积。"""
    _, _, inside = sample(shape, n, seed)
    return float(shape.bbox_area * inside.mean())


def estimate_pi(n: int, seed: int | None = None) -> float:
    """单位正方形里撒点，落在 1/4 圆内的比例 × 4。"""
    _check_n(n)
    rng = _rng(seed)
    x = rng.uniform(0.0, 1.0, n)
    y = rng.uniform(0.0, 1.0, n)
    return float(4.0 * ((x * x + y * y) <= 1.0).mean())


def pi_series(ns: list[int], seed: int | None = None) -> list[float]:
    return [estimate_pi(n, seed) for n in ns]


def area_series(shape: Shape, ns: list[int], seed: int | None = None) -> list[float]:
    return [estimate_area(shape, n, seed) for n in ns]
