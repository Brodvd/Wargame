# Wargame – Game Manual

## 1. Game Objective

Two teams face off on a grid-based battlefield. Each team consists of a certain number of unit types (pieces) (infantry, tanks, artillery, etc.) that act once per turn, while the map is divided into cells, each with a terrain type that can influence movement, defense, and line of sight. The team that eliminates all opposing units or reaches the objective score first wins.

---

## 2. Unit Properties

Each unit possesses:
- **Name**
- **Type** (e.g., Rifle, Medium Tank, Mortar, etc.)
- **Health Points (HP)**
- **Movement Distance** (how many cells it can move)
- **Attack Distance** (range within which it can hit)
- **Firepower** (damage inflicted)
- **Shots per Turn** (how many attacks it can perform)
- **Hit Probability** (each shot has a certain probability of dealing damage, otherwise it will miss the target)
- **Point Value** (for team balancing)

---

## 3. Unit Types
Below is a list of all unit types with their properties:

| Unit         | Point Value | HP  | Move Distance | Attack Distance | Fire Power | Number Shots | Hit Probability | Note                                                  |
| :------------ | :---------: | :-: | :-----------: | :-------------: | :--------: | :----------: | :-------------: | :---------------------------------------------------- |
| rifle         | 50          | 50  | 2             | 2               | 10         | 1            | 0.9             | Basic unit                                            |
| assault rifle | 100         | 50  | 3             | 2               | 10         | 2            | 0.85            | More mobile, higher volume of fire                    |
| LMG           | 150         | 80  | 2             | 3               | 15         | 2            | 0.75            | Support infantry, greater range/HP                    |
| MMG           | 200         | 90  | 1             | 3               | 18         | 3            | 0.7             | Heavy fire, slow, defensive                           |
| HMG           | 250         | 100 | 1             | 4               | 20         | 3            | 0.65            | Maximum anti-infantry fire, very slow                 |
| pyromaniac    | 175         | 60  | 3             | 1               | 30         | 1            | 0.8             | Close-quarters assault, very powerful but vulnerable, `HE` |
| howitzer      | 225         | 90  | 2             | 10              | 75         | 1            | 0.75            | Heavy artillery, powerful against vehicles, `HE`      |
| mortar        | 150         | 60  | 2             | 10              | 40         | 1            | 0.8             | Light indirect artillery, `HE`                        |
| anti tank     | 250         | 75  | 1             | 5               | 100        | 1            | 0.9             | Anti-tank specialist, lethal but vulnerable           |
| armored       | 350         | 150 | 4             | *HMG* | *HMG* | *HMG* | *HMG* | Infantry support                                      |
| medium tank   | 400         | 300 | 3             | 4* | 70* | 1* | 0.85* | Main battle tank,   adaptable                         |
| heavy tank    | 500         | 500 | 2             | 4* | 90* | 1* | 0.85* | Assault tank, very durable                            |

`*` Values used for vehicle vs. vehicle combat; otherwise, if the opponent is an infantry unit, these values are replaced by those of the *HMG*.

---

## 4. Turn Progression

1.  **Unit Selection:** The player selects one of their units that has not yet acted.
2.  **Action Choice:** For each unit, you can choose between:
    -   **Shoot:** Attacks an enemy unit with effective damage within range.
    -   **forward:** Move up to the movement distance and, if possible, immediately attack with half effective damage after moving.
    -   **Move:** Move the unit up to its movement distance plus one square.
    -   **Ambush:** The unit remains stationary but prepares to strike with double normal damage on its next turn.
    -   **Rally:** Recovers health points.
    -   **Down:** The unit remains stationary but gains an additional defense bonus for one turn.
3.  **Action Resolution:** The action is executed, and prints appear in the console.
4.  **End Turn:** When all units of a team have acted, the turn passes to the other team.

---

## 5. Terrain

- Each cell can affect movement, defense, and attack.
- Consult the following legend for details on terrain types:

| Terrain  | Defense Bonus (%) | Movement Cost | Attack Cost | Blocks Line of Sight | Walkable |
| :------- | :---------------: | :-----------: | :---------: | :------------------: | :------: |
| forest   | 30                | -1            | 0           | false                | true     |
| hill     | 0                 | -1            | 3           | true                 | true     |
| river    | 0                 | 0             | 0           | false                | false    |
| plain    | 0                 | 0             | 0           | false                | true     |
| building | 0                 | 0             | 0           | true                 | false    |
| road     | 0                 | 1             | 0           | false                | true     |
| bridge   | 10                | 1             | 0           | false                | true     |
| rough    | 0                 | -1            | 0           | false                | true     |
| ruined   | 20                | -1            | 0           | true                 | true** |
| cover    | 30                | -1            | 2           | false                | true* |

- `*` Passable by all units except vehicles
- `**` Passable by all units that are not vehicles or artillery
**NOTE:** "Ruined" refers to a ruined building, therefore not passable by vehicles and artillery but only soldiers, while "cover" refers to small trenches built with sandbags or stones.

---

## 6. Movement

- Units can only move onto "walkable" cells.
- Movement can be affected by terrain type (e.g., forests, hills, etc.) which modify the maximum distance.
- You cannot enter a cell already occupied by another unit.

---

## 7. Attack

- You can only attack if the target is within range and visible (clear line of sight, except for howitzers or mortars).
- Some weapons can hit multiple times per turn.
- Damage can vary slightly due to random effects (within a range of +/- 25% of initial damage) to simulate various weapon defects.
- Terrain defense bonus and "down" status reduce damage taken.
- Some unit types cannot hit certain targets (e.g., rifle against tank); in such cases, the attack stops.
- Some units possess area damage (`HE`). This works as follows:
  - An enemy is selected.
  - An explosion occurs in each cell within a one-square radius around the target, with the same mechanics as a traditional hit from other units, but a single action covers multiple cells.

---

## 8. Scoring and Victory

- Each eliminated unit earns points for the opponent equal to its value, as seen on the counter in the top center of the screen.
- The player who eliminates all opposing units, reaching the established maximum score, wins.

---

## 9. Known Issues
- Pygame does not directly support animation playback, only single images. In fact, GIFs are played as a sequence of images at the FPS speed. However, this means that during animation playback, Pygame is "suspended" until the GIF finishes, so the screen freezes while playing the animation, but all clicks and actions are not executed.

**For questions or concerns, consult the Issues section of the repository!**
