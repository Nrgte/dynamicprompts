from __future__ import annotations

import dataclasses

from dynamicprompts.commands import Command

@dataclasses.dataclass(frozen=True)
class ReplaceCommand(Command):
    var: Command | None = None
    src: Command | None = None
    dest: Command | None = None
    sampling_method = None
