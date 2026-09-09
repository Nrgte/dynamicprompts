# Automatic1111 entry point.

import sys
from pathlib import Path

_LIB_DIR = str(Path(__file__).resolve().parent.parent / "lib")
if _LIB_DIR not in sys.path:
    sys.path.insert(0, _LIB_DIR)

from sd_ui_dynamic_prompts.dynamic_prompting import Script

__all__ = ["Script"]
