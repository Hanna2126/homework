"""把随机点渲染成 PNG：点画、四图对比、收敛曲线。"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from src.montecarlo import estimate_area, sample  # noqa: E402
from src.shapes import Shape, circle, grid_area, heart, snowflake, star  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SHOT_DIR = ROOT / "截图"

DEFAULT_SHAPES = [circle(), heart(), star(), snowflake()]


def _dot_axis(ax, shape: Shape, n: int, seed: int, color: str) -> None:
    x, y, inside = sample(shape, n, seed)
    ax.scatter(x[~inside], y[~inside], s=0.3, c="#e6e6e6", linewidths=0, rasterized=True)
    ax.scatter(x[inside], y[inside], s=0.4, c=color, linewidths=0, rasterized=True)
    ax.set_xlim(shape.bbox[0], shape.bbox[1])
    ax.set_ylim(shape.bbox[2], shape.bbox[3])
    ax.set_aspect("equal")
    ax.axis("off")


def render_pi(path: Path, n: int = 30000, seed: int = 7) -> Path:
    fig = plt.figure(figsize=(6, 6), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    rng = np.random.default_rng(seed)
    x = rng.uniform(0, 1, n)
    y = rng.uniform(0, 1, n)
    inside = x * x + y * y <= 1
    ax.scatter(x[~inside], y[~inside], s=0.4, c="#dedede", linewidths=0, rasterized=True)
    ax.scatter(x[inside], y[inside], s=0.5, c="#2f6fdb", linewidths=0, rasterized=True)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path


def render_shape(shape: Shape, path: Path, n: int = 60000, seed: int = 11) -> Path:
    fig = plt.figure(figsize=(6, 6), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    _dot_axis(ax, shape, n, seed, "#c0392b")
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path


def render_gallery(path: Path, n: int = 50000) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(10, 10), dpi=160)
    for ax, shape, seed in zip(axes.ravel(), DEFAULT_SHAPES, (21, 22, 23, 24)):
        _dot_axis(ax, shape, n, seed, "#c0392b")
        ax.set_title(f"Monte Carlo · {shape.name_en} · {n:,} dots", fontsize=9, color="#444444")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.96, bottom=0.01, wspace=0.02, hspace=0.06)
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path


def render_convergence(path: Path, ns: list[int] | None = None, runs: int = 5) -> Path:
    ns = ns or [10**k for k in range(2, 7)]
    fig, ax = plt.subplots(figsize=(8, 5.4), dpi=150)
    colors = ["#2f6fdb", "#c0392b", "#e67e22", "#16a085"]
    for shape, color in zip(DEFAULT_SHAPES, colors):
        ref = shape.ref_area if shape.ref_area is not None else grid_area(shape, n=900)
        errors = []
        for n in ns:
            errs = [abs(estimate_area(shape, n, seed=s) - ref) / ref for s in range(runs)]
            errors.append(np.mean(errs))
        ax.plot(ns, errors, "o-", color=color, linewidth=1.4, markersize=4, label=shape.name_en)
    x = np.array(ns, dtype=float)
    ax.plot(x, 0.4 / np.sqrt(x), "--", color="#888888", linewidth=1, label="0.4 / sqrt(n)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("samples n")
    ax.set_ylabel("mean relative error")
    ax.set_title(f"Monte Carlo error vs sample size (mean of {runs} runs)", fontsize=11, color="#333333")
    ax.grid(True, which="both", alpha=0.25, linewidth=0.6)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path


def render_all() -> list[Path]:
    SHOT_DIR.mkdir(exist_ok=True)
    paths = [render_pi(SHOT_DIR / "01-圆周率散点.png")]
    names = ["02-圆.png", "03-心形.png", "04-五角星.png", "05-雪花.png"]
    for shape, name in zip(DEFAULT_SHAPES, names):
        paths.append(render_shape(shape, SHOT_DIR / name))
    paths.append(render_gallery(SHOT_DIR / "06-四图对比.png"))
    paths.append(render_convergence(SHOT_DIR / "07-收敛曲线.png"))
    return paths
