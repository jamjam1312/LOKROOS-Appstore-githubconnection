"""Strict validation and filtering for the untrusted public catalog."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

MAX_CATALOG_BYTES = 2 * 1024 * 1024
ITEM_KINDS = {"application", "design-pack", "cursor", "theme", "wallpaper"}
ITEM_KEYS = {
    "id", "kind", "name", "summary", "description", "categories", "icon",
    "homepage", "source", "license", "featured", "install",
}
ROOT_KEYS = {"$schema", "schemaVersion", "generatedAt", "repository", "items"}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FLATPAK_RE = re.compile(r"^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+){2,}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class CatalogError(ValueError):
    """The catalog is malformed or asks for an unsafe action."""


def _text(value: Any, field: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise CatalogError(f"{field} must be a non-empty string up to {maximum} characters")
    return value


def _https(value: Any, field: str) -> str:
    text = _text(value, field, 2048)
    parsed = urlparse(text)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise CatalogError(f"{field} must be a credential-free HTTPS URL")
    return text


def _validate_icon(value: Any) -> str:
    icon = _text(value, "icon", 180)
    if "\\" in icon:
        raise CatalogError("icon must use a safe repository-relative path")
    path = PurePosixPath(icon)
    if path.is_absolute() or ".." in path.parts or path.parts[:2] != ("assets", "icons"):
        raise CatalogError("icon must live under assets/icons")
    if path.suffix.lower() not in {".png", ".svg", ".webp"}:
        raise CatalogError("icon must be PNG, SVG or WebP")
    return icon


def _validate_install(value: Any, kind: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise CatalogError("install must be an object")
    method = value.get("method")
    if method == "flatpak":
        if set(value) != {"method", "remote", "ref"}:
            raise CatalogError("flatpak install has unknown or missing fields")
        if kind != "application" or value.get("remote") != "flathub":
            raise CatalogError("flatpak is allowed only for applications on flathub")
        ref = value.get("ref")
        if not isinstance(ref, str) or not FLATPAK_RE.fullmatch(ref):
            raise CatalogError("invalid Flatpak application ID")
    elif method == "lokro-design-pack":
        if set(value) != {"method", "url", "sha256"}:
            raise CatalogError("design-pack install has unknown or missing fields")
        if kind not in {"design-pack", "cursor", "theme", "wallpaper"}:
            raise CatalogError("design-pack installation is not valid for this item kind")
        url = _https(value.get("url"), "install.url")
        if not urlparse(url).path.endswith(".lokrodesign"):
            raise CatalogError("design-pack URL must end in .lokrodesign")
        digest = value.get("sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise CatalogError("design-pack sha256 must be 64 lowercase hexadecimal characters")
    elif method == "builtin":
        if set(value) != {"method"}:
            raise CatalogError("builtin install has unknown fields")
    elif method == "project-link":
        if set(value) != {"method", "url"}:
            raise CatalogError("project-link has unknown or missing fields")
        if kind != "application":
            raise CatalogError("project-link is allowed only for applications")
        _https(value.get("url"), "install.url")
    else:
        raise CatalogError(f"unsupported install method: {method!r}")
    return dict(value)


def validate_catalog(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) - ROOT_KEYS:
        raise CatalogError("catalog root must be an object with only documented fields")
    if value.get("schemaVersion") != 1:
        raise CatalogError("only catalog schemaVersion 1 is supported")
    _https(value.get("repository"), "repository")
    generated = _text(value.get("generatedAt"), "generatedAt", 64)
    try:
        datetime.fromisoformat(generated.replace("Z", "+00:00"))
    except ValueError as error:
        raise CatalogError("generatedAt must be an ISO-8601 timestamp") from error
    items = value.get("items")
    if not isinstance(items, list) or len(items) > 2000:
        raise CatalogError("items must be an array with at most 2000 entries")
    seen: set[str] = set()
    clean_items: list[dict[str, Any]] = []
    for position, item in enumerate(items):
        prefix = f"items[{position}]"
        if not isinstance(item, dict) or set(item) != ITEM_KEYS:
            raise CatalogError(f"{prefix} has unknown or missing fields")
        item_id = _text(item.get("id"), f"{prefix}.id", 80)
        if not ID_RE.fullmatch(item_id) or item_id in seen:
            raise CatalogError(f"{prefix}.id is invalid or duplicated")
        seen.add(item_id)
        kind = item.get("kind")
        if kind not in ITEM_KINDS:
            raise CatalogError(f"{prefix}.kind is unsupported")
        categories = item.get("categories")
        if not isinstance(categories, list) or not categories or len(categories) > 12:
            raise CatalogError(f"{prefix}.categories must contain 1 to 12 entries")
        clean_categories: list[str] = []
        for category in categories:
            clean_category = _text(category, f"{prefix}.categories", 40)
            if clean_category in clean_categories:
                raise CatalogError(f"{prefix}.categories contains duplicates")
            clean_categories.append(clean_category)
        clean_items.append({
            "id": item_id,
            "kind": kind,
            "name": _text(item.get("name"), f"{prefix}.name", 80),
            "summary": _text(item.get("summary"), f"{prefix}.summary", 120),
            "description": _text(item.get("description"), f"{prefix}.description", 600),
            "categories": clean_categories,
            "icon": _validate_icon(item.get("icon")),
            "homepage": _https(item.get("homepage"), f"{prefix}.homepage"),
            "source": _https(item.get("source"), f"{prefix}.source"),
            "license": _text(item.get("license"), f"{prefix}.license", 120),
            "featured": item.get("featured") if isinstance(item.get("featured"), bool) else False,
            "install": _validate_install(item.get("install"), kind),
        })
        if not isinstance(item.get("featured"), bool):
            raise CatalogError(f"{prefix}.featured must be boolean")
    return {
        "$schema": value.get("$schema", ""),
        "schemaVersion": 1,
        "generatedAt": generated,
        "repository": value["repository"],
        "items": clean_items,
    }


def loads_catalog(raw: bytes | str) -> dict[str, Any]:
    if isinstance(raw, bytes):
        if len(raw) > MAX_CATALOG_BYTES:
            raise CatalogError("catalog exceeds the 2 MiB limit")
        raw = raw.decode("utf-8")
    elif len(raw.encode("utf-8")) > MAX_CATALOG_BYTES:
        raise CatalogError("catalog exceeds the 2 MiB limit")
    try:
        return validate_catalog(json.loads(raw))
    except (json.JSONDecodeError, UnicodeError) as error:
        raise CatalogError(f"catalog is not valid UTF-8 JSON: {error}") from error


def load_catalog(path: Path) -> dict[str, Any]:
    return loads_catalog(path.read_bytes())


def filter_items(items: list[dict[str, Any]], query: str = "", category: str = "Alle") -> list[dict[str, Any]]:
    needle = query.casefold().strip()
    result = []
    for item in items:
        if category not in {"", "Alle"} and category not in item["categories"] and category != item["kind"]:
            continue
        haystack = " ".join([
            item["name"], item["summary"], item["description"], item["kind"], *item["categories"]
        ]).casefold()
        if needle and needle not in haystack:
            continue
        result.append(item)
    return sorted(result, key=lambda row: (not row["featured"], row["name"].casefold()))
