# Project state

Last updated: 2026-10-16

## User intent

Build an independent LOKRO app store that can later be included in LOKRO OS.
The catalog must cover applications and later user-contributed design packs,
cursors, themes and wallpapers. It should be searchable, visually dark,
straightforward to browse and useful offline with bundled metadata.

## Completed in this milestone

- Inspected both GitHub repositories and all visible branches/pull requests.
  No open contribution or friend-authored branch was present to review.
- Defined a versioned, validation-first catalog and safe installer boundary.
- Added the Qt/QML store UI, local/offline catalog, remote refresh, search,
  categories, featured apps, install state and install/update controls.
- Added initial open-source productivity and creative applications.
- Added repository instructions, security documentation, tests, CI and Arch
  packaging metadata.
- Opened pull request #1. Ubuntu's older distribution `qmllint` produced false
  type-resolution failures for the newer PySide runtime. CI now installs the
  declared PySide6 runtime, runs its matching linter and loads/renders the real
  interface offscreen with Ubuntu's minimal EGL runtime.
- Corrected the Arch dependency name to the official `pyside6` package and
  separated Arch's hyphen-free `pkgver` from the SemVer Git tag in the package
  template. This correction is intended for the alpha-2 tag used by LOKRO OS.
- Tagged and merged alpha 1 and alpha 2, then integrated the ArtCraft Launcher
  as a neutral, clearly marked experimental suite preview for alpha 3.
- Added `project-link`: a validation-only action that opens an official HTTPS
  release page but cannot download or execute catalog-supplied code.

## Still to do

- Run the Linux UI and capture final screenshots in an Arch/KDE environment.
- Review, merge and tag alpha 3, then pin that exact release and checksum in
  the LOKRO OS build.
- Add real design packs after the user supplies artwork. Each pack must pass
  the LOKRO validator and include license/author metadata.
- Decide whether an opt-in proprietary category (for example Steam) belongs in
  a later catalog. It is intentionally absent from the open-source seed list.
- Add localization after UI strings stabilize.

## ISO note

Do not ZIP the existing offline ISO merely to bypass GitHub's asset limit. Its
SquashFS payload is already compressed, so ZIP is expected to save very little
and would still exceed the per-asset limit. The existing checksummed multipart
release is the reliable transport until external release hosting is selected.
