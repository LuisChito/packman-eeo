"""Tabla 2 · Operadores del análisis EEO (1–21) + reglas nuevas (22–24).

Cada operador se define con dos funciones sobre el `Estado`:
  - condición: las condiciones de aplicabilidad (lado "Si ...").
  - acción: el nuevo estado (lado "entonces ...").
Las variables que la regla dice "se conservan" simplemente no se tocan.

Con dos fantasmas, las reglas que hablan de "el fantasma" (10–14, 17 y
22–24) son reglas PARAMETRIZADAS: se crea una copia por fantasma, por
ejemplo `salir_casa·verde` y `salir_casa·rosa`. Cada copia solo lee y
escribe las variables (Ff, Fc, E) de su fantasma.

    Fantasma VERDE (con IA):  salir_casa, perseguir_inteligente (22),
                              perseguir (11), huir_inteligente (23), huir (12)
    Fantasma ROSA  (sin IA):  salir_casa, deambular (24)
"""
from __future__ import annotations

from ..config import (
    ABAJO, ARRIBA, ASUSTADO, BLOQUEADAS, CASA, COMIDO, DELTAS, DERECHA, GANADO,
    INICIO, IZQUIERDA, JUGANDO, NORMAL, ORBE, ORBES_INICIALES, PASILLO, PAUSA,
    PERDIDO, PTS_FANTASMA, PTS_ORBE, PTS_SUPER, RADIO_PELIGRO, ROSA, RUTA_SALIDA,
    SPAWN_PAC, SUPER_INICIALES, SUPER_PASTILLA, TIEMPO_PODER, UMBRAL_EMBOSCADA,
    VERDE, VIDAS_INICIALES, ZONA_CASA,
)
from ..dominio.entidades import Estado, Fantasma
from ..dominio.mapa import Mapa
from ..ia.bfs import bfs, mejor_vecina
from ..ia.estrategias import emboscada, huida_por_territorio, paso_al_azar
from .base import EVIDENTE, OCULTO, Regla


def _jugando(e: Estado) -> bool:
    return e.EJ == JUGANDO


def _reaparecer_pacman(e: Estado) -> None:
    e.pacman.Pf, e.pacman.Pc = SPAWN_PAC
    e.pacman.Dir = IZQUIERDA
    e.pacman.P = 0
    e.pacman.T = 0


def _mover(f: Fantasma, destino) -> None:
    if destino:
        f.Ff, f.Fc = destino


# ======================================================================
#  Reglas globales (no dependen de un fantasma en particular)
# ======================================================================

# ---------------------------------------------------------------- 1 iniciar
def _c_iniciar(e: Estado) -> bool:
    return e.EJ == INICIO


def _a_iniciar(e: Estado) -> None:
    e.EJ = JUGANDO
    e.M = Mapa.inicial()
    _reaparecer_pacman(e)
    e.pacman.V = VIDAS_INICIALES
    e.O = ORBES_INICIALES
    e.S = SUPER_INICIALES
    for f in e.fantasmas:
        f.reaparecer()
        f.E = NORMAL
    e.tablero.Pts = 0


# ----------------------------------------------------- 2 pausar / 3 reanudar
def _a_pausar(e: Estado) -> None:
    e.EJ = PAUSA


def _c_reanudar(e: Estado) -> bool:
    return e.EJ == PAUSA


def _a_reanudar(e: Estado) -> None:
    e.EJ = JUGANDO


# ------------------------------------------------------- 4-7 movimientos
def _movimiento(direccion: str):
    df, dc = DELTAS[direccion]

    def condicion(e: Estado) -> bool:
        destino = (e.pacman.Pf + df, e.pacman.Pc + dc)
        return (_jugando(e)
                and e.M.dentro(destino)
                and e.M.valor(destino) not in BLOQUEADAS   # M[..] ∉ {1, 2}
                and destino not in ZONA_CASA)              # (..) ∉ zona_casa

    def accion(e: Estado) -> None:
        e.pacman.Pf += df
        e.pacman.Pc += dc
        e.pacman.Dir = direccion

    return condicion, accion


