import pygame

class Boss:
    def __init__(self):
        self.rect = pygame.Rect(550, 100, 180, 150) 
        self.heart_rect = pygame.Rect(620, 170, 40, 40) 
        
        self.hp = 5
        self.state = 'HOVER' 
        self.state_timer = 0
        self.speed_x = 2
        self.target_x = 550

    def update(self, player_rect):
        self.state_timer += 1
        
        
        self.heart_rect.x = self.rect.x + 70
        self.heart_rect.y = self.rect.y + 70

        if self.state == 'HOVER':
            
            if self.rect.centerx < player_rect.centerx:
                self.rect.x += self.speed_x
            elif self.rect.centerx > player_rect.centerx:
                self.rect.x -= self.speed_x
            
            
            self.rect.x = max(450, min(self.rect.x, 620))

            
            if self.state_timer > 150:
                self.state = 'CRUSH'
                self.state_timer = 0

        elif self.state == 'CRUSH':
            
            self.rect.y += 12
            if self.rect.bottom >= 500: 
                self.rect.bottom = 500
                self.state = 'RECOVER'
                self.state_timer = 0

        elif self.state == 'RECOVER':
           
            if self.state_timer > 60:
                self.state = 'RETREAT'
                self.state_timer = 0

        elif self.state == 'RETREAT':
           
            self.rect.y -= 4
            if self.rect.y <= 100:
                self.rect.y = 100
                self.state = 'HOVER'
                self.state_timer = 0

    def draw(self, surface):
        if self.hp > 0:
         
            pygame.draw.rect(surface, (80, 80, 90), self.rect)
            pygame.draw.rect(surface, (40, 40, 50), self.rect, 5)
            
            
            pygame.draw.rect(surface, (255, 0, 50), self.heart_rect)
