import pygame
from player import Entidade

class InimigoBasico(Entidade):
    def __init__(self, x, y, tipo):
        super().__init__(x, y, hp_maximo=1)
        self.tipo = tipo 
        self.velocidade = 2

    def update(self):
        self.x += self.velocidade

class ChefeScorpion(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, hp_maximo=5)
        self.nome = "Scorpion"
        
    def receber_ataque(self, jogador):
        """Verifica se o ataque recebido veio da forma correta"""
        if jogador.forma_atual.causa_dano_impacto:
            self.tomar_dano(1)
        else:
            pass

    def ataque_esmagamento(self):
        pass
        
    def ataque_sopro_vento(self):
        pass
