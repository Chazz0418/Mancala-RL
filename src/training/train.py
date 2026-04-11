import os
import sys
import argparse
import random

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

def make_env_factory(opponent_type="self", model_pool=None, incremental_reward=False, random_start_moves=3):
    """
    Creates an environment with specific opponent types for the Diversity Curriculum.
    """
    def _init():
        if opponent_type == "minimax":
            # The Enforcer: Fast Greedy Defense
            opp = MinimaxAgent("The_Enforcer", depth=1, time_limit=0.05)
        elif opponent_type == "pool" and model_pool:
            # The Council: Random selection from past generations
            chosen_model = random.choice(model_pool)
            opp = RLAgent(f"Council_{os.path.basename(chosen_model)}", chosen_model)
        else:
            # Self-Play: The latest best model
            if model_pool and len(model_pool) > 0:
                opp = RLAgent("Latest_Self", model_pool[-1])
            else:
                opp = RandomAgent("Random_Fallback")
        
        return MancalaEnv(opponent_agent=opp, incremental_reward=incremental_reward, random_start_moves=random_start_moves)
    return _init

def train_grandmaster_2(total_steps=10000000, start_model="./models/backups/alpha.zip", n_envs=8):
    os.makedirs("./models", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)

    # 1. Initial Setup
    print(f"🚀 Starting Grandmaster 2.0 Regime from {start_model}")
    model_pool = [start_model]
    
    # Create the initial diverse environment set
    # 4 Self-Play, 2 Council (from pool), 2 Minimax
    env_fns = []
    for _ in range(4): env_fns.append(make_env_factory("self", model_pool))
    for _ in range(2): env_fns.append(make_env_factory("pool", model_pool))
    for _ in range(2): env_fns.append(make_env_factory("minimax"))
    
    env = SubprocVecEnv(env_fns)

    # 2. Load and Upgrade the Model
    # We load Alpha and apply the new high-precision hyperparameters
    model = MaskablePPO.load(start_model, env=env)
    model.learning_rate = 5e-5
    model.n_steps = 4096
    model.batch_size = 256
    model.ent_coef = 0.01
    model.gamma = 0.995
    model.tensorboard_log = "./logs/"
    
    print(f"🧠 Brain Upgraded: LR={model.learning_rate}, Batch={model.batch_size}, Ent={model.ent_coef}")

    # 3. The Generational Diversity Loop
    steps_per_gen = 1000000
    num_gens = total_steps // steps_per_gen
    
    for gen in range(num_gens):
        gen_num = gen + 1
        print(f"\n--- ⚔️ STARTING OMEGA GENERATION {gen_num}/{num_gens} ---")
        
        # Refresh environment with the latest model pool
        env_fns = []
        for _ in range(4): env_fns.append(make_env_factory("self", model_pool))
        for _ in range(2): env_fns.append(make_env_factory("pool", model_pool))
        for _ in range(2): env_fns.append(make_env_factory("minimax"))
        
        new_env = SubprocVecEnv(env_fns)
        model.set_env(new_env)
        
        # Train for 1M steps
        callbacks = get_callbacks(save_path="./models/")
        model.learn(
            total_timesteps=steps_per_gen, 
            callback=callbacks, 
            reset_num_timesteps=False, 
            tb_log_name=f"omega_gen_{gen_num}"
        )
        
        # Save and Update Pool
        save_path = f"./models/omega_gen_{gen_num}.zip"
        model.save(save_path)
        model.save("./models/final_model")
        model_pool.append(save_path)
        
        print(f"✅ Generation {gen_num} complete. Added to Council pool.")

    print("\n🏆 Grandmaster 2.0 Training Complete! final_model.zip is your new champion.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=10000000)
    parser.add_argument("--resume", type=str, default="./models/backups/alpha.zip")
    parser.add_argument("--envs", type=int, default=8)
    args = parser.parse_args()
    
    train_grandmaster_2(total_steps=args.steps, start_model=args.resume, n_envs=args.envs)
