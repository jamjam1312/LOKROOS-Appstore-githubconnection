"""Qt/QML desktop front end for the validated LOKRO Store catalog."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from PySide6.QtCore import QIODevice, QObject, Property, QProcess, QSaveFile, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QGuiApplication
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from .catalog import CatalogError, filter_items, load_catalog, loads_catalog
from .installer import (
    InstallError,
    flatpak_bundle_plan,
    flatpak_plan,
    installation_scope,
    remote_design_pack_plan,
)

REMOTE_CATALOG = (
    "https://raw.githubusercontent.com/jamjam1312/"
    "LOKROOS-Appstore-githubconnection/main/catalog/v1/catalog.json"
)
REMOTE_ASSET_ROOT = (
    "https://raw.githubusercontent.com/jamjam1312/"
    "LOKROOS-Appstore-githubconnection/main/"
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def catalog_candidates() -> list[Path]:
    override = os.environ.get("LOKRO_STORE_CATALOG")
    return [candidate for candidate in [
        Path(override).expanduser() if override else None,
        Path.home() / ".cache" / "lokro-store" / "catalog-v1.json",
        Path("/usr/share/lokro-store/catalog/v1/catalog.json"),
        _repo_root() / "catalog" / "v1" / "catalog.json",
    ] if candidate is not None]


def load_initial_catalog() -> tuple[Path, dict]:
    errors: list[str] = []
    for candidate in catalog_candidates():
        if not candidate.is_file():
            continue
        try:
            return candidate, load_catalog(candidate)
        except (CatalogError, OSError) as error:
            errors.append(f"{candidate}: {error}")
    details = "; ".join(errors) if errors else "no candidate exists"
    raise FileNotFoundError(f"No valid bundled LOKRO Store catalog was found ({details})")


def qml_path() -> Path:
    candidates = [
        Path("/usr/share/lokro-store/qml/Main.qml"),
        Path(__file__).with_name("qml") / "Main.qml",
        _repo_root() / "src" / "lokro_store" / "qml" / "Main.qml",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("LOKRO Store QML interface is missing")


class StoreBackend(QObject):
    itemsChanged = Signal()
    categoriesChanged = Signal()
    busyChanged = Signal()
    messageChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._query = ""
        self._category = "Alle"
        self._busy = False
        self._message = "Offline-Katalog geladen"
        self._catalog_file, self._catalog = load_initial_catalog()
        self._items: list[dict] = []
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.MergedChannels)
        self._process.finished.connect(self._process_finished)
        self._process.errorOccurred.connect(self._process_error)
        self._network = QNetworkAccessManager(self)
        self._network.finished.connect(self._catalog_downloaded)
        self._rebuild()

    def _local_asset(self, relative: str) -> Path | None:
        roots = [Path("/usr/share/lokro-store"), _repo_root()]
        for root in roots:
            candidate = root / Path(relative)
            try:
                candidate.resolve().relative_to(root.resolve())
            except ValueError:
                continue
            if candidate.is_file():
                return candidate
        return None

    def _present(self, item: dict) -> dict:
        row = dict(item)
        local_icon = self._local_asset(item["icon"])
        row["iconUrl"] = (
            QUrl.fromLocalFile(str(local_icon)).toString()
            if local_icon else REMOTE_ASSET_ROOT + item["icon"]
        )
        row["categoriesText"] = " · ".join(item["categories"])
        scope = installation_scope(item)
        row["installed"] = scope is not None
        row["installScope"] = scope or ""
        method = item["install"]["method"]
        row["actionText"] = (
            "Installiert" if method == "builtin" else
            "Projekt öffnen" if method == "project-link" else
            "Herunterladen" if method == "lokro-design-pack" else
            "Systemweit installiert" if scope == "system" else
            "Aktualisieren" if row["installed"] else
            "Installieren"
        )
        row["actionEnabled"] = (
            method in {"project-link", "lokro-design-pack"}
            or (method in {"flatpak", "flatpak-bundle"} and scope != "system")
        )
        return row

    def _rebuild(self) -> None:
        filtered = filter_items(self._catalog["items"], self._query, self._category)
        self._items = [self._present(item) for item in filtered]
        self.itemsChanged.emit()
        self.categoriesChanged.emit()

    @Property("QVariantList", notify=itemsChanged)
    def items(self) -> list[dict]:
        return self._items

    @Property("QStringList", notify=categoriesChanged)
    def categories(self) -> list[str]:
        values = sorted({category for item in self._catalog["items"] for category in item["categories"]})
        kinds = ["design-pack", "cursor", "theme", "wallpaper"]
        present_kinds = [kind for kind in kinds if any(item["kind"] == kind for item in self._catalog["items"])]
        return ["Alle", *values, *present_kinds]

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(str, notify=messageChanged)
    def message(self) -> str:
        return self._message

    def _set_busy(self, value: bool) -> None:
        if self._busy != value:
            self._busy = value
            self.busyChanged.emit()

    def _set_message(self, value: str) -> None:
        if self._message != value:
            self._message = value
            self.messageChanged.emit()

    @Slot(str)
    def setSearch(self, query: str) -> None:
        self._query = query[:200]
        self._rebuild()

    @Slot(str)
    def setCategory(self, category: str) -> None:
        self._category = category
        self._rebuild()

    def _find(self, item_id: str) -> dict:
        for item in self._catalog["items"]:
            if item["id"] == item_id:
                return item
        raise InstallError("Unbekannter Katalogeintrag")

    @Slot(str)
    def installOrUpdate(self, item_id: str) -> None:
        if self._busy:
            self._set_message("Bitte warte, bis der laufende Vorgang abgeschlossen ist.")
            return
        try:
            item = self._find(item_id)
            method = item["install"]["method"]
            if method == "project-link":
                self.openUrl(item["install"]["url"])
                self._set_message(
                    "Offizielle Projektseite geöffnet; diese Alpha installiert keine ungeprüften Binärdateien."
                )
                return
            if method == "lokro-design-pack":
                plan = remote_design_pack_plan(item)
            else:
                scope = installation_scope(item)
                if scope == "system":
                    raise InstallError("systemweit installierte Flatpaks werden in dieser Alpha nicht verändert")
                if method == "flatpak-bundle":
                    plan = flatpak_bundle_plan(item, scope == "user")
                else:
                    plan = flatpak_plan(item, scope == "user")
        except InstallError as error:
            self._set_message(f"Nicht möglich: {error}")
            return
        self._set_busy(True)
        self._set_message(f"{plan.label} …")
        self._process.setProgram(plan.executable)
        self._process.setArguments(list(plan.arguments))
        self._process.start()

    @Slot(int, int)
    def _process_finished(self, exit_code: int, _status: int) -> None:
        output = bytes(self._process.readAll()).decode("utf-8", "replace").strip()
        self._set_busy(False)
        if exit_code == 0:
            self._set_message("Vorgang erfolgreich abgeschlossen.")
        else:
            final_line = output.splitlines()[-1] if output else f"Fehlercode {exit_code}"
            self._set_message(f"Vorgang fehlgeschlagen: {final_line[:240]}")
        self._rebuild()

    def _process_error(self, _error: QProcess.ProcessError) -> None:
        if self._process.state() == QProcess.NotRunning and self._busy:
            self._set_busy(False)
            self._set_message(f"Prozess konnte nicht gestartet werden: {self._process.errorString()}")

    @Slot(str)
    def openUrl(self, raw_url: str) -> None:
        parsed = urlparse(raw_url)
        if parsed.scheme == "https" and parsed.netloc and not parsed.username and not parsed.password:
            QDesktopServices.openUrl(QUrl(raw_url))
        else:
            self._set_message("Unsichere oder ungültige URL blockiert.")

    @Slot()
    def refreshCatalog(self) -> None:
        if self._busy:
            return
        self._set_busy(True)
        self._set_message("Katalog wird von GitHub aktualisiert …")
        request = QNetworkRequest(QUrl(REMOTE_CATALOG))
        request.setRawHeader(b"User-Agent", b"LOKRO-Store/0.1")
        request.setTransferTimeout(15000)
        self._network.get(request)

    @Slot(QNetworkReply)
    def _catalog_downloaded(self, reply: QNetworkReply) -> None:
        try:
            if reply.error() != QNetworkReply.NoError:
                raise CatalogError(reply.errorString())
            raw = bytes(reply.readAll())
            catalog = loads_catalog(raw)
            cache = Path.home() / ".cache" / "lokro-store" / "catalog-v1.json"
            cache.parent.mkdir(parents=True, exist_ok=True)
            output = QSaveFile(str(cache))
            if not output.open(QIODevice.WriteOnly):
                raise OSError(output.errorString())
            if output.write(raw) != len(raw) or not output.commit():
                raise OSError(output.errorString())
            self._catalog = catalog
            self._catalog_file = cache
            self._set_message("Katalog ist aktuell.")
            self._rebuild()
        except (CatalogError, OSError, UnicodeError) as error:
            self._set_message(f"Online-Aktualisierung fehlgeschlagen; Offline-Katalog bleibt aktiv: {error}")
        finally:
            reply.deleteLater()
            self._set_busy(False)


def main() -> int:
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Material")
    os.environ.setdefault("QT_QUICK_CONTROLS_MATERIAL_THEME", "Dark")
    QQuickStyle.setStyle("Material")
    app = QGuiApplication(sys.argv)
    app.setApplicationName("LOKRO Store")
    app.setOrganizationName("LOKRO")
    engine = QQmlApplicationEngine()
    try:
        backend = StoreBackend()
        ui = qml_path()
    except (CatalogError, OSError) as error:
        print(f"lokro-store: {error}", file=sys.stderr)
        return 2
    engine.setInitialProperties({"storeBackend": backend})
    engine.load(QUrl.fromLocalFile(str(ui)))
    if not engine.rootObjects():
        return 3
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
