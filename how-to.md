# How-To: Training your Mancala RL Agent

This guide will walk you through the process of training a Reinforcement Learning (RL) agent using the Maskable PPO algorithm. By the end, you'll have an AI that can play Mancala at a competitive level.

---

## 🚀 1. Setup Environment

Before training, ensure you have all dependencies installed. It is recommended to use a virtual environment.

```bash
# 1. Clone the repository (if using Git)
git clone <repository-url>
cd Mancala

# 2. Initialize the game engine submodule (CRITICAL)
# If you downloaded a ZIP, ensure the 'mancala_ai' folder is not empty.
# If using Git, run:
git submodule update --init --recursive

# 3. Install required libraries
pip install -r requirements.txt
```

*Note: This project uses `pygame-ce` for the GUI and `stable-baselines3` with `sb3-contrib` for the RL logic.*

---

## 🏋️ 2. Starting a Training Session

The training is handled entirely through `main.py`. To start a default training session (100,000 steps), run:

```bash
python main.py --mode train --steps 100000
```

### The 3-Phase Curriculum
The training script follows a "curriculum" to help the AI learn effectively:
1.  **Phase 1 (Random)**: The AI plays against a Random opponent to learn the basic rules and simple scoring.
2.  **Phase 2 (Self-Play)**: The AI plays against its own "Phase 1" version to discover more advanced strategies.
3.  **Phase 3 (Minimax)**: The AI plays against a Minimax planning algorithm to learn how to counter "look-ahead" strategies.

---

## 📊 3. Monitoring Progress

While the AI is training, you can watch its "learning curve" using **TensorBoard**.

1.  Open a new terminal in the project folder.
2.  Run the following command:
    ```bash
    tensorboard --logdir ./logs/
    ```
3.  Open the URL provided (usually `http://localhost:6006`) in your browser.

**What to look for:**
- `rollout/ep_rew_mean`: This should steadily increase. It represents the average reward the agent is getting per game.
- `train/loss`: This should eventually stabilize.

---

## 📁 4. Where is my Agent?

Trained models are saved automatically in the `/models` directory:

- **`models/best_model/best_model.zip`**: The most successful version of the AI found during training.
- **`models/phase_x_final.zip`**: The snapshot of the AI at the end of each training phase.
- **`models/rl_model_XXXXX_steps.zip`**: Periodic checkpoints saved every 50,000 steps.

---

## 🎮 5. Playing Against Your Agent

Once training is complete (or even while it's still running), you can test your agent in the GUI:

```bash
# Launch the GUI
python main.py
```

1.  Click **"Human vs AI"**.
2.  The game will automatically load the model from `models/best_model/best_model.zip`.
3.  If no model is found, the game will default to a Random AI.

---

## 🏆 6. Running a Tournament

To see how your trained agent performs against a Minimax AI without the GUI, use the tournament mode:

```bash
python main.py --mode tournament --games 100 --model models/best_model/best_model.zip
```

This will run 100 games in the console and give you a final win/loss percentage.

---

## 💡 Tips for Better Training

- **Patience**: A good agent usually needs at least **300,000 to 500,000 steps** to become very strong.
- **CPU vs GPU**: This training runs on the CPU by default. It is lightweight enough that you can still use your computer for other tasks while it runs.
- **Incremental Training**: If you want to continue training from a specific file, you can modify the `resume_from` logic in `src/training/train.py`.

---

## 🧪 Advanced: Creating a Unique Agent

If you and a friend use the default settings, your agents will play very similarly. To create an AI with a unique "personality" or strategy, try experimenting with these files:

### 1. Change the "Personality" (Reward Function)
Open `src/env_wrapper.py` and find the `step()` method. You can change what the AI "cares" about:
- **Aggressive**: Give it a small reward `+0.1` every time it performs a **capture**.
- **Efficiency**: Give it a small penalty `-0.01` for every turn it takes to encourage faster wins.
- **Greedy**: Increase the `incremental_reward` for every stone added to its store.

### 2. Change the "Brain" (Neural Network)
Open `src/training/train.py` and look for `policy_kwargs`.
- **Deeper Brain**: Change `[128, 128]` to `[256, 256, 256]` for a more complex "thinking" process (requires more training time).
- **Simple Brain**: Change to `[64, 64]` for a faster, more reactive agent.

### 3. Change the "Schooling" (Curriculum)
In `src/training/train.py`, you can alter the phases:
- **Hard Mode**: Skip the Random phase and go straight to Minimax.
- **Pure Self-Play**: Train exclusively against the `RLAgent` for all 500k steps. This often results in "unorthodox" strategies that can surprise human players.

### 4. Hyperparameters
In the `MaskablePPO` initialization in `src/training/train.py`:
- **`learning_rate`**: Default is `3e-4`. Try `1e-4` for more stable, careful learning.
- **`gamma`**: Default is `0.99`. Lowering this (e.g., `0.90`) makes the AI care more about immediate points than long-term victory.
