"""Bucle principal: une teclado → motor de reglas → renderizador."""
from __future__ import annotations

import pygame

from ..config import JUGANDO
from ..dominio.entidades import Estado
from ..infraestructura.persistencia import cargar_record, guardar_record
from ..reglas.motor import MotorReglas
from . import tema
from .controles import direccion_de, operador_de
from .render import ALTO_VENTANA, ANCHO_VENTANA, Renderizador


class Aplicacion:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pac-Man EEO · Equipo 4")
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        self.reloj = pygame.time.Clock()
        self.estado = Estado.inicial(record=cargar_record())
        self.motor = MotorReglas(self.estado)
        self.render = Renderizador(self.pantalla)
        self.direccion_deseada: str | None = None
        self.acumulado = 0
        self.prev_pac = self.estado.pacman.pos
        self.prev_fan = {f.nombre: f.pos for f in self.estado.fantasmas}
        # Animación de muerte: (foto del motor, ms transcurridos) o None
        self.muerte = None
        self.ms_muerte = 0

    def ejecutar(self) -> None:
        corriendo = True
        while corriendo:
            dt = self.reloj.tick(tema.FPS)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False
                elif evento.type == pygame.KEYDOWN:
                    self._tecla(evento.key)

            if self.muerte is not None:
                # Las rondas se congelan ~2 s mientras se anima la muerte
                self.ms_muerte += dt
                if self.ms_muerte >= tema.PAUSA_MUERTE_MS or (
                        self.estado.EJ != JUGANDO and self.ms_muerte >= tema.MUERTE_MS):
                    self._terminar_muerte()
            elif self.estado.EJ == JUGANDO:
                self.acumulado += dt
                while self.acumulado >= tema.MS_POR_RONDA and self.muerte is None:
                    self.acumulado -= tema.MS_POR_RONDA
                    self._ronda()

            animando = self.muerte is not None
            progreso = self.acumulado / tema.MS_POR_RONDA if self.estado.EJ == JUGANDO and not animando else 1.0
            self.render.dibujar(self.estado, self.motor, progreso,
                                self.prev_pac, self.prev_fan, pygame.time.get_ticks(),
                                (self.muerte, self.ms_muerte) if animando else None)
            pygame.display.flip()
        pygame.quit()

    def _ronda(self) -> None:
        self.prev_pac = self.estado.pacman.pos
        self.prev_fan = {f.nombre: f.pos for f in self.estado.fantasmas}
        rec_antes = self.estado.tablero.Rec
        self.motor.ejecutar_ronda(self.direccion_deseada)
        self.render.marcar_cambios(self.estado)
        if self.estado.tablero.Rec != rec_antes:
            guardar_record(self.estado.tablero.Rec)
        if self.motor.muerte is not None:
            self.muerte = self.motor.muerte
            self.ms_muerte = 0
            self.acumulado = 0

    def _terminar_muerte(self) -> None:
        self.muerte = None
        self.acumulado = 0
        self.prev_pac = self.estado.pacman.pos
        self.prev_fan = {f.nombre: f.pos for f in self.estado.fantasmas}

    def _tecla(self, tecla: int) -> None:
        direccion = direccion_de(tecla)
        if direccion:
            self.direccion_deseada = direccion
            return
        if self.muerte is not None:
            return                      # durante la animación no se pausa ni reinicia
        nombre = operador_de(tecla, self.estado.EJ)
        if nombre and self.motor.aplicar_evidente(nombre):
            if nombre == "iniciar_juego":
                self.direccion_deseada = None
                self.acumulado = 0
                self.prev_pac = self.estado.pacman.pos
                self.prev_fan = {f.nombre: f.pos for f in self.estado.fantasmas}
            self.render.marcar_cambios(self.estado)