_c_arriba, _a_arriba = _movimiento(ARRIBA)
_c_abajo, _a_abajo = _movimiento(ABAJO)
_c_izquierda, _a_izquierda = _movimiento(IZQUIERDA)
_c_derecha, _a_derecha = _movimiento(DERECHA)


# --------------------------------------------------------- 8 comer orbe
def _c_comer_orbe(e: Estado) -> bool:
    return _jugando(e) and e.M[e.pacman.Pf][e.pacman.Pc] == ORBE


def _a_comer_orbe(e: Estado) -> None:
    e.M[e.pacman.Pf][e.pacman.Pc] = PASILLO
    e.O -= 1
    e.tablero.Pts += PTS_ORBE


# ------------------------------------------------- 9 comer súper pastilla
def _c_comer_super(e: Estado) -> bool:
    return _jugando(e) and e.M[e.pacman.Pf][e.pacman.Pc] == SUPER_PASTILLA


def _a_comer_super(e: Estado) -> None:
    e.M[e.pacman.Pf][e.pacman.Pc] = PASILLO
    e.S -= 1
    e.tablero.Pts += PTS_SUPER
    e.pacman.P = 1
    e.pacman.T = TIEMPO_PODER
    for f in e.fantasmas:            # si E ≠ 2 entonces E = 1 (cada fantasma)
        if f.E != COMIDO:
            f.E = ASUSTADO


# -------------------------------------- 15 reducir / 16 terminar poder
def _c_reducir_poder(e: Estado) -> bool:
    return _jugando(e) and e.pacman.P == 1 and e.pacman.T > 1


def _a_reducir_poder(e: Estado) -> None:
    e.pacman.T -= 1


def _c_terminar_poder(e: Estado) -> bool:
    return _jugando(e) and e.pacman.P == 1 and e.pacman.T == 1


def _a_terminar_poder(e: Estado) -> None:
    e.pacman.P = 0
    e.pacman.T = 0
    for f in e.fantasmas:            # si E = 1 entonces E = 0 (cada fantasma)
        if f.E == ASUSTADO:
            f.E = NORMAL


# --------------------------------------------- 18 ganar / 19 perder juego
def _c_ganar(e: Estado) -> bool:
    return _jugando(e) and e.O == 0 and e.S == 0


def _a_ganar(e: Estado) -> None:
    e.EJ = GANADO


def _c_perder_juego(e: Estado) -> bool:
    return _jugando(e) and e.pacman.V == 0


def _a_perder_juego(e: Estado) -> None:
    e.EJ = PERDIDO


# ------------------------------------- 20 actualizar récord / 21 reiniciar
def _terminada(e: Estado) -> bool:
    return e.EJ in (GANADO, PERDIDO)


def _c_actualizar_record(e: Estado) -> bool:
    return _terminada(e) and e.tablero.Pts > e.tablero.Rec


def _a_actualizar_record(e: Estado) -> None:
    e.tablero.Rec = e.tablero.Pts


def _a_reiniciar(e: Estado) -> None:
    e.EJ = INICIO


