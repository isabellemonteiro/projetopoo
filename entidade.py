import pygame
from visual import carregar_sprite

class Entidade:
    def __init__(self, x, y, largura, altura, sprite=None, tamanho_sprite=None):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.x = float(x)         
        self.y = float(y)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.no_chao = False
        self.olhando_direita = True
        self.sprite = carregar_sprite(sprite, tamanho_sprite or (largura, altura)) if sprite else None

    def aplicar_gravidade(self, gravidade, queda_maxima):
        self.vel_y = min(self.vel_y + gravidade, queda_maxima)

    def bateu_parede(self):
      
        pass

    def empurrar(self, deslocamento_x):
        self.x += deslocamento_x
        self.rect.x = round(self.x)

    def mover(self, solidos):
        self.x += self.vel_x
        self.rect.x = round(self.x)
        for bloco in solidos:
            if self.rect.colliderect(bloco):
                if self.vel_x > 0:
                    self.rect.right = bloco.left
                elif self.vel_x < 0:
                    self.rect.left = bloco.right
                self.x = self.rect.x
                self.bateu_parede()

        self.y += self.vel_y
        self.rect.y = round(self.y)
        self.no_chao = False
        for bloco in solidos:
            if self.rect.colliderect(bloco):
                if self.vel_y > 0:
                    self.rect.bottom = bloco.top
                    self.no_chao = True
                elif self.vel_y < 0:
                    self.rect.top = bloco.bottom
                self.vel_y = 0
                self.y = self.rect.y

       
        if not self.no_chao and self.vel_y >= 0:
            sonda = self.rect.move(0, 1)
            if any(sonda.colliderect(b) for b in solidos):
                self.no_chao = True
                self.vel_y = 0
                self.y = self.rect.y

    def desenhar(self, tela, cam_x, t):
        r = self.rect.move(-cam_x, 0)  
        if self.sprite:
            imagem = self.sprite if self.olhando_direita else pygame.transform.flip(self.sprite, True, False)
            tela.blit(imagem, imagem.get_rect(midbottom=r.midbottom))   
        else:
            self.desenhar_formas(tela, r, t)

    def desenhar_formas(self, tela, r, t):
        pygame.draw.rect(tela, (255, 0, 255), r)
