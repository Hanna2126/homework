"""python -m src 时执行的包入口。"""

from __future__ import annotations

import os
import sys

print(f"NAME={__name__} PACKAGE={__package__} MAIN={sys.modules['__main__'].__name__} "
      f"ARGV0={os.path.basename(sys.argv[0])}")
print("[pkg] 这是 src/__main__.py：`python -m src` 的入口")
