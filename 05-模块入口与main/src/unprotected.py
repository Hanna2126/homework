"""反面教材：入口逻辑直接写在模块顶层，一被 import 就执行。"""

from __future__ import annotations

print("[unprotected] 模块级副作用执行了：假装启动服务、解析命令行参数")


def serve() -> str:
    return "服务已启动"


# 等价于“没有 if __name__ == '__main__' 守卫”
serve()
