"""Pruebas de las reglas contra el análisis EEO.

Ejecutar:  python -m unittest -v
"""
import unittest

from pacman.config import (
    ASUSTADO, COMIDO, GANADO, INICIO, JUGANDO, NORMAL, PAUSA, PERDIDO, ROSA, SPAWN_PAC,
    VERDE,
)
from pacman.dominio import Estado
from pacman.ia import estrategias
from pacman.ia.bfs import bfs, distancias_desde, mejor_vecina, vecinas
from pacman.reglas import MotorReglas
from pacman.reglas import operadores as op


def jugando() -> Estado:
    e = Estado.inicial()
    op.INICIAR_JUEGO.aplicar(e)
    return e


class TablaDeEstados(unittest.TestCase):
    """Tabla 3: cada fila aplica un solo operador."""

    FILAS = [
        # operador,           EJ,      Pf, Pc, Dir, P, T, V, O,   S, Ff, Fc, E, Pts, Rec
        (None,               "inicio",  13, 9, "←", 0, 0, 3, 167, 7, 9, 8, 0, 0, 0),
        ("iniciar_juego",    "jugando", 13, 9, "←", 0, 0, 3, 167, 7, 9, 8, 0, 0, 0),
        ("mover_izquierda",  "jugando", 13, 8, "←", 0, 0, 3, 167, 7, 9, 8, 0, 0, 0),
        ("comer_orbe",       "jugando", 13, 8, "←", 0, 0, 3, 166, 7, 9, 8, 0, 20, 0),
        ("salir_casa·verde", "jugando", 13, 8, "←", 0, 0, 3, 166, 7, 9, 9, 0, 20, 0),
        ("mover_izquierda",  "jugando", 13, 7, "←", 0, 0, 3, 166, 7, 9, 9, 0, 20, 0),
        ("comer_orbe",       "jugando", 13, 7, "←", 0, 0, 3, 165, 7, 9, 9, 0, 40, 0),
        ("salir_casa·verde", "jugando", 13, 7, "←", 0, 0, 3, 165, 7, 8, 9, 0, 40, 0),
        ("mover_izquierda",  "jugando", 13, 6, "←", 0, 0, 3, 165, 7, 8, 9, 0, 40, 0),
        ("comer_orbe",       "jugando", 13, 6, "←", 0, 0, 3, 164, 7, 8, 9, 0, 60, 0),
        ("perseguir·verde",  "jugando", 13, 6, "←", 0, 0, 3, 164, 7, 7, 9, 0, 60, 0),
    ]

    def test_corrida_completa(self):
        e = Estado.inicial()
        for nombre, *esperado in self.FILAS:
            if nombre:
                self.assertTrue(op.POR_NOMBRE[nombre].aplicar(e), f"{nombre} no fue aplicable")
            self.assertEqual(e.como_tupla(), tuple(esperado), f"tras {nombre}")
        for celda in [(13, 8), (13, 7), (13, 6)]:
            self.assertEqual(e.M.valor(celda), 0)


