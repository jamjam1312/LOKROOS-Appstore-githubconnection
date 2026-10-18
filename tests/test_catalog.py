from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from lokro_store.catalog import CatalogError, filter_items, load_catalog, loads_catalog, validate_catalog

ROOT = Path(__file__).resolve().parents[1]
ARTCRAFT_APPS = {
    "artcraft-photocraft": "ai.storyteller.photocraft",
    "artcraft-vectorcraft": "ai.storyteller.vectorcraft",
    "artcraft-filmcraft": "ai.storyteller.filmcraft",
    "artcraft-lightcraft": "ai.storyteller.lightcraft",
    "artcraft-pdfcraft": "ai.storyteller.pdfcraft",
    "artcraft-effectcraft": "ai.storyteller.effectcraft",
    "artcraft-designcraft": "ai.storyteller.designcraft",
    "artcraft-figcraft": "ai.storyteller.figcraft",
    "artcraft-wordcraft": "ai.storyteller.wordcraft",
    "artcraft-soundcraft": "ai.storyteller.soundcraft",
    "artcraft-deckcraft": "ai.storyteller.deckcraft",
    "artcraft-cadcraft": "ai.storyteller.cadcraft",
    "artcraft-gridcraft": "ai.storyteller.gridcraft",
}


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
        self.assertIn("lokro-monochrome-large-cursor", {item["id"] for item in filter_items(self.catalog["items"], category="design-pack")})

    def test_artcraft_is_an_immutable_checksummed_flatpak_bundle(self) -> None:
        item = next(item for item in self.catalog["items"] if item["id"] == "artcraft-launcher")
        self.assertEqual(item["install"]["method"], "flatpak-bundle")
        self.assertIn("/releases/download/v0.3.2/", item["install"]["url"])
        self.assertEqual(len(item["install"]["sha256"]), 64)
        candidate = copy.deepcopy(self.catalog)
        candidate["items"][-1]["install"]["url"] = "https://github.com/storytold/craft-launcher/releases/latest"
        with self.assertRaises(CatalogError):
            validate_catalog(candidate)

    def test_artcraft_apps_are_individually_installable_and_pinned(self) -> None:
        by_id = {item["id"]: item for item in self.catalog["items"]}
        self.assertLessEqual(ARTCRAFT_APPS.keys(), by_id.keys())
        for item_id, flatpak_id in ARTCRAFT_APPS.items():
            install = by_id[item_id]["install"]
            self.assertEqual(install["method"], "flatpak-bundle")
            self.assertEqual(install["ref"], flatpak_id)
            self.assertRegex(install["url"], r"/releases/download/v[0-9]+\.[0-9]+\.[0-9]+/")
            self.assertTrue(install["url"].endswith("-linux-x86_64.flatpak"))
            self.assertRegex(install["sha256"], r"^[0-9a-f]{64}$")

    def test_unknown_install_method_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.catalog)
        candidate["items"][0]["install"] = {"method": "shell", "command": "anything"}
        with self.assertRaises(CatalogError):
            validate_catalog(candidate)

    def test_design_pack_is_versioned_and_checksummed(self) -> None:
        item = next(item for item in self.catalog["items"] if item["id"] == "lokro-monochrome-large-cursor")
        self.assertEqual(item["install"]["method"], "lokro-design-pack")
        self.assertIn("/v0.1.0-alpha.6/", item["install"]["url"])
        self.assertEqual(item["install"]["sha256"], "8c039c36e67c3f8cce3d00a712ca88138298cacb721cdef7096f85797be1b7e0")

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
