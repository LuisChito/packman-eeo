"""Capa de dominio: entidades y mapa (solo datos, sin reglas)."""
from .entidades import Estado, Fantasma, Juego, PacMan, TableroPuntajes
from .mapa import MAPA_INICIAL, Mapa

__all__ = ["Estado", "Fantasma", "Juego", "PacMan", "TableroPuntajes", "MAPA_INICIAL", "Mapa"]
