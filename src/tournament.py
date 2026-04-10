import sys
import os

# Add mancala-ai submodule to path
submodule_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mancala_ai"))
if submodule_path not in sys.path:
    sys.path.insert(0, submodule_path)

from mancala_ai.environments.kalah_environment import KalahEnvironment
from mancala_ai.agents.random_agent import RandomAgent

def run_tournament(agent_a, agent_b, n_games: int) -> dict:
    """
    Run N games between agent_a and agent_b.
    agent_a is assigned to Player 0 in even games, and Player 1 in odd games.
    """
    stats = {
        "agent_a_wins": 0,
        "agent_b_wins": 0,
        "draws": 0
    }
    
    env = KalahEnvironment()
    
    for i in range(n_games):
        env.reset()
        
        # Alternate who goes first (Player 0)
        if i % 2 == 0:
            player_0 = agent_a
            player_1 = agent_b
        else:
            player_0 = agent_b
            player_1 = agent_a
            
        while not env.done:
            current_agent = player_0 if env.current_player == 0 else player_1
            action = current_agent.get_action(env)
            if action == -1:
                break
            env.step(action)
            
        winner = env.get_winner()
        if winner == 0:
            if i % 2 == 0:
                stats["agent_a_wins"] += 1
            else:
                stats["agent_b_wins"] += 1
        elif winner == 1:
            if i % 2 == 0:
                stats["agent_b_wins"] += 1
            else:
                stats["agent_a_wins"] += 1
        else:
            stats["draws"] += 1
            
        if (i + 1) % 10 == 0:
            print(f"Game {i + 1}/{n_games}: Agent A: {stats['agent_a_wins']}, Agent B: {stats['agent_b_wins']}, Draws: {stats['draws']}")
            
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
        
    print(f"Winner: {stats['winner']}")
    return stats

if __name__ == "__main__":
    # Test with two random agents
    a = RandomAgent("Random_A")
    b = RandomAgent("Random_B")
    run_tournament(a, b, 100)
