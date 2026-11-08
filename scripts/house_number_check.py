import re
from dataclasses import dataclass

from scripts.config import (
    COMMENT_HOUSE_NUMBER_KEYWORDS,
    ENABLE_COMMENT_HOUSE_NUMBER_CHECK,
)


@dataclass(frozen=True)
class HouseNumberCheckResult:
    """Vergleich der OSM-Hausnummer mit der Angabe in der Bemerkung."""

    comment_house_number: str
    status: str
    detail: str

    def to_output_dict(self) -> dict:
        return {
            "Hausnummer_aus_Bemerkung": self.comment_house_number,
            "Hausnummer_Abgleich": self.status,
            "Hausnummer_Abgleich_Detail": self.detail,
        }


def normalize_house_number(value) -> str:
    """Vereinheitlicht Hausnummern nur für den Vergleich."""

    if value is None:
        return ""

    normalized = str(value).strip().lower()
    normalized = normalized.replace("–", "-").replace("—", "-")
    normalized = re.sub(r"\s+", "", normalized)
    normalized = re.sub(r"(?<=\d)-(?=[a-z])", "", normalized)
    return normalized


def extract_house_numbers_from_comment(comment) -> list[str]:
    """
    Extrahiert ausdrücklich gekennzeichnete Hausnummern aus der Bemerkung.

    Unterstützt werden u. a. Hausnummer, Hausnr., Haus-Nr., Adresse,
    Nr., nr., Nr und nr. Nicht gekennzeichnete Zahlen bleiben unberührt.
    """

    if not ENABLE_COMMENT_HOUSE_NUMBER_CHECK or comment is None:
        return []

    comment_text = str(comment).strip()
    if not comment_text:
        return []

    keyword_pattern = "|".join(
        re.escape(keyword)
        for keyword in COMMENT_HOUSE_NUMBER_KEYWORDS
    )

    pattern = re.compile(
        rf"""
        \b(?:{keyword_pattern})\b
        \s*[.:=\-]?\s*
        (?:[A-Za-zÄÖÜäöüß.\-\s]+?\s+)?
        (?P<number>
            \d+\s*(?:[A-Za-z]|[-/]\s*\d+[A-Za-z]?)?
        )
        \b
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    matches = []
    for match in pattern.finditer(comment_text):
        house_number = match.group("number").strip()
        if house_number:
            matches.append(house_number)

    unique_matches = []
    seen = set()
    for house_number in matches:
        normalized = normalize_house_number(house_number)
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_matches.append(house_number)

    return unique_matches


def compare_osm_and_comment_house_number(
    comment,
    osm_house_number,
) -> HouseNumberCheckResult:
    """
    Vergleicht die OSM-Hausnummer mit einer Hausnummer in der Bemerkung.

    Die Angabe aus der Bemerkung verändert die rekonstruierte Adresse nie.
    """

    if not ENABLE_COMMENT_HOUSE_NUMBER_CHECK:
        return HouseNumberCheckResult(
            "",
            "ABGLEICH_DEAKTIVIERT",
            "Der Abgleich mit einer Hausnummer im Bemerkungsfeld ist deaktiviert.",
        )

    comment_numbers = extract_house_numbers_from_comment(comment)
    osm_original = "" if osm_house_number is None else str(osm_house_number).strip()
    osm_normalized = normalize_house_number(osm_original)

    if not comment_numbers:
        return HouseNumberCheckResult(
            "",
            "HAUSNUMMER_IN_BEMERKUNG_FEHLT",
            "Im Bemerkungsfeld wurde keine ausdrücklich gekennzeichnete Hausnummer gefunden.",
        )

    if len(comment_numbers) > 1:
        return HouseNumberCheckResult(
            "; ".join(comment_numbers),
            "HAUSNUMMER_IN_BEMERKUNG_MEHRDEUTIG",
            "Im Bemerkungsfeld wurden mehrere unterschiedliche Hausnummern gefunden. Ein automatischer Vergleich wurde nicht durchgeführt.",
        )

    comment_original = comment_numbers[0]
    comment_normalized = normalize_house_number(comment_original)

    if not comment_normalized:
        return HouseNumberCheckResult(
            comment_original,
            "NICHT_VERGLEICHBAR",
            "Die Hausnummer aus dem Bemerkungsfeld konnte nicht normalisiert werden.",
        )

    if not osm_normalized:
        return HouseNumberCheckResult(
            comment_original,
            "OSM_HAUSNUMMER_FEHLT",
            f"Im Bemerkungsfeld ist die Hausnummer '{comment_original}' angegeben. OSM hat keine Hausnummer geliefert. Die rekonstruierte Adresse wurde nicht ergänzt.",
        )

    if comment_normalized == osm_normalized:
        return HouseNumberCheckResult(
            comment_original,
            "ÜBEREINSTIMMUNG",
            f"Die OSM-Hausnummer '{osm_original}' stimmt mit der Hausnummer '{comment_original}' aus dem Bemerkungsfeld überein.",
        )

    return HouseNumberCheckResult(
        comment_original,
        "ABWEICHUNG",
        f"Im Bemerkungsfeld ist die Hausnummer '{comment_original}' angegeben. OSM liefert '{osm_original}'. Die OSM-Hausnummer wurde nicht ersetzt.",
    )
