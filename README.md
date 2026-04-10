# Mancala RL (Kalah Variant)

A Reinforcement Learning environment and GUI for playing and training agents in the Kalah variant of Mancala. This project features a Pygame-based visual interface, a Gymnasium-compatible environment wrapper, and a multi-phase RL training pipeline using Maskable PPO.

---

## ✨ Features
- **Interactive GUI**: Play against a trained AI, a Random agent, or a Minimax algorithm.
- **Watch Mode**: Observe AI vs AI matches in real-time.
- **RL Training**: A pre-configured curriculum that takes an agent from zero knowledge to competitive play.
- **Tournament Mode**: Run headless, high-speed simulations to compare different agents.
- **Rule Accuracy**: Implements all standard Kalah rules, including extra turns, captures, and end-game sweeps.

---

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/Chazz0418/Mancala-RL.git
cd Mancala-RL
git submodule update --init --recursive
pip install -r requirements.txt
```

### 2. Launch the Game
```bash
python main.py
```

---

## 📚 Documentation
For detailed instructions on training your own AI models, customizing rewards, or tweaking neural network architectures, see:

👉 **[Training & Development Guide (how-to.md)](how-to.md)**

---

## 📂 Project Structure
- `mancala_ai/`: The core game engine (Git submodule).
- `src/`: Custom environment wrapper, AI agents, and GUI components.
- `models/`: Saved RL models and checkpoints.
- `logs/`: TensorBoard training logs.

---

## 🤝 Contributing
This project was developed to explore the intersection of classical board game AI (Minimax) and modern Reinforcement Learning (PPO). Feel free to fork, experiment, and train your own unique agents!
