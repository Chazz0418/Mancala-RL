# Mancala ML/RL Project Plan

## Context
Building a Mancala (Kalah variant) project from scratch in an empty directory. The project has two parts: (1) a playable game with a visual GUI, and (2) an ML/RL trained agent. The game engine comes from the CaganKiper/mancala-ai GitHub library (not on PyPI — must be cloned). The user wants to be able to watch matches in a GUI, train an RL agent repeatedly, and run AI vs AI tournaments where the majority winner wins.

---

## Tech Stack
- **Language**: Python
- **Game engine**: CaganKiper/mancala-ai (cloned as git submodule into `mancala_ai/`)
- **GUI**: Pygame
- **RL training**: `stable-baselines3` + `sb3-contrib` (MaskablePPO — handles invalid action masking)
- **Deep learning**: PyTorch (used by SB3 under the hood)

---

## Project Structure
```
Mancala/
├── mancala_ai/              # CaganKiper/mancala-ai (git submodule)
├── src/
│   ├── env_wrapper.py       # Gym-compatible wrapper around KalahEnvironment
│   ├── tournament.py        # N-game tournament runner
│   ├── agents/
│   │   └── rl_agent.py      # Trained PPO agent wrapped in mancala_ai's Agent base class
│   ├── gui/
│   │   ├── board_renderer.py  # Pygame drawing functions
│   │   ├── menu.py            # Start menu (mode selection)
│   │   └── game_screen.py     # Main game loop
│   └── training/
│       ├── train.py           # Training entry point
│       └── callbacks.py       # SB3 checkpoint + eval callbacks
├── models/                  # Saved PPO checkpoints (created at runtime)
├── logs/                    # TensorBoard logs (created at runtime)
├── main.py                  # CLI entry point
└── requirements.txt
```

---

## Part 1: Game + GUI

### Step 1 — Setup
```bash
git init
git submodule add https://github.com/CaganKiper/mancala-ai.git mancala_ai
pip install -r requirements.txt
```

**`requirements.txt`**:
```
pygame>=2.5.0
gymnasium>=0.29.0
stable-baselines3>=2.3.0
sb3-contrib>=2.3.0
torch>=2.1.0
numpy>=1.24.0
tensorboard>=2.14.0
```

### Step 2 — `src/env_wrapper.py`
Gymnasium-compatible wrapper around `KalahEnvironment`. This is the foundation everything else builds on.

- **Observation space**: `Box(low=0, high=48, shape=(14,), dtype=np.int32)`
- **Action space**: `Discrete(6)` (pits 0–5, relative to current player)
- **`action_masks() -> np.ndarray`**: boolean array of shape `(6,)` — required by `MaskablePPO`
- **Board perspective normalization**: always return obs from the agent's POV (indices 0–5 = my pits, 6 = my store). When agent is Player 1, swap halves: `np.concatenate([board[7:13], board[13:14], board[0:6], board[6:7]])`. Put this in a shared utility function used by both `MancalaEnv` and `RLAgent`.
- **Opponent handling**: after agent's action, env auto-executes the opponent's move (vs `RandomAgent` or self). SB3 sees a single-agent environment.
- **Reward**: `+1.0` win, `-1.0` loss, `0.0` draw. Optional small incremental reward `(my_score - opp_score) / 48 * 0.01` (default off).
- **First-player fairness**: randomly assign agent to Player 0 or 1 each `reset()`.

### Step 3 — `src/tournament.py`
Headless N-game runner (no Pygame). Test this before building the GUI.

```python
def run_tournament(agent_0, agent_1, n_games: int) -> dict:
    # Returns: {"agent_0_wins": int, "agent_1_wins": int, "draws": int, "winner": str}
    # Alternates who goes first each game for fairness
    # Prints progress every 10 games, summary at end
```

Uses `KalahEnvironment` directly (not the gym wrapper).

### Step 4 — Pygame GUI

