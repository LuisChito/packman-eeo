"""Inteligencia del fantasma: BFS (búsqueda en anchura).

BFS(a, b) = número de pasos reales por los pasillos entre la celda a y b.
Para no repetir una búsqueda por cada vecina, se lanza una sola BFS desde
Pac-Man y se consulta la distancia de cada vecina del fantasma (el grafo es
no dirigido, así que BFS(vecina, Pac-Man) = BFS(Pac-Man, vecina)).
"""
from __future__ import annotations

from collections import deque

from ..config import DELTAS
from ..dominio.mapa import Mapa

Celda = tuple[int, int]
INFINITO = float("inf")


def vecinas(mapa: Mapa, celda: Celda) -> list[Celda]:
    """vecinas(Ff, Fc): adyacentes ↑ ↓ ← → con M ∉ {1, 2} y fuera de la casa."""
    f, c = celda
    resultado = []
    for df, dc in DELTAS.values():          # orden fijo: ↑ ↓ ← →
        n = (f + df, c + dc)
        if mapa.transitable_fantasma(n):
            resultado.append(n)
    return resultado


def distancias_desde(mapa: Mapa, origen: Celda) -> dict[Celda, int]:
    """Distancia BFS desde `origen` a cada celda alcanzable por el fantasma."""
    dist = {origen: 0}
    cola = deque([origen])
    while cola:
        actual = cola.popleft()
        for n in vecinas(mapa, actual):
            if n not in dist:
                dist[n] = dist[actual] + 1
                cola.append(n)
    return dist


def bfs(mapa: Mapa, a: Celda, b: Celda) -> float:
    """BFS(a, b) tal como aparece en la notación de las reglas."""
    return distancias_desde(mapa, b).get(a, INFINITO)


def mejor_vecina(mapa: Mapa, fantasma: Celda, pacman: Celda, acercarse: bool) -> Celda | None:
    """Vecina con menor (perseguir) o mayor (huir) BFS(vecina, Pac-Man)."""
    opciones = vecinas(mapa, fantasma)
    if not opciones:
        return None
    dist = distancias_desde(mapa, pacman)
    if acercarse:
        return min(opciones, key=lambda v: dist.get(v, INFINITO))
    return max(opciones, key=lambda v: dist.get(v, -1))
