# Project state

Last updated: 2026-10-18

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
- Declared `python-setuptools` explicitly so the Arch wheel build can import
  the configured `setuptools.build_meta` backend without build isolation.
- Fixed Flathub installation by creating or repairing the user-scoped Flathub
  remote before every Store install/update operation.
- Added a shell-free, size-bounded and SHA-256-verified Flatpak-bundle path.
  ArtCraft Launcher 0.3.2 x86_64 is the first pinned bundle.
- Completed the matching checksum-verified `.lokrodesign` download path and
  added a first-party monochrome large-cursor pack as an end-to-end example.
- Added all 13 official ArtCraft Crafting Apps as independent catalog entries.
  Each uses its exact `ai.storyteller.*` Flatpak ID, immutable upstream release
  URL and the SHA-256 published in that release's `SHA256SUMS.txt`; the suite
  launcher remains an optional separate entry.
- Refined the QML shell with translucent panels, brighter focus borders and
  clearer alpha-7 status text without changing the safe installer boundary.
- Expanded alpha 8 with optional Steam, Heroic, Bottles, PeaZip, development
  tools, browsers, communication, security, cloud and KDE desktop entries.
- Added fixed shell-free actions for all user Flatpak updates and the existing
  LOKRO system updater. Selected preinstalled Pacman applications are detected
  read-only and never duplicated or updated through catalog-supplied commands.
- Added `docs/FIRST_BOOT_ASSISTANT_HANDOFF.md` for the next installer task. No
  ISO source, boot configuration or current release artifact was changed.

## Still to do

- Run the Linux UI and capture final screenshots in an Arch/KDE environment.
- Review, merge and tag alpha 8. Pinning it in LOKRO OS is a separate future
  change; the current ISO remains unchanged by this milestone.
- Add real design packs after the user supplies artwork. Each pack must pass
  the LOKRO validator and include license/author metadata.
- Consider per-item verification badges once Flathub exposes a stable API the
  Store can cache and validate offline.
- Add localization after UI strings stabilize.

## ISO note

Do not ZIP the existing offline ISO merely to bypass GitHub's asset limit. Its
SquashFS payload is already compressed, so ZIP is expected to save very little
and would still exceed the per-asset limit. The existing checksummed multipart
release is the reliable transport until external release hosting is selected.
