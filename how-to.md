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
Skip the Random and Minimax opponents and have the AI play exclusively against itself from step 1.
- **Why?**: This is how world-class AIs like AlphaZero were trained. It prevents the AI from inheriting biases from other agents.
- **Result**: Can discover unorthodox moves that surprise human players.
- **Implementation**: Modify `train.py` to use `RLAgent` as the opponent for all steps.

### Method C: The "Elite" Direct Challenge
Skip the easy phases and train exclusively against a high-depth `MinimaxAgent` (Depth 3+).
- **Why?**: Forces the AI to play "perfectly" from the start. 
- **Risk**: Training may take much longer to "take off" because the AI will lose almost every game initially.
- **Result**: An extremely defensive agent that prioritizes preventing opponent captures.

### Method D: Targeted Ensemble Training
Train multiple different models—one against `RandomAgent`, one against `Minimax`, and one against `Self`. Use Tournament mode to find which one performs best in specific scenarios.

---

## ⚙️ 3. Technical Background

To get the most out of training, it's helpful to understand the underlying mechanics of how the agent interacts with the Mancala environment.

### The Observation Space (What the AI "Sees")
The AI perceives the game board as a 1D array of 14 integers:
- **Indices 0–5**: The AI's own pits (left to right).
- **Index 6**: The AI's own store (Mancala).
- **Indices 7–12**: The opponent's pits (relative to the AI).
- **Index 13**: The opponent's store.
*Note: Thanks to **Perspective Normalization**, the AI always views itself as "Player 0," regardless of whether it actually moved first or second in the engine.*

### The Action Space (What the AI "Does")
The AI has a **Discrete(6)** action space. It simply chooses a number from 0 to 5, representing which of its 6 pits it wants to pick stones from.

### Action Masking (Why it's faster)
In standard RL, if an agent chooses an invalid move (like an empty pit), it usually receives a penalty and the turn is wasted. This is slow and inefficient.
- **How it works**: We use `sb3-contrib`'s **MaskablePPO**. This algorithm "masks out" the probability of choosing invalid pits before the AI even makes a decision.
- **Benefit**: The AI never makes a "mistake" regarding the rules, allowing it to focus 100% of its energy on strategy rather than rule-following.

### Maskable PPO Algorithm
We use **Proximal Policy Optimization (PPO)**, which is an industry-standard actor-critic algorithm. It is known for being stable, reliable, and relatively easy to tune. The "Maskable" variant is a specialized version that natively supports the action masking described above.

### Reward Shaping (Motivation)
By default, the AI is "sparse-reward" driven (+1 for a win, -1 for a loss). However, the environment supports **Incremental Rewards**:
- If enabled, the AI receives a tiny reward every turn based on the difference in store scores. This "dense reward" helps the AI understand that "more stones in store = good" much earlier in the training process.

---

## 📂 4. Directory Map & File Structure

### Agents & Models
- **`models/best_model/best_model.zip`**: The most successful version of the AI found during evaluation. The GUI loads this by default.
- **`models/phase_x_final.zip`**: Snapshots taken at the end of each training phase.
- **`models/rl_model_XXXXX_steps.zip`**: Checkpoints saved every 50,000 steps.
- **`logs/`**: Contains TensorBoard data for monitoring rewards and learning progress.

### Source Code
- **`src/env_wrapper.py`**: The "Mancala-to-Gym" translator. Defines the observation space and **Reward Function**.
- **`src/training/train.py`**: The main training logic and curriculum definition.
- **`src/agents/rl_agent.py`**: The bridge that allows a saved `.zip` model to play in the game engine.
- **`src/gui/`**: All visual components (Pygame).

---

## 🛠️ 5. Customizing your Agent: The "Levers"

To create a unique agent, you can tweak these specific "levers" in the code:

### Lever A: The Reward Function (`src/env_wrapper.py`)
Edit the `step()` method to change what the agent values:
- **`incremental_reward`**: If `True`, the agent gets tiny rewards `(score_diff / 48 * 0.01)` every turn. Increasing this makes the agent "greedier" for immediate points.
- **Capture Bonus**: Add `reward += 0.2` inside the capture logic to make the agent prioritize stealing stones.
- **Speed Penalty**: Add `reward -= 0.01` for every turn to force the agent to find the fastest way to end the game.

### Lever B: Neural Network Architecture (`src/training/train.py`)
Modify the `policy_kwargs` to change the size of the AI's "brain":
- **Default**: `[128, 128]` (Two layers of 128 neurons).
- **Deeper**: `[256, 256, 256]` (Better at complex patterns, but slower to train).
- **Wider**: `[512, 512]` (Good for recognizing a vast number of board states).

### Lever C: Training Hyperparameters (`src/training/train.py`)
- **`learning_rate`**: Default `3e-4`. Lower values (e.g., `1e-4`) make learning more stable but slower.
- **`gamma`**: Default `0.99`. Lowering this (e.g., `0.80`) makes the agent care more about immediate points than the final outcome.
- **`ent_coef`**: Controls exploration. Increase this if the agent gets "stuck" in a bad strategy and stops trying new things.
- **`n_envs`**: Number of parallel environments. Set this to match your CPU cores for maximum training speed.

---

## 📈 6. Training & Evaluation Commands

### Core Training Commands
**Start default training (100k steps):**
```bash
python main.py --mode train --steps 100000
```

**Run a full 500k step curriculum:**
```bash
python main.py --mode train --steps 500000
```

**Resume training from a specific model:**
```bash
python main.py --mode train --steps 200000 --resume ./models/phase_1_final.zip
```

### Monitoring & Evaluation
**Watch the AI learn (TensorBoard):**
```bash
tensorboard --logdir ./logs/
```

**Run a 100-game Headless Tournament (AI vs Minimax):**
```bash
python main.py --mode tournament --games 100 --model models/best_model/best_model.zip
```

**Test a specific checkpoint in the GUI:**
```bash
python main.py --model models/rl_model_50000_steps.zip
```

### Playing the Game
**Launch the GUI:**
```bash
python main.py
```
- **Human vs AI**: You play against the model at `models/best_model/best_model.zip`.
- **AI vs AI Watch**: Watch the AI play against a Depth-3 Minimax algorithm.
