import logging
import shutil
import time
from datetime import datetime
from pathlib import Path

from scripts.config import MOVE_ATTEMPTS, MOVE_RETRY_SECONDS, PROCESSED_DIR


def create_target_path(input_path: Path) -> Path:
    target = PROCESSED_DIR / input_path.name
    if not target.exists():
        return target
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = PROCESSED_DIR / f"{input_path.stem}_{stamp}{input_path.suffix}"
    counter = 1
    while target.exists():
        target = PROCESSED_DIR / f"{input_path.stem}_{stamp}_{counter}{input_path.suffix}"
        counter += 1
    return target


def archive_input(input_path: Path) -> Path:
    for attempt in range(1, MOVE_ATTEMPTS + 1):
        try:
            target = create_target_path(input_path)
            moved_path = Path(shutil.move(str(input_path), str(target)))
            logging.info("Eingabedatei verschoben: %s -> %s", input_path, moved_path)
            return moved_path
        except PermissionError:
            if attempt >= MOVE_ATTEMPTS:
                raise
            time.sleep(MOVE_RETRY_SECONDS)
    raise RuntimeError("Archivierung unerwartet beendet")
