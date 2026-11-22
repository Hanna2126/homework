"""作业 03 的 pytest 用例：采样、估面积、估 π、参数校验。"""

from __future__ import annotations

import math

import numpy as np
import pytest

from src.montecarlo import estimate_area, estimate_pi, pi_series, sample
from src.shapes import circle, grid_area, heart, polygon_area, snowflake, star

HEART_REF = grid_area(heart(), n=900)


def test_sample_single_point() -> None:
    x, y, inside = sample(circle(), 1, seed=1)
    assert x.shape == (1,) and inside.shape == (1,)


@pytest.mark.parametrize("n", [1000, 200_000])
def test_sample_hit_rate(n: int) -> None:
    shape = circle()
    x, y, inside = sample(shape, n, seed=1)
    assert x.shape == y.shape == inside.shape == (n,)
    assert inside.dtype == bool
    assert 0.70 < inside.mean() < 0.86  # π/4 ≈ 0.785


def test_sample_stays_inside_bbox() -> None:
    shape = heart()
    x, y, _ = sample(shape, 5000, seed=2)
    assert x.min() >= shape.bbox[0] and x.max() <= shape.bbox[1]
    assert y.min() >= shape.bbox[2] and y.max() <= shape.bbox[3]


def test_same_seed_reproduces() -> None:
    a = sample(circle(), 1000, seed=42)
    b = sample(circle(), 1000, seed=42)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[2], b[2])


def test_different_seed_changes_points() -> None:
    a = sample(circle(), 1000, seed=1)[0]
    b = sample(circle(), 1000, seed=2)[0]
    assert not np.array_equal(a, b)


def test_pi_estimate_accuracy() -> None:
    assert abs(estimate_pi(1_000_000, seed=5) - math.pi) < 0.01


def test_pi_series_shrinks() -> None:
    errors = [abs(v - math.pi) for v in pi_series([100, 10_000, 1_000_000], seed=8)]
    assert errors[0] > errors[1] > errors[2]


def test_circle_area() -> None:
    est = estimate_area(circle(), 200_000, seed=11)
    assert abs(est - math.pi) / math.pi < 0.01


def test_heart_area_matches_grid() -> None:
    est = estimate_area(heart(), 200_000, seed=12)
    assert abs(est - HEART_REF) / HEART_REF < 0.02


@pytest.mark.parametrize("factory", [lambda: star(), lambda: snowflake()])
def test_polygon_area_matches_shoelace(factory) -> None:  # type: ignore[no-untyped-def]
    shape = factory()
    est = estimate_area(shape, 200_000, seed=13)
    ref = shape.ref_area
    assert ref is not None
    assert abs(est - ref) / ref < 0.02


def test_star_vertices() -> None:
    shape = star()
    assert shape.name == "5 角星"
    assert shape.ref_area is not None and shape.ref_area > 1.0


def test_snowflake_bbox_and_area() -> None:
    shape = snowflake(3, size=2.0)
    assert shape.ref_area is not None
    # 边长 2 的初始三角形面积 √3；3 阶面积 = √3 × [1 + 3/4 Σ(4/9)^k]
    ratio = 1 + 0.75 * sum((4 / 9) ** k for k in range(1, 4))
    assert math.isclose(shape.ref_area, math.sqrt(3) * ratio, rel_tol=1e-12)


def test_heart_contains_known_points() -> None:
    shape = heart()
    yes = shape.contains(np.array([0.0, 0.0, 0.5]), np.array([0.1, -0.2, 0.3]))
    no = shape.contains(np.array([1.2, -1.2]), np.array([0.0, 0.0]))
    assert yes.all() and not no.any()


def test_bbox_area_positive() -> None:
    for shape in (circle(), heart(), star(), snowflake()):
        assert shape.bbox_area > 0


def test_polygon_area_square() -> None:
    assert math.isclose(polygon_area([(0, 0), (1, 0), (1, 1), (0, 1)]), 1.0)


@pytest.mark.parametrize("bad", [0, -3])
def test_non_positive_n_raises_value_error(bad: int) -> None:
    with pytest.raises(ValueError):
        estimate_area(circle(), bad)


@pytest.mark.parametrize("bad", [2.5, "100", None, True])
def test_non_integer_n_raises_type_error(bad: object) -> None:
    with pytest.raises(TypeError):
        estimate_pi(bad)  # type: ignore[arg-type]


def test_hit_rate_equals_mc_area_over_bbox() -> None:
    shape = circle()
    x, y, inside = sample(shape, 10_000, seed=4)
    hit = inside.mean()
    assert math.isclose(shape.bbox_area * hit, estimate_area(shape, 10_000, seed=4), rel_tol=1e-12)
