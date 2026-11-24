"""Entidad Mapa: matriz 19 × 19 con (fila, columna, valor).

La matriz se transcribió celda por celda del estado inicial M del análisis
EEO. La casa de los fantasmas forma parte del mapa (no es una variable).
"""
from __future__ import annotations

from ..config import (
    BLOQUEADAS, CASA, COLUMNAS, FILAS, ORBE, SUPER_PASTILLA, ZONA_CASA,
)

# 0 pasillo · 1 pared · 2 túnel · 3 spawn sin IA · 4 spawn con IA
# 5 spawn Pac-Man · 6 orbe · 7 súper pastilla · 8 puerta
MAPA_INICIAL: tuple[tuple[int, ...], ...] = (
    (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),  # 0
    (1, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 1),  # 1
    (1, 6, 1, 1, 6, 1, 6, 1, 1, 1, 1, 1, 6, 1, 6, 1, 1, 6, 1),  # 2
    (1, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 1),  # 3
    (1, 1, 1, 6, 1, 1, 6, 1, 1, 1, 1, 1, 6, 1, 1, 6, 1, 1, 1),  # 4
    (1, 6, 6, 6, 6, 1, 6, 6, 6, 7, 6, 6, 6, 1, 6, 6, 6, 6, 1),  # 5
    (1, 6, 1, 1, 1, 1, 6, 1, 1, 1, 1, 1, 6, 1, 1, 1, 1, 6, 1),  # 6
    (2, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 2),  # 7
    (1, 6, 1, 1, 6, 1, 6, 1, 1, 8, 1, 1, 6, 1, 6, 1, 1, 6, 1),  # 8
    (1, 6, 7, 1, 6, 1, 6, 1, 4, 0, 3, 1, 6, 1, 6, 1, 7, 6, 1),  # 9
    (1, 1, 6, 1, 6, 1, 6, 1, 1, 1, 1, 1, 6, 1, 6, 1, 6, 1, 1),  # 10
    (1, 6, 6, 6, 6, 1, 6, 6, 6, 6, 6, 6, 6, 1, 6, 6, 6, 6, 1),  # 11
    (1, 1, 1, 1, 6, 1, 6, 1, 1, 1, 1, 1, 6, 1, 6, 1, 1, 1, 1),  # 12
    (1, 6, 6, 6, 6, 6, 6, 6, 6, 5, 6, 6, 6, 6, 6, 6, 6, 6, 1),  # 13
    (1, 6, 1, 1, 1, 1, 6, 1, 1, 1, 1, 1, 6, 1, 1, 1, 1, 6, 1),  # 14
    (1, 6, 6, 6, 6, 1, 6, 6, 6, 1, 6, 6, 6, 1, 6, 6, 6, 6, 1),  # 15
    (1, 1, 1, 6, 1, 1, 1, 1, 6, 1, 6, 1, 1, 1, 1, 6, 1, 1, 1),  # 16
    (1, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 1),  # 17
    (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),  # 18
)


class Mapa:
    """Contenido de cada celda. Es mutable: los orbes comidos quedan en 0."""

    def __init__(self, celdas: list[list[int]] | None = None) -> None:
        self.celdas = celdas if celdas is not None else [list(f) for f in MAPA_INICIAL]

    # ------------------------------------------------------------ consultas
    def __getitem__(self, fila: int) -> list[int]:
        return self.celdas[fila]

    def valor(self, celda: tuple[int, int]) -> int:
        f, c = celda
        return self.celdas[f][c]

    def dentro(self, celda: tuple[int, int]) -> bool:
        f, c = celda
        return 0 <= f < FILAS and 0 <= c < COLUMNAS

    def transitable(self, celda: tuple[int, int]) -> bool:
        """M ∉ {1, 2}: ningún personaje entra a pared ni túnel."""
        return self.dentro(celda) and self.valor(celda) not in BLOQUEADAS

    def transitable_pacman(self, celda: tuple[int, int]) -> bool:
        """M ∉ {1, 2} y celda ∉ zona_casa."""
        return self.transitable(celda) and celda not in ZONA_CASA

    def transitable_fantasma(self, celda: tuple[int, int]) -> bool:
        """vecinas(Ff, Fc): M ∉ {1, 2} y fuera de la casa (la puerta sí vale)."""
        return self.transitable(celda) and celda not in CASA

    def contar(self, valor: int) -> int:
        return sum(fila.count(valor) for fila in self.celdas)

    def orbes(self) -> int:
        return self.contar(ORBE)

    def super_pastillas(self) -> int:
        return self.contar(SUPER_PASTILLA)

    def copia(self) -> "Mapa":
        return Mapa([fila[:] for fila in self.celdas])

    @classmethod
    def inicial(cls) -> "Mapa":
        return cls()
