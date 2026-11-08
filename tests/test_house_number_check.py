from scripts.house_number_check import (
    compare_osm_and_comment_house_number,
    extract_house_numbers_from_comment,
    normalize_house_number,
)


def test_normalization():
    assert normalize_house_number("16 A") == "16a"
    assert normalize_house_number("16-a") == "16a"
    assert normalize_house_number("16 / 17") == "16/17"


def test_nr_variants():
    for comment in ("Nr. 16", "nr. 16", "NR. 16", "Nr 16", "nr 16"):
        assert extract_house_numbers_from_comment(comment) == ["16"]


def test_unmarked_numbers_are_ignored():
    assert extract_house_numbers_from_comment("2 Haussperlinge um 16:30 Uhr") == []


def test_agreement_wording_and_status():
    result = compare_osm_and_comment_house_number("vor Nr. 24a", "24 A")
    assert result.status == "ÜBEREINSTIMMUNG"
    assert result.comment_house_number == "24a"
    assert "Bemerkungsfeld" in result.detail


def test_missing_comment_house_number_status():
    result = compare_osm_and_comment_house_number("ohne Nummernangabe", "24")
    assert result.status == "HAUSNUMMER_IN_BEMERKUNG_FEHLT"


def test_ambiguous_comment_house_number_status():
    result = compare_osm_and_comment_house_number("Nr. 16, später Nr. 18", "16")
    assert result.status == "HAUSNUMMER_IN_BEMERKUNG_MEHRDEUTIG"
