import os
import sys
import gymnasium as gym
from gymnasium import spaces
import numpy as np

# Add mancala-ai submodule to path
submodule_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mancala_ai"))
if submodule_path not in sys.path:
    sys.path.insert(0, submodule_path)

from mancala_ai.environments.kalah_environment import KalahEnvironment
from mancala_ai.agents.random_agent import RandomAgent

def normalize_observation(board, player_idx):
    """
    Normalize the board from the perspective of player_idx.
    Indices 0-5: player's pits
    Index 6: player's store
    Indices 7-12: opponent's pits
    Index 13: opponent's store
    """
    if player_idx == 0:
        return board.copy()
    else:
        # Swap halves: [p1_pits, p1_store, p0_pits, p0_store]
        return np.concatenate([board[7:14], board[0:7]])

class MancalaEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, opponent_agent=None, incremental_reward=False):
        super(MancalaEnv, self). __init__()
        self.kalah = KalahEnvironment()
        
        # Observation space: 14 pits/stores, each with 0-48 stones
        self.observation_space = spaces.Box(low=0, high=48, shape=(14,), dtype=np.int32)
        
        # Action space: 6 pits
        self.action_space = spaces.Discrete(6)
        
        self.opponent = opponent_agent or RandomAgent("Opponent")
        self.incremental_reward = incremental_reward
        self.agent_player_idx = 0

    def _get_obs(self):
        obs = normalize_observation(self.kalah.board, self.agent_player_idx)
        return obs

    def action_masks(self):
        # Masks for the agent's perspective
        mask = np.zeros(6, dtype=bool)
        for i in range(6):
            # Map agent's pit index (0-5) to absolute board index
            abs_idx = i if self.agent_player_idx == 0 else 7 + i
            if self.kalah.board[abs_idx] > 0:
                mask[i] = True
        return mask

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.kalah.reset()
        
        # Randomly assign agent to Player 0 or 1
        self.agent_player_idx = self.np_random.integers(0, 2)
        
        # If it's opponent's turn, let them move
        if self.kalah.current_player != self.agent_player_idx:
            self._opponent_move()
            
        return self._get_obs(), {}

    def _opponent_move(self):
        while not self.kalah.done and self.kalah.current_player != self.agent_player_idx:
            action = self.opponent.get_action(self.kalah)
            if action == -1:
                break
            self.kalah.step(action)

    def step(self, action):
        # Action is 0-5 from agent's perspective
        if not self.action_masks()[action]:
            # Invalid action penalty (though MaskablePPO should avoid this)
            return self._get_obs(), -2.0, self.kalah.done, False, {"error": "Invalid action"}

        # Perform the action
        self.kalah.step(action)
        
        # If it's now the opponent's turn, let them move until it's our turn again
        self._opponent_move()
        
        # Calculate reward
        terminated = self.kalah.done
        reward = 0.0
        
        if terminated:
            winner = self.kalah.get_winner()
            if winner == self.agent_player_idx:
                reward = 1.0
            elif winner is None:
                reward = 0.0 # Draw
            else:
                reward = -1.0
        
        if self.incremental_reward:
            # (my_score - opp_score) / 48 * 0.01
            my_store = 6 if self.agent_player_idx == 0 else 13
            opp_store = 13 if self.agent_player_idx == 0 else 6
            score_diff = self.kalah.board[my_store] - self.kalah.board[opp_store]
            reward += (score_diff / 48.0) * 0.01

        return self._get_obs(), reward, terminated, False, {}

    def render(self):
        self.kalah.render()

    def close(self):
        pass
