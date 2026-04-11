# 📊 TensorBoard Guide: Understanding Your RL Agent

TensorBoard is your window into the "brain" of your Reinforcement Learning agent. When you train a model using `stable-baselines3` (specifically PPO), it outputs a lot of data. This guide will help you focus on what actually matters.

---

## 🚀 How to Launch TensorBoard

Open a terminal in your project folder and run:
```bash
python -m tensorboard.main --logdir ./logs/
```
Then, open your web browser and go to: `http://localhost:6006`

---

## 🔍 Navigating the Interface

### 1. The Left Sidebar (Runs)
Every time your training script starts a new phase or generation (e.g., `phase_1_0`, `phase_2_gen_1_0`), a new "run" appears here.
- **Tip**: You can check or uncheck these boxes to overlay different training runs on the same graph. This is incredibly useful for comparing Phase 1 vs Phase 2, or comparing your agent against your friend's!

### 2. The Smoothing Slider (Top Left)
RL training is naturally noisy (the graphs jump up and down constantly). 
- **Tip**: Keep the "Smoothing" slider around **0.8 or 0.9**. This draws a solid line through the noise so you can easily see the overall trend.

---

## 📉 The Most Important Graphs

There are dozens of graphs, but you only need to watch a few to know if your agent is learning.

### 1. `rollout/ep_rew_mean` (The "Scoreboard")
*   **What it is**: The average reward the agent gets per episode (game).
*   **What to look for**: This line should go **UP**.
*   **Context**: 
    - **Phase 1 (vs Random)**: A rapid climb here means the AI is quickly learning the basic rules and scoring. 
    - **Phase 2 (Self-Play)**: Expect a "sawtooth" pattern. Every time a new generation starts, the reward will drop (as the AI faces a harder version of itself) and then climb back up as it solves the new challenge.
    - **Phase 4 (Refinement)**: In this phase, `incremental_reward` is OFF. A value of **1.0** means 100% win rate, **0.0** means 50/50, and **-1.0** means 100% loss.
*   **Convergence**: When this line flattens into a high plateau, the agent has mastered its current opponent.

### 2. `rollout/ep_len_mean` (The "Game Length")
*   **What it is**: The average number of turns per game.
*   **What to look for**: A steady **DOWNWARD** slope or a low plateau.
*   **Context**: 
    - **Efficiency**: A high-level Mancala AI wins by making powerful combos and captures that end the game faster. 
    - **Stalling**: If this number is increasing while your reward is flat, your AI might be "running away" from the opponent without actually trying to win, dragging the game out.
    - **Sudden Drops**: A sharp drop in game length usually means the AI has discovered a "kill shot" strategy or a way to trigger the end-game sweep early.

### 3. `train/loss` (The "Headache" Meter)
*   **What it is**: A combined measure of how well the AI predicts rewards and how much it updates its policy.
*   **What to look for**: It should start high, then drop and **STABILIZE**.
*   - **Initial Spike**: Large spikes early on are normal as the "brain" is essentially in shock from new data.
    - **Plateau**: As long as the line is stable (not exploding upward), the training is healthy.
    - **Spike at Phase Change**: You will see a small spike whenever you change opponents (e.g., switching to Minimax). This is just the AI adjusting to a new style of play.

### 4. `train/entropy_loss` (The "Decisiveness" Meter)
*   **What it is**: A measure of how random the AI's choices are.
*   **What to look for**: The line should move **UP** (from a low negative number like -1.0 toward 0.0).
*   **Context**: 
    - This graph shows **Negative Entropy**. 
    - A low value (e.g., **-1.0**) means the AI is being "creative" and exploring many options. 
    - A high value (e.g., **-0.2**) means the AI is becoming very certain and decisive. 
    - **Self-Play Pattern**: You will see this "reset" (drop down) at the start of every new generation as the AI explores how to beat its new opponent, then climb back up as it masters the new strategy.

### 5. `train/explained_variance` (The "Understanding" Meter)
*   **What it is**: Measures how accurately the AI can predict the "Value" (winning potential) of any given board state.
*   **What to look for**: A line moving from near 0.0 toward **1.0**.
*   **Context**: 
    - **Values < 0**: The AI's "intuition" is worse than random guessing. This is common at the very start of training.
    - **Values > 0.5**: The AI has a strong grasp of the board state. It can accurately tell you "I am currently winning" or "I am in trouble" before the game even ends.
    - **The Goal**: High-level agents usually stay between **0.8 and 0.9**.

---

## 💡 Quick Troubleshooting

*   **"My `ep_rew_mean` is totally flat and negative!"**
    Your AI is likely stuck making bad moves and isn't learning. Try increasing the `ent_coef` in `train.py` to force it to try new things, or check your Reward Function.
*   **"The graphs disappeared!"**
    Make sure the terminal running TensorBoard didn't close or throw an error. You can always restart the command without losing any data.
*   **"The graphs look like a heart monitor (huge spikes everywhere)."**
    Turn up the "Smoothing" slider on the left.
