# 作业 05 · 模块入口与 `__main__`

> 题目：`if __name__ == '__main__':` 的含义，why?

用六种真实启动方式测出 `__name__` 的取值矩阵，再用 guarded / unprotected 两个模块对比 import 副作用，最后验证脚本模式与 `python -m` 的相对导入差异。

结论一句话：这行代码判断的是「当前模块是不是被 Python 当作程序入口在执行」；作用是把「定义」和「执行」分开，让同一份文件既能被 import，也能单独运行。

## 运行

```bash
python demo.py matrix      # 六种启动方式的身份矩阵
python demo.py import      # 守卫 / 无守卫的 import 对比
python demo.py relative    # 脚本 vs -m 的相对导入
python demo.py all

python -m pytest -q        # 22 条用例
```

## 目录

```
05-模块入口与main/
├── src/
│   ├── name_probe.py    # 打印 __name__ / __package__ / sys.modules['__main__']
│   ├── guarded.py       # 正确写法：main() + 守卫
│   ├── unprotected.py   # 反面教材：顶层副作用
│   ├── relative_demo.py # 相对导入实验
│   ├── greeting.py
│   └── __main__.py      # python -m src 的包入口
├── tests/test_name_main.py
├── demo.py
├── 截图/                # 01 矩阵，02 守卫对比，03 相对导入，04 pytest
├── blog/
└── pytest.ini
```

## 输出规格

六种启动方式：

| 启动方式 | `__name__` | `__package__` | `sys.modules['__main__']` |
| --- | --- | --- | --- |
| `python src/name_probe.py` | `__main__` | `None` | `__main__` |
| `python -m src.name_probe` | `__main__` | `src` | `__main__` |
| `python -m src` | `__main__` | `src` | `__main__` |
| `import src.name_probe` | `src.name_probe` | `src` | `__main__` |
| `runpy.run_module(..., run_name='alias')` | `alias` | `src` | `__main__` |
| `exec(..., {'__name__': 'fake'})` | `fake` | `None` | `__main__` |

import 副作用对比：

- `import src.guarded`：无输出，只定义；
- `python src/guarded.py`：输出 `MAIN 执行：服务已启动`；
- `import src.unprotected`：立刻打印顶层副作用。

相对导入：

- `python src/relative_demo.py`：`RELATIVE=fail ImportError`（没有包上下文）；
- `python -m src.relative_demo`：`RELATIVE=ok hello from src.greeting`。

## 测试

```text
22 passed
```

覆盖：六种启动方式的 `__name__` / `__package__`、守卫在 import 与直接运行时的差异、`main` 导入后仍可调用、unprotected 的顶层副作用、相对导入的失败与成功、`src/__main__.py` 入口、`__name__` 类型、包名。

## 说明

- 截图 01~04 全部来自本机真实运行；矩阵用 `subprocess` 逐个启动解释器后解析输出，不是手写表格。
- `__name__` 是可被 `runpy` / `exec` 改写的普通字符串，守卫不是安全边界，只是「模块 / 程序」两种身份的约定。
- `python -m` 与脚本模式的差异（`__package__`、相对导入）在博客第 3 节有实测截图。
