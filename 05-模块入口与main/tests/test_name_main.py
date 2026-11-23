"""`if __name__ == '__main__'` 的实证测试：全部用子进程观察真实运行结果。"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
ENV = os.environ | {"PYTHONIOENCODING": "utf-8", "PYTHONWARNINGS": "ignore"}


def run(arg: list[str] | str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    cmd = [PY, *arg] if isinstance(arg, list) else [PY, "-c", arg]
    return subprocess.run(cmd, cwd=ROOT, env=ENV, text=True, encoding="utf-8",
                          capture_output=True, timeout=timeout)


def fields(arg: list[str] | str) -> dict[str, str]:
    out = run(arg).stdout
    for line in out.splitlines():
        if line.startswith("NAME="):
            return dict(pair.split("=", 1) for pair in line.split() if "=" in pair)
    raise AssertionError(f"没有找到 NAME= 行：{out!r}")


# ---------- 六种启动方式 ----------

def test_script_mode_name():
    f = fields(["src/name_probe.py"])
    assert f["NAME"] == "__main__"
    assert f["PACKAGE"] == "None"
    assert f["MAIN"] == "__main__"


def test_module_mode_name():
    f = fields(["-m", "src.name_probe"])
    assert f["NAME"] == "__main__"
    assert f["PACKAGE"] == "src"
    assert f["ARGV0"] == "name_probe.py"


def test_package_main_entry():
    out = run(["-m", "src"]).stdout
    assert "NAME=__main__" in out and "PACKAGE=src" in out
    assert "src/__main__.py" in out


def test_import_name():
    f = fields("import src.name_probe as m; m.report()")
    assert f["NAME"] == "src.name_probe"
    assert f["PACKAGE"] == "src"
    assert f["MAIN"] == "__main__"


def test_runpy_custom_run_name():
    f = fields("import runpy; g=runpy.run_module('src.name_probe', run_name='alias'); g['report']()")
    assert f["NAME"] == "alias"
    assert f["PACKAGE"] == "src"


def test_exec_custom_name():
    code = ("ns={'__name__':'fake','__package__':None}; "
            "exec(open('src/name_probe.py',encoding='utf-8').read(), ns); ns['report']()")
    f = fields(code)
    assert f["NAME"] == "fake"
    assert f["PACKAGE"] == "None"


def test_main_module_is_always_registered():
    out = run("import sys; print(sys.modules['__main__'].__name__)").stdout.strip()
    assert out == "__main__"


# ---------- 守卫的实际作用 ----------

def test_guarded_import_is_silent():
    out = run("import src.guarded").stdout
    assert out.strip() == ""


def test_guarded_run_executes_main():
    out = run(["src/guarded.py"]).stdout
    assert "MAIN 执行：服务已启动" in out


def test_guarded_main_is_callable_after_import():
    out = run("import src.guarded as g; print(callable(g.main)); g.main()").stdout
    assert out.splitlines()[0] == "True"
    assert "MAIN 执行" in out


def test_unprotected_import_has_side_effect():
    out = run("import src.unprotected").stdout
    assert "[unprotected] 模块级副作用执行了" in out


def test_unprotected_has_no_guard():
    src = (ROOT / "src" / "unprotected.py").read_text(encoding="utf-8")
    code = [ln for ln in src.splitlines() if not ln.strip().startswith("#")]
    assert not any("__name__" in ln for ln in code)


def test_guarded_source_contains_guard():
    src = (ROOT / "src" / "guarded.py").read_text(encoding="utf-8")
    assert "if __name__ == \"__main__\":" in src


def test_guarded_bad_import_does_not_exit_process():
    # 反面教材里没有 sys.exit；这里确认 import 后进程仍能继续执行后续语句
    out = run("import src.unprotected; print('AFTER-IMPORT-OK')").stdout
    assert "AFTER-IMPORT-OK" in out


# ---------- 相对导入 ----------

def test_relative_import_fails_as_script():
    out = run(["src/relative_demo.py"]).stdout
    assert out.startswith("RELATIVE=fail ImportError")
    assert "脚本模式没有包上下文" in out


def test_relative_import_works_with_dash_m():
    out = run(["-m", "src.relative_demo"]).stdout
    assert out.startswith("RELATIVE=ok hello from src.greeting")


def test_greeting_module():
    out = run("from src.greeting import hello; print(hello())").stdout.strip()
    assert out == "hello from src.greeting"


# ---------- 文件与包结构 ----------

def test_package_main_file_exists():
    assert (ROOT / "src" / "__main__.py").exists()


def test_probe_import_prints_nothing():
    assert run("import src.name_probe").stdout.strip() == ""


def test_report_is_callable_without_main_guard():
    out = run("import src.name_probe as m; print(callable(m.report))").stdout.strip()
    assert out == "True"


def test_dunder_name_is_string_when_imported():
    out = run("import src.name_probe as m; print(type(m.__name__).__name__)").stdout.strip()
    assert out == "str"


def test_package_dunder_name():
    out = run("import src; print(src.__name__)").stdout.strip()
    assert out == "src"
