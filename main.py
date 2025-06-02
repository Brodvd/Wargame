import pygame
import sys
import json
import random
from variables import *

# Inizializza Pygame
pygame.init()

# Configura la finestra
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wargame WW2")

game_data = []  # Lista per memorizzare lo stato e le azioni di ogni turno

def registra_turno(pedine, action, teams, file_path=file_dataset):
    """
    Registra lo stato del gioco e le azioni eseguite in un turno e salva immediatamente su file.

    :param state: Stato attuale del gioco (pedine e loro proprietà).
    :param action: Azione eseguita dalla squadra.
    :param file_path: Percorso del file JSON in cui salvare i dati.
    """
    global current_team_index
    current_team = teams[current_team_index]
    if current_team.name == squadraBot:
        turno = {
            "state": {
                "pedine": [
                    {
                        "name": pedina.nome,
                        "position": list(pedina.posizione),
                        "type": type(pedina).__name__,
                        "team": pedina.team.name,
                        "hp": pedina.vita
                    }
                    for pedina in pedine  # Registra tutte le pedine
                ]
            },
            "action_bot": action,
            "strategy": strategy_bot,
        }
    else:
        turno = {
                "state": {
                    "pedine": [
                        {
                            "name": pedina.nome,
                            "position": list(pedina.posizione),
                            "type": type(pedina).__name__,
                            "team": pedina.team.name,
                            "hp": pedina.vita
                        }
                        for pedina in pedine  # Registra tutte le pedine
                    ]
                },
                "action_enemy": action,
                "strategy": strategy_enemy,
            }
    game_data.append(turno)  # Aggiungi il turno alla lista globale

    # Salva immediatamente il file JSON
    with open(file_path, 'w') as f:
        json.dump(game_data, f, indent=4)
    print(f"Turno registrato e salvato in {file_path}")

def extract_frames_from_sprite_sheet(sprite_sheet_path, frame_width, frame_height):
    """
    Estrae i fotogrammi da uno sprite sheet.

    :param sprite_sheet_path: Percorso del file dello sprite sheet.
    :param frame_width: Larghezza di ogni fotogramma.
    :param frame_height: Altezza di ogni fotogramma.
    :return: Lista di superfici Pygame (fotogrammi estratti).
    """
    sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
    sheet_width, sheet_height = sprite_sheet.get_size()
    frames = []

    for y in range(0, sheet_height, frame_height):  # Itera sulle righe
        for x in range(0, sheet_width, frame_width):  # Itera sulle colonne
            # Estrai il fotogramma come una superficie Pygame
            frame = sprite_sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
            frames.append(frame)

    return frames

def play_animation(screen, frames, position, frame_delay=FPS):
    """
    Riproduce un'animazione sullo schermo.

    :param screen: Superficie Pygame su cui disegnare.
    :param frames: Lista di superfici Pygame (fotogrammi dell'animazione).
    :param position: Posizione (x, y) in cui disegnare l'animazione.
    :param frame_delay: Numero di frame di gioco tra un fotogramma e il successivo.
    """
    # controllo per non rendere troppo veloce l'animazione (da adattare in caso si cambiasse lo sprite sheet)
    if frame_delay > 60:
        frame_delay = 60

    clock = pygame.time.Clock()
    for frame in frames:
        screen.blit(frame, position)
        pygame.display.flip()
        clock.tick(frame_delay)

def draw_volume_slider(screen, volume, volume_sound):
    """Disegna gli slider del volume nell'area extra a destra dello schermo."""

    # Disegna la barra dello slider
    pygame.draw.rect(screen, MILITARY_GREEN, (slider_x, slider_y, slider_width, slider_height), 2)  # Contorno di 2 pixel
    pygame.draw.rect(screen, MILITARY_GREEN, (sound_slider_x, sound_slider_y, sound_slider_width, sound_slider_height), 2)

    # Disegna le icone sopra le barre
    screen.blit(music_icon, (slider_x, slider_y - 20))
    screen.blit(sound_icon, (sound_slider_x, sound_slider_y - 20))

    # Calcola la posizione dell'indicatore in base al volume
    indicator_y = slider_y + slider_height - int(volume * slider_height)
    sound_indicator_y = sound_slider_y + sound_slider_height - int(volume_sound * sound_slider_height)

    # Limita l'indicatore ai bordi della barra
    indicator_y = max(slider_y + 5, min(slider_y + slider_height - 5, indicator_y))
    sound_indicator_y = max(sound_slider_y + 5, min(sound_slider_y + sound_slider_height - 5, sound_indicator_y))

    # Disegna l'indicatore verde per la musica
    pygame.draw.rect(screen, MILITARY_GREEN, (slider_x, indicator_y - 5, slider_width, 10))  # Indicatore
    # Disegna l'indicatore verde per i suoni
    pygame.draw.rect(screen, MILITARY_GREEN, (sound_slider_x, sound_indicator_y - 5, sound_slider_width, 10))

def handle_volume_slider(event, volume):
    """Gestisce il trascinamento dello slider del volume."""

    # Controlla se il mouse è sull'area dello slider
    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
        mouse_x, mouse_y = event.pos
        if slider_x <= mouse_x <= slider_x + slider_width and slider_y <= mouse_y <= slider_y + slider_height:
            # Calcola il nuovo volume in base alla posizione verticale del mouse
            new_volume = 1 - (mouse_y - slider_y) / slider_height
            new_volume = max(0.0, min(1.0, new_volume))  # Limita il volume tra 0.0 e 1.0
            pygame.mixer.music.set_volume(new_volume)
            
            # Interrompi la musica se il volume è zero (verificare le prestazioni)
            if new_volume == 0.0:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
            return new_volume

    return volume

