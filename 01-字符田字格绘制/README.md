# 作业 01：字符田字格绘制

教材 P196 程序练习题 5.1。用字符方式打印田字格（图 5.16 效果），要求采用函数方式，以田字格宽度为参数，能够绘制任意大小的田字格。

博客：[字符田字格绘制：把一条 print 拆成一个能任意缩放的函数](blog/字符田字格绘制.md)

## 实现

`src/tian_grid.py` 提供两个函数：

- `draw_tian(cells=4, width=10, height=4) -> str`：按参数生成整块字符画，返回字符串，不直接打印；
- `grid_size(cells, width, height) -> (rows, cols)`：算出图形的行数与每行字符数。

默认参数对应教材图 5.16：4×4 格、每格 10 个短横、格高 4 行，输出 45 字符宽、21 行。

## 快速开始

```bash
python demo.py textbook   # 教材图 5.16 复现
python demo.py sizes      # 1×1、2×2、3×3
python demo.py big        # 5×5
python demo.py heights    # 格高对比：height=1 与 height=3
python demo.py errors     # 非法参数
python demo.py all        # 全部

python -m pytest -v       # 20 条用例
```

## 输出规格

| cells | width | height | 每行字符数 | 总行数 |
| --- | --- | --- | --- | --- |
| 1 | 6 | 1 | 8 | 3 |
| 2 | 4 | 2 | 11 | 7 |
| 3 | 3 | 1 | 13 | 7 |
| 4 | 10 | 4 | 45 | 21 |
| 5 | 5 | 2 | 31 | 16 |

公式：每行 `1 + cells × (width + 1)` 个字符，总行数 `cells × (height + 1) + 1`。

## 目录结构

```text
01-字符田字格绘制/
├─ demo.py                    # 命令行演示
├─ pytest.ini                 # pythonpath = .
├─ src/tian_grid.py           # draw_tian / grid_size
├─ tests/test_tian_grid.py    # 20 条 pytest 用例
├─ 截图/                      # 6 张真实运行截图
└─ blog/                      # 博客与配图
```

## 环境

- Windows 11
- Python 3.13.18
- pytest 9.2.0
- 截图来自本机 Windows PowerShell 真实运行
