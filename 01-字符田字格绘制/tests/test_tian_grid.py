"""作业 01 的 pytest 用例：形状、字符、参数校验各测一遍。"""

from __future__ import annotations

import pytest

from src.tian_grid import draw_tian, grid_size


def test_default_matches_textbook_figure() -> None:
    """默认参数就是教材图 5.16：21 行、每行 45 字符。"""
    lines = draw_tian().split("\n")
    assert len(lines) == 21
    assert all(len(line) == 45 for line in lines)


def test_border_and_body_rows() -> None:
    """边框行与格身行必须严格交替，不能出现接缝上的“++”。"""
    lines = draw_tian(4, 10, 4).split("\n")
    assert lines[0] == "+" + ("-" * 10 + "+") * 4
    assert lines[1] == "|" + (" " * 10 + "|") * 4
    border_rows = [i for i, line in enumerate(lines) if line.startswith("+")]
    assert border_rows == [0, 5, 10, 15, 20]
    assert all(line.count("+") == 5 for line in lines if line.startswith("+"))
    assert all(line.count("|") == 5 for line in lines if line.startswith("|"))


@pytest.mark.parametrize(
    "cells,width,height",
    [(1, 1, 1), (1, 6, 1), (2, 4, 2), (3, 3, 1), (4, 10, 4), (5, 5, 3)],
)
def test_grid_size_matches_output(cells: int, width: int, height: int) -> None:
    rows, cols = grid_size(cells, width, height)
    lines = draw_tian(cells, width, height).split("\n")
    assert len(lines) == rows
    assert all(len(line) == cols for line in lines)


def test_minimal_grid() -> None:
    assert draw_tian(1, 1, 1) == "+-+\n| |\n+-+"


def test_output_is_pure_ascii() -> None:
    """全部是 ASCII 字符，复制到任何等宽字体环境都不会错位。"""
    text = draw_tian(3, 7, 2)
    assert all(ord(ch) < 128 for ch in text)
    assert "\t" not in text


def test_no_trailing_newline() -> None:
    assert not draw_tian(2, 3, 1).endswith("\n")


def test_does_not_print(capsys: pytest.CaptureFixture[str]) -> None:
    """draw_tian 只返回字符串，打印由调用方负责。"""
    draw_tian(2, 2, 1)
    assert capsys.readouterr().out == ""


def test_height_changes_only_row_count() -> None:
    short = draw_tian(2, 3, 1).split("\n")
    tall = draw_tian(2, 3, 5).split("\n")
    assert len(tall) - len(short) == 2 * (5 - 1)
    assert all(len(line) == 9 for line in short + tall)


@pytest.mark.parametrize("bad", [0, -3])
def test_non_positive_values_raise_value_error(bad: int) -> None:
    with pytest.raises(ValueError):
        draw_tian(bad, 10, 4)
    with pytest.raises(ValueError):
        draw_tian(4, bad, 4)
    with pytest.raises(ValueError):
        draw_tian(4, 10, bad)


@pytest.mark.parametrize("bad", [2.5, "4", None, True])
def test_non_integer_values_raise_type_error(bad: object) -> None:
    with pytest.raises(TypeError):
        draw_tian(bad, 10, 4)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        draw_tian(4, bad, 4)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        draw_tian(4, 10, bad)  # type: ignore[arg-type]


def test_error_message_names_the_parameter() -> None:
    with pytest.raises(ValueError, match="width"):
        draw_tian(4, 0, 4)
    with pytest.raises(TypeError, match="height"):
        draw_tian(4, 10, "4")  # type: ignore[arg-type]
