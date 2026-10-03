import pygame
from settings import LARGURA
import visual


class Menu:
    def __init__(self, opcoes):
        self.opcoes = opcoes
        self.indice = 0
        self.retangulos = []

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                self.indice = (self.indice - 1) % len(self.opcoes)
            elif evento.key == pygame.K_DOWN:
                self.indice = (self.indice + 1) % len(self.opcoes)
            elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.opcoes[self.indice]
        elif evento.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.retangulos):
                if r.collidepoint(evento.pos):
                    self.indice = i
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for i, r in enumerate(self.retangulos):
                if r.collidepoint(evento.pos):
                    return self.opcoes[i]
        return None

    def desenhar(self, tela, centros_y, largura=260, altura=46, tamanho_fonte=26):
        
        self.retangulos = []
        for i, texto in enumerate(self.opcoes):
            r = pygame.Rect(0, 0, largura, altura)
            r.centerx = LARGURA // 2
            r.centery = int(centros_y[i])
            self.retangulos.append(r)
            selecionado = i == self.indice
            pygame.draw.rect(tela, (30, 15, 75) if selecionado else (20, 12, 50), r, border_radius=8)
            pygame.draw.rect(tela, (170, 120, 255) if selecionado else (95, 70, 170), r, 3, border_radius=8)
            visual.desenhar_texto(tela, texto, tamanho_fonte, (235, 225, 255) if selecionado else (170, 150, 220), centro=r.center)
            if selecionado: 
                pygame.draw.polygon(tela, (235, 225, 255), [(r.x + 22, r.centery - 8), (r.x + 22, r.centery + 8), (r.x + 36, r.centery)])
