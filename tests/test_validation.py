from scripts.validation import validate_address


def test_street_without_house_number_is_tolerated():
    result = validate_address(
        coordinate_source="Beobachtungsmarker",
        street="Pacelliallee",
        house_number="",
        postcode="14195",
        city="Berlin",
        distance_meters=20,
    )
    assert result.status == "PLAUSIBEL_OHNE_HAUSNUMMER"
    assert result.allow_street is True
    assert result.allow_house_number is False
