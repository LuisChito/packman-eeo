"""Representación de un operador como regla de producción.

    Si <condiciones>  operador  entonces <variable = nuevo valor>

Cada `Regla` guarda su condición de aplicabilidad (antecedente) y su acción
(consecuente). Aplicarla es Modus Ponens: si se cumple A, se ejecuta B.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..dominio.entidades import Estado

EVIDENTE = "evidente"   # lo decide el jugador
OCULTO = "oculto"       # lo dispara el sistema en cuanto se cumple

Condicion = Callable[[Estado], bool]
Accion = Callable[[Estado], None]


@dataclass(frozen=True)
class Regla:
    numero: int
    nombre: str          # verbo del operador, p. ej. "comer_orbe"
    tipo: str            # EVIDENTE u OCULTO
    condicion: Condicion
    accion: Accion
    formal: str          # texto de la regla tal cual aparece en la Tabla 2

    def es_aplicable(self, estado: Estado) -> bool:
        return self.condicion(estado)

    def aplicar(self, estado: Estado) -> bool:
        """Modus Ponens. Devuelve True si la regla se disparó."""
        if not self.condicion(estado):
            return False
        self.accion(estado)
        return True

    def __str__(self) -> str:
        return f"{self.numero}. {self.nombre}"