# ======================================================================
#  Reglas parametrizadas por fantasma
# ======================================================================
class ReglasFantasma:
    """Crea las reglas 10–14, 17 y 22–24 ligadas a UN fantasma."""

    def __init__(self, nombre: str) -> None:
        self.nombre = nombre
        f = lambda e: e.fantasma_por(nombre)   # noqa: E731  (su Ff, Fc, E)
        sufijo = f"·{nombre}"

        def fuera_de_casa(e: Estado) -> bool:
            return f(e).pos not in CASA

        def distancia(e: Estado) -> float:
            return bfs(e.M, f(e).pos, e.pacman.pos)

        # ---------------------------------------------- 10 salir de casa
        def c_salir(e):
            return _jugando(e) and f(e).pos in CASA and f(e).E != COMIDO

        def a_salir(e):
            _mover(f(e), RUTA_SALIDA[f(e).pos])

        # ------------------------------------------------- 11 perseguir
        def c_perseguir(e):
            return _jugando(e) and f(e).E == NORMAL and fuera_de_casa(e)

        def a_perseguir(e):
            _mover(f(e), mejor_vecina(e.M, f(e).pos, e.pacman.pos, acercarse=True))

        # ------------------------------------------------------ 12 huir
        def c_huir(e):
            return _jugando(e) and f(e).E == ASUSTADO and fuera_de_casa(e)

        def a_huir(e):
            _mover(f(e), mejor_vecina(e.M, f(e).pos, e.pacman.pos, acercarse=False))

        # ------------------------------------------- 13 comer fantasma
        def c_comer(e):
            return _jugando(e) and e.pacman.pos == f(e).pos and f(e).E == ASUSTADO

        def a_comer(e):
            e.tablero.Pts += PTS_FANTASMA
            f(e).E = COMIDO
            f(e).reaparecer()

        # ---------------------------------------------- 14 perder vida
        def c_perder(e):
            return _jugando(e) and e.pacman.pos == f(e).pos and f(e).E == NORMAL

        def a_perder(e):
            e.pacman.V -= 1
            _reaparecer_pacman(e)
            for otro in e.fantasmas:      # todos regresan a su spawn
                otro.reaparecer()

        # --------------------------------------- 17 regenerar fantasma
        def c_regenerar(e):
            return _jugando(e) and f(e).E == COMIDO and e.pacman.P == 0

        def a_regenerar(e):
            f(e).E = NORMAL

        # ------------------------------- 22 perseguir inteligente (IA)
        def c_perseguir_int(e):
            return c_perseguir(e) and distancia(e) > UMBRAL_EMBOSCADA

        def a_perseguir_int(e):
            _mover(f(e), emboscada(e.M, f(e).pos, e.pacman.pos, e.pacman.Dir))

        # ----------------------------------- 23 huir inteligente (IA)
        def c_huir_int(e):
            return c_huir(e) and distancia(e) <= RADIO_PELIGRO

        def a_huir_int(e):
            _mover(f(e), huida_por_territorio(e.M, f(e).pos, e.pacman.pos))

        # ------------------------------------- 24 deambular (sin IA)
        def c_deambular(e):
            return _jugando(e) and f(e).E != COMIDO and fuera_de_casa(e)

        def a_deambular(e):
            _mover(f(e), paso_al_azar(e.M, f(e).pos))

        F = "(Ff, Fc, E)" + sufijo
        self.salir_casa = Regla(10, "salir_casa" + sufijo, OCULTO, c_salir, a_salir,
            f"Si EJ = jugando y (Ff, Fc) ∈ casa y E ≠ 2 entonces (Ff, Fc) = siguiente(Ff, Fc)   [{F}]")
        self.perseguir = Regla(11, "perseguir" + sufijo, OCULTO, c_perseguir, a_perseguir,
            "Si EJ = jugando y E = 0 y (Ff, Fc) ∉ casa entonces (Ff, Fc) = vecina con menor BFS(vecina, (Pf, Pc))")
        self.huir = Regla(12, "huir" + sufijo, OCULTO, c_huir, a_huir,
            "Si EJ = jugando y E = 1 y (Ff, Fc) ∉ casa entonces (Ff, Fc) = vecina con mayor BFS(vecina, (Pf, Pc))")
        self.comer_fantasma = Regla(13, "comer_fantasma" + sufijo, OCULTO, c_comer, a_comer,
            "Si EJ = jugando y (Pf, Pc) = (Ff, Fc) y E = 1 entonces Pts = Pts+200, E = 2, (Ff, Fc) = spawn")
        self.perder_vida = Regla(14, "perder_vida" + sufijo, OCULTO, c_perder, a_perder,
            "Si EJ = jugando y (Pf, Pc) = (Ff, Fc) y E = 0 entonces V = V−1, (Pf, Pc) = (13, 9), "
            "Dir = ←, P = 0, T = 0, todos los fantasmas a su spawn")
        self.regenerar = Regla(17, "regenerar_fantasma" + sufijo, OCULTO, c_regenerar, a_regenerar,
            "Si EJ = jugando y E = 2 y P = 0 entonces E = 0")
        self.perseguir_inteligente = Regla(22, "perseguir_inteligente" + sufijo, OCULTO,
            c_perseguir_int, a_perseguir_int,
            "Si EJ = jugando y E = 0 y (Ff, Fc) ∉ casa y BFS((Ff, Fc), (Pf, Pc)) > 4 entonces "
            "(Ff, Fc) = vecina con menor BFS(vecina, predicción(Pf, Pc, Dir, 4))")
        self.huir_inteligente = Regla(23, "huir_inteligente" + sufijo, OCULTO,
            c_huir_int, a_huir_int,
            "Si EJ = jugando y E = 1 y (Ff, Fc) ∉ casa y BFS((Ff, Fc), (Pf, Pc)) ≤ 8 entonces "
            "(Ff, Fc) = vecina con mayor territorio(vecina) (celdas a las que llega antes que Pac-Man)")
        self.deambular = Regla(24, "deambular" + sufijo, OCULTO, c_deambular, a_deambular,
            "Si EJ = jugando y E ≠ 2 y (Ff, Fc) ∉ casa entonces (Ff, Fc) = vecina al azar")

    # Grupo de conflicto del movimiento: orden = prioridad (la regla más
    # específica va primero; si no aplica, se prueba la siguiente).
    def movimiento(self) -> tuple[Regla, ...]:
        if self.nombre == VERDE:
            return (self.salir_casa, self.perseguir_inteligente, self.perseguir,
                    self.huir_inteligente, self.huir)
        return (self.salir_casa, self.deambular)

    def colision(self) -> tuple[Regla, ...]:
        return (self.comer_fantasma, self.perder_vida)

    def todas(self) -> tuple[Regla, ...]:
        return (*self.movimiento(), *self.colision(), self.regenerar)


