from __future__ import annotations

import dataclasses
from pathlib import Path

@dataclasses.dataclass(frozen=True)
class Source:
    name: str
    path: Path