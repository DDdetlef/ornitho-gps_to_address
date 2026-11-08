import logging
from pathlib import Path

from scripts.archiving import archive_input
from scripts.basic_presentation import create_basic_validation_fields
from scripts.config import INPUT_DIR, SUPPORTED_INPUT_SUFFIXES, ensure_directories
from scripts.coordinates import select_coordinates
from scripts.excel_export import build_ornitho_link, write_outputs
from scripts.geocoding import reverse_address
from scripts.house_number_check import compare_osm_and_comment_house_number
from scripts.input_loader import load_input_file
from scripts.logging_utils import configure_logging, show_error, show_warning
from scripts.normalizers import (
    extract_iso_date,
    extract_iso_time,
    normalize_date,
    normalize_time,
    to_float,
)


def create_output_row(sighting: dict, number: int) -> dict:
    """
    Erstellt eine vollständige Ausgabezeile.

    Eine Hausnummer aus dem Bemerkungsfeld wird nur mit der OSM-Hausnummer
    verglichen. Sie ergänzt oder ersetzt die rekonstruierte Adresse nie.
    """

    date_data = sighting.get("date") or {}
    species = sighting.get("species") or {}
    place = sighting.get("place") or {}
    observers = sighting.get("observers") or []
    observer = observers[0] if observers and isinstance(observers[0], dict) else {}
    timing = observer.get("timing") or {}

    if not isinstance(date_data, dict):
        date_data = {"#text": str(date_data)}
    if not isinstance(species, dict):
        species = {}
    if not isinstance(place, dict):
        place = {}
    if not isinstance(timing, dict):
        timing = {"#text": str(timing)}

    date_iso = date_data.get("@ISO8601", "")
    timing_iso = timing.get("@ISO8601", "")

    selection = select_coordinates(sighting, observer)
    geocoding = reverse_address(selection)

    house_number_check = compare_osm_and_comment_house_number(
        comment=observer.get("comment", ""),
        osm_house_number=geocoding.house_number,
    )

    basic_validation = create_basic_validation_fields(
        address_status=geocoding.address_status,
        house_number_check_status=house_number_check.status,
        distance_meters=geocoding.distance_meters,
        coordinate_source=selection.source,
    )

    if selection.source == "Beobachtungsmarker":
        coordinate_assessment = "Für Adressrekonstruktion geeignet"
    elif selection.source == "GPS-Position des Erfassungsgeräts":
        coordinate_assessment = "Rückfallwert: kann vom Vogelstandort abweichen"
    elif selection.source == "Referenzpunkt des Meldegebiets":
        coordinate_assessment = "Ungeeignet für eine verlässliche Hausadresse"
    else:
        coordinate_assessment = "Keine Koordinaten verfügbar"

    return {
        "Datensatz": number,
        "Datum": extract_iso_date(date_iso) or normalize_date(date_data.get("#text", "")),
        "Beobachtungszeit": extract_iso_time(timing_iso) or normalize_time(timing.get("#text", "")),
        "Art": species.get("name", ""),
        "Anzahl": observer.get("count", ""),
        "Kommentar": observer.get("comment", ""),
        "Beobachter": observer.get("name", ""),
        "ID_Beobachtung": observer.get("id_sighting", ""),
        "Ornitho_Link": build_ornitho_link(observer.get("id_sighting", "")),
        "GUID": observer.get("guid", ""),
        "Datum_ISO": date_iso,
        "Beobachtungszeit_ISO": timing_iso,
        "Lateinname": species.get("latin_name", ""),
        "Meldeort": place.get("name", ""),
        "Gemeinde_JSON": place.get("municipality", ""),
        "Meldeort_Typ": place.get("place_type", ""),
        "Meldeort_Genauigkeit": place.get("loc_precision", ""),
        "Höhe": observer.get("altitude", place.get("altitude", "")),
        "Flugnummer": observer.get("flight_number", ""),
        "Marker_Latitude": to_float(observer.get("coord_lat")),
        "Marker_Longitude": to_float(observer.get("coord_lon")),
        "GPS_Latitude": to_float(observer.get("gps_lat")),
        "GPS_Longitude": to_float(observer.get("gps_lon")),
        "Meldeort_Latitude": to_float(place.get("coord_lat")),
        "Meldeort_Longitude": to_float(place.get("coord_lon")),
        "Verwendete_Latitude": selection.latitude,
        "Verwendete_Longitude": selection.longitude,
        "Koordinatenquelle": selection.source,
        "Koordinatenpriorität": selection.priority,
        "Koordinatenbewertung": coordinate_assessment,
        **geocoding.to_output_dict(),
        **house_number_check.to_output_dict(),
        **basic_validation,
    }


def process_file(input_path: Path) -> bool:
    print(f"Verarbeite Datei: {input_path.name}")

    try:
        sightings, input_format = load_input_file(input_path)

        if not sightings:
            show_warning(
                f"{input_path.name} ist gültig, enthält aber keine Beobachtungen."
            )
            archive_input(input_path)
            return True

        rows = [
            create_output_row(sighting, number)
            for number, sighting in enumerate(sightings, start=1)
        ]

        full_path, basic_path = write_outputs(rows, input_path)
        print(f"Vollständige Ausgabe: {full_path}")
        print(f"Basic-Ausgabe: {basic_path}")
        print(f"Archiviert: {archive_input(input_path)}")
        logging.info("Datei %s als %s verarbeitet", input_path, input_format)
        return True

    except Exception as exc:
        logging.exception("Verarbeitung fehlgeschlagen: %s", input_path)
        show_error(f"{input_path.name}: {type(exc).__name__}: {exc}")
        return False


def process_input_directory() -> tuple[int, int]:
    ensure_directories()
    configure_logging()

    input_files = sorted(
        path
        for path in INPUT_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_INPUT_SUFFIXES
        and not path.name.startswith("~$")
        and not path.stem.endswith("_mit_adressen")
    )

    if not input_files:
        show_warning(f"Keine unterstützten Eingabedateien in {INPUT_DIR} gefunden.")
        return 0, 0

    successful = sum(1 for path in input_files if process_file(path))
    return successful, len(input_files) - successful
