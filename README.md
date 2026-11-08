# Ornitho-Adressenrekonstruktion

## Ziel und Zweck

Dieses Projekt verarbeitet Exporte aus ornitho.de und ergänzt die Beobachtungsdaten um eine aus Koordinaten abgeleitete postalische Zuordnung. Ausgegeben werden eine vollständige Excel-Datei für Prüfung und Nachweis sowie eine reduzierte `export_basic`-Datei für die praktische Nutzung.

Das Verfahren arbeitet konservativ. Es soll keine vollständige Adresse vortäuschen, wenn die Datenlage nur eine Straße, einen Ort oder einen räumlichen Hinweis zulässt.

## Fachlicher Grundsatz

Die rekonstruierte Adresse wird ausschließlich aus dem Ergebnis von OpenStreetMap Nominatim und den hinterlegten Plausibilitätsregeln gebildet.

Eine Hausnummer im Bemerkungsfeld dient als unabhängige Vergleichsangabe. Sie wird:

- erkannt, wenn sie ausdrücklich gekennzeichnet ist,
- mit der OSM-Hausnummer verglichen,
- im vollständigen Export dokumentiert,
- niemals zur Ergänzung oder Korrektur der OSM-Adresse verwendet.

Unterstützte Schreibweisen sind unter anderem:

```text
Hausnummer 16
Hausnr. 16
Haus-Nr. 16
Adresse Pacelliallee 16
Nr. 16
nr. 16
Nr 16
nr 16
```

Nicht gekennzeichnete Zahlen wie `2 Haussperlinge um 16:30 Uhr` werden nicht als Hausnummer interpretiert.

## Koordinatenpriorität

1. `observer.coord_lat` und `observer.coord_lon`: gesetzter Beobachtungsmarker
2. `observer.gps_lat` und `observer.gps_lon`: GPS-Position des Erfassungsgeräts
3. `place.coord_lat` und `place.coord_lon`: Referenzpunkt des Meldegebiets

Der Beobachtungsmarker ist die bevorzugte Quelle. Ein Gebietsreferenzpunkt ist für eine belastbare Hausadresszuordnung ungeeignet.

## OSM-Distanz

`OSM_Distanz_Meter` ist die Luftlinienentfernung zwischen der verwendeten Beobachtungskoordinate und der Position des von Nominatim gelieferten OSM-Objekts.

| Distanz | Vereinfachte Anzeige |
|---:|---|
| 0 bis 30 m | Sehr nah |
| über 30 bis 75 m | Nah |
| über 75 bis 150 m | Weiter entfernt |
| über 150 m | Zu weit entfernt |
| nicht bestimmbar | Nicht bestimmbar |

Die Distanz ist keine GPS-Genauigkeit und kein Beweis für die Zugehörigkeit zu einem Grundstück. Sie ist eine projektinterne Plausibilitätsgröße.

## Adressbewertung

### Vollständige Adresse plausibel

Straße, Hausnummer, PLZ und Ort sind vorhanden. Der OSM-Treffer liegt räumlich plausibel zum Beobachtungsmarker. Die Bewertung ist keine amtliche Bestätigung.

### Plausibel ohne Hausnummer

Straße, PLZ und Ort sind plausibel, OSM liefert jedoch keine belastbare Hausnummer. Die Hausnummer bleibt leer. Fälle wie Pacelliallee oder Pasewalker Straße ohne Hausnummer sind zulässig.

### Plausibel mit Prüfhinweis

Die Adresse ist grundsätzlich verwendbar, weist aber einen begrenzten Unsicherheitsfaktor auf, beispielsweise einen OSM-Treffer zwischen 30 und 75 Metern.

### Eingeschränkt plausibel

Teile der Adresse sind verwertbar, die räumliche oder inhaltliche Zuordnung ist aber deutlich unsicher. Eine manuelle Prüfung ist erforderlich.

### Nicht bewertbar

Wesentliche Informationen für die Bewertung fehlen, beispielsweise die Koordinaten des OSM-Treffers oder eine berechenbare Distanz.

### Nicht belastbar

Die vorhandenen Informationen sprechen gegen eine verlässliche Adresszuordnung, beispielsweise bei einem Gebietsreferenzpunkt oder einem OSM-Treffer über 150 Meter.

### Keine Bewertung

Es liegt kein bekannter interner Bewertungsstatus vor. Dieser Auffangwert sollte im regulären Betrieb geprüft werden.

## Hausnummernabgleich

Die vereinfachte Spalte `Hausnummernabgleich` kann folgende Werte enthalten:

