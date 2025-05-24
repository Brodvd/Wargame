import pygame
# Variabili globali per il gioco

# Spazio extra
WIDTH_EXTRA_LEFT = 35
WIDTH_EXTRA_RIGHT = 60
HEIGHT_EXTRA_TOP = 60
HEIGHT_EXTRA_BOTTOM = 20

# larghezza = (altezza * 16) / 10
WIDTH, HEIGHT = 1260 + WIDTH_EXTRA_LEFT + WIDTH_EXTRA_RIGHT, 585 + HEIGHT_EXTRA_TOP + HEIGHT_EXTRA_BOTTOM

FPS = 30
GRID_SIZE = 45  # Dimensione celle
squadraInizio = "Rosso"

# Bot
squadraBot ="Rosso"
registra_dataset = True
file_dataset = "IA/dataset/try.json"
# avanza compatto, pressa a destra, pressa a sinistra, pressa centrale, difendi, attacca, ritirati
strategy_bot = "attacca"
strategy_enemy = "difendi"

# punteggi
punteggio_rosso = 0
punteggio_blu = 0
max_punti = 1000

# Colori
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
#MILITARY_GREEN = (29, 29.4, 17.3)
MILITARY_GREEN = (53.3, 57.6, 31)

# Variabili per gli slider laterali dei volumi (qui solo per ridurre le righe del codice)
slider_x = WIDTH - 25                                               # Posizione orizzontale dello slider
slider_height = HEIGHT / 2.5                                        # Altezza dello slider
slider_y = (HEIGHT - slider_height) // 12 + (HEIGHT_EXTRA_TOP) / 2  # Posizione verticale dello slider
slider_width = 20                                                   # Larghezza dello slider

sound_slider_x = WIDTH - 25
sound_slider_y = (HEIGHT - (HEIGHT / 2.5)) // 1.1 + (HEIGHT_EXTRA_TOP) / 2
sound_slider_height = HEIGHT / 2.5
sound_slider_width = 20

volume_sound = 0.0
volume = 0.0

# Immagini
background_image = pygame.image.load("assets/extra_background.tiff")
explosion_image = "assets/explosion3.png"
music_icon = pygame.image.load("assets/music_icon.webp")
sound_icon = pygame.image.load("assets/sound_icon.webp")
