"""turtle 版：在有 tkinter 的机器上运行，就是教材里那种画法。

    python src/draw_turtle.py 4      # 画 4 阶

和 src/koch.py 的几何完全一致：三角形顶点逆时针排列，每条边向左凸（外凸），
所以从上方顶点出发、航向 -60°，每画完一条边右转 120°。
"""

from __future__ import annotations

import sys


def koch(order: int, size: float) -> None:
    """沿当前航向画一条 order 阶科赫曲线，向左凸。"""
    if order == 0:
        import turtle

        turtle.forward(size)
        return
    koch(order - 1, size / 3)
    import turtle

    turtle.left(60)
    koch(order - 1, size / 3)
    turtle.right(120)
    koch(order - 1, size / 3)
    turtle.left(60)
    koch(order - 1, size / 3)


def draw_snowflake(order: int, size: float = 300, speed: int = 0) -> None:
    import turtle

    turtle.setup(720, 720)
    turtle.title(f"科赫雪花 · {order} 阶")
    turtle.speed(speed)
    turtle.hideturtle()
    turtle.penup()
    turtle.goto(0, size / (3 ** 0.5))  # 顶部顶点
    turtle.setheading(-60)
    turtle.pendown()
    for _ in range(3):
        koch(order, size)
        turtle.right(120)
    turtle.done()


if __name__ == "__main__":
    order = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    draw_snowflake(order)
