import pygame
import sys
import json
import random
from config import *

# Initialize Pygame
pygame.init()

# Configure the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wargame")

game_data = []  # List to store the state and actions of each turn

def record_turn(pieces, action, teams, file_path=dataset_file):
    """Records the game state and actions performed in a turn and immediately saves to file."""
    global current_team_index
    current_team = teams[current_team_index]
    if current_team.name == bot_team:
        turn = {
            "state": {
                "pieces": [
                    {
                        "name": piece.name,
                        "position": list(piece.position),
                        "type": type(piece).__name__,
                        "team": piece.team.name,
                        "hp": piece.hp
                    }
                    for piece in pieces
                ]
            },
            "action_bot": action,
            "strategy": bot_strategy,
        }
    else:
        turn = {
            "state": {
                "pieces": [
                    {
                        "name": piece.name,
                        "position": list(piece.position),
                        "type": type(piece).__name__,
                        "team": piece.team.name,
                        "hp": piece.hp
                    }
                    for piece in pieces
                ]
            },
            "action_enemy": action,
            "strategy": enemy_strategy,
        }
    game_data.append(turn)
    with open(file_path, 'w') as f:
        json.dump(game_data, f, indent=4)
    print(f"Turn recorded and saved in {file_path}")

def extract_frames_from_sprite_sheet(sprite_sheet_path, frame_width, frame_height):
    """
    Extracts frames from a sprite sheet.

    :param sprite_sheet_path: Path to the sprite sheet file.
    :param frame_width: Width of each frame.
    :param frame_height: Height of each frame.
    :return: List of Pygame surfaces (extracted frames).
    """
    sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
    sheet_width, sheet_height = sprite_sheet.get_size()
    frames = []

    for y in range(0, sheet_height, frame_height):
        for x in range(0, sheet_width, frame_width):
            # Extract only if the frame is within bounds
            if x + frame_width <= sheet_width and y + frame_height <= sheet_height:
                frame = sprite_sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                frames.append(frame)
    return frames

def play_animation(screen, frames, position, frame_delay=FPS):
    """
    Plays an animation on the screen.

    :param screen: Pygame surface to draw on.
    :param frames: List of Pygame surfaces (animation frames).
    :param position: Position (x, y) to draw the animation.
    :param frame_delay: Number of game frames between each animation frame.
    """
    # Control to not make the animation too fast (to be adapted if the sprite sheet changes)
    if frame_delay > MAX_FPS_GIF:
        frame_delay = MAX_FPS_GIF

    clock = pygame.time.Clock()
    for frame in frames:
        screen.blit(frame, position)
        pygame.display.flip()
        clock.tick(frame_delay)

def draw_volume_slider(screen, volume, volume_sound):
    """Draws the volume sliders in the extra area to the right of the screen."""

    # Draw the slider bar
    pygame.draw.rect(screen, MILITARY_GREEN, (slider_x, slider_y, slider_width, slider_height), 2)  # Contour of 2 pixels
    pygame.draw.rect(screen, MILITARY_GREEN, (sound_slider_x, sound_slider_y, sound_slider_width, sound_slider_height), 2)

    # Draw the icons above the bars
    screen.blit(music_icon, (slider_x, slider_y - 20))
    screen.blit(sound_icon, (sound_slider_x, sound_slider_y - 20))

    # Calculate the position of the indicator based on the volume
    indicator_y = slider_y + slider_height - int(volume * slider_height)
    sound_indicator_y = sound_slider_y + sound_slider_height - int(volume_sound * sound_slider_height)

    # Limit the indicator to the edges of the bar
    indicator_y = max(slider_y + 5, min(slider_y + slider_height - 5, indicator_y))
    sound_indicator_y = max(sound_slider_y + 5, min(sound_slider_y + sound_slider_height - 5, sound_indicator_y))

    # Draw the green indicator for music
    pygame.draw.rect(screen, MILITARY_GREEN, (slider_x, indicator_y - 5, slider_width, 10))  # Indicator
    # Draw the green indicator for sounds
    pygame.draw.rect(screen, MILITARY_GREEN, (sound_slider_x, sound_indicator_y - 5, sound_slider_width, 10))

def handle_volume_slider(event, volume):
    """Handles dragging the volume slider."""

    # Check if the mouse is over the slider area
    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
        mouse_x, mouse_y = event.pos
        if slider_x <= mouse_x <= slider_x + slider_width and slider_y <= mouse_y <= slider_y + slider_height:
            # Calculate the new volume based on the vertical position of the mouse
            new_volume = 1 - (mouse_y - slider_y) / slider_height
            new_volume = max(0.0, min(1.0, new_volume))  # Limit the volume between 0.0 and 1.0
            pygame.mixer.music.set_volume(new_volume)
            
            # Pause the music if the volume is zero (check performance)
            if new_volume == 0.0:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
            return new_volume

    return volume

def handle_sound_volume_drag(event, sound_volume):
    """Handles dragging the sound volume slider."""

    # Check if the mouse is over the slider area
    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
        mouse_x, mouse_y = event.pos
        if sound_slider_x <= mouse_x <= sound_slider_x + sound_slider_width and sound_slider_y <= mouse_y <= sound_slider_y + sound_slider_height:
            # Calculate the new volume based on the vertical position of the mouse
            new_sound_volume = 1 - (mouse_y - sound_slider_y) / sound_slider_height
            new_sound_volume = max(0.0, min(1.0, new_sound_volume))  # Limit the volume between 0.0 and 1.0
            return new_sound_volume

    return sound_volume

def play_sound_with_pan(sound, panpot, volume_sound):
    """
    Plays a sound with a specific pan value.

    :param sound: pygame.mixer.Sound object.
    :param pan: Pan value (-1.0 = left, 0.0 = center, 1.0 = right).
    """
    if volume_sound == 0.0:
        return  # Do not play the sound if the volume is zero
    
    # Calculate the volumes for the left and right channels
    left_volume = max(0.0, volume_sound * (-panpot))
    right_volume = max(0.0, volume_sound * panpot)

    # Get a free channel and set the volume
    channel = pygame.mixer.find_channel()
    if channel:
        channel.set_volume(left_volume, right_volume)
        channel.play(sound)

