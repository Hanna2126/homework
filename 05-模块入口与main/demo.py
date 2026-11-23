"""演示 __name__ 在不同启动方式下的取值，以及守卫的作用。

用法：
    python demo.py matrix     # 六种启动方式的身份矩阵
    python demo.py import     # import 副作用对比
    python demo.py relative   # 相对导入：脚本 vs -m
    python demo.py all
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable
ENV = os.environ | {"PYTHONIOENCODING": "utf-8", "PYTHONWARNINGS": "ignore"}
W = 96


def dwidth(s: str) -> int:
    return sum(2 if ord(ch) > 0x2E7F else 1 for ch in s)


def pad(s: str, width: int) -> str:
    return s + " " * max(0, width - dwidth(s))


def run(args: list[str] | str) -> str:
    cmd = [PY, *args] if isinstance(args, list) else [PY, "-c", args]
    out = subprocess.run(cmd, cwd=ROOT, env=ENV, text=True, encoding="utf-8",
                         capture_output=True, timeout=30)
    return (out.stdout + out.stderr).strip()


def parse_name_line(text: str) -> dict[str, str]:
    for line in text.splitlines():
        if line.startswith("NAME="):
            return dict(pair.split("=", 1) for pair in line.split() if "=" in pair)
    return {}


def show_matrix() -> None:
    cases = [
        ("脚本  python src/name_probe.py", ["src/name_probe.py"]),
        ("模块  python -m src.name_probe", ["-m", "src.name_probe"]),
        ("包    python -m src", ["-m", "src"]),
        ("导入  import src.name_probe", "import src.name_probe as m; m.report()"),
        ("runpy run_name='alias'", "import runpy; g=runpy.run_module('src.name_probe', run_name='alias'); g['report']()"),
        ("exec  __name__='fake'", "ns={'__name__':'fake','__package__':None}; "
                                   "exec(open('src/name_probe.py',encoding='utf-8').read(), ns); ns['report']()"),
    ]
    print("=" * W)
    print("if __name__ == '__main__'：同一份代码，六种身份")
    print("=" * W)
    print(f"  {pad('启动方式', 32)}{pad('__name__', 16)}{pad('__package__', 12)}{pad('__main__', 12)}argv[0]")
    print("-" * W)
    for label, arg in cases:
        raw = parse_name_line(run(arg))
        info = {"name": raw.get("NAME", "?"), "package": raw.get("PACKAGE", "?"),
                "main": raw.get("MAIN", "?"), "argv0": raw.get("ARGV0", "?")}
        print(f"  {pad(label, 32)}{pad(info['name'], 16)}"
              f"{pad(info['package'], 12)}{pad(info['main'], 12)}{info['argv0']}")
    print("-" * W)
    print("  只有前三种让 __name__ 等于 '__main__'；import / runpy / exec 都不是。")
    print()


def show_import() -> None:
    print("【守卫有没有用：import 同一份文件】")
    print("-" * W)
    cases = [
        ("import src.guarded", "import src.guarded"),
        ("python src/guarded.py", ["src/guarded.py"]),
        ("import src.unprotected", "import src.unprotected"),
    ]
    for label, arg in cases:
        out = run(arg)
        print(f"  {label}")
        print(f"    {out if out else '（无输出：模块只被定义，main 没有执行）'}")
    print("-" * W)
    print("  guarded.py 被 import 时安静；unprotected.py 一被 import 就执行顶层副作用。")
    print()


def show_relative() -> None:
    print("【相对导入：脚本模式为什么容易炸】")
    print("-" * W)
    for label, arg in [("python src/relative_demo.py", ["src/relative_demo.py"]),
                       ("python -m src.relative_demo", ["-m", "src.relative_demo"])]:
        out = run(arg)
        first = out.splitlines()[0] if out else "（无输出）"
        print(f"  {pad(label, 30)} {first}")
    print("-" * W)
    print("  脚本模式把 src/ 当成 sys.path[0]，模块没有包上下文，相对导入失败；-m 才带 __package__。")
    print()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="all", choices=["matrix", "import", "relative", "all"])
    args = ap.parse_args()
    if args.cmd in ("matrix", "all"):
        show_matrix()
    if args.cmd in ("import", "all"):
        show_import()
    if args.cmd in ("relative", "all"):
        show_relative()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
