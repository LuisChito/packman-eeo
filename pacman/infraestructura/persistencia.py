"""Guarda el récord (Rec) entre ejecuciones en un archivo JSON."""
from __future__ import annotations

import json
from pathlib import Path

RUTA_POR_DEFECTO = Path(__file__).resolve().parents[2] / "record.json"


def cargar_record(ruta: Path = RUTA_POR_DEFECTO) -> int:
    try:
        return int(json.loads(ruta.read_text(encoding="utf-8")).get("Rec", 0))
    except (OSError, ValueError, AttributeError):
        return 0


def guardar_record(rec: int, ruta: Path = RUTA_POR_DEFECTO) -> None:
    try:
        ruta.write_text(json.dumps({"Rec": rec}), encoding="utf-8")
    except OSError:
        pass  # sin permisos de escritura: el récord vive solo en memoria
