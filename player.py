import pygame
import time

class FormaJogador:
  def __init__ (self):
    self.nome = "base"
    self.forca_pulo = -10
    self.gravidade = 0.5
    self.velocidade_movimento = 5 
    self.pode_atravessar_obstaculos = false
    self.causa_dano_impacto = false
  def aplicar_fisica(self,jogador):
    pass

class FormaFantasma(FormaJogador):
    def __init__(self):
        super().__init__()
        self.nome = "Fantasma"
        self.forca_pulo = -15        
        self.gravidade = 0.2         
        self.velocidade_movimento = 6
        self.pode_atravessar_obstaculos = True
        self.causa_dano_impacto = False

class FormaHumana(FormaJogador):
    def __init__(self):
        super().__init__()
        self.nome = "Humano"
        self.forca_pulo = -8
        self.gravidade = 0.8
        self.pode_atravessar_obstaculos = False
        self.causa_dano_impacto = True

    