class Operadores(unittest.TestCase):
    def test_pausar_y_reanudar_conservan_todo(self):
        e = jugando()
        antes = e.como_tupla()[1:]
        self.assertTrue(op.PAUSAR.aplicar(e))
        self.assertEqual(e.EJ, PAUSA)
        self.assertFalse(op.MOVER_IZQUIERDA.es_aplicable(e))
        self.assertTrue(op.REANUDAR.aplicar(e))
        self.assertEqual(e.EJ, JUGANDO)
        self.assertEqual(e.como_tupla()[1:], antes)

    def test_pacman_no_entra_a_paredes_ni_a_zona_casa(self):
        e = jugando()
        self.assertFalse(op.MOVER_ARRIBA.es_aplicable(e))   # (12, 9) es pared
        self.assertFalse(op.MOVER_ABAJO.es_aplicable(e))    # (14, 9) es pared
        e.pacman.Pf, e.pacman.Pc = 7, 9
        self.assertFalse(op.MOVER_ABAJO.es_aplicable(e))    # (8, 9) puerta
        e.pacman.Pf, e.pacman.Pc = 7, 1
        self.assertFalse(op.MOVER_IZQUIERDA.es_aplicable(e))  # (7, 0) túnel

    def test_comer_super_asusta_fantasma(self):
        e = jugando()
        e.pacman.Pf, e.pacman.Pc = 1, 1
        self.assertTrue(op.COMER_SUPER.aplicar(e))
        self.assertEqual((e.S, e.tablero.Pts, e.pacman.P, e.pacman.T, e.fantasma.E),
                         (6, 50, 1, 31, ASUSTADO))

    def test_comer_super_no_revive_fantasma_comido(self):
        e = jugando()
        e.fantasma.E = COMIDO
        e.pacman.Pf, e.pacman.Pc = 1, 1
        op.COMER_SUPER.aplicar(e)
        self.assertEqual(e.fantasma.E, COMIDO)

    def test_comer_fantasma(self):
        e = jugando()
        e.fantasma.E = ASUSTADO
        e.fantasma.Ff, e.fantasma.Fc = e.pacman.pos
        self.assertTrue(op.COMER_FANTASMA.aplicar(e))
        self.assertEqual((e.tablero.Pts, e.fantasma.E, e.fantasma.pos), (200, COMIDO, (9, 8)))
        self.assertFalse(op.SALIR_CASA.es_aplicable(e))     # comido no sale

    def test_perder_vida(self):
        e = jugando()
        e.pacman.Pf, e.pacman.Pc, e.pacman.Dir = 13, 4, "→"
        e.fantasma.Ff, e.fantasma.Fc = 13, 4
        self.assertTrue(op.PERDER_VIDA.aplicar(e))
        self.assertEqual((e.pacman.V, e.pacman.pos, e.pacman.Dir, e.fantasma.pos),
                         (2, (13, 9), "←", (9, 8)))

    def test_poder_reduce_termina_y_regenera(self):
        e = jugando()
        e.pacman.P, e.pacman.T, e.fantasma.E = 1, 2, ASUSTADO
        self.assertTrue(op.REDUCIR_PODER.aplicar(e))
        self.assertEqual(e.pacman.T, 1)
        self.assertFalse(op.REDUCIR_PODER.es_aplicable(e))
        self.assertTrue(op.TERMINAR_PODER.aplicar(e))
        self.assertEqual((e.pacman.P, e.pacman.T, e.fantasma.E), (0, 0, NORMAL))
        e.fantasma.E = COMIDO
        self.assertTrue(op.REGENERAR_FANTASMA.aplicar(e))
        self.assertEqual(e.fantasma.E, NORMAL)

    def test_salir_casa_ruta_fija(self):
        e = jugando()
        e.fantasma.Ff, e.fantasma.Fc = 9, 10
        op.SALIR_CASA.aplicar(e)
        self.assertEqual(e.fantasma.pos, (9, 9))
        op.SALIR_CASA.aplicar(e)
        self.assertEqual(e.fantasma.pos, (8, 9))
        self.assertFalse(op.SALIR_CASA.es_aplicable(e))

    def test_huir_maximiza_distancia_bfs(self):
        e = jugando()
        e.fantasma.Ff, e.fantasma.Fc, e.fantasma.E = 7, 9, ASUSTADO
        antes = bfs(e.M, e.fantasma.pos, e.pacman.pos)
        op.HUIR.aplicar(e)
        self.assertGreater(bfs(e.M, e.fantasma.pos, e.pacman.pos), antes)

    def test_fin_de_partida_y_record(self):
        e = jugando()
        e.O, e.S, e.tablero.Pts = 0, 0, 3690
        self.assertTrue(op.GANAR.aplicar(e))
        self.assertEqual(e.EJ, GANADO)
        self.assertTrue(op.ACTUALIZAR_RECORD.aplicar(e))
        self.assertEqual(e.tablero.Rec, 3690)
        self.assertTrue(op.REINICIAR.aplicar(e))
        self.assertEqual((e.EJ, e.tablero.Rec), (INICIO, 3690))

    def test_perder_juego(self):
        e = jugando()
        e.pacman.V = 0
        self.assertTrue(op.PERDER_JUEGO.aplicar(e))
        self.assertEqual(e.EJ, PERDIDO)

    def test_son_25_operadores(self):
        self.assertEqual(sorted({r.numero for r in op.TODAS}), list(range(1, 26)))

    def test_portal_izquierdo_y_derecho(self):
        e = jugando()
        e.pacman.Pf, e.pacman.Pc = 7, 1
        self.assertFalse(op.MOVER_IZQUIERDA.es_aplicable(e))      # el túnel sigue siendo pared
        self.assertTrue(op.CRUZAR_PORTAL_IZQUIERDA.aplicar(e))
        self.assertEqual((e.pacman.pos, e.pacman.Dir), ((7, 17), "←"))
        e.pacman.Dir = "→"
        self.assertTrue(op.CRUZAR_PORTAL_DERECHA.aplicar(e))
        self.assertEqual((e.pacman.pos, e.pacman.Dir), ((7, 1), "→"))

    def test_portal_solo_junto_al_tunel(self):
        e = jugando()
        self.assertFalse(op.CRUZAR_PORTAL_IZQUIERDA.es_aplicable(e))   # en (13, 9)

    def test_motor_cruza_portal_y_come_orbe(self):
        e = Estado.inicial()
        m = MotorReglas(e)
        m.aplicar_evidente("iniciar_juego")
        e.pacman.Pf, e.pacman.Pc = 7, 1
        nombres = [r.nombre for r in m.ejecutar_ronda("←")]
        self.assertEqual(nombres[:2], ["cruzar_portal_izquierda", "comer_orbe"])
        self.assertEqual(e.pacman.pos, (7, 17))
        self.assertEqual(e.M.valor((7, 17)), 0)


