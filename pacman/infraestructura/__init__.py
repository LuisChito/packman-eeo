"""Capa de infraestructura: persistencia (no conoce reglas ni pygame)."""
from .persistencia import cargar_record, guardar_record

__all__ = ["cargar_record", "guardar_record"]
