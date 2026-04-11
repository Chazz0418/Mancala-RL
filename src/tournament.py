import sys
import os

# Add mancala-ai submodule to path
submodule_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mancala_ai"))
if submodule_path not in sys.path:
    sys.path.insert(0, submodule_path)

from mancala_ai.environments.kalah_environment import KalahEnvironment
from mancala_ai.agents.random_agent import RandomAgent

import sys
import os
from concurrent.futures import ProcessPoolExecutor
from mancala_ai.environments.kalah_environment import KalahEnvironment
from mancala_ai.agents.random_agent import RandomAgent

def _play_single_game(args):
    """Worker function to play one game in a separate process."""
    agent_0, agent_1, random_start_moves = args
    env = KalahEnvironment()
    env.reset()
    
    # Execute random starting moves
    if random_start_moves > 0:
        import random as py_random
        for _ in range(random_start_moves):
            if env.done:
                break
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                break
            action = py_random.choice(valid_actions)
            env.step(action)
    
    while not env.done:
        current_agent = agent_0 if env.current_player == 0 else agent_1
        action = current_agent.get_action(env)
        if action == -1:
            break
        env.step(action)
        
    return env.get_winner()

def run_tournament(agent_a, agent_b, n_games: int, n_envs: int = 8, random_start_moves: int = 0) -> dict:
    """
    Run N games between agent_a and agent_b in parallel using n_envs processes.
    agent_a is assigned to Player 0 in even games, and Player 1 in odd games.
    """
    stats = {
        "agent_a_wins": 0,
        "agent_b_wins": 0,
        "draws": 0
    }
    
    print(f"Starting tournament: {agent_a.name} vs {agent_b.name} ({n_games} games, {n_envs} cores, {random_start_moves} random starts)")
    
    # Prepare the match-ups (alternating who goes first)
    match_ups = []
    for i in range(n_games):
        if i % 2 == 0:
            match_ups.append((agent_a, agent_b, random_start_moves)) # A is P0
        else:
            match_ups.append((agent_b, agent_a, random_start_moves)) # B is P0

    # Run games in parallel
    with ProcessPoolExecutor(max_workers=n_envs) as executor:
        results = list(executor.map(_play_single_game, match_ups))

    # Process results
    for i, winner in enumerate(results):
        if winner == 0: # Player 0 won
            if i % 2 == 0:
                stats["agent_a_wins"] += 1
            else:
                stats["agent_b_wins"] += 1
        elif winner == 1: # Player 1 won
            if i % 2 == 0:
                stats["agent_b_wins"] += 1
            else:
                stats["agent_a_wins"] += 1
        else:
            stats["draws"] += 1
            
    # Final summary
    print("\nTournament Final Summary:")
    print(f"Total Games: {n_games}")
    print(f"Agent A ({agent_a.name}) Wins: {stats['agent_a_wins']}")
    print(f"Agent B ({agent_b.name}) Wins: {stats['agent_b_wins']}")
    print(f"Draws: {stats['draws']}")
    
    if stats["agent_a_wins"] > stats["agent_b_wins"]:
        stats["winner"] = agent_a.name
    elif stats["agent_b_wins"] > stats["agent_a_wins"]:
        stats["winner"] = agent_b.name
    else:
        stats["winner"] = "Tie"
        
    print(f"Overall Winner: {stats['winner']}")
    return stats

if __name__ == "__main__":
    # Test with two random agents
    a = RandomAgent("Random_A")
    b = RandomAgent("Random_B")
    run_tournament(a, b, 100)
