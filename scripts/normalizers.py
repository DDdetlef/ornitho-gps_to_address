from datetime import date, datetime, time

import pandas as pd


def clean_value(value, default=""):
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass
    return value


def as_string(value, default="") -> str:
    value = clean_value(value, default)
    if value == default:
        return default
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def to_float(value) -> float | None:
    value = clean_value(value, None)
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_date(value) -> str:
    value = clean_value(value)
    if value == "":
        return ""
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.strftime("%Y-%m-%d")
    text = str(value).strip()
    for pattern in (
        "%Y-%m-%d", "%d.%m.%Y", "%d.%m.%Y %H:%M",
        "%d.%m.%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(text, pattern).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return text


def normalize_time(value) -> str:
    value = clean_value(value)
    if value == "":
        return ""
    if isinstance(value, (pd.Timestamp, datetime, time)):
        return value.strftime("%H:%M:%S")
    text = str(value).strip()
    for pattern in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(text, pattern).strftime("%H:%M:%S")
        except ValueError:
            continue
    return text


def extract_iso_date(value) -> str:
    text = as_string(value)
    if not text:
        return ""
    return text.split("T", 1)[0] if "T" in text else normalize_date(text)


def extract_iso_time(value) -> str:
    text = as_string(value)
    if not text:
        return ""
    if "T" not in text:
        return normalize_time(text)
    result = text.split("T", 1)[1].replace("Z", "")
    if "+" in result:
        result = result.split("+", 1)[0]
    if len(result) > 8 and "-" in result[8:]:
        result = result[:8]
    return result


def normalize_tabular_record(record: dict) -> dict:
    date_value = normalize_date(record.get("DATE", ""))
    time_value = normalize_time(record.get("TIMING", ""))
    timestamp = f"{date_value}T{time_value}" if date_value and time_value else date_value
    precision = as_string(record.get("PRECISION", ""))
    accuracy = as_string(record.get("ACCURACY_LOCATION", ""))

    return {
        "date": {"#text": date_value, "@ISO8601": date_value},
        "species": {
            "id": as_string(record.get("ID_SPECIES", "")),
            "name": as_string(record.get("NAME_SPECIES", "")),
            "latin_name": as_string(record.get("LATIN_SPECIES", "")),
        },
        "place": {
            "id": as_string(record.get("ID_PLACE", "")),
            "name": as_string(record.get("PLACE", "")),
            "municipality": as_string(record.get("MUNICIPALITY", "")),
            "county": as_string(record.get("COUNTY", "")),
            "country": as_string(record.get("COUNTRY", "")),
            "coord_lat": clean_value(record.get("COORD_LAT", "")),
            "coord_lon": clean_value(record.get("COORD_LON", "")),
            "altitude": clean_value(record.get("ALTITUDE", "")),
            "loc_precision": precision or accuracy,
            "place_type": precision,
        },
        "observers": [{
            "id_sighting": as_string(record.get("ID_SIGHTING", "")),
            "guid": as_string(record.get("GUID", "")),
            "coord_lat": clean_value(record.get("COORD_LAT", "")),
            "coord_lon": clean_value(record.get("COORD_LON", "")),
            "gps_lat": clean_value(record.get("GPS_LAT", "")),
            "gps_lon": clean_value(record.get("GPS_LON", "")),
            "altitude": clean_value(record.get("ALTITUDE", "")),
            "count": clean_value(record.get("TOTAL_COUNT", "")),
            "comment": as_string(record.get("COMMENT", "")),
            "private_comment": as_string(record.get("PRIVATE_COMMENT", "")),
            "detail": as_string(record.get("DETAIL", "")),
            "name": as_string(record.get("SEARCH_EXPORT_ENTITY_FULL_NAME", "")),
            "flight_number": as_string(record.get("FLIGHT_NUMBER", "")),
            "timing": {"#text": time_value, "@ISO8601": timestamp},
        }],
    }
