import pygame
import random
import math

class Enemy:
    def __init__(self, x, y, type):
        self.type = type 
        self.rect = pygame.Rect(x, y, 30, 30)
        self.speed = random.uniform(2, 4)
        self.direction = 1
        self.initial_y = y

    def update(self, speed_multiplier):
        current_speed = self.speed * speed_multiplier
        if self.type == 'bat':
           
            self.rect.x -= current_speed
            self.rect.y = self.initial_y + int(math.sin(self.rect.x * 0.05) * 30)
        elif self.type == 'skeleton':
           
            self.rect.x -= current_speed

class LevelManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        
        self.platforms = [
            pygame.Rect(0, 500, 350, 100),
            pygame.Rect(500, 500, 400, 100),
            pygame.Rect(200, 380, 150, 20)
        ]
        
        self.enemies = []
        self.spawn_timer = 0
        self.portal_rect = None
        self.portal_spawned = False

    def update(self, delta_time, total_time, phase_duration):
       
        progress = min(total_time / phase_duration, 1.0)
        speed_multiplier = 1.0 + progress

        
        if total_time < phase_duration:
            self.spawn_timer += delta_time
            spawn_interval = max(0.5, 2.0 - (progress * 1.2)) 
            
            if self.spawn_timer >= spawn_interval:
                self.spawn_timer = 0
                enemy_type = random.choice(['bat', 'skeleton'])
                spawn_y = random.randint(200, 350) if enemy_type == 'bat' else 470
                self.enemies.append(Enemy(self.screen_width + 20, spawn_y, enemy_type))
        
        
        elif not self.portal_spawned:
            self.portal_spawned = True
            self.portal_rect = pygame.Rect(650, 400, 50, 100)

        
        for enemy in self.enemies[:]:
            enemy.update(speed_multiplier)
            if enemy.rect.right < 0:
                self.enemies.remove(enemy)

    def draw(self, surface):
        
        for plat in self.platforms:
            pygame.draw.rect(surface, (50, 50, 60), plat)
            pygame.draw.rect(surface, (30, 30, 40), plat, 3) 

        
        for enemy in self.enemies:
            if enemy.type == 'bat':
                pygame.draw.ellipse(surface, (100, 50, 150), enemy.rect) 
            else:
                pygame.draw.rect(surface, (220, 220, 200), enemy.rect) 

        # Desenhar Portal
        if self.portal_rect:
            pygame.draw.ellipse(surface, (0, 255, 200), self.portal_rect, 4)
