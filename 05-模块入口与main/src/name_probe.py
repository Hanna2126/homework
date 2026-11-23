"""打印当前模块的身份信息：__name__ / __package__ / sys.modules['__main__']。"""

from __future__ import annotations

import os
import sys


def snapshot() -> dict[str, str | None]:
    main = sys.modules.get("__main__")
    return {
        "__name__": __name__,
        "__package__": __package__,
        "__main__": getattr(main, "__name__", None),
        "argv0": os.path.basename(sys.argv[0]) if sys.argv else "",
    }


def report() -> None:
    s = snapshot()
    print(f"NAME={s['__name__']} PACKAGE={s['__package__']} MAIN={s['__main__']} ARGV0={s['argv0']}")


if __name__ == "__main__":
    report()
