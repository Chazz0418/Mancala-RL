from stable_baselines3.common.callbacks import CheckpointCallback
from sb3_contrib.common.maskable.callbacks import MaskableEvalCallback
from src.env_wrapper import MancalaEnv

def get_callbacks(eval_env, save_path="./models/", log_path="./logs/"):
    checkpoint_callback = CheckpointCallback(
        save_freq=50000,
        save_path=save_path,
        name_prefix="rl_model"
    )
    
    eval_callback = MaskableEvalCallback(
        eval_env,
        best_model_save_path=f"{save_path}best_model/",
        log_path=log_path,
        eval_freq=10000,
        deterministic=True,
        render=False
    )
    
    return [checkpoint_callback, eval_callback]
