import pygame
from entidade import Entidade
from settings import VIDAS_INICIAIS, PONTOS_CRISTAL, TEMPO_INVENCIVEL
import visual

FANTASMA = "fantasma"
HUMANO = "humano"


class Jogador(Entidade):
    ATRIBUTOS = {
        FANTASMA: {"velocidade": 4.0, "gravidade": 0.40, "pulo": -14.5, "queda_maxima": 3.2},   
        HUMANO:   {"velocidade": 3.2, "gravidade": 0.90, "pulo": -17.0, "queda_maxima": 16.0}, 
    }

    def __init__(self, x, y):
        super().__init__(x, y, 32, 48)
        self.__vidas = VIDAS_INICIAIS      
        self.__pontos = 0
        self.__forma = FANTASMA
        self._invencivel_ate = 0           
        self.pode_trocar_forma = False      
        self.sprites = {FANTASMA: visual.carregar_sprite("fantasma.png", (62, 66)),
                        HUMANO: visual.carregar_sprite("humano.png", (50, 66))}

    
    @property
    def vidas(self):
        return self.__vidas

    @vidas.setter
    def vidas(self, valor):
        self.__vidas = max(0, min(VIDAS_INICIAIS, valor)) 

    @property
    def pontos(self):
        return self.__pontos

    @property
    def forma(self):
        return self.__forma

    @property
    def invencivel(self):
        return pygame.time.get_ticks() < self._invencivel_ate

    def pular(self):
        if self.no_chao:
            self.vel_y = self.ATRIBUTOS[self.__forma]["pulo"]
            self.no_chao = False

    def soltar_pulo(self):

        if self.vel_y < -4:
            self.vel_y *= 0.5

    def quicar(self, forca=9):
        self.vel_y = -forca
        self.no_chao = False

    def mudar_forma(self, nova_forma):
        self.__forma = nova_forma

    def trocar_forma(self):
        if not self.pode_trocar_forma:
            return False
        self.mudar_forma(HUMANO if self.__forma == FANTASMA else FANTASMA)
        return True

    def coletar_cristal(self):
        self.__pontos += PONTOS_CRISTAL

    def tomar_dano(self):

        if self.invencivel:
            return False
        self.vidas -= 1
        self._invencivel_ate = pygame.time.get_ticks() + TEMPO_INVENCIVEL
        self.vel_y = -7
        return True

    def perder_vida_abismo(self):
        self.vidas -= 1   

    def reaparecer(self, x, y):
        self.x, self.y = float(x), float(y)
        self.rect.topleft = (x, y)
        self.vel_x = self.vel_y = 0
        self._invencivel_ate = pygame.time.get_ticks() + TEMPO_INVENCIVEL

    def limitar(self, minimo_x, maximo_x):
        
        if self.rect.left < minimo_x:
            self.rect.left = minimo_x
            self.x = self.rect.x
        if self.rect.right > maximo_x:
            self.rect.right = maximo_x
            self.x = self.rect.x


    def atualizar(self, teclas, solidos):
        atr = self.ATRIBUTOS[self.__forma]
        self.vel_x = 0
        if teclas[pygame.K_LEFT]:
            self.vel_x = -atr["velocidade"]
            self.olhando_direita = False
        if teclas[pygame.K_RIGHT]:
            self.vel_x = atr["velocidade"]
            self.olhando_direita = True
        self.aplicar_gravidade(atr["gravidade"], atr["queda_maxima"])
        self.mover(solidos)

    def desenhar(self, tela, cam_x, t):
        if self.invencivel and (t // 80) % 2 == 0:  
            return
        r = self.rect.move(-cam_x, 0)
        sprite = self.sprites[self.__forma]
        if sprite:
            imagem = sprite if self.olhando_direita else pygame.transform.flip(sprite, True, False)
            tela.blit(imagem, imagem.get_rect(midbottom=r.midbottom))
        elif self.__forma == FANTASMA:
            visual.desenhar_fantasma(tela, r, self.olhando_direita, t)
        else:
            visual.desenhar_humano(tela, r, self.olhando_direita, t)
