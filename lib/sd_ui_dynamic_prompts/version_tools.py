# NB: this file may not import anything from `sd_ui_dynamic_prompts` because it is used by `install.py`.

from __future__ import annotations

import dataclasses
import importlib.metadata
import logging
import re
import shlex
import subprocess
import sys
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path

try:
    import tomllib as tomli  # Python 3.11+
except ImportError:
    try:
        import tomli  # may have been installed already
    except ImportError:
        try:
            # pip has had this since version 21.2
            from pip._vendor import tomli
        except ImportError:
            raise ImportError(
                "A TOML library is required to install sd_forge_dynamicprompts, "
                "but could not be imported. "
                "Please install tomli (pip install tomli) and try again.",
            ) from None

try:
    from packaging.requirements import Requirement
except ImportError:
    # pip has had this since 2018
    from pip._vendor.packaging.requirements import (  # type: ignore[assignment]
        Requirement,
    )

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class InstallResult:
    requirement: Requirement
    installed: str | None

    @property
    def message(self) -> str | None:
        if self.correct:
            return None
        return (
            f"You have {self.requirement.name} version {self.installed or 'not'} installed, "
            f"but this extension requires version {self.requirement.specifier}. "
            f"Please run `install.py` from the sd_forge_dynamicprompts extension directory, "
            f"or `{self.pip_install_command}`."
        )

    @property
    def specifier_str(self) -> str:
        return str(self.requirement)

    @property
    def correct(self) -> bool:
        return bool(
            self.installed and self.requirement.specifier.contains(self.installed),
        )

    @property
    def pip_install_command(self) -> str:
        return f"pip install {self.specifier_str}"

    def raise_if_incorrect(self) -> None:
        message = self.message
        if message:
            raise RuntimeError(message)


@lru_cache(maxsize=1)
def get_requirements() -> tuple[str, ...]:
    toml_text = (Path(__file__).parent.parent.parent / "pyproject.toml").read_text()
    deps = tomli.loads(toml_text)["project"]["dependencies"]
    return tuple(str(dep) for dep in deps)


def get_install_result(req_str: str) -> InstallResult:
    req = Requirement(req_str)
    try:
        installed_version = importlib.metadata.version(req.name)
    except ImportError:
        installed_version = None
    res = InstallResult(requirement=req, installed=installed_version)
    return res


def get_requirements_install_results() -> Iterable[InstallResult]:
    """
    Get InstallResult objects for all requirements.
    """
    return (get_install_result(req_str) for req_str in get_requirements())


def get_dynamicprompts_install_result() -> InstallResult:
    """
    Get the InstallResult for the dynamicprompts requirement.

    This extension vendors the dynamicprompts package in its own directory,
    so the version is read from the vendored distribution rather than pip
    metadata.
    """
    requirement = Requirement("dynamicprompts~=0.29.0")
    return InstallResult(
        requirement=requirement,
        installed=_get_vendored_dynamicprompts_version(),
    )


def _get_vendored_dynamicprompts_version() -> str | None:
    """
    Get the version of the dynamicprompts package vendored in this
    extension's lib/ directory, or None if it is not present.
    """
    lib_dir = Path(__file__).parent.parent
    dist_infos = sorted(lib_dir.glob("dynamicprompts-*.dist-info"))
    for dist_info in dist_infos:
        try:
            return importlib.metadata.PathDistribution(dist_info).version
        except Exception:
            logger.exception(f"Failed to read version from {dist_info}")
    init_file = lib_dir / "dynamicprompts" / "__init__.py"
    try:
        for line in init_file.read_text("utf-8").splitlines():
            match = re.match(r'^__version__\s*=\s*["\']([^"\']+)["\']', line)
            if match:
                return match.group(1)
    except OSError:
        pass
    return None


def install_requirements(force=False) -> None:
    """
    Invoke pip to install the requirements for the extension.
    """
    try:
        from launch import args

        if getattr(args, "skip_install", False):
            logger.info(
                "webui launch.args.skip_install is true, skipping dynamicprompts installation",
            )
            return
    except ImportError:
        pass

    requirements_to_install = [
        str(ires.requirement)
        for ires in get_requirements_install_results()
        if (force or not ires.correct)
    ]

    if not requirements_to_install:
        return

    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        *requirements_to_install,
    ]
    print(f"sd_forge_dynamicprompts installer: running {shlex.join(command)}")
    subprocess.check_call(command)


def selftest() -> None:
    for res in get_requirements_install_results():
        print("[OK]" if res.correct else "????", res.requirement, res)


if __name__ == "__main__":
    selftest()
