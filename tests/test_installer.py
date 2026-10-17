from __future__ import annotations

import unittest
from unittest.mock import patch

from lokro_store.installer import InstallError, flatpak_bundle_plan, flatpak_plan, installation_scope


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.item = {
            "name": "Example",
            "install": {"method": "flatpak", "remote": "flathub", "ref": "org.example.App"},
        }

    @patch("lokro_store.installer.shutil.which", return_value="/usr/bin/lokro-store-flatpak")
    def test_install_plan_has_no_shell(self, _which) -> None:
        plan = flatpak_plan(self.item, installed=False)
        self.assertEqual(plan.executable, "/usr/bin/lokro-store-flatpak")
        self.assertEqual(plan.arguments, ("install", "org.example.App"))
        self.assertNotIn("sh", plan.arguments)

    @patch("lokro_store.installer.shutil.which", return_value="/usr/bin/lokro-store-flatpak")
    def test_update_plan_is_user_scoped(self, _which) -> None:
        plan = flatpak_plan(self.item, installed=True)
        self.assertEqual(plan.arguments, ("update", "org.example.App"))

    @patch("lokro_store.installer.shutil.which", return_value="/usr/bin/lokro-store-flatpak")
    def test_pinned_bundle_plan_has_no_shell(self, _which) -> None:
        item = {
            "name": "ArtCraft",
            "install": {
                "method": "flatpak-bundle",
                "ref": "ai.storyteller.artcraft-launcher",
                "url": "https://example.invalid/artcraft-0.3.2.flatpak",
                "sha256": "a" * 64,
            },
        }
        plan = flatpak_bundle_plan(item, installed=False)
        self.assertEqual(plan.executable, "/usr/bin/lokro-store-flatpak")
        self.assertEqual(plan.arguments[0], "install-bundle")
        self.assertNotIn("sh", plan.arguments)
        self.assertEqual(flatpak_bundle_plan(item, installed=True).arguments, plan.arguments)

    def test_malformed_id_is_rejected(self) -> None:
        self.item["install"]["ref"] = "org.example.App;touch /tmp/no"
        with self.assertRaises(InstallError):
            flatpak_plan(self.item, installed=False)

    @patch("lokro_store.installer.shutil.which", return_value="/usr/bin/flatpak")
    def test_system_install_is_reported_separately(self, _which) -> None:
        def runner(command, **_kwargs):
            class Result:
                returncode = 0 if "--system" in command else 1
            return Result()

        self.assertEqual(installation_scope(self.item, runner), "system")


if __name__ == "__main__":
    unittest.main()
