"""Capa de reglas: operadores (Tabla 2) y motor de inferencia."""
from .base import EVIDENTE, OCULTO, Regla
from .motor import MotorReglas
from . import operadores

__all__ = ["EVIDENTE", "OCULTO", "Regla", "MotorReglas", "operadores"]
