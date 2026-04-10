import numpy as np
from sb3_contrib import MaskablePPO
from mancala_ai.agents.base_agent import Agent
from src.env_wrapper import normalize_observation

class RLAgent(Agent):
    DISPLAY_NAME = "Trained RL Agent"

    def __init__(self, name: str, model_path: str):
        super().__init__(name)
        self.model = MaskablePPO.load(model_path)

    def get_action(self, env) -> int:
        # env here is KalahEnvironment
        board = env.board
        player_idx = env.current_player
        
        # 1. Normalize observation
        obs = normalize_observation(board, player_idx)
        
        # 2. Get action masks
        masks = self._get_action_masks(env)
        
        # 3. Predict
        action, _states = self.model.predict(obs, action_masks=masks, deterministic=True)
        
        return int(action)

    def _get_action_masks(self, env):
        # Maps current player's relative pit indices (0-5) to absolute board indices
        mask = np.zeros(6, dtype=bool)
        for i in range(6):
            abs_idx = i if env.current_player == 0 else 7 + i
            if env.board[abs_idx] > 0:
                mask[i] = True
        return mask
