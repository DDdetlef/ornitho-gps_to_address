from scripts.config import (
    DISTANCE_PLAUSIBLE_MAX_METERS,
    DISTANCE_RESTRICTED_MAX_METERS,
    DISTANCE_VERIFIED_MAX_METERS,
)

ADDRESS_RATING_LABELS = {
    "VERIFIZIERT": "Vollständige Adresse plausibel",
    "PLAUSIBEL_OHNE_HAUSNUMMER": "Plausibel ohne Hausnummer",
    "PLAUSIBEL_MIT_PRÜFHINWEIS": "Plausibel mit Prüfhinweis",
    "EINGESCHRÄNKT_PLAUSIBEL": "Eingeschränkt plausibel",
    "NICHT_BEWERTBAR": "Nicht bewertbar",
    "NICHT_BELASTBAR": "Nicht belastbar",
}

HOUSE_NUMBER_CHECK_LABELS = {
    "ÜBEREINSTIMMUNG": "Stimmt mit Bemerkung überein",
    "ABWEICHUNG": "Weicht von Bemerkung ab",
    "OSM_HAUSNUMMER_FEHLT": "OSM-Hausnummer fehlt",
    "HAUSNUMMER_IN_BEMERKUNG_FEHLT": "Keine Hausnummer in Bemerkung",
    "HAUSNUMMER_IN_BEMERKUNG_MEHRDEUTIG": "Hausnummer in Bemerkung mehrdeutig",
    "NICHT_VERGLEICHBAR": "Nicht vergleichbar",
    "ABGLEICH_DEAKTIVIERT": "Abgleich nicht durchgeführt",
}


def simplify_address_rating(address_status: str) -> str:
    return ADDRESS_RATING_LABELS.get(address_status, "Keine Bewertung")


def simplify_house_number_check(check_status: str) -> str:
    return HOUSE_NUMBER_CHECK_LABELS.get(check_status, "Abgleich nicht durchgeführt")


def spatial_plausibility(distance_meters) -> str:
    if distance_meters is None or distance_meters == "":
        return "Nicht bestimmbar"

    try:
        distance = float(distance_meters)
    except (TypeError, ValueError):
        return "Nicht bestimmbar"

    if distance <= DISTANCE_VERIFIED_MAX_METERS:
        return "Sehr nah"
    if distance <= DISTANCE_PLAUSIBLE_MAX_METERS:
        return "Nah"
    if distance <= DISTANCE_RESTRICTED_MAX_METERS:
        return "Weiter entfernt"
    return "Zu weit entfernt"


def determine_review_need(
    address_status: str,
    house_number_check_status: str,
    distance_meters,
    coordinate_source: str,
) -> str:
    """Leitet Nein, Empfohlen oder Erforderlich nach Prioritätsregeln ab."""

    if address_status in {"NICHT_BEWERTBAR", "NICHT_BELASTBAR"}:
        return "Erforderlich"

    if house_number_check_status in {
        "ABWEICHUNG",
        "HAUSNUMMER_IN_BEMERKUNG_MEHRDEUTIG",
        "NICHT_VERGLEICHBAR",
    }:
        return "Erforderlich"

    if coordinate_source == "Referenzpunkt des Meldegebiets":
        return "Erforderlich"

    try:
        distance = float(distance_meters) if distance_meters not in (None, "") else None
    except (TypeError, ValueError):
        distance = None

    if distance is not None and distance > DISTANCE_PLAUSIBLE_MAX_METERS:
        return "Erforderlich"

    if address_status == "EINGESCHRÄNKT_PLAUSIBEL":
        return "Erforderlich"

    if distance is not None and distance > DISTANCE_VERIFIED_MAX_METERS:
        return "Empfohlen"

    if coordinate_source == "GPS-Position des Erfassungsgeräts":
        return "Empfohlen"

    return "Nein"


def create_basic_validation_fields(
    address_status: str,
    house_number_check_status: str,
    distance_meters,
    coordinate_source: str,
) -> dict:
    return {
        "Hausnummernabgleich": simplify_house_number_check(
            house_number_check_status
        ),
        "Adressbewertung": simplify_address_rating(address_status),
        "Räumliche_Plausibilität": spatial_plausibility(distance_meters),
        "Prüfbedarf": determine_review_need(
            address_status,
            house_number_check_status,
            distance_meters,
            coordinate_source,
        ),
    }
