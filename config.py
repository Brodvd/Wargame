import pygame
# Global variables for the game

# Extra space
EXTRA_WIDTH_LEFT = 35
EXTRA_WIDTH_RIGHT = 60
EXTRA_HEIGHT_TOP = 60
EXTRA_HEIGHT_BOTTOM = 20

CELL_SIZE = 45  # Cell size
NUM_CELLS_X = 25
NUM_CELLS_Y = 13

# width = (height * 16) / 10
WIDTH, HEIGHT = (CELL_SIZE*NUM_CELLS_X) + EXTRA_WIDTH_LEFT + EXTRA_WIDTH_RIGHT, (CELL_SIZE*NUM_CELLS_Y) + EXTRA_HEIGHT_TOP + EXTRA_HEIGHT_BOTTOM

FPS = 30
MAX_FPS_GIF = 30
starting_team = "Red"

# Bot
bot_team ="Red"
record_dataset = False
dataset_file = "IA/dataset/try.json"
predict_dataset = 'IA/predict/predict_right.json'
# advance compact, press right, press left, press center, defend, attack, retreat
bot_strategy = "attack left"
enemy_strategy = "defend"

# Scores
score_red = 0
score_blue = 0
max_points = 1000

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
#MILITARY_GREEN = (29, 29.4, 17.3)
MILITARY_GREEN = (53.3, 57.6, 31)

# Variables for the side volume sliders (here just to reduce code lines)
slider_x = WIDTH - 25                                               # Horizontal position of the slider
slider_height = HEIGHT / 2.5                                        # Height of the slider
slider_y = (HEIGHT - slider_height) // 12 + (EXTRA_HEIGHT_TOP) / 2  # Vertical position of the slider
slider_width = 20                                                   # Width of the slider

sound_slider_x = WIDTH - 25
sound_slider_y = (HEIGHT - (HEIGHT / 2.5)) // 1.1 + (EXTRA_HEIGHT_TOP) / 2
sound_slider_height = HEIGHT / 2.5
sound_slider_width = 20

sound_volume = 0.0
music_volume = 0.0

zoom = 1.0
ZOOM_MIN = 0.5
ZOOM_MAX = 2.0
offset_x = 0
offset_y = 0

# Paths
background_image = pygame.image.load("assets/extra_background.webp")
explosion_image = "assets/explosion3.png"
music_icon = pygame.image.load("assets/music_icon.webp")
sound_icon = pygame.image.load("assets/sound_icon.webp")
sound_effect = "assets/sound.wav"
background_music = "assets/background_music.ogg"
grid_json_file = 'assets/grid_properties.json'
