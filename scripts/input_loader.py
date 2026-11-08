import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from scripts.normalizers import clean_value, normalize_tabular_record

REQUIRED_TABULAR_COLUMNS = {
    "ID_SIGHTING", "NAME_SPECIES", "DATE", "COORD_LAT", "COORD_LON"
}


def _validate_tabular_columns(dataframe: pd.DataFrame, label: str) -> None:
    missing = sorted(REQUIRED_TABULAR_COLUMNS - set(dataframe.columns))
    if missing:
        raise ValueError(f"Im {label}-Export fehlen Spalten: {', '.join(missing)}")


def _dataframe_to_sightings(dataframe: pd.DataFrame) -> list[dict]:
    sightings = []
    for _, row in dataframe.iterrows():
        record = row.to_dict()
        if all(clean_value(value, "") == "" for value in record.values()):
            continue
        sightings.append(normalize_tabular_record(record))
    return sightings


def load_json_sightings(input_path: Path) -> list[dict]:
    with input_path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)
    sightings = data.get("data", {}).get("sightings") if isinstance(data, dict) else None
    if not isinstance(sightings, list):
        raise ValueError("Fehlende oder ungültige Liste 'data.sightings'.")
    return sightings


def _xml_to_value(element):
    result = {f"@{key}": value for key, value in element.attrib.items()}
    text_value = (element.text or "").strip()
    children = list(element)
    if not children:
        if result:
            if text_value:
                result["#text"] = text_value
            return result
        return text_value
    for child in children:
        value = _xml_to_value(child)
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(value)
        else:
            result[child.tag] = value
    if text_value:
        result["#text"] = text_value
    return result


def _as_mapping(value) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        return {"#text": value}
    return {}


def _normalize_xml_sighting(element) -> dict:
    date_element = element.find("date")
    species_element = element.find("species")
    place_element = element.find("place")
    date_data = _as_mapping(_xml_to_value(date_element)) if date_element is not None else {}
    species_data = _as_mapping(_xml_to_value(species_element)) if species_element is not None else {}
    place_data = _as_mapping(_xml_to_value(place_element)) if place_element is not None else {}
    if species_element is not None:
        species_data["id"] = species_element.attrib.get("id", "")
    if place_element is not None:
        place_data["id"] = place_element.attrib.get("id", "")
    observers_element = element.find("observers")
    observers = []
    if observers_element is not None:
        for observer_element in observers_element.findall("observer"):
            observer = _as_mapping(_xml_to_value(observer_element))
            observer["timing"] = _as_mapping(observer.get("timing", {}))
            observers.append(observer)
    return {"date": date_data, "species": species_data, "place": place_data, "observers": observers}


def load_xml_sightings(input_path: Path) -> list[dict]:
    root = ET.parse(input_path).getroot()
    data_element = root if root.tag == "data" else root.find("data")
    if data_element is None:
        raise ValueError("XML-Element <data> fehlt.")
    sightings_element = data_element.find("sightings")
    if sightings_element is None:
        raise ValueError("XML-Element <sightings> fehlt.")
    return [_normalize_xml_sighting(item) for item in sightings_element.findall("sighting")]


def load_excel_sightings(input_path: Path) -> list[dict]:
    with pd.ExcelFile(input_path, engine="openpyxl") as excel_file:
        if not excel_file.sheet_names:
            return []
        sheet_name = "Export" if "Export" in excel_file.sheet_names else excel_file.sheet_names[0]
        dataframe = pd.read_excel(
            excel_file,
            sheet_name=sheet_name,
            header=0,
            skiprows=[1],
            dtype=object,
        )
    if dataframe.empty:
        return []
    dataframe.columns = [str(column).strip().upper() for column in dataframe.columns]
    _validate_tabular_columns(dataframe, "XLSX")
    return _dataframe_to_sightings(dataframe)


def load_text_sightings(input_path: Path) -> list[dict]:
    dataframe = None
    last_error = None
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            dataframe = pd.read_csv(
                input_path,
                sep="\t",
                header=0,
                skiprows=[1],
                encoding=encoding,
                dtype=object,
                keep_default_na=False,
            )
            break
        except UnicodeDecodeError as exc:
            last_error = exc
        except pd.errors.EmptyDataError:
            return []
    if dataframe is None:
        raise ValueError(f"Zeichenkodierung konnte nicht ermittelt werden: {last_error}")
    if dataframe.empty:
        return []
    dataframe.columns = [str(column).strip().upper() for column in dataframe.columns]
    _validate_tabular_columns(dataframe, "TXT/TSV")
    return _dataframe_to_sightings(dataframe)


def load_input_file(input_path: Path) -> tuple[list[dict], str]:
    suffix = input_path.suffix.lower()
    loaders = {
        ".json": (load_json_sightings, "JSON"),
        ".xml": (load_xml_sightings, "XML"),
        ".xlsx": (load_excel_sightings, "XLSX"),
        ".txt": (load_text_sightings, "TSV"),
        ".tsv": (load_text_sightings, "TSV"),
    }
    if suffix not in loaders:
        raise ValueError(f"Nicht unterstütztes Dateiformat: {suffix}")
    loader, label = loaders[suffix]
    return loader(input_path), label
