"""Traduce teclas a intenciones del jugador (operadores evidentes).

Aquí no se decide si el operador es aplicable: eso lo dicen las reglas.
"""
from __future__ import annotations

import pygame

from ..config import ABAJO, ARRIBA, DERECHA, GANADO, INICIO, IZQUIERDA, JUGANDO, PAUSA, PERDIDO

TECLAS_DIRECCION = {
    pygame.K_UP: ARRIBA, pygame.K_w: ARRIBA,
    pygame.K_DOWN: ABAJO, pygame.K_s: ABAJO,
    pygame.K_LEFT: IZQUIERDA, pygame.K_a: IZQUIERDA,
    pygame.K_RIGHT: DERECHA, pygame.K_d: DERECHA,
}

TECLAS_CONFIRMAR = {pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE}
TECLAS_PAUSA = {pygame.K_p, pygame.K_ESCAPE}


def direccion_de(tecla: int) -> str | None:
    return TECLAS_DIRECCION.get(tecla)


def operador_de(tecla: int, EJ: str) -> str | None:
    """Operador evidente que el jugador intenta aplicar con esa tecla."""
    if tecla in TECLAS_CONFIRMAR:
        if EJ == INICIO:
            return "iniciar_juego"
        if EJ in (GANADO, PERDIDO):
            return "reiniciar"
        if EJ == PAUSA:
            return "reanudar"
    if tecla in TECLAS_PAUSA:
        if EJ == JUGANDO:
            return "pausar"
        if EJ == PAUSA:
            return "reanudar"
    return None
