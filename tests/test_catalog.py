from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from lokro_store.catalog import CatalogError, filter_items, load_catalog, loads_catalog, validate_catalog

ROOT = Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog(ROOT / "catalog" / "v1" / "catalog.json")

    def test_bundled_catalog_is_valid_and_unique(self) -> None:
        ids = [item["id"] for item in self.catalog["items"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 10)

    def test_search_matches_categories_and_description(self) -> None:
        self.assertIn("gimp", {item["id"] for item in filter_items(self.catalog["items"], "bildbearbeitung")})
        self.assertIn("libreoffice", {item["id"] for item in filter_items(self.catalog["items"], category="Büro")})
        self.assertIn("artcraft-launcher", {item["id"] for item in filter_items(self.catalog["items"], "wordcraft")})

    def test_project_link_is_https_and_never_a_shell_command(self) -> None:
        item = next(item for item in self.catalog["items"] if item["id"] == "artcraft-launcher")
        self.assertEqual(item["install"]["method"], "project-link")
        self.assertTrue(item["install"]["url"].startswith("https://github.com/storytold/"))
        candidate = copy.deepcopy(self.catalog)
        candidate["items"][-1]["install"]["url"] = "file:///tmp/payload"
        with self.assertRaises(CatalogError):
            validate_catalog(candidate)

    def test_unknown_install_method_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.catalog)
        candidate["items"][0]["install"] = {"method": "shell", "command": "anything"}
        with self.assertRaises(CatalogError):
            validate_catalog(candidate)

    def test_credentialed_url_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.catalog)
        candidate["items"][0]["source"] = "https://user:secret@example.invalid/repo"
        with self.assertRaises(CatalogError):
            validate_catalog(candidate)

    def test_traversal_icon_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.catalog)
        candidate["items"][0]["icon"] = "assets/icons/../../payload"
        with self.assertRaises(CatalogError):
            validate_catalog(candidate)

    def test_oversized_catalog_is_rejected(self) -> None:
        raw = json.dumps(self.catalog) + (" " * (2 * 1024 * 1024))
        with self.assertRaises(CatalogError):
            loads_catalog(raw)


if __name__ == "__main__":
    unittest.main()
