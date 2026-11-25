"""Parámetros visuales y de ritmo. Cambiarlos no altera ninguna regla."""

CELDA = 32                    # píxeles por celda
ANCHO_PANEL = 360
ALTO_BARRA = 34
from ..config import MS_POR_RONDA  # noqa: E402,F401  (duración de una ronda; vive en config)
FPS = 60

# Animación al perder una vida (las rondas se congelan mientras dura)
MUERTE_MS = 1200              # Pac-Man se desvanece donde lo atraparon
REAPARICION_MS = 800          # Pac-Man y fantasmas aparecen en su spawn
PAUSA_MUERTE_MS = MUERTE_MS + REAPARICION_MS   # ≈ 2 s en total

# Paleta
FONDO = (10, 12, 24)
PARED = (14, 22, 70)
PARED_BORDE = (60, 100, 255)   # azul: para no confundir con el fantasma verde
TUNEL = (64, 40, 90)
PUERTA = (255, 150, 190)
CASA = (22, 20, 40)
ORBE = (255, 236, 200)
SUPER = (255, 140, 60)
PACMAN = (255, 214, 0)
FANTASMA_VERDE = (46, 242, 196)     # con IA (valor 4)
FANTASMA_ROSA = (255, 79, 163)      # sin IA (valor 3)
FANTASMA_ASUSTADO = (60, 90, 255)
FANTASMA_PARPADEO = (240, 240, 255)
OJOS = (250, 250, 250)
PUPILA = (30, 40, 120)

PANEL = (16, 19, 36)
TEXTO = (225, 228, 240)
TEXTO_TENUE = (130, 138, 170)
ACENTO = (40, 196, 182)
CAMBIO = (255, 214, 0)
EVIDENTE = (120, 200, 255)
OCULTO = (255, 160, 110)
