"""Dibuja el Estado. Solo LEE el estado; nunca lo modifica."""
from __future__ import annotations

import math

import pygame

from ..config import (
    ASUSTADO, CASA as CELDAS_CASA, COLUMNAS, COMIDO, FILAS, GANADO, INICIO,
    ORBE, PARED, PAUSA, PERDIDO, PUERTA, SUPER_PASTILLA, TUNEL,
)
from ..dominio.entidades import Estado
from ..reglas.base import EVIDENTE
from ..reglas.motor import MotorReglas
from . import tema as t

ANCHO_TABLERO = COLUMNAS * t.CELDA
ALTO_TABLERO = FILAS * t.CELDA
ANCHO_VENTANA = ANCHO_TABLERO + t.ANCHO_PANEL
ALTO_VENTANA = ALTO_TABLERO + t.ALTO_BARRA

NOMBRES_E = {0: "normal", 1: "asustado", 2: "comido"}
ANGULO_DIR = {"→": 0, "↑": 90, "←": 180, "↓": 270}


def _fuente(tam: int, negrita: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("consolas,dejavusansmono,couriernew,monospace", tam, bold=negrita)


class Renderizador:
    def __init__(self, pantalla: pygame.Surface) -> None:
        self.pantalla = pantalla
        self.f_chica = _fuente(14)
        self.f_media = _fuente(17, True)
        self.f_grande = _fuente(44, True)
        self.f_titulo = _fuente(20, True)
        self._fondo_mapa: pygame.Surface | None = None
        self._estado_anterior: dict | None = None
        self._cambios: set[str] = set()

    # ================================================================ API
    def dibujar(self, estado: Estado, motor: MotorReglas, progreso: float,
                prev_pac: tuple[int, int], prev_fan: dict[str, tuple[int, int]], ms: int) -> None:
        self.pantalla.fill(t.FONDO)
        self._dibujar_laberinto(estado)
        self._dibujar_objetos(estado, ms)
        if estado.EJ != INICIO:
            ocupadas: set[tuple[int, int]] = set()
            for f in estado.fantasmas:
                origen = prev_fan.get(f.nombre, f.pos)
                pos = self._interpolar(origen, f.pos, progreso)
                if f.pos in ocupadas:        # dos fantasmas en la misma celda: se desplaza un poco
                    pos = (pos[0], pos[1] + 0.3)
                ocupadas.add(f.pos)
                self._dibujar_fantasma(estado, f, pos, ms)
            self._dibujar_pacman(estado, self._interpolar(prev_pac, estado.pacman.pos, progreso), ms)
        self._dibujar_panel(estado, motor)
        self._dibujar_barra(estado)
        self._dibujar_superposicion(estado)

    def marcar_cambios(self, estado: Estado) -> None:
        """Compara con la ronda anterior para resaltar variables que cambiaron."""
        actual = estado.variables()
        if self._estado_anterior is not None:
            self._cambios = {k for k, v in actual.items() if self._estado_anterior.get(k) != v}
        self._estado_anterior = actual

    # ========================================================== auxiliares
    @staticmethod
    def _interpolar(origen, destino, progreso):
        if abs(origen[0] - destino[0]) + abs(origen[1] - destino[1]) != 1:
            return destino  # teletransporte (reaparición): sin animación
        p = min(max(progreso, 0.0), 1.0)
        return (origen[0] + (destino[0] - origen[0]) * p,
                origen[1] + (destino[1] - origen[1]) * p)

    @staticmethod
    def _centro(celda) -> tuple[float, float]:
        f, c = celda
        return (c * t.CELDA + t.CELDA / 2, f * t.CELDA + t.CELDA / 2)

    # ============================================================ tablero
    def _dibujar_laberinto(self, estado: Estado) -> None:
        if self._fondo_mapa is None:
            self._fondo_mapa = self._crear_fondo(estado)
        self.pantalla.blit(self._fondo_mapa, (0, 0))

    def _crear_fondo(self, estado: Estado) -> pygame.Surface:
        sup = pygame.Surface((ANCHO_TABLERO, ALTO_TABLERO))
        sup.fill(t.FONDO)
        C = t.CELDA
        for f in range(FILAS):
            for c in range(COLUMNAS):
                v = estado.M.valor((f, c))
                r = pygame.Rect(c * C, f * C, C, C)
                if v == PARED:
                    pygame.draw.rect(sup, t.PARED, r.inflate(-2, -2), border_radius=7)
                    pygame.draw.rect(sup, t.PARED_BORDE, r.inflate(-2, -2), 2, border_radius=7)
                elif v == TUNEL:
                    pygame.draw.rect(sup, t.TUNEL, r.inflate(-2, -2), border_radius=4)
                    for i in range(0, C, 8):
                        pygame.draw.line(sup, t.PARED_BORDE, (r.x + i, r.y + 2), (r.x + i, r.bottom - 3), 1)
                elif (f, c) in CELDAS_CASA:
                    pygame.draw.rect(sup, t.CASA, r)
                elif v == PUERTA:
                    pygame.draw.rect(sup, t.CASA, r)
                    pygame.draw.rect(sup, t.PUERTA, (r.x + 2, r.centery - 3, C - 4, 6), border_radius=3)
        return sup

    def _dibujar_objetos(self, estado: Estado, ms: int) -> None:
        pulso = 0.5 + 0.5 * math.sin(ms / 160)
        for f in range(FILAS):
            for c in range(COLUMNAS):
                v = estado.M[f][c]
                if v == ORBE:
                    pygame.draw.circle(self.pantalla, t.ORBE, self._centro((f, c)), 3)
                elif v == SUPER_PASTILLA:
                    radio = 6 + 3 * pulso
                    pygame.draw.circle(self.pantalla, t.SUPER, self._centro((f, c)), radio)

    def _dibujar_pacman(self, estado: Estado, pos, ms: int) -> None:
        cx, cy = self._centro(pos)
        radio = t.CELDA * 0.43
        apertura = 8 + 34 * abs(math.sin(ms / 90)) if estado.EJ == "jugando" else 30
        base = ANGULO_DIR[estado.pacman.Dir]
        puntos = [(cx, cy)]
        for i in range(31):
            a = math.radians(base + apertura + (360 - 2 * apertura) * i / 30)
            puntos.append((cx + radio * math.cos(a), cy - radio * math.sin(a)))
        color = t.PACMAN
        if estado.pacman.P == 1:  # halo de poder
            pygame.draw.circle(self.pantalla, t.SUPER, (cx, cy), radio + 3, 2)
        pygame.draw.polygon(self.pantalla, color, puntos)

    def _dibujar_fantasma(self, estado: Estado, fantasma, pos, ms: int) -> None:
        cx, cy = self._centro(pos)
        E = fantasma.E
        w = t.CELDA * 0.84
        h = t.CELDA * 0.84
        x0, y0 = cx - w / 2, cy - h / 2
        if E != COMIDO:
            if E == ASUSTADO:
                # parpadea en el último segundo y medio de poder
                parpadeo = estado.pacman.T * t.MS_POR_RONDA <= 1500 and (ms // 180) % 2 == 0
                color = t.FANTASMA_PARPADEO if parpadeo else t.FANTASMA_ASUSTADO
            else:
                color = t.FANTASMA_VERDE if fantasma.ia else t.FANTASMA_ROSA
            pygame.draw.circle(self.pantalla, color, (cx, y0 + w / 2), w / 2)
            pygame.draw.rect(self.pantalla, color, (x0, y0 + w / 2, w, h / 2 - 3))
            ondas = 4
            fase = (ms // 140) % 2
            for i in range(ondas):
                px = x0 + i * w / ondas
                py = y0 + h - 3 - (3 if (i + fase) % 2 else 0)
                pygame.draw.polygon(self.pantalla, color,
                                    [(px, y0 + h - 4), (px + w / ondas, y0 + h - 4), (px + w / (2 * ondas), py + 4)])
        # ojos (lo único visible cuando está comido)
        if E == ASUSTADO:
            for dx in (-5, 5):
                pygame.draw.circle(self.pantalla, t.OJOS, (cx + dx, cy - 3), 2)
            return
        mirar = self._mirada(estado, fantasma)
        for dx in (-5, 5):
            pygame.draw.circle(self.pantalla, t.OJOS, (cx + dx, cy - 3), 4)
            pygame.draw.circle(self.pantalla, t.PUPILA, (cx + dx + mirar[0] * 2, cy - 3 + mirar[1] * 2), 2)

    @staticmethod
    def _mirada(estado: Estado, fantasma) -> tuple[int, int]:
        if not fantasma.ia:
            return (0, 0)              # el rosa no mira a Pac-Man
        df = estado.pacman.Pf - fantasma.Ff
        dc = estado.pacman.Pc - fantasma.Fc
        return ((dc > 0) - (dc < 0), (df > 0) - (df < 0))

    # ============================================================== panel
    def _dibujar_panel(self, estado: Estado, motor: MotorReglas) -> None:
        x0 = ANCHO_TABLERO
        pygame.draw.rect(self.pantalla, t.PANEL, (x0, 0, t.ANCHO_PANEL, ALTO_VENTANA))
        pygame.draw.line(self.pantalla, t.ACENTO, (x0, 0), (x0, ALTO_VENTANA), 2)
        x = x0 + 16
        y = 12
        self._texto("ESTADO", (x, y), self.f_titulo, t.ACENTO)
        y += 28
        variables = list(estado.variables().items())
        por_columna = (len(variables) + 1) // 2
        for i, (nombre, valor) in enumerate(variables):
            col, fila = divmod(i, por_columna)
            px = x + col * 168
            py = y + fila * 21
            if nombre.startswith("E") and nombre != "EJ":
                valor = f"{valor} {NOMBRES_E[valor]}"
            color = t.CAMBIO if nombre in self._cambios else t.TEXTO
            etiqueta = {"Ffv": t.FANTASMA_VERDE, "Fcv": t.FANTASMA_VERDE, "Ev": t.FANTASMA_VERDE,
                        "Ffr": t.FANTASMA_ROSA, "Fcr": t.FANTASMA_ROSA, "Er": t.FANTASMA_ROSA,
                        }.get(nombre, t.TEXTO_TENUE)
            self._texto(f"{nombre:<4}", (px, py), self.f_chica, etiqueta)
            self._texto(str(valor), (px + 40, py), self.f_chica, color)
        y += por_columna * 21 + 14

        self._texto("ÚLTIMA RONDA", (x, y), self.f_titulo, t.ACENTO)
        self._texto(f"#{motor.ronda}", (x + 250, y + 3), self.f_chica, t.TEXTO_TENUE)
        y += 28
        if not motor.ultimos:
            self._texto("—", (x, y), self.f_chica, t.TEXTO_TENUE)
            y += 19
        for regla in motor.ultimos[:9]:
            color = t.EVIDENTE if regla.tipo == EVIDENTE else t.OCULTO
            self._texto(f"{regla.numero:>2}. {regla.nombre}", (x, y), self.f_chica, color)
            y += 19
        y = max(y, 450) + 6

        self._texto("TRAZA DEL MOTOR", (x, y), self.f_titulo, t.ACENTO)
        y += 28
        espacio = (ALTO_VENTANA - 16 - y) // 18
        recientes = [d for d in motor.traza if not d.regla.nombre.startswith("mover_")][-espacio:]
        for d in recientes:
            color = t.EVIDENTE if d.regla.tipo == EVIDENTE else t.OCULTO
            self._texto(f"r{d.ronda:<4}", (x, y), self.f_chica, t.TEXTO_TENUE)
            self._texto(d.regla.nombre, (x + 56, y), self.f_chica, color)
            y += 18

    def _dibujar_barra(self, estado: Estado) -> None:
        y = ALTO_TABLERO
        pygame.draw.rect(self.pantalla, t.PANEL, (0, y, ANCHO_TABLERO, t.ALTO_BARRA))
        vidas = "● " * estado.pacman.V
        self._texto(f"Pts {estado.tablero.Pts}", (12, y + 8), self.f_media, t.TEXTO)
        self._texto(f"Rec {estado.tablero.Rec}", (120, y + 8), self.f_media, t.TEXTO_TENUE)
        self._texto(vidas, (230, y + 8), self.f_media, t.PACMAN)
        ayuda = self.f_chica.render("Flechas/WASD · P pausa · Enter", True, t.TEXTO_TENUE)
        self.pantalla.blit(ayuda, (ANCHO_TABLERO - ayuda.get_width() - 12, y + 10))

    def _dibujar_superposicion(self, estado: Estado) -> None:
        mensajes = {
            INICIO: ("PAC-MAN EEO", "Enter: iniciar_juego", t.PACMAN),
            PAUSA: ("PAUSA", "P / Enter: reanudar", t.ACENTO),
            GANADO: ("¡GANASTE!", "Enter: reiniciar", t.ACENTO),
            PERDIDO: ("GAME OVER", "Enter: reiniciar", t.FANTASMA_ROSA),
        }
        if estado.EJ not in mensajes:
            return
        titulo, sub, color = mensajes[estado.EJ]
        velo = pygame.Surface((ANCHO_TABLERO, ALTO_TABLERO), pygame.SRCALPHA)
        velo.fill((5, 6, 14, 170))
        self.pantalla.blit(velo, (0, 0))
        cx = ANCHO_TABLERO // 2
        self._texto(titulo, (cx, ALTO_TABLERO // 2 - 40), self.f_grande, color, centrado=True)
        self._texto(sub, (cx, ALTO_TABLERO // 2 + 18), self.f_media, t.TEXTO, centrado=True)
        if estado.EJ in (GANADO, PERDIDO):
            self._texto(f"Pts {estado.tablero.Pts}  ·  Rec {estado.tablero.Rec}",
                        (cx, ALTO_TABLERO // 2 + 50), self.f_media, t.TEXTO_TENUE, centrado=True)
        if estado.EJ == INICIO:
            self._texto("Equipo 4 · Análisis EEO · IA", (cx, ALTO_TABLERO // 2 + 50),
                        self.f_chica, t.TEXTO_TENUE, centrado=True)

    def _texto(self, texto: str, pos, fuente, color, centrado: bool = False) -> None:
        sup = fuente.render(texto, True, color)
        if centrado:
            pos = (pos[0] - sup.get_width() // 2, pos[1] - sup.get_height() // 2)
        self.pantalla.blit(sup, pos)
