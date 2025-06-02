import json
import os
import glob
import pickle
from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import learning_curve
import seaborn as sns
import matplotlib.pyplot as plt
from variables import squadraBot, predict_dataset, HEIGHT, GRID_SIZE, HEIGHT_EXTRA_BOTTOM, HEIGHT_EXTRA_TOP

train = True
#test = False
raggio_controllo = 6
team_bot = squadraBot
random_state = 42
cv = 5

# --- Livello 1: Strategia di squadra ---
class TeamStrategyPolicy:
    def __init__(self):
        self.model = MLPClassifier(hidden_layer_sizes=(32,), max_iter=1000, random_state=random_state)
        self.strategies = ["avanza compatto", "attacca a destra", "attacca a sinistra", "attacca centrale", "difendi", "rispondi all'attacco", "ritirati"]
        #---PARAMETRI CONSIDERATI---
        #avanza compatto                        - distanza_baricentri, numero_nemici, numero_alleati
        #attacca a destra, sinistra o centro    - distanza_baricentri, loc
        #difendi                                - hp_tot_nemici
        #rispondi all'attacco                   - distanza_baricentri
        #ritirati                               - hp_tot_alleati, hp_tot_nemici

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)

    def load(self, path):
        with open(path, 'rb') as f:
            self.model = pickle.load(f)

