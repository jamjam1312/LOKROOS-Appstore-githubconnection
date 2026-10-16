"""Safe command planning. Catalog data is never interpreted by a shell."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

FLATPAK_RE = re.compile(r"^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+){2,}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
FLATHUB_DESCRIPTOR = "https://dl.flathub.org/repo/flathub.flatpakrepo"
MAX_BUNDLE_BYTES = 512 * 1024 * 1024


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
    executable = shutil.which("lokro-store-flatpak") or "lokro-store-flatpak"
    if installed:
        arguments = ("update", ref)
        label = f"Update {item['name']}"
    else:
        arguments = ("install", ref)
        label = f"Install {item['name']}"
    return CommandPlan(executable, arguments, label)


def flatpak_bundle_plan(item: dict, installed: bool) -> CommandPlan:
    install = item.get("install", {})
    ref = install.get("ref")
    url = install.get("url")
    digest = install.get("sha256")
    if install.get("method") != "flatpak-bundle":
        raise InstallError("item is not an allowed Flatpak bundle")
    if not isinstance(ref, str) or not FLATPAK_RE.fullmatch(ref):
        raise InstallError("invalid Flatpak application ID")
    if not isinstance(url, str) or not _valid_bundle_url(url):
        raise InstallError("invalid Flatpak bundle URL")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise InstallError("invalid Flatpak bundle checksum")
    executable = shutil.which("lokro-store-flatpak") or "lokro-store-flatpak"
    arguments = ("install-bundle", ref, url, digest)
    label = f"Update {item['name']}" if installed else f"Install {item['name']}"
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
    if install.get("method") not in {"flatpak", "flatpak-bundle"}:
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


def _valid_bundle_url(raw: str) -> bool:
    parsed = urlparse(raw)
    return (
        parsed.scheme == "https"
        and bool(parsed.netloc)
        and parsed.username is None
        and parsed.password is None
        and parsed.path.endswith(".flatpak")
        and not parsed.query
        and not parsed.fragment
    )


def _run_flatpak(arguments: list[str]) -> None:
    executable = shutil.which("flatpak")
    if executable is None:
        raise InstallError("Flatpak ist nicht installiert")
    result = subprocess.run([executable, *arguments], check=False)
    if result.returncode:
        raise InstallError(f"Flatpak wurde mit Fehlercode {result.returncode} beendet")


def _ensure_flathub() -> None:
    executable = shutil.which("flatpak")
    if executable is None:
        raise InstallError("Flatpak ist nicht installiert")
    info = subprocess.run(
        [executable, "remotes", "--user", "--columns=name"],
        check=False,
        capture_output=True,
        text=True,
    )
    names = {line.strip() for line in info.stdout.splitlines()} if info.returncode == 0 else set()
    if "flathub" in names:
        _run_flatpak(["remote-modify", "--user", "--enable", "--url=https://dl.flathub.org/repo/", "flathub"])
    else:
        _run_flatpak(["remote-add", "--user", "--if-not-exists", "--from", "flathub", FLATHUB_DESCRIPTOR])


def _download_verified_bundle(url: str, expected_sha256: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "LOKRO-Store/0.1"})
    digest = sha256()
    total = 0
    with urllib.request.urlopen(request, timeout=30) as response, destination.open("xb") as output:
        while block := response.read(1024 * 1024):
            total += len(block)
            if total > MAX_BUNDLE_BYTES:
                raise InstallError("Flatpak-Bundle überschreitet das 512-MiB-Limit")
            digest.update(block)
            output.write(block)
    if digest.hexdigest() != expected_sha256:
        destination.unlink(missing_ok=True)
        raise InstallError("SHA-256-Prüfung des Flatpak-Bundles ist fehlgeschlagen")


def helper_main(arguments: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if arguments is None else arguments)
    try:
        if len(argv) == 2 and argv[0] in {"install", "update"} and FLATPAK_RE.fullmatch(argv[1]):
            action, ref = argv
            _ensure_flathub()
            if action == "install":
                _run_flatpak(["install", "--user", "--noninteractive", "flathub", ref])
            else:
                _run_flatpak(["update", "--user", "--noninteractive", ref])
            return 0
        if (
            len(argv) == 4
            and argv[0] == "install-bundle"
            and FLATPAK_RE.fullmatch(argv[1])
            and _valid_bundle_url(argv[2])
            and SHA256_RE.fullmatch(argv[3])
        ):
            _action, ref, url, expected_sha256 = argv
            with tempfile.TemporaryDirectory(prefix="lokro-store-flatpak-") as temporary:
                bundle = Path(temporary) / f"{ref}.flatpak"
                _download_verified_bundle(url, expected_sha256, bundle)
                _run_flatpak(["install", "--user", "--noninteractive", str(bundle)])
            return 0
        raise InstallError("Ungültiger Installationsauftrag")
    except (InstallError, OSError, urllib.error.URLError) as error:
        print(f"lokro-store-flatpak: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(helper_main())
