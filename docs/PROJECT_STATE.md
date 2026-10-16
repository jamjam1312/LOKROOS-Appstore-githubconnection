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

## Still to do

- Run the Linux UI and capture final screenshots in an Arch/KDE environment.
- Review and merge the alpha-1 pull request.
- Tag an app-store release and pin that release in the LOKRO OS build.
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