class Motor(unittest.TestCase):
    def test_orden_de_una_ronda(self):
        e = Estado.inicial()
        m = MotorReglas(e)
        m.aplicar_evidente("iniciar_juego")
        disparadas = [r.nombre for r in m.ejecutar_ronda("←")]
        self.assertEqual(disparadas, ["mover_izquierda", "comer_orbe",
                                      "salir_casa·verde", "salir_casa·rosa"])

    def test_reducir_y_terminar_no_en_la_misma_ronda(self):
        e = Estado.inicial()
        m = MotorReglas(e)
        m.aplicar_evidente("iniciar_juego")
        e.pacman.P, e.pacman.T = 1, 2
        nombres = [r.nombre for r in m.ejecutar_ronda()]
        self.assertIn("reducir_poder", nombres)
        self.assertNotIn("terminar_poder", nombres)

    def test_partida_automatica_termina(self):
        """Pac-Man quieto: el fantasma con BFS lo atrapa 3 veces → perdido."""
        e = Estado.inicial(record=0)
        m = MotorReglas(e)
        m.aplicar_evidente("iniciar_juego")
        for _ in range(500):
            if e.EJ != JUGANDO:
                break
            # forzamos a que no se mueva apuntando hacia una pared
            e.pacman.Dir = "↑"
            m.ejecutar_ronda("↑")
        self.assertEqual(e.EJ, PERDIDO)
        self.assertEqual(e.pacman.V, 0)
        self.assertEqual(e.tablero.Rec, e.tablero.Pts)

    def test_superpastilla_dura_5_segundos(self):
        from pacman.config import MS_POR_RONDA
        e = Estado.inicial()
        m = MotorReglas(e)
        m.aplicar_evidente("iniciar_juego")
        e.pacman.Pf, e.pacman.Pc, e.pacman.Dir = 1, 2, "←"
        m.ejecutar_ronda("←")                     # come la súper pastilla en (1, 1)
        self.assertEqual(e.pacman.P, 1)
        rondas = 0
        while e.pacman.P == 1:
            e.pacman.Dir = "↑"                    # quieto contra la pared
            m.ejecutar_ronda("↑")
            rondas += 1
        self.assertGreaterEqual(rondas * MS_POR_RONDA, 5000)
        self.assertLess(rondas * MS_POR_RONDA, 5000 + MS_POR_RONDA)

    def test_foto_de_la_muerte(self):
        e = Estado.inicial()
        m = MotorReglas(e)
        m.aplicar_evidente("iniciar_juego")
        e.pacman.Pf, e.pacman.Pc, e.pacman.Dir = 1, 3, "↑"    # quieto contra la pared
        v = e.fantasma_por("verde")
        v.Ff, v.Fc = 1, 3                                       # lo atrapa ahí mismo
        m.ejecutar_ronda("↑")
        self.assertIsNotNone(m.muerte)
        self.assertEqual(m.muerte.pacman, (1, 3))               # dónde murió (antes de la regla 14)
        self.assertEqual(e.pacman.pos, SPAWN_PAC)               # el estado ya reapareció
        self.assertEqual(e.pacman.V, 2)
        m.ejecutar_ronda("↑")
        self.assertIsNone(m.muerte)                             # solo dura una ronda

    def test_evidente_rechaza_ocultos(self):
        m = MotorReglas(Estado.inicial())
        with self.assertRaises(ValueError):
            m.aplicar_evidente("comer_orbe")


def colocar(e: Estado, nombre: str, celda, E=NORMAL):
    f = e.fantasma_por(nombre)
    f.Ff, f.Fc = celda
    f.E = E
    return f


