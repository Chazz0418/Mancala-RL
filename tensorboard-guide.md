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
    - In Phase 1 (vs Random), this will climb steadily as the AI learns to beat a bad opponent.
    - In Phase 2 (Self-Play), this line will look like a staircase. Every time a new generation starts, the AI faces a harder version of itself, so the score drops. As it figures out a new counter-strategy, the score climbs back up.
*   **Convergence**: When this line flattens out and stops rising for a very long time, the agent has learned as much as it can.

### 2. `rollout/ep_len_mean` (The "Game Length")
*   **What it is**: The average number of turns a game lasts.
*   **What to look for**: In Mancala, you generally want this to go **DOWN** or stabilize.
*   **Context**: If this number is very high, the AI is likely playing aimlessly and dragging the game out. A dropping line means the AI is finding efficient, ruthless ways to end the game quickly.

### 3. `train/loss` (The "Headache" Meter)
*   **What it is**: How much the AI is struggling to predict the outcome of its actions.
*   **What to look for**: It should start high and eventually drop and **STABILIZE**.
*   **Context**: It will never reach zero. If it suddenly spikes massively late in training, it might indicate "catastrophic forgetting" (the AI suddenly got confused).

### 4. `train/entropy_loss` (The "Decisiveness" Meter)
*   **What it is**: A measure of how random the AI's choices are.
*   **What to look for**: The line should move **UP** (from a low negative number like -1.0 toward 0.0).
*   **Context**: 
    - This graph shows **Negative Entropy**. 
    - A low value (e.g., **-1.0**) means the AI is being "creative" and exploring many options. 
    - A high value (e.g., **-0.2**) means the AI is becoming very certain and decisive. 
    - **Self-Play Pattern**: You will see this "reset" (drop down) at the start of every new generation as the AI explores how to beat its new opponent, then climb back up as it masters the new strategy.

### 5. `train/explained_variance` (The "Understanding" Meter)
*   **What it is**: How well the AI understands the "value" of the current board state.
*   **What to look for**: A number between 0 and 1. Closer to **1.0 is better**.
*   **Context**: If this number is negative or zero, the AI has no idea if it's winning or losing. Once it consistently stays above 0.5, the AI has developed a good "intuition" for the game.

---

## 💡 Quick Troubleshooting

*   **"My `ep_rew_mean` is totally flat and negative!"**
    Your AI is likely stuck making bad moves and isn't learning. Try increasing the `ent_coef` in `train.py` to force it to try new things, or check your Reward Function.
*   **"The graphs disappeared!"**
    Make sure the terminal running TensorBoard didn't close or throw an error. You can always restart the command without losing any data.
*   **"The graphs look like a heart monitor (huge spikes everywhere)."**
    Turn up the "Smoothing" slider on the left.
