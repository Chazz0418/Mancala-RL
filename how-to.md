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

## 🧠 2. Training Methodologies

Training an RL agent is as much an art as it is a science. While this project includes a default "Curriculum" script, there are several viable ways to train a Mancala AI. Each method will produce an agent with a different "playstyle."

### Method A: The 3-Phase Curriculum (Balanced)
This is the default approach in `src/training/train.py`. It is designed to minimize "stalling" (where the AI learns nothing because it loses too fast).
1.  **Phase 1 (Random)**: Learns basic mechanics and scoring.
2.  **Phase 2 (Self-Play)**: Refines tactics by playing against its own previous version.
3.  **Phase 3 (Minimax)**: Polishes the strategy by playing against a planning algorithm.
- **Best for**: A reliable, all-around strong agent.

### Method B: Pure Self-Play (Emergent Strategy)
In this method, you skip the Random and Minimax opponents and have the AI play exclusively against itself from step 1.
- **Why?**: This is how world-class AIs like AlphaZero were trained. It prevents the AI from inheriting "human" biases or flaws from other agents.
- **Result**: Can discover "weird" or unorthodox moves that surprise human players.
- **How-to**: Modify `train.py` to use `RLAgent` as the opponent for all 500k steps.

### Method C: The "Elite" Direct Challenge
Skip the easy phases and train exclusively against a high-depth `MinimaxAgent` (Depth 3+).
- **Why?**: Forces the AI to play "perfectly" from the start. 
- **Risk**: Training may take much longer to "take off" because the AI will lose almost every game for the first 100k steps.
- **Result**: An extremely defensive and cautious agent that prioritizes preventing opponent captures.

### Method D: Targeted Ensemble Training
Train multiple different models—one against `RandomAgent`, one against `Minimax`, and one against `Self`. Then, use the best-performing parts of each.
- **How-to**: Run separate training sessions with different `--model` save paths and compare their win rates in Tournament mode.

---

## ⚙️ 3. Technical Background

To get the most out of training, it's helpful to understand how the agent "sees" the game.

- **Action Masking**: In Mancala, you cannot pick stones from an empty pit. Action masking prevents the AI from even considering invalid moves. This significantly speeds up training by focusing the "brain" only on legal plays.
- **Perspective Normalization**: To simplify learning, the environment always presents the board from the agent's perspective. No matter if the AI is Player 0 or Player 1, it always sees its own pits at indices 0–5 and its store at index 6. 
- **Reward Shaping**: The AI learns by receiving "points" (rewards). While winning is the ultimate goal, we can give smaller rewards for things like "capturing stones" to guide the AI toward good behavior earlier in training.

---

## 📂 4. Directory Map & File Structure

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
