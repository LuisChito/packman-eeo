"""Entidades y variables de la Tabla 1.

Cada clase es una entidad del análisis y sus atributos llevan el mismo
nombre que la variable del documento (Pf, Pc, Dir, P, T, V, Ff, Fc, E...).
Las entidades NO contienen lógica de juego: solo guardan valores.
La lógica vive en `pacman.reglas`.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..config import (
    INICIO, IZQUIERDA, NORMAL, ORBES_INICIALES, ROSA, SPAWN_FANTASMA,
    SPAWN_FANTASMA_SIN_IA_POS, SPAWN_PAC, SUPER_INICIALES, VERDE, VIDAS_INICIALES,
)
from .mapa import Mapa


@dataclass
class Juego:
    """Entidad Juego · variable EJ ∈ {inicio, jugando, pausa, ganado, perdido}."""
    EJ: str = INICIO


@dataclass
class PacMan:
    """Entidad Pac-Man · Pf, Pc, Dir, P, T, V."""
    Pf: int = SPAWN_PAC[0]
    Pc: int = SPAWN_PAC[1]
    Dir: str = IZQUIERDA
    P: int = 0          # 0 = normal, 1 = con poder
    T: int = 0          # 0..31 rondas restantes de poder (≈ 5 s)
    V: int = VIDAS_INICIALES

    @property
    def pos(self) -> tuple[int, int]:
        return (self.Pf, self.Pc)


@dataclass
class Fantasma:
    """Entidad Fantasma · Ff, Fc, E.

    `nombre`, `ia` y `spawn` son constantes de cada fantasma (no cambian
    durante la partida), no variables de estado:
      - verde: spawn valor 4 en (9, 8), CON IA (reglas inteligentes).
      - rosa:  spawn valor 3 en (9, 10), SIN IA (movimiento al azar).
    """
    nombre: str = VERDE
    ia: bool = True
    spawn: tuple[int, int] = SPAWN_FANTASMA
    Ff: int = SPAWN_FANTASMA[0]
    Fc: int = SPAWN_FANTASMA[1]
    E: int = NORMAL     # 0 = normal, 1 = asustado, 2 = comido

    @property
    def pos(self) -> tuple[int, int]:
        return (self.Ff, self.Fc)

    def reaparecer(self) -> None:
        self.Ff, self.Fc = self.spawn


def _fantasmas_iniciales() -> list[Fantasma]:
    verde = Fantasma(VERDE, True, SPAWN_FANTASMA, *SPAWN_FANTASMA)
    rosa = Fantasma(ROSA, False, SPAWN_FANTASMA_SIN_IA_POS, *SPAWN_FANTASMA_SIN_IA_POS)
    return [verde, rosa]


@dataclass
class TableroPuntajes:
    """Entidad Tablero de puntajes · Pts, Rec."""
    Pts: int = 0
    Rec: int = 0


@dataclass
class Estado:
    """Fórmula del estado (con dos fantasmas):

        (EJ, (Fila, Columna, Valor)19x19, (Pf, Pc, Dir, P, T, V), O, S,
         (Ff, Fc, E)verde, (Ff, Fc, E)rosa, (Pts, Rec))

    O y S son las entidades "Orbes" y "Súper pastillas": cada una tiene un
    único atributo (cuántos quedan), por eso se guardan como enteros.
    """
    juego: Juego = field(default_factory=Juego)
    M: Mapa = field(default_factory=Mapa.inicial)
    pacman: PacMan = field(default_factory=PacMan)
    O: int = ORBES_INICIALES
    S: int = SUPER_INICIALES
    fantasmas: list[Fantasma] = field(default_factory=_fantasmas_iniciales)
    tablero: TableroPuntajes = field(default_factory=TableroPuntajes)

    # Atajo para la variable más consultada
    @property
    def EJ(self) -> str:
        return self.juego.EJ

    @EJ.setter
    def EJ(self, valor: str) -> None:
        self.juego.EJ = valor

    def fantasma_por(self, nombre: str) -> Fantasma:
        return next(f for f in self.fantasmas if f.nombre == nombre)

    @property
    def fantasma(self) -> Fantasma:
        """El fantasma de la fórmula original: el que tiene IA (verde)."""
        return self.fantasma_por(VERDE)

    def como_tupla(self) -> tuple:
        """Fila de la Tabla 3 (sin M), con el fantasma con IA (verde)."""
        p, f, t = self.pacman, self.fantasma, self.tablero
        return (self.EJ, p.Pf, p.Pc, p.Dir, p.P, p.T, p.V, self.O, self.S,
                f.Ff, f.Fc, f.E, t.Pts, t.Rec)

    def variables(self) -> dict[str, object]:
        """Todas las variables del estado (sin M), para el panel y trazas."""
        p, t = self.pacman, self.tablero
        datos: dict[str, object] = {
            "EJ": self.EJ, "Pf": p.Pf, "Pc": p.Pc, "Dir": p.Dir, "P": p.P,
            "T": p.T, "V": p.V, "O": self.O, "S": self.S,
        }
        for f in self.fantasmas:
            sufijo = f.nombre[0]          # v / r
            datos[f"Ff{sufijo}"] = f.Ff
            datos[f"Fc{sufijo}"] = f.Fc
            datos[f"E{sufijo}"] = f.E
        datos["Pts"] = t.Pts
        datos["Rec"] = t.Rec
        return datos

    @classmethod
    def inicial(cls, record: int = 0) -> "Estado":
        estado = cls()
        estado.tablero.Rec = record
        return estado