| Anzeige | Bedeutung |
|---|---|
| Stimmt mit Bemerkung überein | OSM-Hausnummer und ausdrücklich genannte Hausnummer im Bemerkungsfeld stimmen überein |
| Weicht von Bemerkung ab | OSM und Bemerkung nennen unterschiedliche Hausnummern |
| OSM-Hausnummer fehlt | In der Bemerkung steht eine Hausnummer, OSM liefert keine Hausnummer |
| Keine Hausnummer in Bemerkung | Im Bemerkungsfeld wurde keine ausdrücklich gekennzeichnete Hausnummer erkannt |
| Hausnummer in Bemerkung mehrdeutig | Im Bemerkungsfeld wurden mehrere unterschiedliche Hausnummern erkannt |
| Nicht vergleichbar | Die erkannte Angabe konnte nicht zuverlässig normalisiert werden |
| Abgleich nicht durchgeführt | Die Funktion ist deaktiviert oder es liegt kein verwertbarer Status vor |

Der vollständige Export enthält zusätzlich:

- `Hausnummer_aus_Bemerkung`
- `Hausnummer_Abgleich`
- `Hausnummer_Abgleich_Detail`

Der `export_basic` wiederholt die extrahierte Hausnummer nicht, weil die Originalangabe im Feld `Kommentar` nachvollziehbar bleibt.

## Prüfbedarf

| Wert | Bedeutung |
|---|---|
| Nein | Ergebnis kann nach den Projektregeln ohne besondere Einzelfallprüfung verwendet werden |
| Empfohlen | Ergebnis ist grundsätzlich verwendbar, eine Kontrolle ist sinnvoll |
| Erforderlich | Ergebnis darf nicht ungeprüft übernommen werden |

`Erforderlich` wird insbesondere gesetzt bei Abweichung der Hausnummern, mehrdeutiger Angabe in der Bemerkung, nicht bewertbaren oder nicht belastbaren Adressen, Gebietsreferenzpunkten sowie OSM-Distanzen über 75 Metern.

Eine plausible Straße ohne OSM-Hausnummer kann dagegen `Prüfbedarf = Nein` erhalten. Die Hausnummer aus der Bemerkung wird trotzdem nicht in die Adresse übernommen.

## Endgültige Spaltenfolge im export_basic

1. `Datensatz`
2. `Datum`
3. `Beobachtungszeit`
4. `Art`
5. `Anzahl`
6. `Kommentar`
7. `Straße`
8. `Hausnummer`
9. `Postleitzahl`
10. `Ort`
11. `Ortsteil`
12. `Bezirk`
13. `Hausnummernabgleich`
14. `Adressbewertung`
15. `Räumliche_Plausibilität`
16. `Prüfbedarf`
17. `Ornitho_Link`
18. `ID_Beobachtung`
19. `Koordinatenquelle`
20. `Marker_Latitude`
21. `Marker_Longitude`

Im vollständigen Export bleibt das interne Feld `Ort_Adresse` erhalten. Im Basic-Export wird es anwenderfreundlich als `Ort` ausgegeben.

## Beispiel: OSM-Hausnummer fehlt

```text
Kommentar: Gebüsch vor Nr. 16
Straße: Pacelliallee
Hausnummer: [leer]
Hausnummernabgleich: OSM-Hausnummer fehlt
Adressbewertung: Plausibel ohne Hausnummer
Räumliche_Plausibilität: Sehr nah
Prüfbedarf: Nein
```

Die Angabe `Nr. 16` bleibt im Kommentar sichtbar, wird aber nicht als rekonstruierte Hausnummer ausgegeben.

## Beispiel: Hausnummer weicht ab

```text
Kommentar: Beobachtung vor Nr. 24
Straße: Hauptstraße
Hausnummer: 22
Hausnummernabgleich: Weicht von Bemerkung ab
Adressbewertung: Vollständige Adresse plausibel
Räumliche_Plausibilität: Sehr nah
Prüfbedarf: Erforderlich
```

Die OSM-Adresse bleibt unverändert. Der Widerspruch wird separat ausgewiesen.

## Projektstruktur

```text
gps_to_address/
├── main.py
├── scripts/
│   ├── config.py
│   ├── input_loader.py
│   ├── normalizers.py
│   ├── coordinates.py
│   ├── geocoding.py
│   ├── validation.py
│   ├── house_number_check.py
│   ├── basic_presentation.py
│   ├── excel_export.py
│   ├── archiving.py
│   └── processing.py
├── data/
│   ├── input/
│   ├── output/
│   └── processed/
├── log/
├── tests/
├── requirements.txt
└── README.md
```

## Verwendung

```powershell
python -m pip install -r .\requirements.txt
python -m pytest
python .\main.py
```

Erfolgreich verarbeitete Quelldateien werden erst nach Erstellung beider Excel-Ausgaben nach `data/processed` verschoben.

## Datenschutz

Die Dateien können genaue Koordinaten, Beobachternamen, Kommentare, sensible Beobachtungen und direkte Links zu ornitho.de enthalten. Die Verzeichnisse `data/input`, `data/output`, `data/processed` und `log` sollten nur berechtigten Personen zugänglich sein.

## Qualitätsprinzip

```text
So genau wie möglich,
so zurückhaltend wie nötig,
und jede Unsicherheit sichtbar machen.
```
