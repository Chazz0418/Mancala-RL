import pygame

# Colors
BOARD_COLOR = (139, 69, 19)
PIT_COLOR = (101, 67, 33)
STONE_COLOR = (200, 200, 200)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 215, 0)

# Layout Constants
BOARD_WIDTH = 800
BOARD_HEIGHT = 400
PIT_RADIUS = 40
STORE_WIDTH = 60
STORE_HEIGHT = 150

def draw_board(surface, board, current_player, valid_moves):
    surface.fill((30, 30, 30))
    
    # Draw Board Background
    board_rect = pygame.Rect(50, 50, 700, 300)
    pygame.draw.rect(surface, BOARD_COLOR, board_rect, border_radius=20)
    
    font = pygame.font.SysFont(None, 36)
    
    # P0 Pits (bottom row)
    for i in range(6):
        center_x = 150 + i * 100
        center_y = 280
        color = HIGHLIGHT_COLOR if current_player == 0 and i in valid_moves else PIT_COLOR
        pygame.draw.circle(surface, color, (center_x, center_y), PIT_RADIUS)
        
        # Stone count
        text = font.render(str(board[i]), True, TEXT_COLOR)
        text_rect = text.get_rect(center=(center_x, center_y))
        surface.blit(text, text_rect)
        
        # Label
        label = font.render(f"P{i}", True, (150, 150, 150))
        surface.blit(label, (center_x - 10, center_y + 50))

    # P1 Pits (top row, mirrored)
    for i in range(6):
        # Index 7 corresponds to pit 0 for P1, which is top-right?
        # Let's say index 7-12 are right-to-left on top row.
        # Or let's just do it simple: 12-7 left-to-right.
        center_x = 150 + (5 - i) * 100 # i=0 -> 650, i=5 -> 150
        center_y = 120
        board_idx = 7 + i
        color = HIGHLIGHT_COLOR if current_player == 1 and i in valid_moves else PIT_COLOR
        pygame.draw.circle(surface, color, (center_x, center_y), PIT_RADIUS)
        
        # Stone count
        text = font.render(str(board[board_idx]), True, TEXT_COLOR)
        text_rect = text.get_rect(center=(center_x, center_y))
        surface.blit(text, text_rect)
        
        # Label
        label = font.render(f"P{i}", True, (150, 150, 150))
        surface.blit(label, (center_x - 10, center_y - 70))

    # P0 Store (right)
    p0_store_rect = pygame.Rect(680, 125, STORE_WIDTH, STORE_HEIGHT)
    pygame.draw.rect(surface, PIT_COLOR, p0_store_rect, border_radius=30)
    text = font.render(str(board[6]), True, TEXT_COLOR)
    text_rect = text.get_rect(center=p0_store_rect.center)
    surface.blit(text, text_rect)

    # P1 Store (left)
    p1_store_rect = pygame.Rect(60, 125, STORE_WIDTH, STORE_HEIGHT)
    pygame.draw.rect(surface, PIT_COLOR, p1_store_rect, border_radius=30)
    text = font.render(str(board[13]), True, TEXT_COLOR)
    text_rect = text.get_rect(center=p1_store_rect.center)
    surface.blit(text, text_rect)

    # Turn info
    turn_text = font.render(f"Current Player: {'Player 0' if current_player == 0 else 'Player 1'}", True, TEXT_COLOR)
    surface.blit(turn_text, (300, 20))

def get_pit_at_pos(pos):
    # pos is (x, y)
    # Check P0 pits
    for i in range(6):
        center_x = 150 + i * 100
        center_y = 280
        if (pos[0] - center_x)**2 + (pos[1] - center_y)**2 <= PIT_RADIUS**2:
            return i # Returns relative index
            
    # Check P1 pits
    for i in range(6):
        center_x = 150 + (5 - i) * 100
        center_y = 120
        if (pos[0] - center_x)**2 + (pos[1] - center_y)**2 <= PIT_RADIUS**2:
            return i # Returns relative index
            
    return None
