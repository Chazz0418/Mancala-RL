import os
import sys
import argparse

# Add mancala-ai submodule to path
submodule_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "mancala_ai"))
if submodule_path not in sys.path:
    sys.path.insert(0, submodule_path)

from sb3_contrib import MaskablePPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv
from src.env_wrapper import MancalaEnv
from src.training.callbacks import get_callbacks
from mancala_ai.agents.random_agent import RandomAgent
from mancala_ai.agents.minimax_agent import MinimaxAgent

from src.agents.rl_agent import RLAgent

def train(total_timesteps=500000, resume_from=None):
    # Create directories
    os.makedirs("./models", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)

    # Setup environment
    def make_env(opponent_type="random", model_path=None):
        if opponent_type == "random":
            opp = RandomAgent("Random")
        elif opponent_type == "rl":
            opp = RLAgent("RL_Opponent", model_path)
        elif opponent_type == "minimax":
            opp = MinimaxAgent("Minimax")
            opp.set_setting("depth", 2)
        else:
            opp = RandomAgent("Random")
        return MancalaEnv(opponent_agent=opp)

    # Phase 1: 0-200k (Random)
    if total_timesteps > 0:
        print("Starting Phase 1: Training against RandomAgent...")
        env = make_vec_env(lambda: make_env("random"), n_envs=4, vec_env_cls=SubprocVecEnv)
        
        if resume_from and os.path.exists(resume_from):
            print(f"Resuming from {resume_from}")
            model = MaskablePPO.load(resume_from, env=env)
        else:
            model = MaskablePPO(
                "MlpPolicy",
                env,
                verbose=1,
                learning_rate=3e-4,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                policy_kwargs={"net_arch": [128, 128]},
                tensorboard_log="./logs/"
            )

        eval_env = make_env("random")
        callbacks = get_callbacks(eval_env)
        
        steps = min(200000, total_timesteps)
        model.learn(total_timesteps=steps, callback=callbacks, reset_num_timesteps=False, tb_log_name="phase_1")
        model.save("./models/phase_1_final")

    # Phase 2: 200k-400k (Self-play)
    if total_timesteps > 200000:
        print("Starting Phase 2: Self-play against Phase 1 model...")
        env = make_vec_env(lambda: make_env("rl", "./models/phase_1_final.zip"), n_envs=4, vec_env_cls=SubprocVecEnv)
        model.set_env(env)
        eval_env = make_env("random") # Still eval against random for consistency
        callbacks = get_callbacks(eval_env)
        
        steps = min(200000, total_timesteps - 200000)
        model.learn(total_timesteps=steps, callback=callbacks, reset_num_timesteps=False, tb_log_name="phase_2")
        model.save("./models/phase_2_final")

    # Phase 3: 400k+ (Minimax)
    if total_timesteps > 400000:
        print("Starting Phase 3: Training against MinimaxAgent...")
        env = make_vec_env(lambda: make_env("minimax"), n_envs=4, vec_env_cls=SubprocVecEnv)
        model.set_env(env)
        eval_env = make_env("random")
        callbacks = get_callbacks(eval_env)
        
        steps = total_timesteps - 400000
        model.learn(total_timesteps=steps, callback=callbacks, reset_num_timesteps=False, tb_log_name="phase_3")
        model.save("./models/final_model")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=100000)
    parser.add_argument("--resume", type=str, default=None)
    args = parser.parse_args()
    
    train(total_timesteps=args.steps, resume_from=args.resume)
