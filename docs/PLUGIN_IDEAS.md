# Future plugin and automation ideas

These are notes, not enabled features.

- CI bot: validate catalog pull requests, verify URLs, licenses and icon sizes.
- Preview bot: render a store card and design-pack preview for reviewers.
- Dependency bot: report vanished Flatpak IDs without editing the catalog.
- Release automation: produce a source archive, SHA-256 and Arch package in a
  draft release after all checks pass.
- LOKRO OS integration bot: open a pull request that updates the pinned store
  version only after the standalone release succeeds.
- Design submission form: generate a pull request rather than granting direct
  write access to the catalog.

Any automation that merges, publishes or updates the OS must remain approval
gated.
