# Security model

The catalog is remote data and must never become a remote-code execution
channel.

## Allowed alpha-1 installation methods

`flatpak` accepts an exact application ID and the fixed `flathub` remote. The
application invokes `flatpak` without a shell and installs into the current
user's account.

`lokro-design-pack` is reserved for HTTPS URLs ending in `.lokrodesign` and a
lowercase 64-character SHA-256. The archive is downloaded to a temporary file,
verified and passed to LOKRO OS's separate validator/importer. The catalog does
not get to provide arguments or executable content.

`builtin` describes content already present on the system and performs no
installation.

## Explicit non-features

- no shell command fields;
- no AUR or third-party repository enablement;
- no automatic root access or embedded passwords;
- no mutable `latest` executable downloads;
- no package scripts delivered through the catalog;
- no automatic login to GitHub, Microsoft, Minecraft or any listed service.

Remote refresh failure leaves the bundled offline catalog available. Cached
catalog writes are atomic. All URLs shown to the user must be HTTPS.
