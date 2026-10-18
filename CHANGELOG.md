# Changelog

## 0.1.0-alpha.8

- Expand the catalog with gaming, Epic/GOG support through Heroic, archive
  tools, browsers, development tools, communication, security and cloud apps.
- Mark proprietary and unverified community Flatpaks clearly in catalog text.
- Detect selected Pacman-managed desktop applications and route their updates
  to the existing LOKRO system updater instead of duplicating them as Flatpaks.
- Add fixed, shell-free controls for updating every user Flatpak and opening
  the reviewed system updater.
- Add a detailed installation/first-boot hand-off document without changing
  the current ISO.

## 0.1.0-alpha.7

- Add all 13 ArtCraft Crafting Apps as individually installable, immutable
  x86_64 Flatpak bundles alongside the optional suite launcher.
- Pin every upstream version and SHA-256 published in its official release.
- Give the Store shell a more translucent, high-contrast glass treatment.

## 0.1.0-alpha.6

- Complete the safe Store-to-`lokro-design-pack` download path.
- Add a checksummed first-party monochrome large-cursor pack for end-to-end
  installation testing.

## 0.1.0-alpha.5

- Repair or create the user-scoped Flathub remote before installs and updates.
- Install the official ArtCraft Launcher 0.3.2 x86_64 Flatpak bundle only after
  checking its immutable release URL and SHA-256.
- Keep all installer processes shell-free and user-scoped.

## 0.1.0-alpha.4

- Declare `python-setuptools` explicitly for non-isolated Arch wheel builds.

## 0.1.0-alpha.3

- Add the official ArtCraft Launcher as a clearly marked experimental suite.
- Add a safe `project-link` action that only opens validated HTTPS pages.
- Replace competitor-brand comparison labels with neutral functional wording.
- Keep all established Flathub applications and offline catalog data intact.

## 0.1.0-alpha.2

- Correct the official Arch dependency name from `python-pyside6` to `pyside6`.
- Separate the Arch-compatible package version from the SemVer release tag in
  `PKGBUILD.in`.

## 0.1.0-alpha.1

- First validated catalog with 11 open-source applications.
- Native dark Qt/QML interface with offline metadata and icons.
- User-scoped Flathub installation/update planning without shell evaluation.
- Design-pack contribution and security model, tests, CI and documentation.
