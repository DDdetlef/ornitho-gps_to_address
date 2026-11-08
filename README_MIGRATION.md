# Modulare Ornitho-Adressenrekonstruktion

Das Projekt trennt Einlesen, Normalisierung, Koordinatenauswahl, Geocoding,
Validierung, Excel-Ausgabe und Archivierung.

## Start

```powershell
python -m pip install -r requirements.txt
python .\main.py
```

## Unterstützte Eingaben

- JSON
- XML
- XLSX
- tabulatorgetrennte TXT- und TSV-Dateien

## Ausgaben

Pro Eingabedatei werden zwei Excel-Dateien erzeugt:

- vollständige Ausgabe: `export_..._mit_adressen.xlsx`
- reduzierte Ausgabe: `export_basic_..._mit_adressen.xlsx`

Erst wenn beide Dateien erfolgreich geschrieben wurden, wird die Quelle nach
`data/processed` verschoben.

## Qualitätssicherung

```powershell
python -m pytest
```

Die Validierungsregeln stehen in `scripts/validation.py`. Schwellenwerte für
30, 75 und 150 Meter stehen zentral in `scripts/config.py`.
