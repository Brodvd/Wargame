# 🕹️ Wargame

This **Wargame** is a turn-based strategy video game inspired by classic tabletop wargames like *[Bolt Action](https://eu.warlordgames.com/collections/bolt-action?srsltid=AfmBOoomOFNwsMfr3qrIDN47BaIVOAbGaVkJNtKUVCzWRagfxdHIy6p0)*, developed in Python with Pygame. The game simulates battles between squads of units on a grid map, with simple but effective rules and very low computer resource usage.

## 💪 Main Features

- **Turn-based gameplay**: Each player controls a squad of units and performs actions such as movement, attack, ambush, heal, etc.
- **Units**: Infantry, tanks, machine guns, mortars, howitzers, armored vehicles, each with unique stats and abilities.
- **Point system**: Each unit has a point cost to balance the squads.
- **Multi-shot attacks**: Some weapons fire multiple shots per turn, each with its own hit probability.
- **Terrain Properties** : Use the battlefield to your advantage to exploit properties such as line of sight or defense bonus.
- **Visual and sound effects**: Explosion animations, missed shots, health bar, ambient and attack sounds.
- **Supervised AI (MLP Neural Network)(in the future)**: The game can record matches and train a bot using a Multilayer Perceptron (MLP, via scikit-learn) and use it as an opponent.
- **Customization**: Easily add new units, change scenarios, rules, and maps via JSON files.

## 💻 Requirements

- Python 3.8+
- [pygame](https://www.pygame.org/)
- [scikit-learn](https://scikit-learn.org/) (only for the AI part)
- [matplotlib](https://matplotlib.org/) (only for the AI part)
- [seaborn](https://seaborn.pydata.org/) (only for the AI part)
- All dependencies can be installed via pip:

```sh
pip install pygame scikit-learn matplotlib seaborn
```

## 🌳 Project Structure

The following image shows the function of the different contents:

<p align="center">
  <img align="middle" width="800" src="doc/structure.png"/>
</p>

And this is the folder-structure:
```
Wargame
│
├── assets
│   ├── background_music.ogg
│   ├── explosion3.png
│   ├── grid_properties.json
│   ├── sound.wav
│   └── (other files)
│
├── doc
│   ├── custom.md
│   ├── rulebook.md
│   └── structure.png
│
├── IA (after)
│   ├── dataset
│   │	└── dataset.json
│   ├── model
│   │	├── strategy_checkpoint.pkl
│   │	├── Policy_model_checkpoint.pkl
│   │	└── Move_model_checkpoint.pkl
│   └── predict
│	└── predict.json
│
├── LICENSE
├── MLP.py
├── README.md
├── main.py
├── requirements.txt
└── variables.py
```
All this allows you to quickly change the scenario simply by creating a copy of the folder `assets/` and modifying it.

## 🏃 Starting the Game

1. Clone the repository and navigate to the project folder.
```
git clone https://github.com/Brodvd/Wargame.git
```
2. Check the rulebook.
3. Make sure you have the resource files (`assets/`), configuration files (`grid_properties.json`, etc.).
4. Build your army respecting the 1000-point limit per squad (if you don't want to use the default one).
5. Start the game with:

```sh
python main.py
```

## 🎮 Gameplay

- **Select a unit** by clicking on it.
- Choose the action using the buttons that appear around the unit (Fire, Forward, Run, Ambush, Rally, Down).
- Move units and attack enemies following the movement rules, line of sight, and weapon-target compatibility.
- The team that eliminates all enemy units and reaches 1000 points wins.

## 🤖 AI and Match Recording

- The game can record each turn in a JSON file to train a supervised bot.
- The bot uses a Multilayer Perceptron (MLP) neural network to learn strategies from the collected data.
- For details on how to train and use the bot, see the separate `readme.md` and the `MLP.py` file.

## 🖌️ Customization

- **Units and squads**: Editable via JSON files in the `assets/` folder.
- **Rules**: You can change unit parameters directly in the code.
- **Animations, images, and sounds**: Replace or add sprites and audio files in the `assets/` folder.
  For more details, see the [custom.md](https://github.com/Brodvd/Wargame/blob/c1910f565838f6671587640123f2ece945e45a53/doc/custom.md) file.

## 📚 Rulebook

For detailed game rules, see the [rulebook](https://github.com/Brodvd/Wargame/blob/c1910f565838f6671587640123f2ece945e45a53/doc/rulebook.md).

## 📖 License

This project is distributed under the GPL-3 license. Images and sounds are for demonstration purposes only.

## 🗃️ Resources

Some resources are temporary and will be improved in the future.
I'm sorry for having written the code in Italian; it will be translated into English in the future.

## ❓ Questions, bugs, or ideas?

For anything, open an issue in this repository ;)
