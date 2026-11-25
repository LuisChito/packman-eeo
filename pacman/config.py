"""Constantes del análisis EEO (Tabla 1 y notación de las reglas).

Todo valor "mágico" del juego vive aquí para que las reglas, las entidades
y la interfaz hablen exactamente el mismo idioma que el documento.
"""

# --- Valores de la matriz -------------------------------------------------
PASILLO = 0
PARED = 1
TUNEL = 2              # se trata como pared
SPAWN_FANTASMA_SIN_IA = 3
SPAWN_FANTASMA_IA = 4
SPAWN_PACMAN = 5
ORBE = 6
SUPER_PASTILLA = 7
PUERTA = 8

BLOQUEADAS = frozenset({PARED, TUNEL})   # M ∈ {1, 2}

# --- Tablero --------------------------------------------------------------
FILAS = 19
COLUMNAS = 19

# --- Zonas especiales (notación de las reglas) ----------------------------
CASA = frozenset({(9, 8), (9, 9), (9, 10)})
PUERTA_CASA = (8, 9)
ZONA_CASA = CASA | {PUERTA_CASA}        # Pac-Man no puede pisarla

# Portales: al intentar entrar a la celda túnel (valor 2), Pac-Man aparece
# en la celda de pasillo del otro lado. Nunca se queda sobre el túnel.
PORTALES = {
    (7, 0): (7, 17),    # entra por la izquierda -> sale por la derecha
    (7, 18): (7, 1),    # entra por la derecha  -> sale por la izquierda
}

# Ruta fija de salida: siguiente(Ff, Fc)
RUTA_SALIDA = {
    (9, 8): (9, 9),
    (9, 10): (9, 9),
    (9, 9): (8, 9),
}

# --- Spawns ---------------------------------------------------------------
SPAWN_PAC = (13, 9)
SPAWN_FANTASMA = (9, 8)    # fantasma con IA (valor 4) -> fantasma VERDE
SPAWN_FANTASMA_SIN_IA_POS = (9, 10)   # fantasma sin IA (valor 3) -> fantasma ROSA

VERDE = "verde"
ROSA = "rosa"

# --- Parámetros de las reglas inteligentes (fantasma verde) ---------------
UMBRAL_EMBOSCADA = 4       # si BFS(fantasma, Pac-Man) > 4 -> perseguir_inteligente
PASOS_PREDICCION = 4       # cuántas celdas adelante predice a Pac-Man
RADIO_PELIGRO = 8          # si BFS(fantasma, Pac-Man) <= 8 -> huir_inteligente

# --- Valores iniciales / límites ------------------------------------------
VIDAS_INICIALES = 3
# --- Tiempo ---------------------------------------------------------------
# Las reglas cuentan RONDAS (un paso de cada personaje). Una ronda dura:
MS_POR_RONDA = 170

# La súper pastilla dura 5 segundos. En la misma ronda en que se come,
# la fase 4 ya aplica reducir_poder una vez; por eso se suma 1:
#   rondas con poder = TIEMPO_PODER − 1 = ceil(5000 / 170) = 30  ->  30 × 170 ms = 5.1 s
DURACION_PODER_MS = 5000
TIEMPO_PODER = -(-DURACION_PODER_MS // MS_POR_RONDA) + 1      # T = 31 al comer súper pastilla
ORBES_INICIALES = 167
SUPER_INICIALES = 7

# --- Puntuación -----------------------------------------------------------
PTS_ORBE = 20
PTS_SUPER = 50
PTS_FANTASMA = 200

# --- Direcciones (Dir) ----------------------------------------------------
ARRIBA = "↑"
ABAJO = "↓"
IZQUIERDA = "←"
DERECHA = "→"

DELTAS = {
    ARRIBA: (-1, 0),
    ABAJO: (1, 0),
    IZQUIERDA: (0, -1),
    DERECHA: (0, 1),
}

# --- Estados del juego (EJ) -----------------------------------------------
INICIO = "inicio"
JUGANDO = "jugando"
PAUSA = "pausa"
GANADO = "ganado"
PERDIDO = "perdido"

# --- Estados del fantasma (E) ---------------------------------------------
NORMAL = 0
ASUSTADO = 1
COMIDO = 2