# Load the properties of the cells from the JSON file
def load_grid_properties(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Function to get the properties of a cell
def get_cell_properties(position, grid_properties):
    for cell in grid_properties['cells']:
        if cell['position'] == list(position):
            terrain_type = cell['terrain']
            return grid_properties['terrain_types'][terrain_type]
    return None

def load_teams_and_pieces(grid_properties):
    teams = []
    pieces = []

    for team_data in grid_properties['teams']:
        team = Team(team_data['name'], tuple(team_data['color']))
        teams.append(team)

        for piece_data in team_data['pieces']:
            piece_type = piece_data['type']
            name = piece_data['name']
            position = tuple(piece_data['position'])
            image_path = f"assets/{name}.webp"

            if piece_type == "MediumTank":
                piece = MediumTank(name, position, team=team)
            elif piece_type == "HeavyTank":
                piece = HeavyTank(name, position, team=team)
            elif piece_type == "Rifle":
                piece = Rifle(name, position, team=team)
            elif piece_type == "AssaultRifle":
                piece = AssaultRifle(name, position, team=team)
            elif piece_type == "LightMachineGun":
                piece = LightMachineGun(name, position, team=team)
            elif piece_type == "MediumMachineGun":
                piece = MediumMachineGun(name, position, team=team)
            elif piece_type == "HeavyMachineGun":
                piece = HeavyMachineGun(name, position, team=team)
            elif piece_type == "Howitzer":
                piece = Howitzer(name, position, team=team)
            elif piece_type == "Mortar":
                piece = Mortar(name, position, team=team)
            elif piece_type == "Armored":
                piece = Armored(name, position, team=team)
            elif piece_type == "AntiTankArtillery":
                piece = AntiTankArtillery(name, position, team=team)
            elif piece_type == "Pyromaniac":
                piece = Pyromaniac(name, position, team=team)
            else:
                raise ValueError(f"Unknown piece type: {piece_type}")

            piece.image = pygame.image.load(image_path).convert_alpha()
            team.add_vehicle(piece)
            pieces.append(piece)

    return teams, pieces

def load_terrain_icons(grid_properties):
    icons = {}
    for terrain_type in grid_properties['terrain_types']:
        icon_path = f"assets/{terrain_type}.webp"
        try:
            icon = pygame.image.load(icon_path).convert_alpha()
            icons[terrain_type] = icon
        except pygame.error:
            print(f"Icon for {terrain_type} not found in {icon_path}")
    return icons

def draw_terrain_icons(screen, grid_properties, icons):
    for cell in grid_properties['cells']:
        x, y = cell['position']
        if x >= NUM_CELLS_X or y >= NUM_CELLS_Y:
            continue
        terrain_type = cell['terrain']
        icon = icons.get(terrain_type)
        if icon:
            # Calculate the position and size consistently
            sx = int(x * CELL_SIZE * zoom + EXTRA_WIDTH_LEFT - offset_x)
            sy = int(y * CELL_SIZE * zoom + EXTRA_HEIGHT_TOP - offset_y)
            sx_next = int((x + 1) * CELL_SIZE * zoom + EXTRA_WIDTH_LEFT - offset_x)
            sy_next = int((y + 1) * CELL_SIZE * zoom + EXTRA_HEIGHT_TOP - offset_y)
            size_x = sx_next - sx
            size_y = sy_next - sy
            # Create a surface without transparency to avoid "white lines"
            icon_scaled = pygame.transform.smoothscale(icon, (size_x, size_y)).convert_alpha()
            # Limit drawing to the map area
            if (EXTRA_WIDTH_LEFT <= sx < WIDTH - EXTRA_WIDTH_RIGHT and
                EXTRA_HEIGHT_TOP <= sy < HEIGHT - EXTRA_HEIGHT_BOTTOM):
                screen.blit(icon_scaled, (sx, sy))

def draw_zoom_indicator(screen, zoom):
    """Draws the value of the zoom in percentage in the top right."""
    font = pygame.font.Font(None, 32)
    zoom_percent = int(zoom * 100)
    text = font.render(f"Zoom: {zoom_percent}%", True, (40, 40, 40))
    margin = 16
    text_rect = text.get_rect(topright=(WIDTH - EXTRA_WIDTH_RIGHT, margin))
    # White background with transparency for readability
    bg_rect = text_rect.inflate(12, 8)
    s = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    s.fill((255, 255, 255, 180))
    screen.blit(s, bg_rect.topleft)
    screen.blit(text, text_rect)

def draw_counters(screen):
    global max_points_red, max_points_blue

    font = pygame.font.Font(None, 36)  # Font for the text
    # Use the real max points instead of max_points
    points_red = max_points_red - score_red
    points_blue = max_points_blue - score_blue

    # Generate the text
    info_text = font.render(f"{points_blue} / {points_red}", True, MILITARY_GREEN)

    # Get the text rectangle and center it in the desired position
    text_rect = info_text.get_rect(center=((WIDTH - EXTRA_WIDTH_RIGHT) // 2, 20))

    # Draw white background
    bg_rect = text_rect.inflate(12, 8)
    s = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    s.fill((255, 255, 255, 120))
    screen.blit(s, bg_rect.topleft)
    # Draw the centered text
    screen.blit(info_text, text_rect)

    # Check victory
    if points_red <= 0:
        victory(screen, "Blue")  # The blue team wins
    elif points_blue <= 0:
        victory(screen, "Red")  # The red team wins

def draw_circles(circle_type, surface, center):
    """
    Draws concentric circles with a filled style and spaces between them.

    :param circle_type: Type of circle ("move" or "fire").
    :param surface: Surface to draw on (screen).
    :param center: Center of the circles (x, y).
    """
    if circle_type == "move":
        radii = [CELL_SIZE/3.5, CELL_SIZE/3, CELL_SIZE/2]  # Radii of the circles
        for radius in radii:
            pygame.draw.circle(surface, BLUE, center, radius, 4)  # Fixed thickness of 4 pixels
    elif circle_type == "fire":
        pygame.draw.circle(surface, RED, center, CELL_SIZE/3, 6)
        pygame.draw.circle(surface, RED, center, CELL_SIZE/2, 4)

def draw_view_scrollbars(screen):
    """Draws the gray scroll bars that show the visible portion of the map, detached and rounded."""
    # Margin between the map and the bars
    margin = 6
    # Visible area dimensions
    view_w = WIDTH - EXTRA_WIDTH_LEFT - EXTRA_WIDTH_RIGHT
    view_h = HEIGHT - EXTRA_HEIGHT_TOP - EXTRA_HEIGHT_BOTTOM
    # Total map dimensions (in pixels, considering zoom)
    map_w = int(NUM_CELLS_X * CELL_SIZE * zoom)
    map_h = int(NUM_CELLS_Y * CELL_SIZE * zoom)

    # --- Horizontal bar (at the bottom) ---
    bar_h = 12
    bar_y = HEIGHT - EXTRA_HEIGHT_BOTTOM + margin
    bar_x = EXTRA_WIDTH_LEFT + margin
    bar_w = view_w - margin * 2
    # Visible area (thumb)
    if map_w > view_w:
        thumb_w = int(bar_w * (view_w / map_w))
        thumb_x = int(bar_x + (offset_x / (map_w - view_w)) * (bar_w - thumb_w))
    else:
        thumb_w = bar_w
        thumb_x = bar_x

    pygame.draw.rect(screen, (180, 180, 180), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(screen, (100, 100, 100), (thumb_x, bar_y, thumb_w, bar_h), border_radius=4)

    # --- Vertical bar (on the right) ---
    bar_w_v = 12
    bar_x_v = WIDTH - EXTRA_WIDTH_RIGHT + margin
    bar_y_v = EXTRA_HEIGHT_TOP + margin
    bar_h_v = view_h - margin * 2
    if map_h > view_h:
        thumb_h = int(bar_h_v * (view_h / map_h))
        thumb_y = int(bar_y_v + (offset_y / (map_h - view_h)) * (bar_h_v - thumb_h))
    else:
        thumb_h = bar_h_v
        thumb_y = bar_y_v

    pygame.draw.rect(screen, (180, 180, 180), (bar_x_v, bar_y_v, bar_w_v, bar_h_v), border_radius=6)
    pygame.draw.rect(screen, (100, 100, 100), (bar_x_v, thumb_y, bar_w_v, thumb_h), border_radius=6)

def victory(screen, winning_team):
    font = pygame.font.Font(None, 72)  # Large font for the victory message
    victory_text = font.render(f"Victory for team {winning_team}!", True, MILITARY_GREEN)
    victory_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    # Draw the victory message on the screen
    screen.fill(WHITE)  # Background
    screen.blit(victory_text, victory_rect)
    pygame.display.flip()

    # Wait a few seconds and end the game
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

def calculate_team_points(pieces, team):
    """
    Calculates the sum of the points of a team's pieces.

    :param pieces: List of all pieces.
    :param team: Team for which to calculate the points.
    :return: Sum of the points of the team's pieces.
    """
    return sum(piece.point_value for piece in pieces if piece.team == team)

def world_to_screen(x, y):
    """Converts grid coordinates to screen coordinates considering zoom and pan."""
    sx = int(x * CELL_SIZE * zoom + EXTRA_WIDTH_LEFT - offset_x)
    sy = int(y * CELL_SIZE * zoom + EXTRA_HEIGHT_TOP - offset_y)
    return sx, sy

def screen_to_world(sx, sy):
    """Converts screen coordinates to grid coordinates (float, not int!)."""
    x = (sx - EXTRA_WIDTH_LEFT + offset_x) / (CELL_SIZE * zoom)
    y = (sy - EXTRA_HEIGHT_TOP + offset_y) / (CELL_SIZE * zoom)
    return x, y

def zoom_at_center(new_zoom, old_zoom):
    global offset_x, offset_y, zoom
    # Current center of the viewport (in pixels)
    center_x = offset_x + (WIDTH - EXTRA_WIDTH_LEFT - EXTRA_WIDTH_RIGHT) // 2
    center_y = offset_y + (HEIGHT - EXTRA_HEIGHT_TOP - EXTRA_HEIGHT_BOTTOM) // 2
    # Center in map coordinates (before zoom)
    center_map_x = (center_x - EXTRA_WIDTH_LEFT) / (CELL_SIZE * old_zoom)
    center_map_y = (center_y - EXTRA_HEIGHT_TOP) / (CELL_SIZE * old_zoom)
    # New offset to keep the center fixed
    offset_x = int(center_map_x * CELL_SIZE * new_zoom + EXTRA_WIDTH_LEFT - (WIDTH - EXTRA_WIDTH_LEFT - EXTRA_WIDTH_RIGHT) // 2)
    offset_y = int(center_map_y * CELL_SIZE * new_zoom + EXTRA_HEIGHT_TOP - (HEIGHT - EXTRA_HEIGHT_TOP - EXTRA_HEIGHT_BOTTOM) // 2)
    zoom = new_zoom

def line_of_sight_blocked(start_pos, end_pos, grid_properties):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while (x1, y1) != (x2, y2):
        # Skip the check for the starting cell
        if (x1, y1) != start_pos:
            cell_properties = get_cell_properties((x1, y1), grid_properties)
            if cell_properties and cell_properties.get('blocks_line_of_sight', False) :
                # Exclude hills from blocking the line of sight
                if cell_properties.get('terrain') != 'hill':
                    return True
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

    return False

class Team:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.vehicles = []

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)
        vehicle.team = self

    def is_enemy(self, other_team):
        return self != other_team

class Piece:
    def __init__(self, name, position, hp, move_distance, attack_distance, team=None):
        self.name = name
        self.position = position
        self.hp = hp
        self.max_hp = hp
        self.move_distance = move_distance
        self.attack_distance = attack_distance
        self.selected = False
        self.team = team
        self.image = None    # boh
        self.has_acted = False
        self.buttons_visible = False
        self.current_action = None
        self.draw_red_circles = True
        
        self.forward = False     # allows to know if the chosen action = "forward" in draw_movement
        self.ambush = False  # ambush action
        self.down = False        # down action

    def move(self, new_position, pieces, teams):
        global game_data
        action = {
            "piece": self.name,
            "type": "move",
            "target": None,
            "position": list(new_position)
        }
        if record_dataset:
            record_turn(pieces, action, teams)  # Register the bot's action
        self.position = new_position

    def take_damage(self, damage, pieces):
        global score_red, score_blue  # Use global variables
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            print(f"{self.name} is dead!")
            pieces.remove(self)
            # Increment the score counter
            if self.team.name == "Red":
                score_blue += self.point_value
            elif self.team.name == "Blue":
                score_red += self.point_value
            else:
                print(f"Unknown team: {self.team.name}")

    def draw(self, screen):
        x, y = self.position
        sx, sy = world_to_screen(x, y)
        size = int(CELL_SIZE * zoom)
        piece_offset = int(size // 10)
        piece_rect = pygame.Rect(
            sx + piece_offset,
            sy + size // 3.5 - piece_offset,
            size - 2 * piece_offset,
            size - 2 * piece_offset
        )
        # Check if the piece is completely outside the visible frame of the map
        if (
            sx < EXTRA_WIDTH_LEFT or
            sx + size > WIDTH - EXTRA_WIDTH_RIGHT or
            sy < EXTRA_HEIGHT_TOP or
            sy + size > HEIGHT - EXTRA_HEIGHT_BOTTOM
        ):
            return  # Do not draw the piece if it is completely outside

        # Draw the piece (only if at least partially visible)
        screen.blit(pygame.transform.smoothscale(self.image, piece_rect.size), piece_rect.topleft)
        self.draw_health_bar(screen, sx, sy, size)

    def draw_health_bar(self, screen, sx, sy, size):
        bar_length = size - 4  # Adjust the length of the bar to the zoomed size
        bar_height = max(3, size // 13)  # Adjust the height of the bar
        health_percentage = self.hp / self.max_hp
        health_length = int(bar_length * health_percentage)

        # Position the bar above the piece, at the top of the zoomed cell
        bar_x = sx + 2
        bar_y = sy + 2

        # Draw the red bar (background)
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_length, bar_height))
        # Draw the green bar (remaining health)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_length, bar_height))
        
    def draw_action_buttons(self, screen):
        if self.buttons_visible:
            x, y = self.position
            center_x, center_y = world_to_screen(x, y)
            center_x += int(CELL_SIZE * zoom // 2)
            center_y += int(CELL_SIZE * zoom // 2)
            radius = int((CELL_SIZE // 5) * zoom)

            offset = [
                (-0.75 * CELL_SIZE * zoom, -0.75 * CELL_SIZE * zoom),
                (-CELL_SIZE * zoom, 0),
                (-0.75 * CELL_SIZE * zoom, 0.75 * CELL_SIZE * zoom),
                (0.75 * CELL_SIZE * zoom, -0.75 * CELL_SIZE * zoom),
                (CELL_SIZE * zoom, 0),
                (0.75 * CELL_SIZE * zoom, 0.75 * CELL_SIZE * zoom),
            ]

            for i, (dx, dy) in enumerate(offset):
                circle_x = center_x + dx
                circle_y = center_y + dy

                circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(circle_surface, (0, 0, 0, 128), (radius, radius), radius)
                screen.blit(circle_surface, (circle_x - radius, circle_y - radius))

                # Draw a number or an icon to identify the button
                font_size = int(24 * zoom)
                font = pygame.font.Font(None, max(12, font_size))

                if i == 0:
                    text = font.render("S", True, WHITE)
                elif i == 1:
                    text = font.render("F", True, WHITE)
                elif i == 2:
                    text = font.render("M", True, WHITE)
                elif i == 3:
                    text = font.render("A", True, WHITE)
                elif i == 4:
                    text = font.render("R", True, WHITE)
                elif i == 5:
                    text = font.render("D", True, WHITE)

                text_rect = text.get_rect(center=(circle_x, circle_y))
                screen.blit(text, text_rect)

    def draw_movement(self, screen, pieces, grid_properties):
        if self.current_action == "move":
            # Draw the blue circles for movement
            x, y = self.position
            cell_properties = get_cell_properties(self.position, grid_properties)
            movement_cost = cell_properties['movement_cost'] if cell_properties else 0
            if self.forward:
                radius_movement = self.move_distance + movement_cost
            else:
                radius_movement = self.move_distance + movement_cost + 1

            for dx in range(-radius_movement, radius_movement + 1):
                for dy in range(-radius_movement, radius_movement + 1):
                    if abs(dx) + abs(dy) <= radius_movement and (dx != 0 or dy != 0):
                        new_position = (x + dx, y + dy)
                        screen_cx, screen_cy = world_to_screen(x + dx + 0.5, y + dy + 0.5)
                        if screen_cy >= EXTRA_HEIGHT_TOP and screen_cy < (HEIGHT - EXTRA_HEIGHT_BOTTOM):
                            cell_properties = get_cell_properties(new_position, grid_properties)
                            if (
                                screen_cx >= EXTRA_WIDTH_LEFT and screen_cx < (WIDTH - EXTRA_WIDTH_RIGHT) and
                                screen_cy >= EXTRA_HEIGHT_TOP and screen_cy < (HEIGHT - EXTRA_HEIGHT_BOTTOM)
                            ):
                                if screen_cx < WIDTH - EXTRA_WIDTH_RIGHT:
                                    if cell_properties and not cell_properties.get('walkable', True):
                                        continue
                                    if not any(p.position == new_position for p in pieces):
                                        draw_circles("move", screen, (screen_cx, screen_cy))


        elif self.current_action == "fire":
            # Draw the red circles for attack
            x, y = self.position
            cell_properties = get_cell_properties(self.position, grid_properties)
            attack_cost = cell_properties['attack_cost'] if cell_properties else 0
            radius_attack = self.attack_distance + attack_cost

            for dx in range(-radius_attack, radius_attack + 1):
                for dy in range(-radius_attack, radius_attack + 1):
                    if abs(dx) + abs(dy) <= radius_attack and (dx != 0 or dy != 0):
                        new_position = (x + dx, y + dy)
                        screen_cx, screen_cy = world_to_screen(x + dx + 0.5, y + dy + 0.5)
                        if screen_cx < WIDTH - EXTRA_WIDTH_RIGHT:
                            type_1 = type(self).__name__
                            target = next((p for p in pieces if p.position == new_position and compatibility(type_1, type(p).__name__)), None)
                            type_2 = type(target).__name__
                            if target:
                                if self.draw_red_circles:
                                    if target.team != self.team:  # Check if the target is an enemy

                                        if self.forward and not compatibility(type_1, type_2): #and self.team.is_enemy(target.team): #for a piece that finds a target with forward action and is not compatible with the attack
                                            self.draw_red_circles = False
                                        else:
                                            if isinstance(self, Howitzer):
                                                # For the Howitzer, ignore the line of sight and draw the red circle anyway
                                                draw_circles("fire", screen, (screen_cx, screen_cy))
                                            elif not line_of_sight_blocked(self.position, target.position, grid_properties):
                                                # For other pieces, consider the line of sight
                                                if compatibility(type_1, type_2):
                                                    draw_circles("fire", screen, (screen_cx, screen_cy))

        elif self.current_action == "forward":
            # Draw the blue circles for movement (first phase)
            self.forward = True
            self.current_action = "move"
            self.draw_movement(screen, pieces, grid_properties)
            # Draw the red circles for attack (second phase) in handle_click

    def attack(self, target, pieces, teams, defense_bonus,):
        global game_data
        if not self.forward:
            action = {
                "piece": self.name,
                "type": "fire",
                "target": target.name,
                "position": list(self.position)
            }
        else:
            action = {
                "piece": self.name,
                "type": "forward",
                "target": target.name,
                "position": list(self.position)
            }
        if record_dataset:
            record_turn(pieces, action, teams)  # Register the action
        
        attack_sound = pygame.mixer.Sound(sound_effect)
        if target.down:    
            down_bonus = 20
        else:
            down_bonus = 0

        # Check if self is a vehicle (should not use cannon but machine gun against infantry)
        type_1 = type(self).__name__
        type_2 = type(target).__name__
        if (type_1 == "MediumTank" or type_1 == "HeavyTank" or type_1 == "Armored") and (type_2 != "MediumTank" or type_2 != "HeavyTank" or type_2 != "Armored"):
            damage = HeavyMachineGun.fire_power
            self.shots = HeavyMachineGun.shots
            self.hit_probability = HeavyMachineGun.hit_probability
        else:
            damage = self.fire_power

        for i in range(self.shots):
            if self.team and target.team and self.team.is_enemy(target.team):
                if random.random() < self.hit_probability:
                    damage_variation = random.randint(int(-25/100 * damage), int(25/100 * damage))
                    if self.forward:
                        effective_damage = int(((damage + damage_variation) * (1 - defense_bonus / 100) / 2) - down_bonus)
                    elif self.ambush:
                        effective_damage = int(((damage + damage_variation) * (1 - defense_bonus / 100) * 2) - down_bonus)
                        self.ambush = False  # The ambush action is valid only for one turn
                    else:
                        effective_damage = int(((damage + damage_variation) * (1 - defense_bonus / 100)) - down_bonus)

                    if effective_damage < 0:
                        effective_damage = 0

                    print(f"{self.name} attacks {target.name} with power {damage} with variation {damage_variation} with defense bonus {defense_bonus}% and down_bonus {down_bonus}. Effective damage: {effective_damage}")
                    target.take_damage(effective_damage, pieces)
                    sx, sy = world_to_screen(target.position[0], target.position[1])
                    size = int(CELL_SIZE * zoom)
                    target.draw_health_bar(screen, sx, sy, size)

                    # Calculate the pan based on the position of the piece
                    panpot = self.position[0] * (2 * CELL_SIZE) / (WIDTH - EXTRA_WIDTH_RIGHT) - 1 # From -1.0 (left) to 1.0 (right)
                    print(f"Calculated panpot: {int(panpot * 100)}")
                    play_sound_with_pan(attack_sound, panpot, sound_volume)

                    # Calculate the screen position of the target
                    sx, sy = world_to_screen(target.position[0], target.position[1])
                    size = int(CELL_SIZE * zoom)

                    #
                    # Extract frames from the sprite sheet at the base resolution
                    explosion_frames = extract_frames_from_sprite_sheet(explosion_image, CELL_SIZE, CELL_SIZE)  # Use the actual resolution of the frames

                    # Resize the frames based on the zoom
                    explosion_frames_zoomed = [
                        pygame.transform.smoothscale(frame, (size, size)) for frame in explosion_frames
                    ]

                    # Play the animation centered on the cell
                    play_animation(
                        screen,
                        explosion_frames_zoomed,
                        (sx, sy)
                    )
                else:
                     print(f"{self.name} shot {i+1}/{self.shots} MISSED at {target.name}!")
                     # Add a missed shot animation (dust instead of explosion

        target.down = False

def compatibility(type_1, type_2):
    """
    Checks the attack compatibility between two opposing pieces through various cases.

    :param type_1: Type of the attacking piece.
    :param type_2: Type of the piece being attacked.
    """
    if type_1 == "Rifle" and (type_2 == "HeavyTank" or type_2 == "MediumTank" or type_2 == "Armored"):
        return False
    elif type_1 == "AssaultRifle" and (type_2 == "HeavyTank" or type_2 == "MediumTank" or type_2 == "Armored"):
        return False
    elif type_1 == "LightMachineGun" and (type_2 == "HeavyTank" or type_2 == "MediumTank" or type_2 == "Armored"):
        return False
    elif type_1 == "AntiTankArtillery" and (not type_2 == "HeavyTank" or not type_2 == "MediumTank" or not type_2 == "Armored"):
        return False
    else:
        return True

# self.valPunti = ogni giocatore può avere una squadra con al massimo un valore di 1000 punti, ogni unità ha un suo "costo" in punti
# self.colpi = numero di colpi che compie l'arma
class MediumTank(Piece):
    def __init__(self, name, position, team=None):
        super().__init__(name, position, hp=300, move_distance=2, attack_distance=4 , team=team)
        self.fire_power = 40
        self.point_value = 500
        self.shots = 1
        self.hit_probability = 0.85

class HeavyTank(Piece):
    def __init__(self, name, position, team=None):
        super().__init__(name, position, hp=500, move_distance=2, attack_distance=4 , team=team)
        self.fire_power = 50
        self.point_value = 600
        self.shots = 1
        self.hit_probability = 0.85

class Rifle(Piece):
    def __init__(self, name, position, team=None):
        super().__init__(name, position, hp=50, move_distance=2, attack_distance=2, team=team)
        self.fire_power = 10
        self.point_value = 100
        self.shots = 1
        self.hit_probability = 0.9

class AssaultRifle(Piece):
    def __init__(self, name, position, team=None):
        super().__init__(name, position, hp=50, move_distance=3, attack_distance=2, team=team)
        self.fire_power = 10
        self.point_value = 150
        self.shots = 2
        self.hit_probability = 0.8

class LightMachineGun(Piece):
    def __init__(self, name, position, team=None):
        super().__init__(name, position, hp=60, move_distance=2, attack_distance=3, team=team)
        self.fire_power = 10
        self.point_value = 250
        self.shots = 3
        self.hit_probability = 0.75

class MediumMachineGun(Piece):
    def __init__(self, name, position, team=None):
        super().__init__(name, position, hp=60, move_distance=1, attack_distance=3, team=team)
        self.fire_power = 10
        self.point_value = 300
        self.shots = 4
        self.hit_probability = 0.7

class HeavyMachineGun(Piece):
    # to use with other classes
    fire_power = 13
    shots = 3
    hit_probability = 0.6
    def __init__(self, name, position, team=None):
        super().__init__(name, position, hp=60, move_distance=1, attack_distance=3, team=team)
        self.fire_power = HeavyMachineGun.fire_power
        self.point_value = 350
        self.shots = HeavyMachineGun.shots
        self.hit_probability = HeavyMachineGun.hit_probability

class Pyromaniac(Piece):
    def __init__(self, name, position, team=None):
        super().__init__(name, position, hp=60, move_distance=3, attack_distance=1, team=team)
        self.fire_power = 30
        self.point_value = 250
        self.shots = 1
        self.hit_probability = 0.8

class Howitzer(Piece):
    def __init__(self, name, position, team=None):
        super().__init__(name, position, hp=75, move_distance=2, attack_distance=10, team=team)
        self.fire_power = 50
        self.point_value = 250
        self.shots = 1
        self.hit_probability = 0.8

class Mortar(Piece):
    def __init__(self, name, position, team=None):
        super().__init__(name, position, hp=50, move_distance=2, attack_distance=10, team=team)
        self.fire_power = 30
        self.point_value = 200
        self.shots = 1
        self.hit_probability = 0.8

class AntiTankArtillery(Piece):
    def __init__(self, name, position, team=None):
        super().__init__(name, position, hp=75, move_distance=1, attack_distance=5, team=team)
        self.fire_power = 50
        self.point_value = 300
        self.shots = 1
        self.hit_probability = 0.9

class Armored(Piece):
    def __init__(self, name, position, team=None):
        super().__init__(name, position, hp=150, move_distance=3, attack_distance=3, team=team)
        self.fire_power = HeavyMachineGun.fire_power
        self.point_value = 400
        self.shots = 3
        self.hit_probability = HeavyMachineGun.hit_probability

def handle_click(mouse_pos, pieces, grid_properties, teams):
    current_team = teams[current_team_index]  # Get the current team

    # Check if a piece is already selected and is performing an action
    piece_in_action = next((p for p in pieces if p.selected and p.current_action is not None), None)
    piece = piece_in_action
    if piece_in_action:
        if piece.current_action == "fire":
            x, y = piece.position
            cell_properties = get_cell_properties(piece.position, grid_properties)
            attack_cost = cell_properties['attack_cost'] if cell_properties else 0
            radius = piece.attack_distance + attack_cost

            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) + abs(dy) <= radius and (dx != 0 or dy != 0):
                        new_position = (x + dx, y + dy)
                        screen_cx, screen_cy = world_to_screen(new_position[0], new_position[1])
                        rect = pygame.Rect(
                            screen_cx,
                            screen_cy,
                            int(CELL_SIZE * zoom),
                            int(CELL_SIZE * zoom)
                        )
                        if rect.top >= EXTRA_HEIGHT_TOP and rect.bottom <= (HEIGHT - EXTRA_HEIGHT_BOTTOM):
                            type_1 = type(piece).__name__
                            target = next((p for p in pieces if p.position == new_position and compatibility(type_1, type(p).__name__)), None)
                            type_2 = type(target).__name__
                            if rect.collidepoint(mouse_pos):
                                cell_properties = get_cell_properties(new_position, grid_properties)
                                defense_bonus = cell_properties['defense_bonus'] if cell_properties else 0
                                if target and piece.team.is_enemy(target.team):
                                    print(f"Target found: {target.name}, Team: {target.team.name}")
                                    if compatibility(type_1, type_2):
                                        if isinstance(piece, Howitzer) or not line_of_sight_blocked(piece.position, target.position, grid_properties):
                                            piece.attack(target, pieces, teams, defense_bonus)
                                            piece.current_action = None  # Reset the current action
                                            piece.has_acted = True
                                            return
                                    elif piece.forward:
                                        piece.current_action = None
                                        piece.has_acted = True
                                elif not piece.forward: # no enemies
                                    piece.current_action = None
                                    piece.has_acted = False
                                    piece.buttons_visible = True
                            elif piece.forward: # due to compatibility it should stop after moving
                                piece.has_acted = True
                                #piece.draw_red_circles = False

        elif piece.current_action == "move":
            x, y = piece.position
            cell_properties = get_cell_properties(piece.position, grid_properties)
            movement_cost = cell_properties['movement_cost'] if cell_properties else 0
            if piece.forward:
                radius = piece.move_distance + movement_cost
            else:
                radius = piece.move_distance + movement_cost + 1

            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) + abs(dy) <= radius and (dx != 0 or dy != 0):
                        new_position = (x + dx, y + dy)
                        screen_cx, screen_cy = world_to_screen(new_position[0], new_position[1])
                        rect = pygame.Rect(
                            screen_cx,
                            screen_cy,
                            int(CELL_SIZE * zoom),
                            int(CELL_SIZE * zoom)
                        )
                        if rect.top >= EXTRA_HEIGHT_TOP and rect.bottom <= (HEIGHT - EXTRA_HEIGHT_BOTTOM):
                            if rect.collidepoint(mouse_pos):
                                cell_properties = get_cell_properties(new_position, grid_properties)
                                if any(p.position == new_position for p in pieces) or not cell_properties.get('walkable', True):
                                    print(f"Movement not allowed: the cell {new_position} is already occupied or is not walkable.")
                                    return
                                print(f"{piece.name} moves to {new_position}")
                                piece.move(new_position, pieces, teams)
                                
                                # Check if there are enemies in the new position (only in case of action=="forward")
                                enemies_found = False
                                cell_properties = get_cell_properties(piece.position, grid_properties)
                                attack_cost = cell_properties['attack_cost'] if cell_properties else 0
                                radius_attack = piece.attack_distance + attack_cost
                                for dx_att in range(-radius_attack, radius_attack + 1):
                                    for dy_att in range(-radius_attack, radius_attack + 1):
                                        if abs(dx_att) + abs(dy_att) <= radius_attack and (dx_att != 0 or dy_att != 0):
                                            attack_position = (new_position[0] + dx_att, new_position[1] + dy_att) #initial position
                                            type_1 = type(piece).__name__
                                            target = next((p for p in pieces if p.position == attack_position and p.team != piece.team and compatibility(type_1, type(p).__name__)), None)
                                            if target and not line_of_sight_blocked(piece.position, target.position, grid_properties):
                                                enemies_found = True
                                                break
                                    if enemies_found:
                                        break

                                if piece.forward and enemies_found:
                                    piece.current_action = "fire"
                                    print("action changed")  # Change the current action to "fire"
                                else:
                                    piece.current_action = None  # Reset the current action
                                    piece.has_acted = True
                                return

        # Prevent selection of other pieces while this one is in action
        return

    # Check first the action buttons
    for piece in pieces:
        if piece.team != current_team or piece.has_acted:
            continue  # Skip pieces that do not belong to the current team or have already acted

        if piece.buttons_visible:
            # Handle click on buttons
            x, y = piece.position
            center_x, center_y = world_to_screen(x, y)
            center_x += int(CELL_SIZE * zoom // 2)
            center_y += int(CELL_SIZE * zoom // 2)
            radius = int((CELL_SIZE // 5) * zoom)

            offset = [
                (-0.75 * CELL_SIZE * zoom, -0.75 * CELL_SIZE * zoom),
                (-CELL_SIZE * zoom, 0),
                (-0.75 * CELL_SIZE * zoom, 0.75 * CELL_SIZE * zoom),
                (0.75 * CELL_SIZE * zoom, -0.75 * CELL_SIZE * zoom),
                (CELL_SIZE * zoom, 0),
                (0.75 * CELL_SIZE * zoom, 0.75 * CELL_SIZE * zoom),
            ]

            for i, (dx, dy) in enumerate(offset):
                circle_x = center_x + dx
                circle_y = center_y + dy
                circle_rect = pygame.Rect(
                    circle_x - radius, circle_y - radius, radius * 2, radius * 2
                )
                if circle_rect.collidepoint(mouse_pos):
                    # Perform the action corresponding to the button
                    if i == 0:
                        piece.current_action = "fire"
                        piece.buttons_visible = False
                    elif i == 1:
                        piece.current_action = "forward"
                        piece.buttons_visible = False
                    elif i == 2:
                        piece.current_action = "move"
                        piece.buttons_visible = False
                    elif i == 3:
                        piece.current_action = "ambush"
                        print(f"Current action set: {piece.current_action}")
                        piece.buttons_visible = False
                        piece.ambush = True
                        piece.has_acted = True
                        piece.current_action = None
                        action = {
                            "piece": piece.name,
                            "type": "ambush",
                            "target": None,
                            "position": list(piece.position)
                        }
                        if record_dataset:
                            record_turn(pieces, action, teams)
                    elif i == 4:
                        piece.current_action = "rally"
                        piece.buttons_visible = False
                        print(f"Current action set: {piece.current_action}")
                        heal = 20
                        if piece.hp + heal <= piece.max_hp:
                            piece.hp += heal
                        else:
                            piece.hp = piece.max_hp
                        print(f"{piece.name} heals for {heal} with final hp {piece.hp}")
                        piece.has_acted = True
                        piece.current_action = None
                        action = {
                            "piece": piece.name,
                            "type": "rally",
                            "target": piece.name,
                            "position": list(piece.position)
                        }
                        if record_dataset:
                            record_turn(pieces, action, teams)
                        return
                    elif i == 5:
                        piece.current_action = "down"
                        print(f"Current action set: {piece.current_action}")
                        piece.buttons_visible = False
                        piece.down = True
                        piece.has_acted = True
                        piece.current_action = None
                        action = {
                            "piece": piece.name,
                            "type": "down", # json does not recognize "ù"
                            "target": None,
                            "position": list(piece.position)
                        }
                        if record_dataset:
                            record_turn(pieces, action, teams)
                        return
                    #print(f"Current action set: {piece.current_action}")
                    return

    # Select the piece
    mx, my = mouse_pos
    wx, wy = screen_to_world(mx, my)
    for piece in pieces:
        if piece.team != current_team or piece.has_acted:
            continue  # Skip pieces that do not belong to the current team or have already acted

        x, y = piece.position
        if int(wx) == x and int(wy) == y:
            if piece.selected:
                print(f"Deselect {piece.name} ({piece.team.name})")
                piece.selected = False
                piece.buttons_visible = False
            else:
                # Deselect all other pieces
                for p in pieces:
                    p.selected = False
                    p.buttons_visible = False
                print(f"Select {piece.name} ({piece.team.name})")
                piece.selected = True
                piece.buttons_visible = True
            return

# Current team index from the teams list
if starting_team == "Red":
    current_team_index = 0
elif starting_team == "Blue":
    current_team_index = 1

# Modify the `all_pieces_moved` function to check if all pieces of a team have acted
def all_pieces_moved(pieces, current_team):
    return all(piece.has_acted for piece in pieces if piece.team == current_team)

def next_turn(teams, pieces):
    global current_team_index
    current_team_index = (current_team_index + 1) % len(teams)
    current_team = teams[current_team_index]
    for piece in pieces:
        if piece.team == current_team:
            piece.selected = False
            piece.has_acted = False
            piece.buttons_visible = False
    print(f"Turn of the team: {current_team.name}")

def main():
    global sound_volume, music_volume
    global max_points_red, max_points_blue
    
    clock = pygame.time.Clock()

    # Load the properties of the cells
    grid_properties = load_grid_properties(grid_json_file)

    # Load the icons of the cells
    terrain_icons = load_terrain_icons(grid_properties)

    # Load the teams and pieces
    teams, pieces = load_teams_and_pieces(grid_properties)

    # Check that the points of the teams are valid
    for team in teams:
        team_points = calculate_team_points(pieces, team)
        if team_points > max_points:
            print(f"Error: The team '{team.name}' has a total of {team_points} points, which exceeds the limit of {max_points}.")
            pygame.quit()
            sys.exit()

    # Load and play the background music
    pygame.mixer.init()  # Initialize the audio mixer
    pygame.mixer.music.load(background_music)
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)  # Play in loop

    # Debugging team assignment
    for piece in pieces:
        print(f"{piece.name} assigned to team {piece.team.name}")

    # main loop
    while True:
        current_team = teams[current_team_index]
        global zoom, offset_x, offset_y

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle the volume slider
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos

                # Check if the mouse is over the music slider area
                if slider_x <= mouse_x <= slider_x + slider_width and slider_y <= mouse_y <= slider_y + slider_height:
                    previous_volume = music_volume
                    music_volume = handle_volume_slider(event, music_volume)
                    if music_volume != previous_volume:
                        continue  # If the music volume has been updated, skip the rest

                # Check if the mouse is over the sound slider area
                if sound_slider_x <= mouse_x <= sound_slider_x + sound_slider_width and sound_slider_y <= mouse_y <= sound_slider_y + sound_slider_height:
                    sound_previous_volume = sound_volume
                    sound_volume = handle_sound_volume_drag(event, sound_volume)
                    if sound_volume != sound_previous_volume:
                        continue  # If the sound volume has been updated, skip the rest

            # Zoom with mouse wheel
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Only left click
                    handle_click(event.pos, pieces, grid_properties, teams)
                if event.button == 4:  # Scroll up
                    if zoom < ZOOM_MAX:
                        zoom_at_center(zoom + 0.1, zoom)
                elif event.button == 5:  # Scroll down
                    if zoom > ZOOM_MIN:
                        new_zoom = max(zoom - 0.1, ZOOM_MIN)
                        zoom_at_center(new_zoom, zoom)
            # Pan with arrow keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    offset_x = max(0, offset_x - int(50 * zoom))
                elif event.key == pygame.K_RIGHT:
                    offset_x = min(int(NUM_CELLS_X * CELL_SIZE * (zoom - 1)), offset_x + int(50 * zoom))
                elif event.key == pygame.K_UP:
                    offset_y = max(0, offset_y - int(50 * zoom))
                elif event.key == pygame.K_DOWN:
                    offset_y = min(int(NUM_CELLS_Y * CELL_SIZE * (zoom - 1)), offset_y + int(50 * zoom))

        # Check if all pieces of the current team have completed their actions
        if all_pieces_moved(pieces, current_team):
            next_turn(teams, pieces)
        
        # Draw the background image
        screen.blit(background_image, (0, 0))

        # Calculate the real max points for each team
        max_points_red = calculate_team_points(pieces, next(t for t in teams if t.name == "Red"))
        max_points_blue = calculate_team_points(pieces, next(t for t in teams if t.name == "Blue"))

        # Draw the counters of killed pieces
        draw_counters(screen)

        # Draw the icons of the cells
        draw_terrain_icons(screen, grid_properties, terrain_icons)
        
        # Draw the volume slider
        draw_volume_slider(screen, music_volume, sound_volume)

        # Draw the pieces
        for piece in pieces:
            piece.draw(screen)

        # Draw the scrollbars
        draw_view_scrollbars(screen)

        # Draw the action buttons around the selected piece
        for piece in pieces:
            piece.draw_action_buttons(screen)

        # Draw the possible movement and red circles
        for piece in pieces: 
            piece.draw_movement(screen, pieces, grid_properties)

        # Draw the scrollbars
        #draw_view_scrollbars(screen)
        # Draw the zoom indicator
        draw_zoom_indicator(screen, zoom)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
