"""Safe command planning. Catalog data is never interpreted by a shell."""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

FLATPAK_RE = re.compile(r"^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+){2,}$")


class InstallError(RuntimeError):
    pass


@dataclass(frozen=True)
class CommandPlan:
    executable: str
    arguments: tuple[str, ...]
    label: str


def flatpak_plan(item: dict, installed: bool) -> CommandPlan:
    install = item.get("install", {})
    ref = install.get("ref")
    if install.get("method") != "flatpak" or install.get("remote") != "flathub":
        raise InstallError("item is not an allowed Flathub application")
    if not isinstance(ref, str) or not FLATPAK_RE.fullmatch(ref):
        raise InstallError("invalid Flatpak application ID")
    executable = shutil.which("flatpak") or "flatpak"
    if installed:
        arguments = ("update", "--user", "--noninteractive", ref)
        label = f"Update {item['name']}"
    else:
        arguments = ("install", "--user", "--noninteractive", "flathub", ref)
        label = f"Install {item['name']}"
    return CommandPlan(executable, arguments, label)


def design_pack_plan(item: dict, verified_archive: Path) -> CommandPlan:
    install = item.get("install", {})
    if install.get("method") != "lokro-design-pack":
        raise InstallError("item is not a LOKRO design pack")
    if not verified_archive.is_file() or verified_archive.suffix != ".lokrodesign":
        raise InstallError("verified design-pack archive is missing")
    executable = shutil.which("lokro-design-pack") or "lokro-design-pack"
    return CommandPlan(executable, ("install", str(verified_archive)), f"Install {item['name']}")


def installation_scope(item: dict, runner: Callable[..., subprocess.CompletedProcess] = subprocess.run) -> str | None:
    install = item.get("install", {})
    if install.get("method") == "builtin":
        return "builtin"
    if install.get("method") != "flatpak":
        return None
    ref = install.get("ref", "")
    if not FLATPAK_RE.fullmatch(ref):
        return None
    flatpak = shutil.which("flatpak")
    if flatpak is None:
        return None
    for scope in ("--user", "--system"):
        result = runner([flatpak, "info", scope, ref], capture_output=True, check=False, timeout=8)
        if result.returncode == 0:
            return scope.removeprefix("--")
    return None


def is_installed(item: dict, runner: Callable[..., subprocess.CompletedProcess] = subprocess.run) -> bool:
    return installation_scope(item, runner) is not None
