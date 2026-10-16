#!/usr/bin/env python3
"""Validate catalog structure and repository-local assets."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lokro_store.catalog import CatalogError, load_catalog  # noqa: E402


def main() -> int:
    try:
        catalog = load_catalog(ROOT / "catalog" / "v1" / "catalog.json")
        for item in catalog["items"]:
            icon = ROOT / item["icon"]
            if not icon.is_file():
                raise CatalogError(f"missing icon for {item['id']}: {item['icon']}")
    except (CatalogError, OSError) as error:
        print(f"catalog validation failed: {error}", file=sys.stderr)
        return 1
    print(f"catalog valid: {len(catalog['items'])} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
