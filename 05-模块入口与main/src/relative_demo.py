"""相对导入实验：包内相对导入只对“按模块方式运行 / 被 import”成立。"""

from __future__ import annotations

try:
    from .greeting import hello

    print(f"RELATIVE=ok {hello()}")
except ImportError as exc:
    print(f"RELATIVE=fail {type(exc).__name__}（脚本模式没有包上下文）")
