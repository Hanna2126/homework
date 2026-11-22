"""作业 02 的 pytest 用例：线段数、周长、面积、闭合性、对称性与参数校验。"""

from __future__ import annotations

import math

import pytest

from src.koch import koch_curve, perimeter, polygon_area, segment_count, snowflake

LIMIT_AREA = math.sqrt(3) / 4 * 8 / 5  # 边长 1 时，科赫雪花面积的极限 = 2√3/5


def test_segment_count_formula() -> None:
    assert [segment_count(n) for n in range(5)] == [3, 12, 48, 192, 768]


@pytest.mark.parametrize("order", range(5))
def test_curve_point_count(order: int) -> None:
    """一条科赫曲线有 4^n + 1 个顶点。"""
    pts = koch_curve(order, 0j, 1 + 0j)
    assert len(pts) == 4**order + 1
    assert pts[0] == 0j and pts[-1] == 1 + 0j


def test_order_zero_is_equilateral_triangle() -> None:
    pts = snowflake(0, 1.0)
    assert len(pts) == 4
    assert pts[0] == pts[-1]
    sides = [abs(b - a) for a, b in zip(pts, pts[1:])]
    assert all(math.isclose(s, 1.0, rel_tol=1e-12) for s in sides)


@pytest.mark.parametrize("order", range(5))
def test_snowflake_is_closed(order: int) -> None:
    pts = snowflake(order, 1.0)
    assert pts[0] == pts[-1]
    assert len(pts) == segment_count(order) + 1


@pytest.mark.parametrize("order", range(5))
def test_perimeter_matches_formula(order: int) -> None:
    pts = snowflake(order, 1.0)
    walked = sum(abs(b - a) for a, b in zip(pts, pts[1:]))
    assert math.isclose(walked, perimeter(order), rel_tol=1e-9)


def test_each_order_multiplies_perimeter_by_4_over_3() -> None:
    ratios = [perimeter(n + 1) / perimeter(n) for n in range(4)]
    assert all(math.isclose(r, 4 / 3, rel_tol=1e-12) for r in ratios)


def test_area_increases_and_converges() -> None:
    areas = [polygon_area(snowflake(n, 1.0)) for n in range(6)]
    assert all(b > a for a, b in zip(areas, areas[1:]))
    assert all(a < LIMIT_AREA for a in areas)
    assert math.isclose(areas[0], math.sqrt(3) / 4, rel_tol=1e-12)
    # 每一阶补上的小三角形面积是上一阶的 4/9，缺口按 4/9 等比缩小
    gaps = [LIMIT_AREA - a for a in areas]
    ratios = [b / a for a, b in zip(gaps, gaps[1:])]
    assert all(math.isclose(r, 4 / 9, rel_tol=1e-6) for r in ratios)
    assert gaps[-1] < 1e-2


def test_rotation_symmetry() -> None:
    """雪花绕中心转 120° 后，点集应重合（3 条边完全等价）。"""
    pts = snowflake(2, 1.0)
    rotated = [p * complex(math.cos(2 * math.pi / 3), math.sin(2 * math.pi / 3)) for p in pts]
    base = {(round(p.real, 9), round(p.imag, 9)) for p in pts}
    moved = {(round(p.real, 9), round(p.imag, 9)) for p in rotated}
    assert base == moved


def test_all_points_stay_inside_bounding_circle() -> None:
    for order in range(5):
        pts = snowflake(order, 1.0)
        radius = max(abs(p) for p in pts)
        assert radius < 1.0  # 边长 1 的雪花远小于半径 1 的圆


@pytest.mark.parametrize("bad", [-1, -5])
def test_negative_order_raises_value_error(bad: int) -> None:
    with pytest.raises(ValueError):
        snowflake(bad, 1.0)


@pytest.mark.parametrize("bad", [2.5, "3", None, True])
def test_non_integer_order_raises_type_error(bad: object) -> None:
    with pytest.raises(TypeError):
        snowflake(bad, 1.0)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", [0, -1.5])
def test_non_positive_size_raises_value_error(bad: float) -> None:
    with pytest.raises(ValueError):
        snowflake(2, bad)


def test_shoelace_area_on_unit_square() -> None:
    square = [0j, 1 + 0j, 1 + 1j, 0 + 1j, 0j]
    assert math.isclose(polygon_area(square), 1.0, rel_tol=1e-12)