def trascina_sound_volume(event, sound_volume):
    """Gestisce il trascinamento dello slider del volume dei suoni."""

    # Controlla se il mouse è sull'area dello slider
    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
        mouse_x, mouse_y = event.pos
        if sound_slider_x <= mouse_x <= sound_slider_x + sound_slider_width and sound_slider_y <= mouse_y <= sound_slider_y + sound_slider_height:
            # Calcola il nuovo volume in base alla posizione verticale del mouse
            new_sound_volume = 1 - (mouse_y - sound_slider_y) / sound_slider_height
            new_sound_volume = max(0.0, min(1.0, new_sound_volume))  # Limita il volume tra 0.0 e 1.0
            return new_sound_volume

    return sound_volume

def play_sound_with_pan(sound, panpot, volume_sound):
    """
    Riproduce un suono con un valore di pan specifico.

    :param sound: Oggetto pygame.mixer.Sound.
    :param pan: Valore di pan (-1.0 = sinistra, 0.0 = centro, 1.0 = destra).
    """
    if volume_sound == 0.0:
        return  # Non riprodurre il suono se il volume è zero
    
    # Calcola i volumi per i canali sinistro e destro
    left_volume = max(0.0, volume_sound * (-panpot))
    right_volume = max(0.0, volume_sound * panpot)

    # Ottieni un canale libero e imposta il volume
    channel = pygame.mixer.find_channel()
    if channel:
        channel.set_volume(left_volume, right_volume)
        channel.play(sound)

