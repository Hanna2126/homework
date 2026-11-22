"""把科赫雪花渲染成 PNG（matplotlib，不需要 GUI）。

图形来自 src.koch.snowflake() 的真实顶点，和 turtle 版用的是同一套坐标。
"""

from __future__ import annotations

from math import ceil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from src.koch import snowflake  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SHOT_DIR = ROOT / "截图"


def _plot(ax, order: int, size: float = 1.0, lw: float = 0.9) -> None:
    pts = snowflake(order, size)
    ax.plot(
        [p.real for p in pts],
        [p.imag for p in pts],
        color="#111111",
        linewidth=lw,
        solid_capstyle="round",
    )
    limit = max(abs(p) for p in pts) * 1.06
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)


def render_order(order: int, path: Path, pixels: int = 900) -> Path:
    fig = plt.figure(figsize=(6, 6), dpi=pixels // 6)
    ax = fig.add_axes([0, 0, 1, 1])
    _plot(ax, order)
    ax.axis("off")
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path


def render_grid(orders: list[int], path: Path, cols: int = 3, panel_px: int = 520) -> Path:
    rows = ceil(len(orders) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 4), dpi=130)
    axes = axes.ravel()
    for ax, order in zip(axes, orders):
        _plot(ax, order)
        ax.axis("off")
        ax.set_title(f"n = {order}", fontsize=13, color="#333333")
    for ax in axes[len(orders):]:
        ax.axis("off")
    fig.subplots_adjust(wspace=0.02, hspace=0.10)
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path


def render_all() -> list[Path]:
    SHOT_DIR.mkdir(exist_ok=True)
    paths = []
    for order in range(5):
        paths.append(render_order(order, SHOT_DIR / f"0{order + 1}-阶数{order}.png"))
    paths.append(render_grid(list(range(5)), SHOT_DIR / "06-阶数对比.png"))
    return paths


if __name__ == "__main__":
    for p in render_all():
        print(f"生成 {p}")
