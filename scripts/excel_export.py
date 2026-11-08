from pathlib import Path
from urllib.parse import quote

import pandas as pd

from scripts.config import (
    BASIC_OUTPUT_COLUMNS,
    FULL_OUTPUT_COLUMNS,
    MAX_EXCEL_COLUMN_WIDTH,
    OUTPUT_DIR,
)
from scripts.normalizers import as_string


def build_ornitho_link(sighting_id) -> str:
    sighting_id = as_string(sighting_id)
    if not sighting_id:
        return ""
    return f"https://www.ornitho.de/index.php?m_id=54&id={quote(sighting_id, safe='')}"


def create_output_paths(input_path: Path) -> tuple[Path, Path]:
    full_path = OUTPUT_DIR / f"{input_path.stem}_mit_adressen.xlsx"
    basic_stem = input_path.stem
    if basic_stem.lower().startswith("export_"):
        basic_stem = basic_stem[len("export_"):]
    basic_path = OUTPUT_DIR / f"export_basic_{basic_stem}_mit_adressen.xlsx"
    return full_path, basic_path


def prepare_dataframe(rows: list[dict], columns: list[str]) -> pd.DataFrame:
    dataframe = pd.DataFrame(rows)
    for column in columns:
        if column not in dataframe.columns:
            dataframe[column] = ""
    return dataframe.reindex(columns=columns)


def prepare_basic_dataframe(rows: list[dict]) -> pd.DataFrame:
    dataframe = pd.DataFrame(rows)

    # Anwenderfreundlicher Alias nur im Basic-Export.
    if "Ort_Adresse" in dataframe.columns:
        dataframe["Ort"] = dataframe["Ort_Adresse"]
    elif "Ort" not in dataframe.columns:
        dataframe["Ort"] = ""

    for column in BASIC_OUTPUT_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = ""

    return dataframe.reindex(columns=BASIC_OUTPUT_COLUMNS)


def format_worksheet(worksheet) -> None:
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    headers = {cell.value: cell.column for cell in worksheet[1] if cell.value}
    link_column = headers.get("Ornitho_Link")

    if link_column:
        for row_number in range(2, worksheet.max_row + 1):
            cell = worksheet.cell(row=row_number, column=link_column)
            if isinstance(cell.value, str) and cell.value.startswith(
                "https://www.ornitho.de/"
            ):
                cell.hyperlink = cell.value
                cell.value = "Datensatz in ornitho.de öffnen"
                cell.style = "Hyperlink"

    for cells in worksheet.columns:
        width = max(
            (len(str(cell.value)) for cell in cells if cell.value is not None),
            default=0,
        )
        worksheet.column_dimensions[cells[0].column_letter].width = min(
            max(width + 2, 10),
            MAX_EXCEL_COLUMN_WIDTH,
        )


def write_workbook(dataframe: pd.DataFrame, output_path: Path) -> None:
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        dataframe.to_excel(writer, sheet_name="Beobachtungen", index=False)
        format_worksheet(writer.sheets["Beobachtungen"])


def write_outputs(rows: list[dict], input_path: Path) -> tuple[Path, Path]:
    full_path, basic_path = create_output_paths(input_path)
    write_workbook(prepare_dataframe(rows, FULL_OUTPUT_COLUMNS), full_path)
    write_workbook(prepare_basic_dataframe(rows), basic_path)
    return full_path, basic_path
