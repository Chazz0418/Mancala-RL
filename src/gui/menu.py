import pygame

class Menu:
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.SysFont(None, 48)
        self.buttons = [
            {"label": "Human vs AI", "rect": pygame.Rect(250, 100, 300, 60), "mode": "play"},
            {"label": "AI vs AI Watch", "rect": pygame.Rect(250, 200, 300, 60), "mode": "watch"},
            {"label": "Tournament", "rect": pygame.Rect(250, 300, 300, 60), "mode": "tournament"}
        ]

    def draw(self):
        self.surface.fill((30, 30, 30))
        for btn in self.buttons:
            pygame.draw.rect(self.surface, (70, 70, 70), btn["rect"], border_radius=10)
            text = self.font.render(btn["label"], True, (255, 255, 255))
            text_rect = text.get_rect(center=btn["rect"].center)
            self.surface.blit(text, text_rect)

    def handle_click(self, pos):
        for btn in self.buttons:
            if btn["rect"].collidepoint(pos):
                return btn["mode"]
        return None
