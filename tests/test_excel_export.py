from scripts.excel_export import build_ornitho_link


def test_ornitho_link_uses_id_parameter():
    assert build_ornitho_link(123325447) == (
        "https://www.ornitho.de/index.php?m_id=54&id=123325447"
    )