# =================================================================== Tabla 2
INICIAR_JUEGO = Regla(1, "iniciar_juego", EVIDENTE, _c_iniciar, _a_iniciar,
    "Si EJ = inicio entonces EJ = jugando, M = mapa inicial, (Pf, Pc) = (13, 9), "
    "Dir = ←, P = 0, T = 0, V = 3, O = 167, S = 7, fantasmas en su spawn con E = 0, Pts = 0")
PAUSAR = Regla(2, "pausar", EVIDENTE, _jugando, _a_pausar,
    "Si EJ = jugando entonces EJ = pausa (el resto se conserva)")
REANUDAR = Regla(3, "reanudar", EVIDENTE, _c_reanudar, _a_reanudar,
    "Si EJ = pausa entonces EJ = jugando (el resto se conserva)")
MOVER_ARRIBA = Regla(4, "mover_arriba", EVIDENTE, _c_arriba, _a_arriba,
    "Si EJ = jugando y M[Pf−1][Pc] ∉ {1,2} y (Pf−1, Pc) ∉ zona_casa entonces Pf = Pf−1, Dir = ↑")
MOVER_ABAJO = Regla(5, "mover_abajo", EVIDENTE, _c_abajo, _a_abajo,
    "Si EJ = jugando y M[Pf+1][Pc] ∉ {1,2} y (Pf+1, Pc) ∉ zona_casa entonces Pf = Pf+1, Dir = ↓")
MOVER_IZQUIERDA = Regla(6, "mover_izquierda", EVIDENTE, _c_izquierda, _a_izquierda,
    "Si EJ = jugando y M[Pf][Pc−1] ∉ {1,2} y (Pf, Pc−1) ∉ zona_casa entonces Pc = Pc−1, Dir = ←")
MOVER_DERECHA = Regla(7, "mover_derecha", EVIDENTE, _c_derecha, _a_derecha,
    "Si EJ = jugando y M[Pf][Pc+1] ∉ {1,2} y (Pf, Pc+1) ∉ zona_casa entonces Pc = Pc+1, Dir = →")