# Carica le proprietà delle caselle dal file JSON
def load_grid_properties(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Funzione per ottenere le proprietà di una casella
def get_cell_properties(position, grid_properties):
    for cell in grid_properties['cells']:
        if cell['position'] == list(position):
            terrain_type = cell['terrain']
            return grid_properties['terrain_types'][terrain_type]
    return None

def load_teams_and_pedine(grid_properties):
    teams = []
    pedine = []

    for team_data in grid_properties['teams']:
        team = Team(team_data['name'], tuple(team_data['color']))
        teams.append(team)

        for pedina_data in team_data['pedine']:
            pedina_type = pedina_data['type']
            nome = pedina_data['name']
            posizione = tuple(pedina_data['position'])
            immagine_path = f"assets/{nome}.webp"

            if pedina_type == "CarroMedio":
                pedina = CarroMedio(nome, posizione, team=team)
            elif pedina_type == "CarroPesante":
                pedina = CarroPesante(nome, posizione, team=team)
            elif pedina_type == "Fucile":
                pedina = Fucile(nome, posizione, team=team)
            elif pedina_type == "FucileAssalto":
                pedina = FucileAssalto(nome, posizione, team=team)
            elif pedina_type == "MitragliatriceLeggera":
                pedina = MitragliatriceLeggera(nome, posizione, team=team)
            elif pedina_type == "MitragliatriceMedia":
                pedina = MitragliatriceMedia(nome, posizione, team=team)
            elif pedina_type == "MitragliatricePesante":
                pedina = MitragliatricePesante(nome, posizione, team=team)
            elif pedina_type == "Obice":
                pedina = Obice(nome, posizione, team=team)
            elif pedina_type == "Mortaio":
                pedina = Mortaio(nome, posizione, team=team)
            elif pedina_type == "Blindato":
                pedina = Blindato(nome, posizione, team=team)
            elif pedina_type == "ArtiglieriaControcarro":
                pedina = ArtiglieriaControcarro(nome, posizione, team=team)
            elif pedina_type == "Piromane":
                pedina = Piromane(nome, posizione, team=team)
            else:
                raise ValueError(f"Tipo di pedina sconosciuto: {pedina_type}")

            pedina.immagine = pygame.image.load(immagine_path)
            pedina.immagine = pygame.transform.smoothscale(pedina.immagine, (GRID_SIZE, GRID_SIZE)) # Ridimensiona l'immagine
            team.add_vehicle(pedina)
            pedine.append(pedina)

    return teams, pedine

def load_terrain_icons(grid_properties):
    icons = {}
    for terrain_type in grid_properties['terrain_types']:
        icon_path = f"assets/{terrain_type}.webp"
        try:
            icon = pygame.image.load(icon_path)
            icon = pygame.transform.smoothscale(icon, (GRID_SIZE, GRID_SIZE))
            icons[terrain_type] = icon
        except pygame.error:
            print(f"Icona per {terrain_type} non trovata in {icon_path}")
    return icons

def draw_terrain_icons(screen, grid_properties, icons):
    for cell in grid_properties['cells']:
        x, y = cell['position']
        terrain_type = cell['terrain']
        icon = icons.get(terrain_type)
        if icon:
            screen.blit(icon, (x * GRID_SIZE + WIDTH_EXTRA_LEFT, y * GRID_SIZE + HEIGHT_EXTRA_TOP))  # Sposta l'icona

def draw_counters(screen):
    font = pygame.font.Font(None, 36)  # Font per il testo
    punti_rosso = max_punti - punteggio_rosso
    punti_blu = max_punti - punteggio_blu

    # Genera il testo
    info_text = font.render(f"{punti_blu} / {punti_rosso}", True, MILITARY_GREEN)

    # Ottieni il rettangolo del testo e centra nella posizione desiderata
    text_rect = info_text.get_rect(center=((WIDTH - WIDTH_EXTRA_RIGHT) // 2, 20))

    # Disegna il testo centrato
    screen.blit(info_text, text_rect)

    # Controlla la vittoria
    if punti_rosso <= 0:
        vittoria(screen, "Blu")  # La squadra blu vince
    elif punti_blu <= 0:
        vittoria(screen, "Rosso")  # La squadra rossa vince

def draw_circles(tipo, surface, center):
    """
    Disegna circonferenze concentriche con uno stile pieno e spazi tra di esse.

    :param tipo: Tipo di circonferenza ("corsa" o "fuoco").
    :param surface: Superficie su cui disegnare (screen).
    :param center: Centro delle circonferenze (x, y).
    """
    if tipo == "corsa":
        raggi = [GRID_SIZE/3.5, GRID_SIZE/3, GRID_SIZE/2]  # Raggi delle circonferenze
        for raggio in raggi:
            pygame.draw.circle(surface, BLUE, center, raggio, 4)  # Spessore fisso di 4 pixel
    elif tipo == "fuoco":
        pygame.draw.circle(surface, RED, center, GRID_SIZE/3, 6)
        pygame.draw.circle(surface, RED, center, GRID_SIZE/2, 4)

def vittoria(screen, squadra_vincente):
    font = pygame.font.Font(None, 72)  # Font grande per il messaggio di vittoria
    vittoria_text = font.render(f"Vittoria della squadra {squadra_vincente}!", True, MILITARY_GREEN)
    vittoria_rect = vittoria_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    # Disegna il messaggio di vittoria sullo schermo
    screen.fill(WHITE)  # Sfondo
    screen.blit(vittoria_text, vittoria_rect)
    pygame.display.flip()

    # Aspetta qualche secondo e termina il gioco
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

def calcola_punti_squadra(pedine, team):
    """
    Calcola la somma dei punti delle pedine di una squadra.

    :param pedine: Lista di tutte le pedine.
    :param team: Squadra per cui calcolare i punti.
    :return: Somma dei punti delle pedine della squadra.
    """
    return sum(pedina.valPunti for pedina in pedine if pedina.team == team)

def line_of_sight_blocked(start_pos, end_pos, grid_properties):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while (x1, y1) != (x2, y2):
        # Salta il controllo per la cella di partenza
        if (x1, y1) != start_pos:
            cell_properties = get_cell_properties((x1, y1), grid_properties)
            if cell_properties and cell_properties.get('blocks_line_of_sight', False) :
                # Escludi le colline dal bloccare la linea di vista
                if cell_properties.get('terrain') != 'collina':
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

class Pedina:
    def __init__(self, nome, posizione, vita, distanza_movimento, distanza_attacco, team=None):
        self.nome = nome
        self.posizione = posizione
        self.vita = vita
        self.vita_massima = vita
        self.distanza_movimento = distanza_movimento
        self.distanza_attacco = distanza_attacco
        self.selezionata = False
        self.team = team
        self.immagine = None    # boh
        self.ha_agito = False
        self.tasti_visibili = False
        self.azione_corrente = None
        self.disegna_rossi = True
        
        self.avanti = False     # permette di sapere se azione scelta = "avanti" in disegna_movimento
        self.imboscata = False  # azione ambush
        self.giù = False        # azione down

    def muovi(self, nuova_posizione, pedine, teams):
        global game_data
        azione = {
            "pedina": self.nome,
            "type": "corsa",
            "target": None,
            "position": list(nuova_posizione)
        }
        if registra_dataset:
            registra_turno(pedine, azione, teams)  # Registra l'azione del bot
        self.posizione = nuova_posizione

    def prendi_danno(self, danno, pedine):
        global punteggio_rosso, punteggio_blu  # Usa le variabili globali
        self.vita -= danno
        if self.vita <= 0:
            self.vita = 0
            print(f"{self.nome} è morto!")
            pedine.remove(self)
            # Incrementa il contatore dei punti
            if self.team.name == "Rosso":
                punteggio_blu += self.valPunti
            elif self.team.name == "Blu":
                punteggio_rosso += self.valPunti
            else:
                print(f"Team sconosciuto: {self.team.name}")

    def disegna(self, screen):
        x, y = self.posizione
        # Ridimensiona leggermente la pedina per lasciare spazio alla barra della vita
        pedina_offset = GRID_SIZE // 10  # Riduce la dimensione della pedina del 10%
        pedina_rect = pygame.Rect(
            x * GRID_SIZE + pedina_offset + WIDTH_EXTRA_LEFT,  # Aggiungi lo spazio extra a sinistra
            y * GRID_SIZE + GRID_SIZE // 3.5 - pedina_offset + HEIGHT_EXTRA_TOP,  # Aggiungi lo spazio extra sopra
            GRID_SIZE - 2 * pedina_offset,
            GRID_SIZE - 2 * pedina_offset
        )
        screen.blit(pygame.transform.scale(self.immagine, pedina_rect.size), pedina_rect.topleft)
        # Disegna la barra della vita sopra la pedina
        self.disegna_barra_vita(screen)

    def disegna_barra_vita(self, screen):
        x, y = self.posizione
        lunghezza_barra = GRID_SIZE - 4  # Riduce lunghezza della barra per adattarla
        altezza_barra = 5
        vita_percentuale = self.vita / self.vita_massima
        lunghezza_vita = int(lunghezza_barra * vita_percentuale)
        
        # Posizioniamo la barra della vita sopra la pedina, nella parte superiore della casella
        barra_x = x * GRID_SIZE + WIDTH_EXTRA_LEFT + 2  # Aggiungi lo spazio extra a sinistra
        barra_y = y * GRID_SIZE + HEIGHT_EXTRA_TOP + 2  # Aggiungi lo spazio extra sopra
        
        # Disegna la barra rossa (sfondo)
        pygame.draw.rect(screen, RED, (barra_x, barra_y, lunghezza_barra, altezza_barra))
        # Disegna la barra verde (vita rimanente)
        pygame.draw.rect(screen, GREEN, (barra_x, barra_y, lunghezza_vita, altezza_barra))
        
    def disegna_tasti_attorno(self, screen):
        if self.tasti_visibili:
            x, y = self.posizione
            centro_x = x * GRID_SIZE + GRID_SIZE // 2 + WIDTH_EXTRA_LEFT
            centro_y = y * GRID_SIZE + GRID_SIZE // 2 + HEIGHT_EXTRA_TOP
            raggio = GRID_SIZE // 5  # Raggio dei cerchi

            # Offset per posizionare i sei cerchi attorno alla pedina
            offset = [
                (-0.75 * GRID_SIZE, -0.75 * GRID_SIZE),  # Alto sinistra
                (-GRID_SIZE, 0),                         # Sinistra
                (-0.75 * GRID_SIZE, 0.75 * GRID_SIZE),   # Basso sinistra
                (0.75 * GRID_SIZE, -0.75 * GRID_SIZE),   # Alto destra
                (GRID_SIZE, 0),                          # Destra
                (0.75 * GRID_SIZE, 0.75 * GRID_SIZE),    # Basso destra
            ]

            for i, (dx, dy) in enumerate(offset):
                cerchio_x = centro_x + dx
                cerchio_y = centro_y + dy

                # Creare una superficie trasparente per il cerchio
                cerchio_surface = pygame.Surface((raggio * 2, raggio * 2), pygame.SRCALPHA)
                pygame.draw.circle(cerchio_surface, (0, 0, 0, 128), (raggio, raggio), raggio)  # Blu trasparente
                screen.blit(cerchio_surface, (cerchio_x - raggio, cerchio_y - raggio))

                # Disegna un numero o un'icona per identificare il tasto
                font = pygame.font.Font(None, 24)

                if i == 0:
                    text = font.render("F", True, WHITE)
                elif i == 1:
                    text = font.render("A", True, WHITE)
                elif i == 2:
                    text = font.render("C", True, WHITE)
                elif i == 3:
                    text = font.render("I", True, WHITE)
                elif i == 4:
                    text = font.render("C", True, WHITE)
                elif i == 5:
                    text = font.render("G", True, WHITE)

                text_rect = text.get_rect(center=(cerchio_x, cerchio_y))
                screen.blit(text, text_rect)

    def disegna_movimento(self, screen, pedine, grid_properties):
        if self.azione_corrente == "corsa":
            # Disegna i cerchi blu per il movimento
            x, y = self.posizione
            cell_properties = get_cell_properties(self.posizione, grid_properties)
            movement_cost = cell_properties['movement_cost'] if cell_properties else 0
            if self.avanti:
                raggio_movimento = self.distanza_movimento + movement_cost
            else:
                raggio_movimento = self.distanza_movimento + movement_cost + 1

            for dx in range(-raggio_movimento, raggio_movimento + 1):
                for dy in range(-raggio_movimento, raggio_movimento + 1):
                    if abs(dx) + abs(dy) <= raggio_movimento and (dx != 0 or dy != 0):
                        nuova_posizione = (x + dx, y + dy)
                        cerchio_x = (x + dx) * GRID_SIZE + GRID_SIZE // 2 + WIDTH_EXTRA_LEFT
                        cerchio_y = (y + dy) * GRID_SIZE + GRID_SIZE // 2 + HEIGHT_EXTRA_TOP
                        if cerchio_y >= HEIGHT_EXTRA_TOP and cerchio_y < (HEIGHT - HEIGHT_EXTRA_BOTTOM):
                            cell_properties = get_cell_properties(nuova_posizione, grid_properties)
                            if (
                                cerchio_x >= WIDTH_EXTRA_LEFT and cerchio_x < (WIDTH - WIDTH_EXTRA_RIGHT) and
                                cerchio_y >= HEIGHT_EXTRA_TOP and cerchio_y < (HEIGHT - HEIGHT_EXTRA_BOTTOM)
                            ):
                                if cerchio_x < WIDTH - WIDTH_EXTRA_RIGHT:
                                    if cell_properties and not cell_properties.get('walkable', True):
                                        continue
                                    if not any(p.posizione == nuova_posizione for p in pedine):
                                        draw_circles("corsa", screen, (cerchio_x, cerchio_y))


        elif self.azione_corrente == "fuoco":
            # Disegna i cerchi rossi per l'attacco
            x, y = self.posizione
            cell_properties = get_cell_properties(self.posizione, grid_properties)
            attacco_cost = cell_properties['attacco_cost'] if cell_properties else 0
            raggio_attacco = self.distanza_attacco + attacco_cost

            for dx in range(-raggio_attacco, raggio_attacco + 1):
                for dy in range(-raggio_attacco, raggio_attacco + 1):
                    if abs(dx) + abs(dy) <= raggio_attacco and (dx != 0 or dy != 0):
                        nuova_posizione = (x + dx, y + dy)
                        cerchio_x = (x + dx) * GRID_SIZE + GRID_SIZE // 2 + WIDTH_EXTRA_LEFT
                        cerchio_y = (y + dy) * GRID_SIZE + GRID_SIZE // 2 + HEIGHT_EXTRA_TOP
                        if cerchio_x < WIDTH - WIDTH_EXTRA_RIGHT:
                            target = next((p for p in pedine if p.posizione == nuova_posizione), None)
                            type_1 = type(self).__name__
                            type_2 = type(target).__name__
                            if target:
                                if self.disegna_rossi:
                                    if target.team != self.team:  # Controlla se il bersaglio è un nemico

                                        if self.avanti and not compatibilità(type_1, type_2): #and self.team.is_enemy(target.team): #per una pedina che trova un target con azione avanti e non è compatibile con l'attacco
                                            self.disegna_rossi = False
                                        else:
                                            if isinstance(self, Obice):
                                                # Per l'Obice, ignora la linea di vista e disegna comunque il cerchio rosso
                                                draw_circles("fuoco", screen, (cerchio_x, cerchio_y))
                                            elif not line_of_sight_blocked(self.posizione, target.posizione, grid_properties):
                                                # Per le altre pedine, considera la linea di vista
                                                if compatibilità(type_1, type_2):
                                                    draw_circles("fuoco", screen, (cerchio_x, cerchio_y))
                                
        elif self.azione_corrente == "avanti":
            # Disegna i cerchi blu per il movimento (prima fase)
            self.avanti = True
            self.azione_corrente = "corsa"
            self.disegna_movimento(screen, pedine, grid_properties)
            # Disegna i cerchi rossi per l'attacco (seconda fase) in gestisci_click

    def attacca(self, bersaglio, pedine, teams, defense_bonus):
        global game_data
        if not self.avanti:
            azione = {
                "pedina": self.nome,
                "type": "fuoco",
                "target": bersaglio.nome,
                "position": list(self.posizione)
            }
        else:
            azione = {
                "pedina": self.nome,
                "type": "avanti",
                "target": bersaglio.nome,
                "position": list(self.posizione)
            }
        if registra_dataset:
            registra_turno(pedine, azione, teams)  # Registra l'azione
        
        attack_sound = pygame.mixer.Sound("assets/sound.wav")
        if bersaglio.giù:    
            giù_bonus = 20
        else:
            giù_bonus = 0

        # controlla se self è un carro armato (non deve usare cannone ma la mitragliatrice contro fanteria)
        type_1 = type(self).__name__
        type_2 = type(bersaglio).__name__
        if (type_1 == "CarroMedio" or type_1 == "CarroPesante") and (type_2 == "Fucile" or type_2 == "FucileAssalto" or type_2 == "MitragliatriceLeggera" or type_2 == "MitragliatriceMedia" or type_2 == "MitragliatricePesante"):
            danno = MitragliatricePesante.potenza_fuoco
            self.colpi = MitragliatricePesante.colpi
            self.probabilità_colpire = MitragliatricePesante.probabilità_colpire
        else:
            danno = self.potenza_fuoco

        for i in range(self.colpi):
            if self.team and bersaglio.team and self.team.is_enemy(bersaglio.team):
                if random.random() < self.probabilità_colpire:
                    variazione_danno = random.randint(int(-25/100 * danno), int(25/100 * danno))
                    if self.avanti:
                        danno_effettivo = int(((danno + variazione_danno) * (1 - defense_bonus / 100) / 2) - giù_bonus)
                    elif self.imboscata:
                        danno_effettivo = int(((danno + variazione_danno) * (1 - defense_bonus / 100) * 2) - giù_bonus)
                        self.imboscata = False  # L'azione imboscata vale solo per il turno successivo
                    else:
                        danno_effettivo = int(((danno + variazione_danno) * (1 - defense_bonus / 100)) - giù_bonus)

                    print(f"{self.nome} attacca {bersaglio.nome} con potenza {danno} con variazione {variazione_danno} con bonus difesa {defense_bonus}% e giù_bonus {giù_bonus}. Danno effettivo: {danno_effettivo}")
                    bersaglio.prendi_danno(danno_effettivo, pedine)
                    bersaglio.disegna_barra_vita(screen)

                    # Calcola il pan in base alla posizione della pedina
                    panpot = self.posizione[0] * (2 * GRID_SIZE) / (WIDTH - WIDTH_EXTRA_RIGHT) - 1 # Da -1.0 (sinistra) a 1.0 (destra)
                    print(f"Pan calcolato: {int(panpot * 100)}")
                    play_sound_with_pan(attack_sound, panpot, volume_sound)

                    explosion_frames = extract_frames_from_sprite_sheet(explosion_image, GRID_SIZE, GRID_SIZE)
                    play_animation(
                        screen,
                        explosion_frames,
                        (
                            bersaglio.posizione[0] * GRID_SIZE + WIDTH_EXTRA_LEFT,
                            bersaglio.posizione[1] * GRID_SIZE + HEIGHT_EXTRA_TOP
                        )
                    )
                else:
                     print(f"{self.nome} spara colpo {i+1}/{self.colpi} MANCATO su {bersaglio.nome}!")
                     # Aggiugere un'animazione di colpo mancato (polvere invece che esplosione

        bersaglio.giù = False

def compatibilità(type_1, type_2):
    """
    Verifica la compatibilità dell'attacco tra due pedine avversarie attraverso le varie casistiche.

    :param type_1: Tipo della pedina che attacca.
    :param type_2: Tipo della pedina che subisce l'attacco.
    """
    if type_1 == "Fucile" and (type_2 == "CarroPesante" or type_2 == "CarroMedio" or type_2 == "Blindato"):
        return False
    elif type_1 == "FucileAssalto" and (type_2 == "CarroPesante" or type_2 == "CarroMedio" or type_2 == "Blindato"):
        return False
    elif type_1 == "MitragliatriceLeggera" and (type_2 == "CarroPesante" or type_2 == "CarroMedio" or type_2 == "Blindato"):
        return False
    elif type_1 == "ArtiglieriaControcarro" and (not type_2 == "CarroPesante" or not type_2 == "CarroMedio" or not type_2 == "Blindato"):
        return False
    else:
        return True

# self.valPunti = ogni giocatore può avere una squadra con al massimo un valore di 1000 punti, ogni unità ha un suo "costo" in punti
# self.colpi = numero di colpi che compie l'arma
class CarroMedio(Pedina):
    def __init__(self, nome, posizione, team=None):
        super().__init__(nome, posizione, vita=300, distanza_movimento=2, distanza_attacco=4 , team=team)
        self.potenza_fuoco = 40
        self.valPunti = 500
        self.colpi = 1
        self.probabilità_colpire = 0.85

class CarroPesante(Pedina):
    def __init__(self, nome, posizione, team=None):
        super().__init__(nome, posizione, vita=500, distanza_movimento=2, distanza_attacco=4 , team=team)
        self.potenza_fuoco = 50
        self.valPunti = 600
        self.colpi = 1
        self.probabilità_colpire = 0.85

class Fucile(Pedina):
    def __init__(self, nome, posizione, team=None):
        super().__init__(nome, posizione, vita=50, distanza_movimento=2, distanza_attacco=2, team=team)
        self.potenza_fuoco = 10
        self.valPunti = 100
        self.colpi = 1
        self.probabilità_colpire = 0.9

class FucileAssalto(Pedina):
    def __init__(self, nome, posizione, team=None):
        super().__init__(nome, posizione, vita=50, distanza_movimento=3, distanza_attacco=2, team=team)
        self.potenza_fuoco = 10
        self.valPunti = 150
        self.colpi = 2
        self.probabilità_colpire = 0.8

class MitragliatriceLeggera(Pedina):
    def __init__(self, nome, posizione, team=None):
        super().__init__(nome, posizione, vita=60, distanza_movimento=2, distanza_attacco=3, team=team)
        self.potenza_fuoco = 10
        self.valPunti = 250
        self.colpi = 3
        self.probabilità_colpire = 0.75

class MitragliatriceMedia(Pedina):
    def __init__(self, nome, posizione, team=None):
        super().__init__(nome, posizione, vita=60, distanza_movimento=1, distanza_attacco=3, team=team)
        self.potenza_fuoco = 10
        self.valPunti = 300
        self.colpi = 4
        self.probabilità_colpire = 0.7

class MitragliatricePesante(Pedina):
    # per utilizzare con altre classi
    potenza_fuoco = 13
    colpi = 3
    probabilità_colpire = 0.6
    def __init__(self, nome, posizione, team=None):
        super().__init__(nome, posizione, vita=60, distanza_movimento=1, distanza_attacco=3, team=team)
        self.potenza_fuoco = MitragliatricePesante.potenza_fuoco
        self.valPunti = 350
        self.colpi = MitragliatricePesante.colpi
        self.probabilità_colpire = MitragliatricePesante.probabilità_colpire

class Piromane(Pedina):
    def __init__(self, nome, posizione, team=None):
        super().__init__(nome, posizione, vita=60, distanza_movimento=3, distanza_attacco=1, team=team)
        self.potenza_fuoco = 30
        self.valPunti = 250
        self.colpi = 1
        self.probabilità_colpire = 0.8

class Obice(Pedina):
    def __init__(self, nome, posizione, team=None):
        super().__init__(nome, posizione, vita=75, distanza_movimento=2, distanza_attacco=10, team=team)
        self.potenza_fuoco = 50
        self.valPunti = 250
        self.colpi = 1
        self.probabilità_colpire = 0.8

class Mortaio(Pedina):
    def __init__(self, nome, posizione, team=None):
        super().__init__(nome, posizione, vita=50, distanza_movimento=2, distanza_attacco=10, team=team)
        self.potenza_fuoco = 30
        self.valPunti = 200
        self.colpi = 1
        self.probabilità_colpire = 0.8

class ArtiglieriaControcarro(Pedina):
    def __init__(self, nome, posizione, team=None):
        super().__init__(nome, posizione, vita=75, distanza_movimento=1, distanza_attacco=5, team=team)
        self.potenza_fuoco = 50
        self.valPunti = 300
        self.colpi = 1
        self.probabilità_colpire = 0.9

class Blindato(Pedina):
    def __init__(self, nome, posizione, team=None):
        super().__init__(nome, posizione, vita=150, distanza_movimento=3, distanza_attacco=3, team=team)
        self.potenza_fuoco = MitragliatricePesante.potenza_fuoco
        self.valPunti = 400
        self.colpi = 3
        self.probabilità_colpire = MitragliatricePesante.probabilità_colpire

def draw_grid():
    offset_x = WIDTH_EXTRA_LEFT  # Spazio extra a sinistra
    offset_y = HEIGHT_EXTRA_TOP  # Spazio extra sopra
    for x in range(offset_x, WIDTH - WIDTH_EXTRA_RIGHT, GRID_SIZE):  # Limita la griglia alla larghezza originale
        for y in range(offset_y, HEIGHT - HEIGHT_EXTRA_BOTTOM, GRID_SIZE):  # Limita la griglia all'altezza originale
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)

def gestisci_click(mouse_pos, pedine, grid_properties, teams):
    current_team = teams[current_team_index]  # Ottieni la squadra corrente

    # Controlla se una pedina è già selezionata e sta eseguendo un'azione
    pedina_in_azione = next((p for p in pedine if p.selezionata and p.azione_corrente is not None), None)
    pedina = pedina_in_azione
    if pedina_in_azione:
        #print(f"{pedina_in_azione.nome} sta eseguendo l'azione {pedina_in_azione.azione_corrente}")
        # Permetti alla pedina selezionata di completare la sua azione

        if pedina.azione_corrente == "fuoco":
            x, y = pedina.posizione
            cell_properties = get_cell_properties(pedina.posizione, grid_properties)
            attacco_cost = cell_properties['attacco_cost'] if cell_properties else 0
            raggio = pedina.distanza_attacco + attacco_cost

            for dx in range(-raggio, raggio + 1):
                for dy in range(-raggio, raggio + 1):
                    if abs(dx) + abs(dy) <= raggio and (dx != 0 or dy != 0):
                        nuova_posizione = (x + dx, y + dy)
                        rect = pygame.Rect(
                            nuova_posizione[0] * GRID_SIZE + WIDTH_EXTRA_LEFT,
                            nuova_posizione[1] * GRID_SIZE + HEIGHT_EXTRA_TOP,
                            GRID_SIZE,
                            GRID_SIZE
                        )
                        if rect.top >= HEIGHT_EXTRA_TOP and rect.bottom <= (HEIGHT - HEIGHT_EXTRA_BOTTOM):
                            target = next((p for p in pedine if p.posizione == nuova_posizione), None)
                            type_1 = type(pedina).__name__
                            type_2 = type(target).__name__
                            if rect.collidepoint(mouse_pos):
                                cell_properties = get_cell_properties(nuova_posizione, grid_properties)
                                defense_bonus = cell_properties['defense_bonus'] if cell_properties else 0
                                if target and pedina.team.is_enemy(target.team):
                                    print(f"Target found: {target.nome}, Team: {target.team.name}")
                                    if compatibilità(type_1, type_2):
                                        if isinstance(pedina, Obice) or not line_of_sight_blocked(pedina.posizione, target.posizione, grid_properties):
                                            pedina.attacca(target, pedine, teams, defense_bonus)
                                            pedina.azione_corrente = None  # Resetta l'azione corrente
                                            pedina.ha_agito = True
                                            return
                                elif not pedina.avanti: # non c'è un belin di nemico
                                    pedina.azione_corrente = None
                                    pedina.ha_agito = False
                                    pedina.tasti_visibili = True
                            elif pedina.avanti: # a causa della compatibilità si deve bloccare dopo il movimento
                                pedina.ha_agito = True
                                #pedina.disegna_rossi = False

        elif pedina.azione_corrente == "corsa":
            x, y = pedina.posizione
            cell_properties = get_cell_properties(pedina.posizione, grid_properties)
            movimento_cost = cell_properties['movement_cost'] if cell_properties else 0
            if pedina.avanti:
                raggio = pedina.distanza_movimento + movimento_cost
            else:
                raggio = pedina.distanza_movimento + movimento_cost + 1

            for dx in range(-raggio, raggio + 1):
                for dy in range(-raggio, raggio + 1):
                    if abs(dx) + abs(dy) <= raggio and (dx != 0 or dy != 0):
                        nuova_posizione = (x + dx, y + dy)
                        rect = pygame.Rect(
                            nuova_posizione[0] * GRID_SIZE + WIDTH_EXTRA_LEFT, 
                            nuova_posizione[1] * GRID_SIZE + HEIGHT_EXTRA_TOP,
                            GRID_SIZE,
                            GRID_SIZE
                        )
                        if rect.top >= HEIGHT_EXTRA_TOP and rect.bottom <= (HEIGHT - HEIGHT_EXTRA_BOTTOM):
                            if rect.collidepoint(mouse_pos):
                                cell_properties = get_cell_properties(nuova_posizione, grid_properties)
                                if any(p.posizione == nuova_posizione for p in pedine) or not cell_properties.get('walkable', True):
                                    print(f"Movimento non consentito: la casella {nuova_posizione} è già occupata o non è percorribile.")
                                    return
                                print(f"{pedina.nome} si muove a {nuova_posizione}")
                                pedina.muovi(nuova_posizione, pedine, teams)
                                
                                # Controlla se ci sono nemici nella nuova posizione (solo nel caso di azione=="avanti")
                                nemici_trovati = False
                                cell_properties = get_cell_properties(pedina.posizione, grid_properties)
                                attacco_cost = cell_properties['attacco_cost'] if cell_properties else 0
                                raggio_attacco = pedina.distanza_attacco + attacco_cost
                                for dx_att in range(-raggio_attacco, raggio_attacco + 1):
                                    for dy_att in range(-raggio_attacco, raggio_attacco + 1):
                                        if abs(dx_att) + abs(dy_att) <= raggio_attacco and (dx_att != 0 or dy_att != 0):
                                            posizione_attacco = (nuova_posizione[0] + dx_att, nuova_posizione[1] + dy_att) #posizione iniziale
                                            target = next((p for p in pedine if p.posizione == posizione_attacco and p.team != pedina.team), None)
                                            if target and not line_of_sight_blocked(pedina.posizione, target.posizione, grid_properties):
                                                nemici_trovati = True
                                                break
                                    if nemici_trovati:
                                        break

                                if pedina.avanti and nemici_trovati:
                                    pedina.azione_corrente = "fuoco"
                                    print("cambia azione")  # Cambia l'azione corrente in "fuoco"
                                else:
                                    pedina.azione_corrente = None  # Resetta l'azione corrente
                                    pedina.ha_agito = True
                                return

        # Blocca la selezione di altre pedine mentre questa è in azione
        return

    # Controlla prima i tasti di azione
    for pedina in pedine:
        if pedina.team != current_team or pedina.ha_agito:
            continue  # Salta le pedine che non appartengono alla squadra corrente o che hanno già agito

        if pedina.tasti_visibili:
            # Gestione del clic sui tasti
            x, y = pedina.posizione
            centro_x = x * GRID_SIZE + GRID_SIZE // 2 + WIDTH_EXTRA_LEFT
            centro_y = y * GRID_SIZE + GRID_SIZE // 2 + HEIGHT_EXTRA_TOP
            raggio = GRID_SIZE // 5

            # Offset per posizionare i sei cerchi attorno alla pedina
            offset = [
                (-0.75 * GRID_SIZE, -0.75 * GRID_SIZE),  # Alto sinistra
                (-GRID_SIZE, 0),                         # Sinistra
                (-0.75 * GRID_SIZE, 0.75 * GRID_SIZE),   # Basso sinistra
                (0.75 * GRID_SIZE, -0.75 * GRID_SIZE),   # Alto destra
                (GRID_SIZE, 0),                          # Destra
                (0.75 * GRID_SIZE, 0.75 * GRID_SIZE),    # Basso destra
            ]

            for i, (dx, dy) in enumerate(offset):
                cerchio_x = centro_x + dx
                cerchio_y = centro_y + dy
                cerchio_rect = pygame.Rect(cerchio_x - raggio, cerchio_y - raggio, raggio * 2, raggio * 2)
                if cerchio_rect.collidepoint(mouse_pos):
                    # Esegui l'azione corrispondente al tasto
                    if i == 0:
                        pedina.azione_corrente = "fuoco"
                        pedina.tasti_visibili = False
                    elif i == 1:
                        pedina.azione_corrente = "avanti"
                        pedina.tasti_visibili = False
                    elif i == 2:
                        pedina.azione_corrente = "corsa"
                        pedina.tasti_visibili = False
                    elif i == 3:
                        pedina.azione_corrente = "imboscata"
                        print(f"Azione corrente impostata: {pedina.azione_corrente}")
                        pedina.tasti_visibili = False
                        pedina.imboscata = True
                        pedina.ha_agito = True
                        pedina.azione_corrente = None
                        azione = {
                            "pedina": pedina.nome,
                            "type": "imboscata",
                            "target": None,
                            "position": list(pedina.posizione)
                        }
                        if registra_dataset:
                            registra_turno(pedine, azione, teams)
                    elif i == 4:
                        pedina.azione_corrente = "cura"
                        pedina.tasti_visibili = False
                        print(f"Azione corrente impostata: {pedina.azione_corrente}")
                        cura = 20
                        if pedina.vita + cura <= pedina.vita_massima:
                            pedina.vita += cura
                        else:
                            pedina.vita = pedina.vita_massima
                        print(f"{pedina.nome} si cura di {cura} con vita finale {pedina.vita}")
                        pedina.ha_agito = True
                        pedina.azione_corrente = None
                        azione = {
                            "pedina": pedina.nome,
                            "type": "cura",
                            "target": pedina.nome,
                            "position": list(pedina.posizione)
                        }
                        if registra_dataset:
                            registra_turno(pedine, azione, teams)
                        return
                    elif i == 5:
                        pedina.azione_corrente = "giù"
                        print(f"Azione corrente impostata: {pedina.azione_corrente}")
                        pedina.tasti_visibili = False
                        pedina.giù = True
                        pedina.ha_agito = True
                        pedina.azione_corrente = None
                        azione = {
                            "pedina": pedina.nome,
                            "type": "giu", # il json non riconosce ù
                            "target": None,
                            "position": list(pedina.posizione)
                        }
                        if registra_dataset:
                            registra_turno(pedine, azione, teams)
                        return
                    print(f"Azione corrente impostata: {pedina.azione_corrente}")
                    return

    # Selezione della pedina
    for pedina in pedine:
        if pedina.team != current_team or pedina.ha_agito:
            continue  # Salta le pedine che non appartengono alla squadra corrente o che hanno già agito

        x, y = pedina.posizione
        rect = pygame.Rect(
            x * GRID_SIZE + WIDTH_EXTRA_LEFT,
            y * GRID_SIZE + HEIGHT_EXTRA_TOP,
            GRID_SIZE,
            GRID_SIZE
        )
        if rect.collidepoint(mouse_pos):
            if pedina.selezionata:
                print(f"Deseleziona {pedina.nome} ({pedina.team.name})")
                pedina.selezionata = False
                pedina.tasti_visibili = False
            else:
                # Deseleziona tutte le altre pedine
                for p in pedine:
                    p.selezionata = False
                    p.tasti_visibili = False
                print(f"Seleziona {pedina.nome} ({pedina.team.name})")
                pedina.selezionata = True
                pedina.tasti_visibili = True
            return

# Indice della squadra corrente dall'elenco teams
if squadraInizio == "Rosso":
    current_team_index = 0
elif squadraInizio == "Blu":
    current_team_index = 1

# Modifica della funzione `all_pedine_moved` per verificare se tutte le pedine di una squadra hanno agito
def all_pedine_moved(pedine, current_team):
    return all(pedina.ha_agito for pedina in pedine if pedina.team == current_team)

def next_turn(teams, pedine):
    global current_team_index
    current_team_index = (current_team_index + 1) % len(teams)
    current_team = teams[current_team_index]
    for pedina in pedine:
        if pedina.team == current_team:
            pedina.selezionata = False
            pedina.ha_agito = False
            pedina.tasti_visibili = False
    print(f"Turno della squadra: {current_team.name}")

def main():
    global volume_sound
    global volume
    
    clock = pygame.time.Clock()

    # Carica le proprietà delle caselle
    grid_properties = load_grid_properties('assets/grid_properties.json')

    # Carica le icone delle caselle
    terrain_icons = load_terrain_icons(grid_properties)

    # Carica le squadre e le pedine
    teams, pedine = load_teams_and_pedine(grid_properties)

    # Controlla che i punti delle squadre siano validi
    for team in teams:
        punti_squadra = calcola_punti_squadra(pedine, team)
        if punti_squadra > max_punti:
            print(f"Errore: La squadra '{team.name}' ha un totale di {punti_squadra} punti, che supera il limite di {max_punti}.")
            pygame.quit()
            sys.exit()

    # Carica e riproduci la musica di sottofondo
    pygame.mixer.init()  # Inizializza il mixer audio
    pygame.mixer.music.load("assets/background_music.ogg")

    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)  # Riproduci in loop

    # Debugging team assignment
    for pedina in pedine:
        print(f"{pedina.nome} assigned to team {pedina.team.name}")

    # ciclo principale
    while True:
        current_team = teams[current_team_index]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Gestisci lo slider del volume
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos

                # Controlla se il mouse è sull'area dello slider della musica
                if slider_x <= mouse_x <= slider_x + slider_width and slider_y <= mouse_y <= slider_y + slider_height:
                    previous_volume = volume
                    volume = handle_volume_slider(event, volume)
                    if volume != previous_volume:
                        continue  # Se il volume della musica è stato aggiornato, salta il resto

                # Controlla se il mouse è sull'area dello slider dei suoni
                if sound_slider_x <= mouse_x <= sound_slider_x + sound_slider_width and sound_slider_y <= mouse_y <= sound_slider_y + sound_slider_height:
                    sound_previous_volume = volume_sound
                    volume_sound = trascina_sound_volume(event, volume_sound)
                    if volume_sound != sound_previous_volume:
                        continue  # Se il volume dei suoni è stato aggiornato, salta il resto

            # Gestisci il click sulle pedine (solo se non è stato gestito dallo slider)
            if event.type == pygame.MOUSEBUTTONDOWN:
                gestisci_click(event.pos, pedine, grid_properties, teams)

        # Controlla se tutte le pedine della squadra corrente hanno completato le loro azioni
        if all_pedine_moved(pedine, current_team):
            next_turn(teams, pedine)
        
        # Disegna l'immagine di sfondo
        screen.blit(background_image, (0, 0))
        draw_grid()

        # Disegna i contatori delle pedine uccise
        draw_counters(screen)

        # Disegna le icone delle caselle
        draw_terrain_icons(screen, grid_properties, terrain_icons)
        
        # Disegna lo slider del volume
        draw_volume_slider(screen, volume, volume_sound)

        # Disegna le pedine
        for pedina in pedine:
            pedina.disegna(screen)

        # Disegna i tasti attorno alla pedina selezionata
        for pedina in pedine:
            pedina.disegna_tasti_attorno(screen)

        # Disegna il possibile movimento e i cerchi rossi
        for pedina in pedine: 
            pedina.disegna_movimento(screen, pedine, grid_properties)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
