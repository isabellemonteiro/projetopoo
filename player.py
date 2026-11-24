import pygame
from entidade import Entidade
from settings import VIDAS_INICIAIS, PONTOS_CRISTAL, TEMPO_INVENCIVEL
import visual

FANTASMA = "fantasma"
HUMANO = "humano"
ANIMACOES = {"andar": 7, "pular": 6, "aterrissar": 5}
TEMPO_QUADRO_ANDAR = 90  
TEMPO_QUADRO_POUSO = 50    
TEMPO_POSE_DANO = 350       
FASES_ATAQUE = [(0, 60), (1, 60), (2, 120), (1, 60)]
INSTANTE_TIRO = FASES_ATAQUE[0][1] + FASES_ATAQUE[1][1]
VELOCIDADE_TIRO = 11       
ALCANCE_TIRO = 700           
TECLAS_ESQUERDA = (pygame.K_LEFT, pygame.K_a)
TECLAS_DIREITA = (pygame.K_RIGHT, pygame.K_d)


class Tiro:
    ESCALA = 0.45
    def __init__(self, x, y, direita):
        self.direita = direita
        self.cx = float(x)
        self.rect = pygame.Rect(0, 0, 60, 26)      
        self.rect.center = (int(x), int(y))
        self.percorrido = 0.0
        self.vivo = True

    def atualizar(self):
        passo = VELOCIDADE_TIRO if self.direita else -VELOCIDADE_TIRO
        self.cx += passo
        self.percorrido += VELOCIDADE_TIRO
        self.rect.centerx = int(self.cx)
        if self.percorrido >= ALCANCE_TIRO:
            self.vivo = False

    def desenhar(self, tela, cam_x):
        sprite = visual.carregar_sprite_escala("efeitos/tiro.png", self.ESCALA)
        r = self.rect.move(-cam_x, 0)
        if sprite is None:
            pygame.draw.ellipse(tela, (190, 120, 255), r)
            return
        if not self.direita:
            sprite = pygame.transform.flip(sprite, True, False)
        tela.blit(sprite, sprite.get_rect(center=r.center))


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
        self.animacao = self._carregar_animacoes()   
        self._no_chao_antes = False
        self._inicio_pouso = -9999
        self._inicio_dano = -9999
        self.sprite_dano = visual.carregar_sprite_escala("heroi/dano_0.png", 1.0)  
        self.sprites_ataque = [visual.carregar_sprite_escala(f"heroi/ataque_{i}.png", 1.0) for i in range(3)]
        if any(q is None for q in self.sprites_ataque):
            self.sprites_ataque = None
        self.pode_atacar = False            
        self._inicio_ataque = -9999
        self._tiro_pendente = False         
        self.tiros = []                     

    @staticmethod
    def _carregar_animacoes():
        quadros = {}
        for nome, qtd in ANIMACOES.items():
            lista = [visual.carregar_sprite(f"heroi/{nome}_{i}.png", (60, 66)) for i in range(qtd)]
            if any(q is None for q in lista):
                return None    
            quadros[nome] = lista
        return quadros

    
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
            return True
        return False

    def atacar(self):
        if not self.pode_atacar or self.atacando:
            return False
        self._inicio_ataque = pygame.time.get_ticks()
        self._tiro_pendente = True
        return True

    def _fase_ataque(self):
        decorrido = pygame.time.get_ticks() - self._inicio_ataque
        for quadro, duracao in FASES_ATAQUE:
            if decorrido < duracao:
                return quadro
            decorrido -= duracao
        return None

    @property
    def atacando(self):
        return self._fase_ataque() is not None

    def _disparar(self):
        x = self.rect.right + 6 if self.olhando_direita else self.rect.left - 6
        self.tiros.append(Tiro(x, self.rect.centery - 4, self.olhando_direita))

    def desenhar_tiros(self, tela, cam_x):
        for tiro in self.tiros:
            tiro.desenhar(tela, cam_x)

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
        self._inicio_dano = pygame.time.get_ticks()
        self.vel_y = -7
        return True

    def perder_vida_abismo(self):
        self.vidas -= 1   

    def reaparecer(self, x, y):
        self.x, self.y = float(x), float(y)
        self.rect.topleft = (x, y)
        self.vel_x = self.vel_y = 0
        self._invencivel_ate = pygame.time.get_ticks() + TEMPO_INVENCIVEL
        self.tiros = []
        self._tiro_pendente = False

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
        if any(teclas[k] for k in TECLAS_ESQUERDA):
            self.vel_x = -atr["velocidade"]
            self.olhando_direita = False
        if any(teclas[k] for k in TECLAS_DIREITA):
            self.vel_x = atr["velocidade"]
            self.olhando_direita = True
        if self._tiro_pendente and pygame.time.get_ticks() - self._inicio_ataque >= INSTANTE_TIRO:
            self._tiro_pendente = False
            self._disparar()
        for tiro in self.tiros:
            tiro.atualizar()
        self.tiros = [t for t in self.tiros if t.vivo]
        self.aplicar_gravidade(atr["gravidade"], atr["queda_maxima"])
        velocidade_queda = self.vel_y
        self.mover(solidos)
        if self.no_chao and not self._no_chao_antes and velocidade_queda > 3:
            self._inicio_pouso = pygame.time.get_ticks()     
        self._no_chao_antes = self.no_chao

    def _quadro_animado(self):
        agora = pygame.time.get_ticks()
        if not self.no_chao:                                   
            vy = self.vel_y
            indice = 1 if vy < -9 else 2 if vy < -3 else 3 if vy <= 3 else 4 if vy <= 9 else 5
            return self.animacao["pular"][indice]
        pouso = self.animacao["aterrissar"]
        if self.vel_x == 0:
            i = (agora - self._inicio_pouso) // TEMPO_QUADRO_POUSO
            if i < len(pouso):                                
                return pouso[i]
            return pouso[-1]                                  
        andar = self.animacao["andar"]                         
        return andar[(agora // TEMPO_QUADRO_ANDAR) % len(andar)]

    def imagem_atual(self):
        fase = self._fase_ataque() if self.sprites_ataque else None
        if self.__forma == HUMANO and fase is not None:
            sprite = self.sprites_ataque[fase]
        elif self.__forma == HUMANO and self.sprite_dano and pygame.time.get_ticks() - self._inicio_dano < TEMPO_POSE_DANO:
            sprite = self.sprite_dano                 
        elif self.__forma == HUMANO and self.animacao:
            sprite = self._quadro_animado()
        else:
            sprite = self.sprites[self.__forma]
        if sprite and not self.olhando_direita:
            sprite = pygame.transform.flip(sprite, True, False)
        return sprite

    def desenhar(self, tela, cam_x, t):
        if self.invencivel and (t // 80) % 2 == 0:  
            return
        r = self.rect.move(-cam_x, 0)
        imagem = self.imagem_atual()
        if imagem:
            tela.blit(imagem, imagem.get_rect(midbottom=r.midbottom))
        elif self.__forma == FANTASMA:
            visual.desenhar_fantasma(tela, r, self.olhando_direita, t)
        else:
            visual.desenhar_humano(tela, r, self.olhando_direita, t)
