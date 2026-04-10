# How-To: Training your Mancala RL Agent

This guide will walk you through the process of training a Reinforcement Learning (RL) agent using the Maskable PPO algorithm. By the end, you'll have an AI that can play Mancala at a competitive level.

---

## 🚀 1. Setup Environment

Before training, ensure you have all dependencies installed. It is recommended to use a virtual environment.

```bash
# Install required libraries
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
