import math
import pygame
from entidade import Entidade
from player import HUMANO, FANTASMA
from settings import LARGURA, GOLPES_PARA_VENCER

LARGURA_CHEFE = 220
ALTURA_CHEFE = 100


class Chefe(Entidade):
    def __init__(self, x, base_y):
        super().__init__(x, base_y - ALTURA_CHEFE, LARGURA_CHEFE, ALTURA_CHEFE, "scorpion.png", (240, 144))
        self.__acertos = 0             
        self.estado = "andando"
        self._inicio_estado = pygame.time.get_ticks()
        self._invulneravel_ate = 0
        self.pousou = False              
        self.derrotado_total = False       
        self.olhando_direita = False
