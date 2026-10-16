# Catalog format v1

`catalog/v1/catalog.json` is the offline and remote data source. Every change
must validate against `catalog.schema.json` and the stricter Python validator.

Each item provides an ID, kind, display text, categories, local icon path,
upstream links, SPDX-style license text and one allowlisted install object.

Kinds are `application`, `design-pack`, `cursor`, `theme` and `wallpaper`.
Valid alpha-1 install methods are:

```json
{"method": "flatpak", "remote": "flathub", "ref": "org.example.App"}
```

```json
{
  "method": "flatpak-bundle",
  "ref": "org.example.App",
  "url": "https://example.org/releases/v1.2.3/example-1.2.3-x86_64.flatpak",
  "sha256": "64 lowercase hexadecimal characters"
}
```

`flatpak-bundle` is reserved for reviewed upstream releases that are not on
Flathub. Mutable `latest` URLs, redirects to unversioned files and missing
checksums are not accepted.

```json
{
  "method": "lokro-design-pack",
  "url": "https://example.org/pack.lokrodesign",
  "sha256": "64 lowercase hexadecimal characters"
}
```

```json
{"method": "builtin"}
```

```json
{"method": "project-link", "url": "https://github.com/example/project/releases/latest"}
```

`project-link` is for promising but not yet packaged or reviewed alpha software.
It opens a credential-free HTTPS page and never downloads or executes a file.

App entries should prefer an upstream-maintained/verified Flatpak. The catalog
may link to GitHub, but it must not transform a GitHub URL into an executable
installer. Icons go under `assets/icons/` with source and license notes in
`assets/icons/SOURCES.md`.

Design-pack contributors put review material under
`contributions/design-packs/ID/` and open a pull request. A maintainer validates
the archive, preview, authorship and license before adding the final catalog
entry.
