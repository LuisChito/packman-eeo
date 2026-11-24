"""Estrategias de movimiento de los fantasmas.

Fantasma VERDE (con IA):
  - emboscada():          usada por la regla 22 perseguir_inteligente.
  - huida_por_territorio(): usada por la regla 23 huir_inteligente.
Fantasma ROSA (sin IA):
  - paso_al_azar():       usada por la regla 24 deambular.

Todas devuelven la celda vecina a la que se mueve el fantasma.
"""
from __future__ import annotations

import random

from ..config import DELTAS, PASOS_PREDICCION
from ..dominio.mapa import Mapa
from .bfs import INFINITO, distancias_desde, vecinas

Celda = tuple[int, int]

# Generador de azar del fantasma rosa. Se puede sembrar para que las
# pruebas sean reproducibles: AZAR.seed(123)
AZAR = random.Random()


# ------------------------------------------------------------ predicción
def predecir_pacman(mapa: Mapa, pacman: Celda, direccion: str,
                    pasos: int = PASOS_PREDICCION) -> Celda:
    """predicción(Pf, Pc, Dir, k): la celda donde estará Pac-Man si sigue
    avanzando en su dirección actual hasta k celdas (o hasta chocar)."""
    df, dc = DELTAS[direccion]
    f, c = pacman
    for _ in range(pasos):
        siguiente = (f + df, c + dc)
        if not mapa.transitable_pacman(siguiente):
            break
        f, c = siguiente
    return (f, c)


# ------------------------------------------- 22 · perseguir inteligente
def emboscada(mapa: Mapa, fantasma: Celda, pacman: Celda, direccion: str) -> Celda | None:
    """En vez de ir a donde ESTÁ Pac-Man, va a donde VA A ESTAR.

    objetivo = predicción(Pac-Man, 4 celdas adelante en su Dir)
    elige la vecina con menor BFS(vecina, objetivo); si empatan, la que
    quede más cerca del propio Pac-Man.
    """
    opciones = vecinas(mapa, fantasma)
    if not opciones:
        return None
    objetivo = predecir_pacman(mapa, pacman, direccion)
    al_objetivo = distancias_desde(mapa, objetivo)
    al_pacman = distancias_desde(mapa, pacman)
    return min(opciones, key=lambda v: (al_objetivo.get(v, INFINITO), al_pacman.get(v, INFINITO)))


# ----------------------------------------------- 23 · huir inteligente
def territorio(mapa: Mapa, desde: Celda, dist_pacman: dict[Celda, int]) -> int:
    """Número de celdas a las que el fantasma llegaría ANTES que Pac-Man
    si estuviera en `desde` (diagrama de Voronoi sobre los pasillos)."""
    propias = distancias_desde(mapa, desde)
    return sum(1 for celda, d in propias.items() if d < dist_pacman.get(celda, INFINITO))


def huida_por_territorio(mapa: Mapa, fantasma: Celda, pacman: Celda) -> Celda | None:
    """No solo se aleja: escoge la salida que le deja MÁS zona segura.

    Huir "simple" (regla 12) toma la vecina más lejana; cuando varias se
    alejan lo mismo, desempata por el orden fijo ↑ ↓ ← → y a menudo se mete
    en un callejón. Esta estrategia:
      1. descarta las vecinas que lo ACERCAN a Pac-Man (si queda alguna);
      2. de las que quedan, elige la de mayor territorio (celdas a las que
         llega antes que Pac-Man), es decir, la que tiene más escapatoria;
      3. si empatan, la que quede más lejos de Pac-Man.
    """
    opciones = vecinas(mapa, fantasma)
    if not opciones:
        return None
    dist_pacman = distancias_desde(mapa, pacman)
    actual = dist_pacman.get(fantasma, INFINITO)
    seguras = [v for v in opciones if dist_pacman.get(v, INFINITO) >= actual] or opciones
    return max(seguras, key=lambda v: (territorio(mapa, v, dist_pacman), dist_pacman.get(v, -1)))


# ---------------------------------------------------- 24 · deambular
def paso_al_azar(mapa: Mapa, fantasma: Celda) -> Celda | None:
    """Regla "pedorra": cualquier vecina válida al azar. No mira a Pac-Man."""
    opciones = vecinas(mapa, fantasma)
    return AZAR.choice(opciones) if opciones else None
