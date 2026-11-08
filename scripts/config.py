from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_ROOT / "data" / "input"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
LOG_DIR = PROJECT_ROOT / "log"
LOG_PATH = LOG_DIR / "gps_to_address.log"

SUPPORTED_INPUT_SUFFIXES = {".json", ".xlsx", ".txt", ".tsv", ".xml"}

NOMINATIM_USER_AGENT = "ornitho_adressrekonstruktion_2026"
NOMINATIM_TIMEOUT_SECONDS = 15
NOMINATIM_DELAY_SECONDS = 1
NOMINATIM_MAX_RETRIES = 2
NOMINATIM_ERROR_WAIT_SECONDS = 5

USE_FALLBACK_COORDINATES = True
GEOCODE_PLACE_FALLBACK = False
CACHE_DECIMAL_PLACES = 7
MAX_EXCEL_COLUMN_WIDTH = 60

MOVE_ATTEMPTS = 3
MOVE_RETRY_SECONDS = 1

DISTANCE_VERIFIED_MAX_METERS = 30
DISTANCE_PLAUSIBLE_MAX_METERS = 75
DISTANCE_RESTRICTED_MAX_METERS = 150

# Dauerhaft nutzbarer Abgleich zwischen einer ausdrücklich in der
# Bemerkung genannten Hausnummer und der von OSM gelieferten Hausnummer.
# Die Angabe aus der Bemerkung ergänzt oder ersetzt niemals die OSM-Adresse.
ENABLE_COMMENT_HOUSE_NUMBER_CHECK = True

# Die Suche erfolgt ohne Beachtung der Groß-/Kleinschreibung.
# "nr" deckt Nr., nr., NR., Nr und nr ab.
COMMENT_HOUSE_NUMBER_KEYWORDS = (
    "hausnummer",
    "hausnr",
    "haus-nr",
    "test-hausnummer",
    "test hausnummer",
    "adresse",
    "nr",
)

FULL_OUTPUT_COLUMNS = [
    "Datensatz", "Datum", "Beobachtungszeit", "Art", "Anzahl", "Kommentar",
    "Straße", "Hausnummer", "Postleitzahl", "Ort_Adresse", "Ortsteil", "Bezirk",
    "Hausnummer_aus_Bemerkung", "Hausnummer_Abgleich",
    "Hausnummer_Abgleich_Detail", "Hausnummernabgleich", "Adressstatus",
    "Adressqualität", "Adressbewertung", "Räumliche_Plausibilität",
    "Manuelle_Prüfung", "Prüfbedarf", "OSM_Distanz_Meter", "Ornitho_Link",
    "ID_Beobachtung", "GUID", "Beobachter", "Datum_ISO",
    "Beobachtungszeit_ISO", "Lateinname", "Meldeort", "Gemeinde_JSON",
    "Meldeort_Typ", "Meldeort_Genauigkeit", "Höhe", "Flugnummer",
    "Marker_Latitude", "Marker_Longitude", "GPS_Latitude", "GPS_Longitude",
    "Meldeort_Latitude", "Meldeort_Longitude", "Verwendete_Latitude",
    "Verwendete_Longitude", "Koordinatenquelle", "Koordinatenpriorität",
    "Koordinatenbewertung", "Adresse", "Landkreis", "Bundesland", "Land",
    "OSM_Objekttyp", "OSM_ID", "OSM_Treffer_Latitude",
    "OSM_Treffer_Longitude", "Geocoding_Status",
]

# Endgültige, anwenderorientierte Reihenfolge im export_basic.
# Die extrahierte Hausnummer wird hier bewusst nicht wiederholt, weil die
# zugrunde liegende Angabe im Feld Kommentar nachvollziehbar ist.
BASIC_OUTPUT_COLUMNS = [
    "Datensatz",
    "Datum",
    "Beobachtungszeit",
    "Art",
    "Anzahl",
    "Kommentar",
    "Straße",
    "Hausnummer",
    "Postleitzahl",
    "Ort",
    "Ortsteil",
    "Bezirk",
    "Hausnummernabgleich",
    "Adressbewertung",
    "Räumliche_Plausibilität",
    "Prüfbedarf",
    "Ornitho_Link",
    "ID_Beobachtung",
    "Koordinatenquelle",
    "Marker_Latitude",
    "Marker_Longitude",
]


def ensure_directories() -> None:
    for directory in (INPUT_DIR, OUTPUT_DIR, PROCESSED_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)