**`src/gui/board_renderer.py`** — pure drawing, no logic:
- `draw_board(surface, board, current_player, valid_moves)`: full board
- Board layout: horizontal, Player 0 pits on bottom row (0–5 left→right), Player 1 pits on top row (7–12, mirrored), stores on far sides
- Stone counts displayed as numbers inside pit circles
- Highlight valid move pits for current player

**`src/gui/menu.py`** — start screen with three buttons:
1. Human vs AI (choose: Random / Minimax depth 3 / Trained RL)
2. AI vs AI watch mode (choose both agents)
3. Tournament mode (enter N games)

**`src/gui/game_screen.py`**:
```python
class GameScreen:
    def __init__(self, agent_0, agent_1, mode="play"):
        # mode: "play" (human interactive), "watch" (auto-advance AI vs AI)
    def run(self): ...
    def handle_human_click(self, mouse_pos) -> int | None: ...
    def advance_ai_turn(self): ...  # uses pygame.time.wait(500) between moves
```
In watch mode: press SPACE to toggle fast/slow speed.

### Step 5 — `main.py`
```python
# python main.py             → launches GUI menu
# python main.py --mode tournament --games 100 --model models/best_model
# python main.py --mode train
```

---

## Part 2: ML/RL Agent

### Step 6 — `src/training/callbacks.py`
SB3 callback wrappers:
- `CheckpointCallback`: save model every N steps to `models/`
- `EvalCallback`: evaluate vs `RandomAgent` every 10k steps, auto-save best model to `models/best_model`

### Step 7 — `src/training/train.py`
Three-phase training curriculum:

| Phase | Steps | Opponent | Goal |
|---|---|---|---|
| 1 | 0–200k | RandomAgent | Learn rules + basic strategy |
| 2 | 200k–500k | Self (Phase 1 model) | Exploit patterns via self-play |
| 3 | 500k+ | MinimaxAgent (depth 1–2) | Learn to handle planning |

```python
model = MaskablePPO(
    "MlpPolicy", env, verbose=1,
    learning_rate=3e-4, n_steps=2048, batch_size=64,
    n_epochs=10, gamma=0.99,
    policy_kwargs={"net_arch": [128, 128]}
)
```

Uses `n_envs=4` (4 parallel envs via `make_vec_env`) for ~4x training speed. Supports `resume_from` path to continue training from a checkpoint.

### Step 8 — `src/agents/rl_agent.py`
Bridge between trained PPO model and mancala-ai's `Agent` base class:

```python
class RLAgent(Agent):
    def __init__(self, model_path: str): ...
    def get_action(self, env) -> int:
        # 1. Extract board from KalahEnvironment
        # 2. Apply perspective normalization (same function as env_wrapper)
        # 3. self.model.predict(obs, action_masks=masks, deterministic=True)
        # 4. Return pit index (0-5)
```

**Critical**: `_env_to_obs()` in `RLAgent` must use the exact same normalization as `MancalaEnv._get_obs()`. Keep this in one shared utility function in `src/env_wrapper.py`.

---

## Build Order
1. `requirements.txt` + submodule setup
2. `src/env_wrapper.py` — test manually: `env.reset()`, `env.step()`, check obs shape
3. `src/tournament.py` — test with two `RandomAgent`s (should be ~50/50)
4. `src/training/train.py` + `callbacks.py` — run Phase 1 (~10 min on CPU)
5. `src/agents/rl_agent.py` — test: RL vs Random tournament, should win >70%
6. `src/gui/board_renderer.py` — test with standalone script rendering a hardcoded board
7. `src/gui/menu.py`
8. `src/gui/game_screen.py`
9. `main.py`
10. Run full Phase 2 + 3 curriculum

---

## Verification
- Tournament: `RandomAgent` vs `RandomAgent` → ~50/50 wins confirms fair alternation
- After Phase 1 training: `RLAgent` vs `RandomAgent` tournament of 100 games → >70% win rate
- After Phase 2+3: `RLAgent` vs `MinimaxAgent(depth=3)` tournament → competitive (>40% win rate)
- GUI: launch `python main.py`, select "AI vs AI watch", observe board updating after each move
- Human mode: click a pit → stones redistribute → opponent AI responds
