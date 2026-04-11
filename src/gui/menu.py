import os
import pygame

class Menu:
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 32)
        self.state = "main" # "main" or "model_select"
        self.selected_model = None
        self.target_mode = None # "play" or "watch"
        
        self.main_buttons = [
            {"label": "Human vs AI", "rect": pygame.Rect(250, 100, 300, 60), "mode": "play"},
            {"label": "AI vs AI Watch", "rect": pygame.Rect(250, 200, 300, 60), "mode": "watch"},
            {"label": "Change Model", "rect": pygame.Rect(250, 300, 300, 60), "mode": "select_model"}
        ]

    def draw(self):
        self.surface.fill((30, 30, 30))
        if self.state == "main":
            self._draw_main()
        elif self.state == "model_select":
            self._draw_model_select()

    def _draw_main(self):
        title = self.font.render("Mancala Grandmaster", True, (255, 215, 0))
        self.surface.blit(title, (230, 30))
        
        current_model_label = self.small_font.render(f"Active Model: {self.selected_model or 'Default (Best)'}", True, (150, 150, 150))
        self.surface.blit(current_model_label, (50, 370))

        for btn in self.main_buttons:
            pygame.draw.rect(self.surface, (70, 70, 70), btn["rect"], border_radius=10)
            text = self.font.render(btn["label"], True, (255, 255, 255))
            text_rect = text.get_rect(center=btn["rect"].center)
            self.surface.blit(text, text_rect)

    def _draw_model_select(self):
        title = self.font.render("Select AI Brain (.zip)", True, (255, 215, 0))
        self.surface.blit(title, (230, 30))
        
        models = self._get_available_models()
        for i, model in enumerate(models[:5]): # Show top 5 for now
            rect = pygame.Rect(150, 100 + i*50, 500, 40)
            pygame.draw.rect(self.surface, (50, 50, 50), rect, border_radius=5)
            text = self.small_font.render(model, True, (255, 255, 255))
            self.surface.blit(text, (170, 110 + i*50))
            
        back_btn = pygame.Rect(300, 350, 200, 40)
        pygame.draw.rect(self.surface, (100, 50, 50), back_btn, border_radius=5)
        back_text = self.small_font.render("Back", True, (255, 255, 255))
        self.surface.blit(back_text, (370, 360))

    def _get_available_models(self):
        if not os.path.exists("./models"):
            return []
        
        # Walk through models folder and find all .zip files
        models = []
        for root, dirs, files in os.walk("./models"):
            for file in files:
                if file.endswith(".zip"):
                    # Get relative path from ./models
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, "./models")
                    models.append(rel_path)
        return sorted(models, reverse=True) # Newest/Highest step count usually first

    def handle_click(self, pos):
        if self.state == "main":
            for btn in self.main_buttons:
                if btn["rect"].collidepoint(pos):
                    if btn["mode"] == "select_model":
                        self.state = "model_select"
                        return None
                    return btn["mode"]
        
        elif self.state == "model_select":
            # Check model list clicks
            models = self._get_available_models()
            for i, model in enumerate(models[:5]):
                rect = pygame.Rect(150, 100 + i*50, 500, 40)
                if rect.collidepoint(pos):
                    self.selected_model = os.path.join("models", model)
                    self.state = "main"
                    print(f"Selected model: {self.selected_model}")
                    return None
            
            # Check back button
            back_btn = pygame.Rect(300, 350, 200, 40)
            if back_btn.collidepoint(pos):
                self.state = "main"
                return None
                
        return None
