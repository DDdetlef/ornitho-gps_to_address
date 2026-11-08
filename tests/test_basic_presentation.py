from scripts.basic_presentation import (
    create_basic_validation_fields,
    simplify_address_rating,
    simplify_house_number_check,
    spatial_plausibility,
)


def test_simplified_wording():
    assert simplify_house_number_check("ÜBEREINSTIMMUNG") == "Stimmt mit Bemerkung überein"
    assert simplify_house_number_check("HAUSNUMMER_IN_BEMERKUNG_FEHLT") == "Keine Hausnummer in Bemerkung"
    assert simplify_address_rating("PLAUSIBEL_OHNE_HAUSNUMMER") == "Plausibel ohne Hausnummer"


def test_spatial_classes():
    assert spatial_plausibility(30) == "Sehr nah"
    assert spatial_plausibility(31) == "Nah"
    assert spatial_plausibility(76) == "Weiter entfernt"
    assert spatial_plausibility(151) == "Zu weit entfernt"
    assert spatial_plausibility(None) == "Nicht bestimmbar"


def test_missing_osm_house_number_can_need_no_review():
    result = create_basic_validation_fields(
        address_status="PLAUSIBEL_OHNE_HAUSNUMMER",
        house_number_check_status="OSM_HAUSNUMMER_FEHLT",
        distance_meters=15,
        coordinate_source="Beobachtungsmarker",
    )
    assert result["Prüfbedarf"] == "Nein"


def test_deviation_requires_review():
    result = create_basic_validation_fields(
        address_status="VERIFIZIERT",
        house_number_check_status="ABWEICHUNG",
        distance_meters=10,
        coordinate_source="Beobachtungsmarker",
    )
    assert result["Prüfbedarf"] == "Erforderlich"
