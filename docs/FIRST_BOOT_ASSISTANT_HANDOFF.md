# Übergabe: Installation und erster Start von LOKRO OS

Diese Datei ist eine Arbeitsvorlage für einen Menschen oder eine KI, die den
Installations- und First-Boot-Ablauf im **separaten Betriebssystem-Repository**
weiterentwickelt. Dieses App-Store-Repository baut keine ISO und verändert
keine Partitionen.

## Zielbild

1. Die Live-ISO startet gut sichtbar in den Calamares-Installer, nicht in
   einen scheinbar bereits installierten Desktop.
2. Vor einer Installation werden Sprache, Tastatur, Zeitzone, Netzwerk,
   Benutzername, Rechnername und Speicherziel abgefragt.
3. Die Zusammenfassung zeigt jede geplante Datenträgeränderung, bevor der
   Benutzer sie ausdrücklich bestätigt.
4. Nach erfolgreicher Installation fordert die Oberfläche zum Entfernen des
   USB-Sticks und Neustarten auf.
5. Beim ersten Start des installierten Systems erscheint nur noch ein kurzer,
   nicht destruktiver Willkommensassistent für Darstellung, Netzwerk und
   optionale Apps.

## Zuständiges Repository

`https://github.com/jamjam1312/LOKROOS-Arch-based`

Vor Änderungen dort zuerst `AI_INFO.md` und `AGENTS.md` lesen. Relevante
Bereiche sind voraussichtlich:

- `packages/lokro-installer-config/`: Calamares-Konfiguration und Branding;
- `profile/`: Archiso-Liveprofil, Autostart und Paketlisten;
- `packages/lokro-shell/`: Willkommensoberfläche und Desktop-Vorgaben;
- `packages/lokro-branding/`: Texte, Bilder und sichtbare Alpha-Hinweise;
- `scripts/` und `Makefile`: ausschließlich reproduzierbare Build- und
  Prüfpfade; keine Datenträgeroperationen auf Entwickler-PCs.

Die tatsächlichen Pfade müssen im OS-Repository geprüft werden. Diese Datei
ist keine Erlaubnis, fehlende Verzeichnisse oder Installationslogik zu erfinden.

## Vorgeschlagener Installationsablauf

### Live-Start

- Deutlicher Titel „LOKRO OS installieren – Alpha/Testversion“.
- Zwei bewusste Aktionen: „Installieren“ und „Live-System ausprobieren“.
- Automatischer Installer-Start darf abgebrochen werden.
- Kein Online-Konto und kein versteckter Netzwerkzugriff.

### Calamares

- Deutsch und Englisch als erste Sprachoptionen.
- Deutsche QWERTZ- und englische QWERTY-Tastaturbelegung.
- Zeitzone mit Karte und manueller Korrektur.
- Lokaler Benutzer; der erste Benutzer darf über `wheel` administrieren,
  bleibt aber im Alltag unprivilegiert.
- Rechnername mit strenger Validierung.
- Offline-Installation muss vollständig funktionieren.
- Optionale Online-Pakete erst nach erkennbarem Opt-in.
- Vorhandene Systeme erkennen und manuelle Partitionierung anbieten.
- **„Datenträger löschen“ niemals still vorauswählen.** Verschlüsselung und
  Dual-Boot erst freigeben, wenn sie in VMs und auf echter Hardware geprüft
  wurden.

### Erster Start nach Installation

- Alpha-Hinweis und Link zu bekannten Einschränkungen.
- Darstellung: Dunkel/Hell, Skalierung, Cursorgröße, Hintergrund.
- Netzwerkstatus und Link zu den KDE-Systemeinstellungen.
- Optionale App-Auswahl öffnet den LOKRO Store; sie führt keine stillen
  Installationen aus.
- Schaltflächen zum LOKRO-System-Updater und zu Flatpak-Updates.
- Kein erneutes Abfragen von Benutzer, Passwort oder Partitionen.

## Akzeptanzkriterien

- BIOS und UEFI booten in einer isolierten VM.
- Offline-Installation auf eine leere virtuelle Platte ist möglich.
- Keine automatische Änderung einer echten Entwicklerfestplatte.
- Installation neben einem vorhandenen System wird nur als manuell geprüfter
  Testfall bezeichnet, bis reale Hardwaretests dokumentiert sind.
- Erster Benutzer kann über `sudo` administrieren; Root-Login bleibt gesperrt.
- Nach Neustart startet die Festplatteninstallation ohne ISO.
- Fehlendes Internet blockiert weder Installer noch ersten Start.
- Wiederholter Start des Willkommensassistenten ist idempotent.

## Kopierbarer Auftrag für eine andere KI

> Arbeite ausschließlich im Repository `jamjam1312/LOKROOS-Arch-based`.
> Lies zuerst `AGENTS.md`, `AI_INFO.md` und `docs/RELEASE_STATUS.md`. Prüfe den
> vorhandenen Calamares- und First-Boot-Code, bevor du etwas änderst. Erstelle
> einen klaren Installationsablauf mit Sprache, Tastatur, Zeitzone, lokalem
> Admin-Benutzer, Rechnername, Netzwerkstatus, Datenträger-Zusammenfassung und
> ausdrücklicher Bestätigung. Die Offline-Installation muss funktionieren.
> Wähle niemals automatisch „Datenträger löschen“, führe keine Partitions-,
> Firmware- oder Bootloader-Tests auf dem Entwickler-PC aus und behaupte keine
> Hardwareprüfung ohne Beleg. Der erste Start nach der Installation darf nur
> nicht destruktive Personalisierung und Links zu Store/System-Updater zeigen.
> Führe `make validate` aus und halte `docs/RELEASE_STATUS.md` faktisch: Quelle,
> CI/VM-Prüfung und echte Hardwareprüfung klar trennen.