class DosFantasmas(unittest.TestCase):
    def test_spawns_y_colores(self):
        e = Estado.inicial()
        self.assertEqual(e.fantasma_por(VERDE).pos, (9, 8))    # valor 4, con IA
        self.assertEqual(e.fantasma_por(ROSA).pos, (9, 10))    # valor 3, sin IA
        self.assertTrue(e.fantasma_por(VERDE).ia)
        self.assertFalse(e.fantasma_por(ROSA).ia)

    def test_super_pastilla_asusta_a_los_dos(self):
        e = jugando()
        e.pacman.Pf, e.pacman.Pc = 1, 1
        op.COMER_SUPER.aplicar(e)
        self.assertEqual([f.E for f in e.fantasmas], [ASUSTADO, ASUSTADO])

    def test_perder_vida_regresa_a_todos(self):
        e = jugando()
        colocar(e, VERDE, (3, 3))
        colocar(e, ROSA, e.pacman.pos)
        self.assertTrue(op.FANTASMA_ROSA.perder_vida.aplicar(e))
        self.assertEqual([f.pos for f in e.fantasmas], [(9, 8), (9, 10)])

    def test_rosa_no_tiene_reglas_inteligentes(self):
        nombres = [r.nombre for r in op.FANTASMA_ROSA.movimiento()]
        self.assertEqual(nombres, ["salir_casa·rosa", "deambular·rosa"])
        self.assertNotIn("perseguir_inteligente·rosa", op.POR_NOMBRE)

    def test_verde_prioriza_reglas_inteligentes(self):
        nombres = [r.nombre for r in op.FANTASMA_VERDE.movimiento()]
        self.assertEqual(nombres, ["salir_casa·verde", "perseguir_inteligente·verde",
                                   "perseguir·verde", "huir_inteligente·verde", "huir·verde"])


class ReglasInteligentes(unittest.TestCase):
    def test_prediccion_sigue_la_direccion_hasta_la_pared(self):
        m = Estado().M
        self.assertEqual(estrategias.predecir_pacman(m, (1, 1), "↓"), (3, 1))   # (4,1) es pared
        self.assertEqual(estrategias.predecir_pacman(m, (13, 9), "←"), (13, 5))

    def test_perseguir_inteligente_embosca(self):
        """Pac-Man en (1,1) bajando: el simple va por arriba hacia (1,6);
        el inteligente baja a (3,6) para cortarle el paso en (3,1)."""
        e = jugando()
        e.pacman.Pf, e.pacman.Pc, e.pacman.Dir = 1, 1, "↓"
        colocar(e, VERDE, (2, 6))
        self.assertEqual(mejor_vecina(e.M, (2, 6), (1, 1), acercarse=True), (1, 6))
        self.assertTrue(op.PERSEGUIR_INTELIGENTE.aplicar(e))
        self.assertEqual(e.fantasma.pos, (3, 6))

    def test_perseguir_inteligente_solo_lejos(self):
        e = jugando()
        e.pacman.Pf, e.pacman.Pc = 13, 6
        colocar(e, VERDE, (13, 4))                       # a 2 pasos
        self.assertFalse(op.PERSEGUIR_INTELIGENTE.es_aplicable(e))
        self.assertTrue(op.PERSEGUIR.es_aplicable(e))     # entra la regla general

    def test_huir_inteligente_evita_callejon(self):
        """Pac-Man en (1,4), verde asustado en (3,1): el simple sube a (2,1)
        (4 celdas seguras); el inteligente va a (3,2) (20 celdas seguras)."""
        e = jugando()
        e.pacman.Pf, e.pacman.Pc = 1, 4
        colocar(e, VERDE, (3, 1), ASUSTADO)
        self.assertEqual(mejor_vecina(e.M, (3, 1), (1, 4), acercarse=False), (2, 1))
        self.assertTrue(op.HUIR_INTELIGENTE.aplicar(e))
        self.assertEqual(e.fantasma.pos, (3, 2))

    def test_huir_inteligente_nunca_se_acerca_si_puede_alejarse(self):
        e = Estado()
        for p in [(1, 1), (13, 9), (7, 3), (17, 17)]:
            dp = distancias_desde(e.M, p)
            for g, d in dp.items():
                if not 0 < d <= 8:
                    continue
                elegido = estrategias.huida_por_territorio(e.M, g, p)
                if any(dp[v] > d for v in vecinas(e.M, g)):
                    self.assertGreater(dp[elegido], d, f"pac {p} fantasma {g}")

    def test_huir_inteligente_solo_cerca(self):
        e = jugando()
        colocar(e, VERDE, (1, 17), ASUSTADO)             # lejísimos de (13, 9)
        self.assertFalse(op.HUIR_INTELIGENTE.es_aplicable(e))
        self.assertTrue(op.HUIR.es_aplicable(e))

    def test_deambular_es_al_azar_y_valido(self):
        e = jugando()
        estrategias.AZAR.seed(7)
        destinos = set()
        for _ in range(30):
            colocar(e, ROSA, (7, 9))
            op.DEAMBULAR.aplicar(e)
            destinos.add(e.fantasma_por(ROSA).pos)
        self.assertEqual(destinos, {(7, 8), (7, 10), (8, 9)})   # todas sus vecinas

    def test_deambular_no_aplica_comido_ni_en_casa(self):
        e = jugando()
        colocar(e, ROSA, (7, 9), COMIDO)
        self.assertFalse(op.DEAMBULAR.es_aplicable(e))
        colocar(e, ROSA, (9, 10))
        self.assertFalse(op.DEAMBULAR.es_aplicable(e))


if __name__ == "__main__":
    unittest.main()
