import json
import pickle
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import learning_curve
import matplotlib.pyplot as plt
from variables import squadraBot, file_dataset

train = True
test = False
autoParam = False
raggio_controllo = 6
team_bot = squadraBot

# --- Livello 1: Strategia di squadra ---
class TeamStrategyPolicy:
    def __init__(self):
        self.model = MLPClassifier(hidden_layer_sizes=(32,), max_iter=1000, random_state=42)
        self.strategies = ["avanza compatto", "attacca a destra", "attacca a sinistra", "attacca centrale", "difendi", "rispondi all'attacco", "ritirati"]

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
    def __init__(self, scenario_file, moves_file, model_checkpoint=None, strategy_checkpoint=None):
        self.scenario_file = scenario_file
        self.moves_file = moves_file
        self.model_checkpoint = model_checkpoint
        self.strategy_checkpoint = strategy_checkpoint
        self.grid_properties = None
        self.model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=1000, random_state=42)
        self.strategy_policy = TeamStrategyPolicy()
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
        with open(self.moves_file, 'r') as f:
            self.moves = json.load(f)

    def prepare_strategy_dataset(self):
        # Esempio: usa feature globali (numero unità per lato, posizione media, ecc.)
        X = []
        y = []
        for move in self.moves:
            state = move['state']
            # Feature globali semplici: puoi arricchirle!
            num_alleati = sum(1 for p in state['pedine'] if p['team'] == team_bot)
            num_nemici = sum(1 for p in state['pedine'] if p['team'] != team_bot)
            # Posizione media alleati/nemici
            pos_alleati = [p['position'] for p in state['pedine'] if p['team'] == team_bot]
            pos_nemici = [p['position'] for p in state['pedine'] if p['team'] != team_bot]
            if pos_alleati and pos_nemici:
                media_alleati_x = sum(x for x, y in pos_alleati) / len(pos_alleati)
                media_nemici_x = sum(x for x, y in pos_nemici) / len(pos_nemici)
            else:
                media_alleati_x = media_nemici_x = 0
            # Feature globali
            feature_vector = [
                num_alleati,
                num_nemici,
                media_alleati_x,
                media_nemici_x,
            ]
            X.append(feature_vector)
            # Usa la strategia annotata per ogni dataset (un dataset corrisponde ad una strategia)
            y.append(move['strategy'])
        return X, y

    def prepare_action_dataset(self, strategies):
        X = []
        y = []
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
        return X, y

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
        X_action, y_action = self.prepare_action_dataset(predicted_strategies)
        self.model.fit(X_action, y_action)
        print(f"Policy delle pedine addestrata su {len(X_action)} esempi.")

        # Valutazione e grafici (come prima, ma ora su X_action/y_action)
        predictions_all = self.model.predict(X_action)
        accuracy_all = accuracy_score(y_action, predictions_all)
        print(f"\nAccuratezza complessiva policy pedine: {accuracy_all * 100:.2f}%")

        # Curva di apprendimento
        train_sizes, train_scores, test_scores = learning_curve(
            self.model, X_action, y_action, cv=2, scoring='accuracy', n_jobs=-1,
            train_sizes=[0.2, 0.4, 0.6, 0.8, 1.0]
        )
        train_scores_mean = train_scores.mean(axis=1)
        test_scores_mean = test_scores.mean(axis=1)

        plt.figure(figsize=(8, 5))
        plt.plot(train_sizes, train_scores_mean, 'o-', color='blue', label='Accuratezza Training')
        plt.plot(train_sizes, test_scores_mean, 'o-', color='orange', label='Accuratezza Cross-Validation')
        plt.title('Curva di Apprendimento Policy Pedine')
        plt.xlabel('Numero di esempi di training')
        plt.ylabel('Accuratezza')
        plt.legend(loc='best')
        plt.grid()
        plt.tight_layout()
        plt.show()

        # Matrice di confusione
        cm = confusion_matrix(y_action, predictions_all, labels=self.model.classes_)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=self.model.classes_)
        disp.plot(cmap=plt.cm.Blues)
        plt.title("Matrice di Confusione - Azioni Predette vs Reali")
        plt.show()

        # Salva entrambi i modelli
        with open(self.model_checkpoint, 'wb') as f:
            pickle.dump(self.model, f)
        self.strategy_policy.save(self.strategy_checkpoint)

    def load_model(self):
        with open(self.model_checkpoint, 'rb') as f:
            self.model = pickle.load(f)
        self.strategy_policy.load(self.strategy_checkpoint)

    def predict(self, pedina_state):
        return self.model.predict([pedina_state])[0]

    def run(self):
        # Carica i file di input dalla cartella IA/predict/
        with open('assets/grid_properties.json', 'r') as f:
            self.grid_properties = json.load(f)
        with open('IA/predict/predict_right.json', 'r') as f:
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
                    print(f"Pedina {pedina['name']} esegue l'azione: {predicted_action} (strategia: {self.inverse_strategy_mapping[strategy]})")

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
        file_dataset,
        model_checkpoint='IA/model/Policy_model_checkpoint.pkl',
        strategy_checkpoint='IA/model/strategy_checkpoint.pkl'
    )
    if train:
        bot.load_data()
        bot.train()
    else:
        bot.run()
