#!/usr/bin/env python3
"""Render the real QML interface with Qt's software/offscreen backend."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Material")
os.environ.setdefault("QT_QUICK_CONTROLS_MATERIAL_THEME", "Dark")

from PySide6.QtCore import QTimer, QUrl  # noqa: E402
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication  # noqa: E402
from PySide6.QtQml import QQmlApplicationEngine  # noqa: E402

from lokro_store.app import StoreBackend, qml_path  # noqa: E402


def main() -> int:
    destination = ROOT / "screenshots" / "lokro-store-alpha1.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    app = QGuiApplication([])
    windows_font = Path("C:/Windows/Fonts/segoeui.ttf")
    if windows_font.is_file() and QFontDatabase.addApplicationFont(str(windows_font)) >= 0:
        app.setFont(QFont("Segoe UI"))
    backend = StoreBackend()
    engine = QQmlApplicationEngine()
    engine.setInitialProperties({"storeBackend": backend})
    engine.load(QUrl.fromLocalFile(str(qml_path())))
    if not engine.rootObjects():
        return 1
    window = engine.rootObjects()[0]
    window.setWidth(1180)
    window.setHeight(760)
    result = {"ok": False}

    def capture() -> None:
        image = window.grabWindow()
        result["ok"] = image.save(str(destination))
        print(f"screenshot: {image.width()}x{image.height()} -> {destination}")
        app.quit()

    QTimer.singleShot(1200, capture)
    app.exec()
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
