# Repository instructions for coding agents

## Purpose

This repository contains the LOKRO Store application and its public, versioned
catalog. It does not contain the LOKRO OS ISO builder.

## Safety invariants

- Never add an installer that executes catalog-provided shell code.
- Keep install methods allowlisted in `src/lokro_store/installer.py`.
- Flatpak entries must contain one exact application ID and use Flathub.
- Remote design packs must be HTTPS `.lokrodesign` files with SHA-256.
- Do not add AUR helpers, `curl | sh`, mutable AppImage URLs or unpinned
  executable downloads.
- Treat catalog text, URLs and images as untrusted data.
- Installation is user-scoped unless a future design is explicitly reviewed.

## Required checks

Run `make validate` and `make test` after catalog or code changes. Keep the
schema, validator, example catalog and documentation synchronized.

## Project boundaries

- `catalog/v1/`: machine-readable store data and schema.
- `src/lokro_store/`: application, validation and safe command planning.
- `assets/`: application artwork and documented upstream icons.
- `packaging/`: distribution packaging metadata.
- `docs/PROJECT_STATE.md`: durable hand-off notes; update it after material
  milestones so another agent can continue after context loss.

Open-source licenses do not automatically grant trademark rights. Preserve
upstream attribution and do not imply that listed projects endorse LOKRO OS.
