import os
import sys
import argparse

# Add mancala-ai submodule to path before other imports
submodule_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "mancala_ai"))
if submodule_path not in sys.path:
    sys.path.insert(0, submodule_path)

import pygame
from src.gui.menu import Menu
from src.gui.game_screen import GameScreen
from src.training.train import train_grandmaster_2
from src.tournament import run_tournament
from mancala_ai.agents.random_agent import RandomAgent
from mancala_ai.agents.minimax_agent import MinimaxAgent
from src.agents.rl_agent import RLAgent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="gui", choices=["gui", "train", "tournament"])
    parser.add_argument("--steps", type=int, default=10000000)
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--model", type=str, default="./models/best_model/best_model.zip")
    args = parser.parse_args()

    if args.mode == "train":
        train_grandmaster_2(total_steps=args.steps)
    elif args.mode == "tournament":
        # Load agent if exists
        if os.path.exists(args.model):
            model_name = os.path.basename(args.model).replace(".zip", "")
            agent_rl = RLAgent(f"AI_{model_name}", args.model)
        else:
            print(f"Warning: model {args.model} not found. Using RandomAgent instead.")
            agent_rl = RandomAgent("AI_Random")
            
        agent_minimax = MinimaxAgent("AI_Minimax")
        agent_minimax.set_setting("depth", 3)
        run_tournament(agent_rl, agent_minimax, args.games)
    else: # gui
        pygame.init()
        surface = pygame.display.set_mode((800, 400))
        pygame.display.set_caption("Mancala RL")
        
        menu = Menu(surface)
        running = True
        while running:
            menu.draw()
            pygame.display.flip()
            
            mode_selected = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mode_selected = menu.handle_click(event.pos)
            
            if mode_selected:
                # Determine which model to use: selected in menu OR from command line OR default best
                model_to_load = menu.selected_model or args.model
                
                if mode_selected == "play":
                    # Human vs RL or Minimax
                    if model_to_load.endswith("Minimax"):
                        agent = MinimaxAgent("AI_Minimax", depth=menu.minimax_depth, time_limit=600.0)
                    elif os.path.exists(model_to_load):
                        model_name = os.path.basename(model_to_load).replace(".zip", "")
                        agent = RLAgent(f"AI_{model_name}", model_to_load)
                    else:
                        print(f"Warning: model {model_to_load} not found. Using Random.")
                        agent = RandomAgent("AI_Random")
                    game = GameScreen(surface, None, agent) # Player 0 is human
                    game.run()
                elif mode_selected == "watch":
                    # RL vs Minimax
                    if os.path.exists(model_to_load):
                        model_name = os.path.basename(model_to_load).replace(".zip", "")
                        agent_0 = RLAgent(f"AI_{model_name}", model_to_load)
                    else:
                        print(f"Warning: model {model_to_load} not found. Using Random.")
                        agent_0 = RandomAgent("AI_Random")
                    agent_1 = MinimaxAgent("AI_Minimax")
                    agent_1.set_setting("depth", menu.minimax_depth)
                    agent_1.set_setting("time_limit", 600.0) # 10 minute limit to allow high depths
                    game = GameScreen(surface, agent_0, agent_1, mode="watch")
                    game.run()
                elif mode_selected == "tournament":
                    # Headless tournament but triggered from GUI?
                    # For now just print a message and run it
                    print("Running tournament in console...")
                    # ...
                    
        pygame.quit()

if __name__ == "__main__":
    main()
