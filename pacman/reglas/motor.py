"""Motor de inferencia (encadenamiento hacia adelante).

Aplica las reglas de la Tabla 2 respetando el "Orden de aplicación en cada
ronda" del análisis:

    1) Pac-Man se mueve
    2) reglas de colisión (comer orbe o súper pastilla, comer fantasma o perder vida)
    3) los fantasmas se mueven (verde y luego rosa)
    4) reglas de poder y regeneración
    5) reglas de fin de partida (ganar, perder juego, actualizar récord)

Cada fase está formada por *grupos de conflicto*: dentro de un grupo se
dispara como máximo UNA regla (la primera aplicable). Así, por ejemplo,
`reducir_poder` y `terminar_poder` nunca se disparan en la misma ronda.

Resolución de conflictos por ESPECIFICIDAD: en el grupo de movimiento del
fantasma verde, `perseguir_inteligente` (E = 0 y lejos) va antes que
`perseguir` (E = 0), y `huir_inteligente` (E = 1 y cerca) va antes que
`huir` (E = 1). La regla general solo se dispara si la específica no aplica.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from ..config import JUGANDO
from ..dominio.entidades import Estado
from . import operadores as op
from .base import EVIDENTE, Regla

Grupo = tuple[Regla, ...]

VERDE = op.FANTASMA_VERDE
ROSA = op.FANTASMA_ROSA

COLISION_OBJETOS: Grupo = (op.COMER_ORBE, op.COMER_SUPER)
PODER: Grupo = (op.REDUCIR_PODER, op.TERMINAR_PODER)
FIN: tuple[Grupo, ...] = ((op.GANAR,), (op.PERDER_JUEGO,), (op.ACTUALIZAR_RECORD,))

FASES: tuple[tuple[str, tuple[Grupo, ...]], ...] = (
    ("2 · colisión", (COLISION_OBJETOS, VERDE.colision(), ROSA.colision())),
    # Cada fantasma se mueve y enseguida se vuelve a evaluar SU colisión con
    # Pac-Man: las reglas ocultas se aplican "en cuanto se cumplen".
    # Grupo verde: salir_casa > perseguir_inteligente > perseguir > huir_inteligente > huir
    # Grupo rosa:  salir_casa > deambular
    ("3 · fantasmas", (VERDE.movimiento(), VERDE.colision(),
                       ROSA.movimiento(), ROSA.colision())),
    ("4 · poder", (PODER, (VERDE.regenerar,), (ROSA.regenerar,))),
    ("5 · fin", FIN),
)


@dataclass
class Disparo:
    ronda: int
    fase: str
    regla: Regla


class MotorReglas:
    def __init__(self, estado: Estado, max_traza: int = 200) -> None:
        self.estado = estado
        self.ronda = 0
        self.traza: deque[Disparo] = deque(maxlen=max_traza)
        self.ultimos: list[Regla] = []   # reglas disparadas en la última ronda

    # ----------------------------------------------------------- utilidades
    def _disparar(self, regla: Regla, fase: str) -> bool:
        if regla.aplicar(self.estado):
            self.traza.append(Disparo(self.ronda, fase, regla))
            self.ultimos.append(regla)
            return True
        return False

    def _disparar_grupo(self, grupo: Grupo, fase: str) -> Regla | None:
        for regla in grupo:
            if self._disparar(regla, fase):
                return regla
        return None

    def aplicables(self) -> list[Regla]:
        """Conjunto de conflicto: todas las reglas que podrían dispararse ahora."""
        return [r for r in op.TODAS if r.es_aplicable(self.estado)]

    # --------------------------------------------- operadores evidentes
    def aplicar_evidente(self, nombre: str) -> bool:
        """Dispara un operador del jugador (iniciar, pausar, reanudar, reiniciar)."""
        regla = op.POR_NOMBRE[nombre]
        if regla.tipo != EVIDENTE:
            raise ValueError(f"{nombre} es un operador oculto; lo aplica el motor")
        disparo = self._disparar(regla, "jugador")
        if disparo and nombre == "iniciar_juego":
            self.ronda = 0
        return disparo

    # ------------------------------------------------------------- ronda
    def ejecutar_ronda(self, direccion_deseada: str | None = None) -> list[Regla]:
        """Ejecuta una ronda completa y devuelve las reglas disparadas en orden."""
        if self.estado.EJ != JUGANDO:
            return []
        self.ronda += 1
        self.ultimos = []

        # 1) Pac-Man se mueve: primero la dirección que pidió el jugador;
        #    si choca, sigue en su dirección actual (Dir); si no, se queda.
        #    Grupo por dirección: [mover_<dir> | cruzar_portal_<dir>].
        for direccion in (direccion_deseada, self.estado.pacman.Dir):
            if not direccion:
                continue
            grupo = (op.MOVIMIENTOS[direccion], *filter(None, [op.PORTALES_POR_DIRECCION.get(direccion)]))
            if self._disparar_grupo(grupo, "1 · Pac-Man"):
                break

        # 2) a 5)
        for fase, grupos in FASES:
            for grupo in grupos:
                self._disparar_grupo(grupo, fase)

        return list(self.ultimos)
