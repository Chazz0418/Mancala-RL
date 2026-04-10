import pygame
from mancala_ai.environments.kalah_environment import KalahEnvironment
from src.gui.board_renderer import draw_board, get_pit_at_pos

class GameScreen:
    def __init__(self, surface, agent_0, agent_1, mode="play"):
        self.surface = surface
        self.agent_0 = agent_0 # None if human
        self.agent_1 = agent_1 # None if human
        print(f"GameScreen init: P0 agent: {type(self.agent_0).__name__ if self.agent_0 else 'Human'}, P1 agent: {type(self.agent_1).__name__ if self.agent_1 else 'Human'}")
        self.mode = mode
        self.kalah = KalahEnvironment()
        self.clock = pygame.time.Clock()
        self.running = True
        self.ai_delay = 1000 # ms
        self.last_ai_move_time = 0

    def run(self):
        while self.running:
            self.clock.tick(60)
            self._handle_events()
            self._update()
            self._draw()
            
            if self.kalah.done:
                # Game finished, show result for 3 seconds then exit
                self._draw()
                pygame.display.flip()
                pygame.time.wait(3000)
                self.running = False

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.kalah.done:
                    # Check whose turn it is in the engine
                    if self.kalah.current_player == 0:
                        current_agent = self.agent_0
                    else:
                        current_agent = self.agent_1
                        
                    if current_agent is None: # Human turn
                        pit_idx = get_pit_at_pos(event.pos)
                        if pit_idx is not None:
                            mouse_y = event.pos[1]
                            clicked_player = 0 if mouse_y > 200 else 1
                            
                            # MUST match current player AND be on their side
                            if clicked_player == self.kalah.current_player:
                                if self.kalah._is_valid_action(pit_idx):
                                    print(f"Human (P{clicked_player}) executes move {pit_idx}")
                                    self.kalah.step(pit_idx)
                                    print(f"Engine now says it is Player {self.kalah.current_player}'s turn")
                            else:
                                print(f"Ignored: Clicked P{clicked_player}'s side but it is P{self.kalah.current_player}'s turn")

    def _update(self):
        if not self.kalah.done:
            if self.kalah.current_player == 0:
                current_agent = self.agent_0
            else:
                current_agent = self.agent_1
                
            if current_agent is not None:
                now = pygame.time.get_ticks()
                if self.last_ai_move_time == 0: # First time seeing AI turn
                    self.last_ai_move_time = now
                    
                if now - self.last_ai_move_time > self.ai_delay:
                    print(f"AI (P{self.kalah.current_player}) is thinking...")
                    action = current_agent.get_action(self.kalah)
                    print(f"AI (P{self.kalah.current_player}) executes move {action}")
                    self.kalah.step(action)
                    self.last_ai_move_time = 0 # Reset for next turn

    def _draw(self):
        valid_moves = self.kalah.get_valid_actions()
        draw_board(self.surface, self.kalah.board, self.kalah.current_player, valid_moves)
        
        if self.kalah.done:
            font = pygame.font.SysFont(None, 72)
            winner = self.kalah.get_winner()
            if winner is None:
                text = "It's a Draw!"
            else:
                text = f"Player {winner} Wins!"
            winner_text = font.render(text, True, (255, 0, 0))
            text_rect = winner_text.get_rect(center=(400, 200))
            self.surface.blit(winner_text, text_rect)
            
        pygame.display.flip()
