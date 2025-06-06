## 🌳 Project Structure

The following image shows the function of the different contents:

<p align="center">
  <img align="middle" width="800" src="structure.png">
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

