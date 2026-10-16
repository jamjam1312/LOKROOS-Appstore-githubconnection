# AI hand-off map

This file is the short entry point for an AI or human continuing the project.

LOKRO Store is a separate catalog/UI repository for LOKRO OS. The operating
system source lives at
`https://github.com/jamjam1312/LOKROOS-Arch-based`. The released OS alpha is
currently independent of this store; integration comes after this repository's
first tagged release.

## Runtime flow

1. `src/lokro_store/app.py` locates a bundled or cached catalog.
2. `catalog.py` validates every field and rejects unknown install methods.
3. The Qt/QML UI reads only validated item dictionaries.
4. `installer.py` converts an item to a fixed executable plus argument list.
5. `QProcess` launches that list directly; no shell parses catalog data.
6. A remote refresh may replace only the cached catalog. The bundled catalog
   remains the offline fallback.

## Important decisions

- Flatpak is the portable application source for alpha 1.
- The source repository URL is metadata, not an executable download URL.
- App icons are committed for offline browsing and separately attributed.
- Design, cursor, theme and wallpaper sections are represented in the schema.
  Remote design installation is enabled only for checksum-pinned
  `.lokrodesign` archives.
- The UI is PySide6 + QML to stay native-looking on KDE without creating a new
  desktop environment.
- The app-store catalog can evolve independently from the large ISO.

Read `AGENTS.md`, `docs/SECURITY.md`, `docs/CATALOG_FORMAT.md` and
`docs/PROJECT_STATE.md` before changing installation behavior.
