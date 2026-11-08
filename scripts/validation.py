from scripts.config import (
    DISTANCE_RESTRICTED_MAX_METERS,
    DISTANCE_VERIFIED_MAX_METERS,
)
from scripts.models import ValidationResult


def validate_address(
    coordinate_source: str,
    street: str,
    house_number: str,
    postcode: str,
    city: str,
    distance_meters: float | None,
) -> ValidationResult:
    if coordinate_source == "Referenzpunkt des Meldegebiets":
        return ValidationResult(
            "NICHT_BELASTBAR",
            "Gebietsreferenzpunkt ist für eine Straßenadresse ungeeignet",
            False,
            False,
            True,
        )
    if distance_meters is None:
        return ValidationResult(
            "NICHT_BEWERTBAR",
            "Entfernung zum OSM-Treffer nicht bestimmbar",
            False,
            False,
            True,
        )
    if distance_meters > DISTANCE_RESTRICTED_MAX_METERS:
        return ValidationResult(
            "NICHT_BELASTBAR",
            f"OSM-Treffer liegt mehr als {DISTANCE_RESTRICTED_MAX_METERS} m entfernt",
            False,
            False,
            True,
        )
    if street and postcode and city and not house_number:
        return ValidationResult(
            "PLAUSIBEL_OHNE_HAUSNUMMER",
            "Straße, PLZ und Ort plausibel; Hausnummer nicht ermittelt",
            True,
            False,
            False,
        )
    if street and house_number and postcode and city and distance_meters <= DISTANCE_VERIFIED_MAX_METERS:
        return ValidationResult(
            "VERIFIZIERT",
            "Vollständiger Treffer in räumlicher Nähe zum Marker",
            True,
            True,
            False,
        )
    return ValidationResult(
        "EINGESCHRÄNKT_PLAUSIBEL",
        "Adressangaben erfordern manuelle Prüfung",
        bool(street),
        False,
        True,
    )
