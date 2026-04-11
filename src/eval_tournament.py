import os
import sys
import argparse
from typing import List

# Add mancala-ai submodule to path
submodule_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mancala_ai"))
if submodule_path not in sys.path:
    sys.path.insert(0, submodule_path)

from src.agents.rl_agent import RLAgent
from src.tournament import run_tournament

def find_refinement_models(models_dir: str) -> List[str]:
    """Find all refine_gen_*.zip files in the models directory."""
    models = []
    if not os.path.exists(models_dir):
        return []
    
    for file in os.listdir(models_dir):
        if file.startswith("refine_gen_") and file.endswith(".zip"):
            models.append(os.path.join(models_dir, file))
    
    # Sort by generation number
    models.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))
    return models

def run_grand_tournament(games_per_match: int = 50):
    models_paths = find_refinement_models("./models")
    
    if not models_paths:
        print("No refinement models found in ./models. Training might not be finished yet.")
        return

    print(f"Found {len(models_paths)} models for the Grand Tournament.")
    
    # Load all agents
    agents = []
    for path in models_paths:
        name = os.path.basename(path).replace(".zip", "")
        print(f"Loading {name}...")
        agents.append(RLAgent(name, path))

    # Leaderboard: {agent_name: total_wins}
    leaderboard = {agent.name: 0 for agent in agents}
    
    # Round Robin: Every agent plays every other agent
    print("\n--- Starting Round Robin Tournament ---")
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            agent_a = agents[i]
            agent_b = agents[j]
            
            print(f"\nMatch: {agent_a.name} vs {agent_b.name}")
            results = run_tournament(agent_a, agent_b, games_per_match)
            
            leaderboard[agent_a.name] += results["agent_a_wins"]
            leaderboard[agent_b.name] += results["agent_b_wins"]

    # Sort and print final leaderboard
    print("\n" + "="*30)
    print("🏆 FINAL TOURNAMENT LEADERBOARD 🏆")
    print("="*30)
    
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    
    for rank, (name, wins) in enumerate(sorted_leaderboard, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"{medal} Rank {rank}: {name} - {wins} Total Wins")
    
    print("="*30)
    
    best_agent = sorted_leaderboard[0][0]
    if "refine_gen_8" in best_agent:
        print(f"\n✅ Verification Success: {best_agent} is the strongest!")
    else:
        print(f"\n⚠️ Observation: {best_agent} outperformed the final generation.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=50, help="Games per match-up")
    args = parser.parse_args()
    
    run_grand_tournament(games_per_match=args.games)
