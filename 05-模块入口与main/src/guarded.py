"""推荐写法：模块级只做定义，入口放在 main() 里，由 __name__ 守卫。"""

from __future__ import annotations


def serve() -> str:
    return "服务已启动"


def main() -> None:
    print(f"MAIN 执行：{serve()}")


if __name__ == "__main__":
    main()
