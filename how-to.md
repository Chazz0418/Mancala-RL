# Mancala RL: Training & Development Guide

Welcome to the Mancala Reinforcement Learning project. This guide provides a comprehensive overview of how to train, evaluate, and customize an AI agent using the Maskable PPO algorithm.

---

## 🚀 1. Getting Started

### Prerequisites
- Python 3.8 or higher.
- A virtual environment is highly recommended.

### Installation
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Chazz0418/Mancala-RL.git
    cd Mancala-RL
    ```
2.  **Initialize the Game Engine (Submodule)**:
    The core game logic lives in a separate repository linked as a submodule. You **must** run this command to fetch the engine code:
    ```bash
    git submodule update --init --recursive
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🧠 2. How Training Works

This project uses **Reinforcement Learning (RL)**, specifically the **Proximal Policy Optimization (PPO)** algorithm from the `stable-baselines3` library.

### Key Concepts
- **Action Masking**: In Mancala, you cannot pick from an empty pit. Action masking prevents the AI from even considering invalid moves, which significantly speeds up training.
- **Perspective Normalization**: To the AI, it is always "Player 0." The environment automatically flips the board so that the AI's pits are always at indices 0–5 and its store is at 6.
- **Curriculum Learning**: Instead of facing a grandmaster immediately, the AI follows a 3-phase training schedule to gradually increase difficulty.

### The 3-Phase Curriculum
1.  **Phase 1: Foundation (vs Random)**
    - **Goal**: Learn the rules and basic scoring.
    - **Opponent**: `RandomAgent`.
2.  **Phase 2: Strategy (Self-Play)**
    - **Goal**: Discover advanced tactics and counter-plays.
    - **Opponent**: The model's own "Phase 1" version.
3.  **Phase 3: Optimization (vs Minimax)**
    - **Goal**: Learn to beat planning algorithms.
    - **Opponent**: `MinimaxAgent` (Depth 2).

---

## 📂 3. Directory Map & File Structure

### Agents & Models
- **`models/best_model/best_model.zip`**: The "gold standard" agent. This is the model that achieved the highest win rate during evaluation. The GUI loads this by default.
- **`models/phase_x_final.zip`**: Snapshots taken at the end of each training phase.
- **`models/rl_model_XXXXX_steps.zip`**: Checkpoints saved every 50,000 steps during training.
- **`logs/`**: Contains TensorBoard data for monitoring win rates, rewards, and learning loss.

### Source Code
- **`src/env_wrapper.py`**: The "Mancala-to-Gym" translator. This defines the observation space and the **Reward Function**.
- **`src/training/train.py`**: The main training logic and curriculum definition.
- **`src/agents/rl_agent.py`**: The bridge that allows a saved `.zip` model to play in the game engine.
- **`src/gui/`**: All visual components (Pygame).

---

## 🛠️ 4. Customizing your Agent

To create a unique agent that plays differently than others, you can tweak the following "levers":

### Lever A: The Reward Function (`src/env_wrapper.py`)
Edit the `step()` method to change the agent's motivation:
- **Aggressive**: `reward += 0.2` if `capture_occurred`.
- **Greedy**: Increase the weight of the store score difference.
- **Efficiency**: `reward -= 0.01` per step to encourage fast wins.

### Lever B: Neural Network Architecture (`src/training/train.py`)
Change the complexity of the agent's "brain" via `policy_kwargs`:
- **Default**: `[128, 128]` (Two layers of 128 neurons).
- **Deep**: `[256, 256, 256]` (Better at complex patterns, slower to train).

### Lever C: Hyperparameters (`src/training/train.py`)
- **`learning_rate`**: How fast the agent updates its knowledge (e.g., `3e-4`).
- **`gamma`**: The "discount factor." `0.99` means it cares about long-term victory; `0.80` makes it very short-sighted.

---

## 📈 5. Evaluation & Monitoring

### Real-time Progress (TensorBoard)
To see graphs of the agent's performance during training:
```bash
tensorboard --logdir ./logs/
```
View the results at `http://localhost:6006`.

### Automated Tournament
Run a headless batch of games to get a win-rate percentage:
```bash
python main.py --mode tournament --games 100 --model models/best_model/best_model.zip
```

### GUI Watch Mode
Observe the AI playing against another AI in the visual interface:
1.  Run `python main.py`.
2.  Select **"AI vs AI Watch"**.

---

## 📝 Training Commands

**Start a new training run (Default 500k steps):**
```bash
python main.py --mode train --steps 500000
```

**Resume training from a checkpoint:**
Modify the `--resume` argument in the CLI or update the path in `train.py`.
