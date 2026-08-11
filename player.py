import pygame

class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 15, 8)
        self.speed = 10

    def update(self):
        self.rect.x += self.speed

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 50)
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        
        
        self.lives = 3
        self.form = 'GHOST' 
        self.bullets = []
        self.is_victorious = False
        self.victory_timer = 0

    def handle_input(self, keys):
        if self.is_victorious:
            return

        
        if self.form == 'GHOST':
            speed = 5
        else: # HUMAN
            speed = 3.5 

        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -speed
        if keys[pygame.K_RIGHT]:
            self.vx = speed

    def jump(self):
        if self.on_ground and not self.is_victorious:
            if self.form == 'GHOST':
                self.vy = -12 
            else:
                self.vy = -9  
            self.on_ground = False

    def shoot(self):
        
        if self.form == 'HUMAN' and not self.is_victorious:
            self.bullets.append(Bullet(self.rect.right, self.rect.centery - 4))

    def update(self, platforms):
        
        if self.is_victorious:
            self.vx = 0
            if self.on_ground:
                self.vy = -8
                self.on_ground = False

        
        if self.form == 'GHOST':
            gravity = 0.3     
            max_fall = 6
        else:
            gravity = 0.7     
            max_fall = 12

        self.vy += gravity
        if self.vy > max_fall:
            self.vy = max_fall

        
        self.x += self.vx
        self.rect.x = int(self.x)
        self.move_and_collide(platforms, 'X')

        
        self.y += self.vy
        self.rect.y = int(self.y)
        self.on_ground = False
        self.move_and_collide(platforms, 'Y')

        
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.x > 800:
                self.bullets.remove(bullet)

        
        if self.rect.y > 600:
            self.lives = 0

    def move_and_collide(self, platforms, direction):
        for plat in platforms:
            if self.rect.colliderect(plat):
                if direction == 'X':
                    if self.vx > 0:
                        self.rect.right = plat.left
                    if self.vx < 0:
                        self.rect.left = plat.right
                    self.x = self.rect.x
                elif direction == 'Y':
                    if self.vy > 0:
                        self.rect.bottom = plat.top
                        self.vy = 0
                        self.on_ground = True
                    if self.vy < 0:
                        self.rect.top = plat.bottom
                        self.vy = 0
                    self.y = self.rect.y

    def reset_position(self):
        self.x = 50
        self.y = 300
        self.rect.x = self.x
        self.rect.y = self.y
        self.vx = 0
        self.vy = 0

    def draw(self, surface):
        
        if self.form == 'GHOST':
            
            pygame.draw.ellipse(surface, (150, 220, 255), self.rect)
            pygame.draw.circle(surface, (255, 255, 255), (self.rect.centerx - 5, self.rect.top + 15), 3)
            pygame.draw.circle(surface, (255, 255, 255), (self.rect.centerx + 5, self.rect.top + 15), 3)
        else:
            
            pygame.draw.rect(surface, (200, 50, 50), self.rect)
            pygame.draw.rect(surface, (230, 150, 100), (self.rect.x + 5, self.rect.y, 20, 15)) # Rosto

        
        for bullet in self.bullets:
            pygame.draw.rect(surface, (255, 255, 0), bullet.rect)
