import pygame
from settings import TAMANHO_BLOCO as T, LARGURA
from enemies import Esqueleto, Morcego
import visual

MAPA_FASE_1 = [
    ".............................................................................................................................................................................................................................................................................................................................................................................",
    ".............................................................................................................................................................................................................................................................................................................................................................................",
    ".............................................................................................................................................................................................................................................................................................................................................................................",
    "......................................................................................................................................................................R......................................................................................................................................................................................................",
    ".....................................................................................................................................................................###......................CC.............................................................................................................................................................................",
    "........................................................................M.........................................................................................C...........................##...................................................................M...........................................................................M.............................",
    "..................................................................M...............................M..............................................................###.......................C...............................M.................................M...........................................................................M...................................",
    "..........................................CC.............................................................................CC...................................C...........................##......................................................................................CC.........................................M...............................................",
    "...............................C.........####......................................CC....................................##...............C..................###.......................C.....................CC..................................C................................##...........................CC............C...............................................",
    "............CCC......................................................C.............##..................................####...........................................................##.....................##.................................................................####...........................##................................................CC.C........",
    "..P.................E.............................E.....F......................................E.....E......F........######....E........H...........F.........................F.........................................E.....E......F.........H...........E....E....E........######....E......F.......................................E....E....E.......F..............G....",
]

BURACOS_FASE_1 = [(30, 32), (82, 85), (137, 139), (198, 200), (204, 207), (240, 242), (296, 298), (302, 305), (316, 318)]

MAPA_CHEFE = [
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "..####............####..",
    "........................",
    "........................",
    "..P.............B....X..",
]


class PlataformaMovel:

    def __init__(self, x, y, largura=80, alcance=160, velocidade=1.5):
        self.rect = pygame.Rect(x, y, largura, 20)
        self.x = float(x)
        self.x_minimo = x
        self.alcance = alcance
        self.velocidade = velocidade
        self.direcao = 1

    def mover(self, jogador):
        em_cima = (abs(jogador.rect.bottom - self.rect.top) <= 2
                   and jogador.rect.right > self.rect.left and jogador.rect.left < self.rect.right)
        antes = self.rect.x
        self.x += self.direcao * self.velocidade
        if self.x >= self.x_minimo + self.alcance:
            self.direcao = -1
        elif self.x <= self.x_minimo:
            self.direcao = 1
        self.rect.x = round(self.x)
        if em_cima:                   
            jogador.empurrar(self.rect.x - antes)


class Nivel:
    def __init__(self, mapa, buracos=()):
        self.linhas = len(mapa)
        self.colunas = max(len(l) for l in mapa)
        self.largura_px = self.colunas * T
        self.blocos = []
        self.cristais = []
        self.inimigos = []
        self.plataformas = []
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
        elif letra == "H":
            self.plataformas.append(PlataformaMovel(x - T, y))
        elif letra == "F":
            self.checkpoints.append({"rect": pygame.Rect(x + 6, base - 60, 28, 60), "ativo": False})
        elif letra == "R":
            self.espelho_secreto = pygame.Rect(x, base - 80, 40, 80)
        elif letra == "G":
            self.grande_espelho = pygame.Rect(x - 20, base - 190, 120, 190)
        elif letra == "P":
            self.inicio = (x + 4, base - 48)
        elif letra == "B":
            self.pos_chefe = (x, base)
        elif letra == "X":
            self.portal = pygame.Rect(x, base - 100, 60, 100)

    def solidos(self):

        return self.blocos + [p.rect for p in self.plataformas]

    def atualizar(self, jogador):
        for plataforma in self.plataformas:
            plataforma.mover(jogador)
        for inimigo in self.inimigos:
            inimigo.atualizar(self.blocos)
        self.inimigos = [i for i in self.inimigos if i.vivo]

    def desenhar(self, tela, cam_x, t):
    
        for bloco in self.blocos:
            if bloco.right > cam_x and bloco.left < cam_x + LARGURA:
                visual.desenhar_bloco(tela, bloco.move(-cam_x, 0))
        for p in self.plataformas:
            visual.desenhar_plataforma_movel(tela, p.rect.move(-cam_x, 0))
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
