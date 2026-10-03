import math
import pygame
from entidade import Entidade
import visual


class Inimigo(Entidade):

    def __init__(self, x, y, largura, altura, sprite=None, tamanho_sprite=None):
        super().__init__(x, y, largura, altura, sprite, tamanho_sprite)
        self.vivo = True

    def atualizar(self, solidos):
        pass 


class Esqueleto(Inimigo):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 44, "esqueleto.png", (54, 56))
        self.direcao = -1

    def bateu_parede(self):        
        self.direcao *= -1

    def atualizar(self, solidos):
        self.vel_x = self.direcao * 1.2
        self.olhando_direita = self.direcao > 0
        self.aplicar_gravidade(0.8, 14)
        self.mover(solidos)
        if self.no_chao:           
            frente_x = self.rect.right + 1 if self.direcao > 0 else self.rect.left - 3
            ponto = pygame.Rect(frente_x, self.rect.bottom + 2, 2, 2)
            if ponto.collidelist(solidos) == -1:
                self.direcao *= -1

    def desenhar_formas(self, tela, r, t):
        visual.desenhar_esqueleto(tela, r, t)


class Morcego(Inimigo):
    def __init__(self, x, y):
        super().__init__(x, y, 36, 24, "morcego.png", (48, 40))
        self.x_inicial = x
        self.y_inicial = y
        self.direcao = 1

    def atualizar(self, solidos):
        self.x += self.direcao * 2
        if abs(self.x - self.x_inicial) > 120:
            self.direcao *= -1
        self.olhando_direita = self.direcao > 0
        self.y = self.y_inicial + math.sin(pygame.time.get_ticks() / 300) * 25
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)

    def desenhar_formas(self, tela, r, t):
        visual.desenhar_morcego(tela, r, t)
