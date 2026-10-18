from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from lokro_store.installer import (
    InstallError,
    _download_verified_file,
    design_pack_helper_main,
    flatpak_bundle_plan,
    flatpak_plan,
    helper_main,
    installation_scope,
    remote_design_pack_plan,
    system_package_installed,
    system_update_plan,
    update_all_flatpaks_plan,
)


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
    def test_update_all_plan_has_fixed_arguments(self, _which) -> None:
        plan = update_all_flatpaks_plan()
        self.assertEqual(plan.executable, "/usr/bin/lokro-store-flatpak")
        self.assertEqual(plan.arguments, ("update-all",))

    @patch("lokro_store.installer._run_flatpak")
    @patch("lokro_store.installer._ensure_flathub")
    def test_update_all_helper_is_user_scoped(self, ensure, run) -> None:
        self.assertEqual(helper_main(["update-all"]), 0)
        ensure.assert_called_once_with()
        run.assert_called_once_with(["update", "--user", "--noninteractive"])

    @patch("lokro_store.installer.shutil.which", return_value="/usr/bin/lokro-update-gui")
    def test_system_update_plan_has_no_catalog_arguments(self, _which) -> None:
        plan = system_update_plan()
        self.assertEqual(plan.executable, "/usr/bin/lokro-update-gui")
        self.assertEqual(plan.arguments, ())

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

    @patch("lokro_store.installer.shutil.which", return_value="/usr/bin/lokro-store-design-pack")
    def test_remote_design_pack_plan_has_no_shell(self, _which) -> None:
        item = {
            "name": "Example Pack",
            "install": {
                "method": "lokro-design-pack",
                "url": "https://example.invalid/example-1.0.0.lokrodesign",
                "sha256": "b" * 64,
            },
        }
        plan = remote_design_pack_plan(item)
        self.assertEqual(plan.executable, "/usr/bin/lokro-store-design-pack")
        self.assertEqual(plan.arguments, (item["install"]["url"], "b" * 64))
        self.assertNotIn("sh", plan.arguments)

    def test_design_pack_helper_rejects_unpinned_or_unsafe_requests(self) -> None:
        self.assertEqual(design_pack_helper_main(["http://example.invalid/pack.lokrodesign", "b" * 64]), 2)
        self.assertEqual(design_pack_helper_main(["https://example.invalid/pack.lokrodesign", "wrong"]), 2)

    @patch("lokro_store.installer.urllib.request.urlopen")
    def test_verified_download_removes_checksum_mismatch(self, urlopen) -> None:
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, _size):
                if getattr(self, "done", False):
                    return b""
                self.done = True
                return b"not-the-expected-pack"

        urlopen.return_value = Response()
        test_temp = Path.cwd() / ".test-tmp"
        test_temp.mkdir(exist_ok=True)
        with TemporaryDirectory(dir=test_temp) as temporary:
            destination = Path(temporary) / "pack.lokrodesign"
            with self.assertRaises(InstallError):
                _download_verified_file(
                    "https://example.invalid/pack.lokrodesign",
                    "b" * 64,
                    destination,
                    1024,
                )
            self.assertFalse(destination.exists())

    @patch("lokro_store.installer.shutil.which", return_value="/usr/bin/flatpak")
    def test_system_install_is_reported_separately(self, _which) -> None:
        def runner(command, **_kwargs):
            class Result:
                returncode = 0 if "--system" in command else 1
            return Result()

        self.assertEqual(installation_scope(self.item, runner), "system")

    @patch("lokro_store.installer.shutil.which", return_value="/usr/bin/pacman")
    def test_system_package_check_is_read_only(self, _which) -> None:
        item = {"id": "firefox"}
        commands = []

        def runner(command, **_kwargs):
            commands.append(command)
            return type("Result", (), {"returncode": 0})()

        self.assertTrue(system_package_installed(item, runner))
        self.assertEqual(commands, [["/usr/bin/pacman", "-Q", "firefox"]])

    def test_system_package_check_rejects_command_text(self) -> None:
        self.assertFalse(system_package_installed({"id": "firefox;rm"}))


if __name__ == "__main__":
    unittest.main()