# --- Livello 2: Azione della pedina ---
class WargameSupervisedBot:
    def __init__(self, scenario_file, dataset_folder, model_checkpoint=None, strategy_checkpoint=None, move_checkpoint=None):
        self.scenario_file = scenario_file
        self.dataset_folder = dataset_folder
        self.model_checkpoint = model_checkpoint
        self.strategy_checkpoint = strategy_checkpoint
        self.move_checkpoint = move_checkpoint
        self.grid_properties = None
        self.model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=1000, random_state=random_state)
        self.strategy_policy = TeamStrategyPolicy()
        self.move_model = MLPRegressor(hidden_layer_sizes=(64,), max_iter=1000, random_state=random_state)
        self.pedina_type_mapping = {
            "Fucile": 1,
            "CarroMedio": 2,
            "Piromane": 3,
            "CarroPesante": 4,
            "FucileAssalto": 5,
            "MitragliatriceLeggera": 6,
            "MitragliatriceMedia": 7,
            "MitragliatricePesante": 8,
            "Obice": 9,
            "Mortaio": 10,
            "ArtiglieriaControcarro": 11,
            "Blindato": 12,
        }
        self.strategy_mapping = {s: i for i, s in enumerate(self.strategy_policy.strategies)}
        self.inverse_strategy_mapping = {i: s for s, i in self.strategy_mapping.items()}

    def load_data(self):
        with open(self.scenario_file, 'r') as f:
            self.grid_properties = json.load(f)
        # Carica tutte le mosse da tutti i file .json nella cartella dataset
        all_moves = []
        dataset_files = glob.glob(os.path.join(self.dataset_folder, "*.json"))
        for file_path in dataset_files:
            with open(file_path, 'r') as f:
                try:
                    moves = json.load(f)
                    if isinstance(moves, list):
                        all_moves.extend(moves)
                except Exception as e:
                    print(f"Errore nel caricamento di {file_path}: {e}")
        self.moves = all_moves

    def prepare_strategy_dataset(self):
        X = []
        y = []
        for move in self.moves:
            state = move['state']
            # Numero di alleati e nemici
            alleati = [p for p in state['pedine'] if p['team'] == team_bot]
            nemici = [p for p in state['pedine'] if p['team'] != team_bot]
            numero_alleati = len(alleati)
            numero_nemici = len(nemici)
            # HP totali
            hp_tot_alleati = sum(p.get('hp', 100) for p in alleati)
            hp_tot_nemici = sum(p.get('hp', 100) for p in nemici)
            # Baricentro alleati e nemici
            if alleati and nemici:
                baricentro_alleati = (
                    sum(p['position'][0] for p in alleati) / numero_alleati,
                    sum(p['position'][1] for p in alleati) / numero_alleati
                )
                baricentro_nemici = (
                    sum(p['position'][0] for p in nemici) / numero_nemici,
                    sum(p['position'][1] for p in nemici) / numero_nemici
                )
                # Distanza tra i baricentri
                distanza_baricentri = ((baricentro_alleati[0] - baricentro_nemici[0]) ** 2 +
                                    (baricentro_alleati[1] - baricentro_nemici[1]) ** 2) ** 0.5
                
                # Localizzazione a grandi linee del baricentro nemico sull'ordinata (1,2,3 a seconda se il baricentro si trova in alto, in centro o in basso)
                n_caselle = (HEIGHT-HEIGHT_EXTRA_TOP-HEIGHT_EXTRA_BOTTOM)/GRID_SIZE
                parte = n_caselle/3
                if baricentro_nemici[1] <= parte:
                    loc = 1
                elif baricentro_nemici[1] <= 2*parte:
                    loc = 2
                elif baricentro_nemici[1] <= 3*parte:
                    loc = 3

            feature_vector = [
                numero_alleati,
                numero_nemici,
                distanza_baricentri,
                loc,
                hp_tot_alleati,
                hp_tot_nemici,
            ]
            X.append(feature_vector)
            y.append(move['strategy'])
        return X, y

    def prepare_action_dataset(self, strategies):
        X = []
        y = []
        moves_xy = []
        for move, strategy in zip(self.moves, strategies):
            state = move['state']
            action = move.get('action_bot') or move.get('action_enemy')
            # Considera solo la pedina che ha effettuato l'azione
            if 'action_bot' in move and move['action_bot']:
                action = move['action_bot']
                pedina_name = action['pedina']
                pedina = next((p for p in state['pedine'] if p['name'] == pedina_name and p['team'] == team_bot), None)
            else:
                action = move['action_enemy']
                pedina_name = action['pedina']
                pedina = next((p for p in state['pedine'] if p['name'] == pedina_name and p['team'] != team_bot), None)
            
            if pedina:
                pedina_type = pedina['type']
                position = pedina['position']
                terrain_properties = self.get_terrain_properties(position)
                delta_x, delta_y = self.get_traslation(move)
                distance_to_enemy, nearest_enemy_type, nearest_enemy_hp, enemy_position = self.get_distance_and_enemy_details(position, self.moves)
                enemies_nearby = self.count_enemies_nearby(position, self.moves)
                enemy_terrain_properties = self.get_terrain_properties(enemy_position)
                more_hp = self.more_hp(pedina, nearest_enemy_hp)
                feature_vector = [
                    delta_x,
                    delta_y,
                    enemies_nearby,
                    int(distance_to_enemy),
                    self.pedina_type_mapping.get(pedina_type, 0),
                    self.pedina_type_mapping.get(nearest_enemy_type, 0),
                    more_hp,
                    terrain_properties.get('defense_bonus', 0),
                    terrain_properties.get('movement_cost', 0),
                    terrain_properties.get('attacco_cost', 0),
                    enemy_terrain_properties.get('defense_bonus', 0),
                    self.strategy_mapping.get(strategy, 0),
                ]
                X.append(feature_vector)
                y.append(action['type'])
                moves_xy.append([delta_x, delta_y])  # aggiungi il vettore spostamento
        return X, y, moves_xy

    def get_terrain_properties(self, position):
        for cell in self.grid_properties['cells']:
            if cell['position'] == position:
                terrain_type = cell['terrain']
                return self.grid_properties['terrain_types'][terrain_type]
        return {}

    def train(self):
        # --- Livello 1: Addestra la strategia di squadra ---
        X_strategy, y_strategy = self.prepare_strategy_dataset()
        self.strategy_policy.fit(X_strategy, y_strategy)
        print("Strategia di squadra addestrata.")

        # --- Livello 2: Addestra la policy delle pedine ---
        # Prima ottieni la strategia predetta per ogni mossa
        predicted_strategies = self.strategy_policy.predict(X_strategy)
        X_action, y_action, moves_xy = self.prepare_action_dataset(predicted_strategies)
        self.model.fit(X_action, y_action)
        self.move_model.fit(X_action, moves_xy)
        print(f"Policy delle pedine addestrata su {len(X_action)} esempi.")
        print(f"Modello di spostamento addestrato su {len(moves_xy)} esempi.")

        # Valutazione e grafici (come prima, ma ora su X_action/y_action)
        predictions_all = self.model.predict(X_action)
        accuracy_all = accuracy_score(y_action, predictions_all)
        print(f"\nAccuratezza complessiva policy pedine: {accuracy_all * 100:.2f}%")

        # Curva di apprendimento
        train_sizes, train_scores, test_scores = learning_curve(
            self.model, X_action, y_action, cv=cv, scoring='accuracy', n_jobs=-1,
            train_sizes=[0.2, 0.4, 0.6, 0.8, 1.0]
        )
        train_scores_mean = train_scores.mean(axis=1)
        test_scores_mean = test_scores.mean(axis=1)

        # Curva di apprendimento per il modello di spostamento (MSE)
        train_sizes_move, train_scores_move, test_scores_move = learning_curve(
            self.move_model, X_action, moves_xy, cv=cv, scoring='neg_mean_squared_error', n_jobs=-1,
            train_sizes=[0.2, 0.4, 0.6, 0.8, 1.0]
        )
        train_scores_move_mean = -train_scores_move.mean(axis=1)
        test_scores_move_mean = -test_scores_move.mean(axis=1)

        # Visualizza entrambe le curve in due sottografici
        fig, axs = plt.subplots(1, 2, figsize=(13, 5))

        # Policy delle pedine
        axs[0].plot(train_sizes, train_scores_mean, 'o-', color='blue', label='Accuratezza Training')
        axs[0].plot(train_sizes, test_scores_mean, 'o-', color='orange', label='Accuratezza Cross-Validation')
        axs[0].set_title('Curva di Apprendimento Policy Pedine')
        axs[0].set_xlabel('Numero di esempi di training')
        axs[0].set_ylabel('Accuratezza')
        axs[0].legend(loc='best')
        axs[0].grid()

        # Modello di spostamento
        axs[1].plot(train_sizes_move, train_scores_move_mean, 'o-', color='green', label='MSE Training')
        axs[1].plot(train_sizes_move, test_scores_move_mean, 'o-', color='red', label='MSE Cross-Validation')
        axs[1].set_title('Curva di Apprendimento Spostamento')
        axs[1].set_xlabel('Numero di esempi di training')
        axs[1].set_ylabel('Errore quadratico medio (MSE)')
        axs[1].legend(loc='best')
        axs[1].grid()

        plt.tight_layout()
        plt.show()

        # Matrice di confusione
        cm = confusion_matrix(y_action, predictions_all, labels=self.model.classes_)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=self.model.classes_)
        disp.plot(cmap=plt.cm.Blues)
        plt.title("Matrice di Confusione - Azioni Predette vs Reali")
        plt.show()

        # Grafico delle azioni predette
        sns.countplot(x=predictions_all)
        plt.title("Distribuzione delle azioni predette")
        plt.show()

        # Errore dello spostamento
        moves_xy_pred = self.move_model.predict(X_action)
        error_dx = [pred[0] - real[0] for pred, real in zip(moves_xy_pred, moves_xy)]
        error_dy = [pred[1] - real[1] for pred, real in zip(moves_xy_pred, moves_xy)]
        plt.hist(error_dx, bins=20, alpha=0.5, label='Δx error')
        plt.hist(error_dy, bins=20, alpha=0.5, label='Δy error')
        plt.legend()
        plt.title("Distribuzione errore vettore spostamento")
        plt.show()

        # Salva entrambi i modelli
        with open(self.model_checkpoint, 'wb') as f:
            pickle.dump(self.model, f)
        self.strategy_policy.save(self.strategy_checkpoint)
        with open(self.move_checkpoint, 'wb') as f:
            pickle.dump(self.move_model, f)

    def load_model(self):
        with open(self.model_checkpoint, 'rb') as f:
            self.model = pickle.load(f)
        self.strategy_policy.load(self.strategy_checkpoint)
        with open(self.move_checkpoint, 'rb') as f:
            self.move_model = pickle.load(f)

    def predict(self, pedina_state):
        return self.model.predict([pedina_state])[0]
    
    def predict_move(self, pedina_state):
        dx, dy = self.move_model.predict([pedina_state])[0]
        return int(round(dx)), int(round(dy))

    def run(self):
        # Carica i file di input
        with open('assets/grid_properties.json', 'r') as f:
            self.grid_properties = json.load(f)
        with open(predict_dataset, 'r') as f:
            self.moves = json.load(f)
        self.load_model()

        # Predici la strategia di squadra per ogni mossa
        X_strategy, _ = self.prepare_strategy_dataset()
        predicted_strategies = self.strategy_policy.predict(X_strategy)

        for move, strategy in zip(self.moves, predicted_strategies):
            state = move['state']
            action_enemy = move['action_enemy']
            action_bot = move.get('action_bot', {})
            for pedina in state['pedine']:
                if pedina['team'] == team_bot:
                    pedina_state = self.get_state(pedina, action_bot, strategy)
                    predicted_action = self.predict(pedina_state)
                    predicted_move = self.predict_move(pedina_state)
                    print(f"Pedina {pedina['name']} esegue l'azione: {predicted_action} (strategia: {self.inverse_strategy_mapping[strategy]}), spostamento predetto: Δx={predicted_move[0]}, Δy={predicted_move[1]}")
                else:
                    pedina_state = self.get_state(pedina, action_enemy, strategy)
                    predicted_action = self.predict(pedina_state)
                    predicted_move = self.predict_move(pedina_state)
                    print(f"Pedina {pedina['name']} esegue l'azione: {predicted_action} (strategia: {self.inverse_strategy_mapping[strategy]}), spostamento predetto: Δx={predicted_move[0]}, Δy={predicted_move[1]}")

    def get_state(self, pedina, action, strategy):
        xi, yi = pedina['position']
        xf, yf = action['position']
        delta_x = xf - xi
        delta_y = yf - yi
        pedina_type = pedina['type']
        terrain_properties = self.get_terrain_properties((xf, yf))
        distance_to_enemy, nearest_enemy_type, nearest_enemy_hp, enemy_position = self.get_distance_and_enemy_details((xf, yf), self.moves)
        enemies_nearby = self.count_enemies_nearby((xf, yf), self.moves)
        enemy_terrain_properties = self.get_terrain_properties(enemy_position)
        more_hp = self.more_hp(pedina, nearest_enemy_hp)
        state = [
            delta_x,
            delta_y,
            enemies_nearby,
            int(distance_to_enemy),
            self.pedina_type_mapping.get(pedina_type, 0),
            self.pedina_type_mapping.get(nearest_enemy_type, 0),
            more_hp,
            terrain_properties.get('defense_bonus', 0),
            terrain_properties.get('movement_cost', 0),
            terrain_properties.get('attacco_cost', 0),
            enemy_terrain_properties.get('defense_bonus', 0),
            self.strategy_mapping.get(strategy, 0),
        ]
        return state

    def count_enemies_nearby(self, position, moves, radius=raggio_controllo):
            """Conta il numero di nemici nelle vicinanze di una posizione."""
            count = 0
            for move in moves:
                for pedina in move['state']['pedine']:
                    if pedina['team'] != team_bot:  # Considera solo i nemici
                        enemy_position = pedina['position']
                        distance = ((position[0] - enemy_position[0]) ** 2 + (position[1] - enemy_position[1]) ** 2) ** 0.5
                        if distance <= radius:
                            count += 1
            return count

    def get_distance_and_enemy_details(self, position, moves):
        """Calcola la distanza dal nemico più vicino, il suo tipo, i suoi punti vita e la sua posizione."""
        min_distance = float('inf')
        nearest_enemy_type = None
        nearest_enemy_hp = 0
        enemy_position = None
        for move in moves:
            action_enemy = move.get('action_enemy', {})
            enemy_position = action_enemy.get('position', None)
            if enemy_position:
                distance = ((position[0] - enemy_position[0]) ** 2 + (position[1] - enemy_position[1]) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    nearest_enemy_type = action_enemy.get('type', None)
                    nearest_enemy_hp = next(
                        (pedina.get('hp') for pedina in move['state']['pedine'] if pedina['name'] == action_enemy.get('pedina')),
                        100
                    )
            else: # forse funziona
                for pedina in move['state']['pedine']:
                    if pedina['team'] != team_bot: 
                        enemy_position = pedina['position']
                        distance = ((position[0] - enemy_position[0]) ** 2 + (position[1] - enemy_position[1]) ** 2) ** 0.5
                        if distance < min_distance:
                            min_distance = distance
                            nearest_enemy_type = pedina['type']
                            nearest_enemy_hp = pedina.get('hp', 100)
                            enemy_position = enemy_position

        return min_distance if min_distance != float('inf') else 0, nearest_enemy_type, nearest_enemy_hp, enemy_position

    def get_traslation(self, move):
        """Calcola le coordinate del vettore spostamento (ΔX e ΔY) per la pedina che sta giocando."""
        # Determina quale azione è presente nel turno corrente
        action = move.get('action_bot') or move.get('action_enemy')

        # Trova la pedina che sta giocando
        pedina_name = action['pedina']
        pedina = next((p for p in move['state']['pedine'] if p['name'] == pedina_name), None)

        # Posizione iniziale (dallo stato)
        xi, yi = pedina['position']

        # Posizione finale (dall'azione)
        xf, yf = action['position']

        # Calcola il vettore spostamento
        delta_x = xf - xi
        delta_y = yf - yi
        return delta_x, delta_y

    def more_hp(self, pedina, enemy_hp):
        """Calcola quale delle due pedine ha l'hp maggiore (0 se è la pedina, 1 se è il nemico)"""
        pedina_hp = pedina.get('hp', 100)
        if pedina_hp >= enemy_hp:
            return 0
        else:
            return 1

if __name__ == "__main__":
    bot = WargameSupervisedBot(
        'assets/grid_properties.json',
        'IA/dataset',
        model_checkpoint='IA/model/Policy_model_checkpoint.pkl',
        strategy_checkpoint='IA/model/strategy_checkpoint.pkl',
        move_checkpoint='IA/model/Move_model_checkpoint.pkl'
    )
    if train:
        bot.load_data()
        bot.train()
    else:
        bot.run()
