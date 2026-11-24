import pygame
from settings import TAMANHO_BLOCO as T, LARGURA
from enemies import Esqueleto, Morcego
import visual

MAPA_FASE_1 = [
    "................................................................................................................................................................................................................................................",
    "................................................................................................................................................................................................................................................",
    "................................................................................................................................................................................................................................................",
    ".................................................................................................R..............................................................................................................................................",
    "................................................................................................###......................CC.....................................................................................................................",
    ".......................................................................M.....................C...........................##................................................M......................................M.............................",
    ".................................................................M..........................###.....M.................C.....................M......M.................M......................................M...................................",
    "....................................CC.......................CC..........................C...........................##................................................................CC.......................................................",
    "............................C......####......................##............C............###.......................C.....................CC.............................................##.......................................................",
    "............CCC............................................####..................................................##.....................##...........................................####...........................................CC.C........",
    "..P.................E.......................E.....F......######....E..............F...E....E.............F......................................E.....E......F.....E....E....E.....######....E......F.....E....E....E.......F..............G....",
]

BURACOS_FASE_1 = [(27, 29), (74, 76), (129, 131), (135, 138)]
MAPA_CHEFE = [
    "................................................",
    "................................................",
    "................................................",
    "................................................",
    "................................................",
    "................................................",
    "................................................",
    "................................................",
    "........#####....#####....#####....#####........",
    "................................................",
    "...P........................B................X..",
]


class Nivel:
    def __init__(self, mapa, buracos=()):
        self.linhas = len(mapa)
        self.colunas = max(len(l) for l in mapa)
        self.largura_px = self.colunas * T
        self.blocos = []
        self.cristais = []
        self.inimigos = []
        self.checkpoints = []            
        self.inicio = (T, T)
        self.espelho_secreto = None
        self.espelho_usado = False
        self.grande_espelho = None
        self.pos_chefe = None
        self.portal = None
        self.portal_aberto = False

        for linha, texto in enumerate(mapa):
            for coluna, letra in enumerate(texto.ljust(self.colunas, ".")):
                self._criar_objeto(letra, coluna * T, linha * T)

        for coluna in range(self.colunas):   
            if not any(a <= coluna <= b for a, b in buracos):
                for k in range(2):
                    self.blocos.append(pygame.Rect(coluna * T, (self.linhas + k) * T, T, T))

    def _criar_objeto(self, letra, x, y):
        base = y + T  
        if letra == "#":
            self.blocos.append(pygame.Rect(x, y, T, T))
        elif letra == "C":
            self.cristais.append(pygame.Rect(x + 8, y + 8, 24, 24))
        elif letra == "E":
            self.inimigos.append(Esqueleto(x + 4, base - 44))
        elif letra == "M":
            self.inimigos.append(Morcego(x, y))
        elif letra == "F":
            self.checkpoints.append({"rect": pygame.Rect(x + 6, base - 60, 28, 60), "ativo": False})
        elif letra == "R":
            self.espelho_secreto = pygame.Rect(x - 10, base - 90, 60, 90)
        elif letra == "G":
            self.grande_espelho = pygame.Rect(x - 20, base - 190, 120, 190)
        elif letra == "P":
            self.inicio = (x + 4, base - 48)
        elif letra == "B":
            self.pos_chefe = (x, base)
        elif letra == "X":
            self.portal = pygame.Rect(x, base - 100, 60, 100)

    def solidos(self):

        return self.blocos

    def atualizar(self, jogador):
        for inimigo in self.inimigos:
            inimigo.atualizar(self.blocos)
        self.inimigos = [i for i in self.inimigos if i.vivo]

    def desenhar(self, tela, cam_x, t):
    
        for bloco in self.blocos:
            if bloco.right > cam_x and bloco.left < cam_x + LARGURA:
                visual.desenhar_bloco(tela, bloco.move(-cam_x, 0))
        for c in self.cristais:
            visual.desenhar_cristal(tela, c.move(-cam_x, 0), t)
        for ck in self.checkpoints:
            visual.desenhar_tocha(tela, ck["rect"].move(-cam_x, 0), ck["ativo"], t)
        if self.espelho_secreto:
            visual.desenhar_espelho(tela, self.espelho_secreto.move(-cam_x, 0), t, not self.espelho_usado)
        if self.grande_espelho:
            visual.desenhar_grande_espelho(tela, self.grande_espelho.move(-cam_x, 0), t)
        if self.portal and self.portal_aberto:
            visual.desenhar_portal(tela, self.portal.move(-cam_x, 0), t)
        for inimigo in self.inimigos:
            inimigo.desenhar(tela, cam_x, t)
