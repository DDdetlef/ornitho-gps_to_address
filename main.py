from scripts.processing import process_input_directory


def main() -> int:
    """Startet die Verarbeitung aller unterstützten Eingabedateien."""
    successful_files, failed_files = process_input_directory()

    print()
    print("=" * 60)
    print("Verarbeitung abgeschlossen.")
    print(f"Erfolgreich: {successful_files}")
    print(f"Fehlgeschlagen: {failed_files}")

    return 0 if failed_files == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