COMER_ORBE = Regla(8, "comer_orbe", OCULTO, _c_comer_orbe, _a_comer_orbe,
    "Si EJ = jugando y M[Pf][Pc] = 6 entonces M[Pf][Pc] = 0, O = O−1, Pts = Pts+20")
COMER_SUPER = Regla(9, "comer_super", OCULTO, _c_comer_super, _a_comer_super,
    "Si EJ = jugando y M[Pf][Pc] = 7 entonces M[Pf][Pc] = 0, S = S−1, Pts = Pts+50, "
    "P = 1, T = 8; para cada fantasma: si E ≠ 2 entonces E = 1")
REDUCIR_PODER = Regla(15, "reducir_poder", OCULTO, _c_reducir_poder, _a_reducir_poder,
    "Si EJ = jugando y P = 1 y T > 1 entonces T = T−1")
TERMINAR_PODER = Regla(16, "terminar_poder", OCULTO, _c_terminar_poder, _a_terminar_poder,
    "Si EJ = jugando y P = 1 y T = 1 entonces P = 0, T = 0; para cada fantasma: si E = 1 entonces E = 0")
GANAR = Regla(18, "ganar", OCULTO, _c_ganar, _a_ganar,
    "Si EJ = jugando y O = 0 y S = 0 entonces EJ = ganado (el resto se conserva)")
PERDER_JUEGO = Regla(19, "perder_juego", OCULTO, _c_perder_juego, _a_perder_juego,
    "Si EJ = jugando y V = 0 entonces EJ = perdido (el resto se conserva)")
ACTUALIZAR_RECORD = Regla(20, "actualizar_record", OCULTO, _c_actualizar_record, _a_actualizar_record,
    "Si (EJ = ganado o EJ = perdido) y Pts > Rec entonces Rec = Pts")
REINICIAR = Regla(21, "reiniciar", EVIDENTE, _terminada, _a_reiniciar,
    "Si EJ = ganado o EJ = perdido entonces EJ = inicio")

# Reglas de cada fantasma
FANTASMA_VERDE = ReglasFantasma(VERDE)
FANTASMA_ROSA = ReglasFantasma(ROSA)
POR_FANTASMA: dict[str, ReglasFantasma] = {VERDE: FANTASMA_VERDE, ROSA: FANTASMA_ROSA}

# Atajos con el nombre original del documento (el fantasma con IA = verde)
SALIR_CASA = FANTASMA_VERDE.salir_casa
PERSEGUIR = FANTASMA_VERDE.perseguir
HUIR = FANTASMA_VERDE.huir
COMER_FANTASMA = FANTASMA_VERDE.comer_fantasma
PERDER_VIDA = FANTASMA_VERDE.perder_vida
REGENERAR_FANTASMA = FANTASMA_VERDE.regenerar
PERSEGUIR_INTELIGENTE = FANTASMA_VERDE.perseguir_inteligente
HUIR_INTELIGENTE = FANTASMA_VERDE.huir_inteligente
DEAMBULAR = FANTASMA_ROSA.deambular

GLOBALES: tuple[Regla, ...] = (
    INICIAR_JUEGO, PAUSAR, REANUDAR, MOVER_ARRIBA, MOVER_ABAJO, MOVER_IZQUIERDA,
    MOVER_DERECHA, COMER_ORBE, COMER_SUPER, REDUCIR_PODER, TERMINAR_PODER,
    GANAR, PERDER_JUEGO, ACTUALIZAR_RECORD, REINICIAR,
)

TODAS: tuple[Regla, ...] = tuple(sorted(
    (*GLOBALES, *FANTASMA_VERDE.todas(), *FANTASMA_ROSA.todas()),
    key=lambda r: (r.numero, r.nombre),
))

POR_NOMBRE: dict[str, Regla] = {r.nombre: r for r in TODAS}

MOVIMIENTOS: dict[str, Regla] = {
    ARRIBA: MOVER_ARRIBA,
    ABAJO: MOVER_ABAJO,
    IZQUIERDA: MOVER_IZQUIERDA,
    DERECHA: MOVER_DERECHA,
}
