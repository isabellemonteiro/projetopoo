import math
import random
import pygame
from entidade import Entidade
from settings import VIDA_CHEFE, LARGURA
import visual


LARGURA_CHEFE = 190
ALTURA_CHEFE = 100
ESCALA_CHEFE = 1.5
ALTURA_QUADRO = 150           
PES_NO_QUADRO = 138           
QUADROS = {"idle": 4, "andar": 3, "garra": 2, "cauda": 1, "especial": 3, "raio": 1}
FRENTE_ORIGINAL = {"idle": -1, "andar": -1, "garra": 1, "cauda": 1, "especial": -1, "raio": 1}
DURACAO = {
    "garra_aviso": 800, "garra_golpe": 380,
    "cauda_aviso": 850, "cauda_golpe": 320,
    "recuo": 350,
    "raio_aviso": 1000, "raio_disparo": 330,
    "cansado": 1500,
    "morrendo": 2000,
}
TEMPO_BRILHO = 140                
ESCALA_RAIO = 0.45
ALTURA_DANO_RAIO = 24             
CENTRO_RAIO = 26                 
ALCANCE_RAIO = 800            
TEMPO_CRESCER_RAIO = 130          
VELOCIDADE_ANDAR = 1.3
DISTANCIA_CORPO_A_CORPO = 230  


class Chefe(Entidade):
    def __init__(self, x, base_y, largura_arena=LARGURA):
        super().__init__(x, base_y - ALTURA_CHEFE, LARGURA_CHEFE, ALTURA_CHEFE)
        self.largura_arena = largura_arena      
        agora = pygame.time.get_ticks()
        self.chao = base_y
        self.vida = VIDA_CHEFE
        self.estado = "andando"
        self._inicio_estado = agora
        self._prox_ataque = agora + 2200         
        self._brilho_ate = 0
        self._ultimo_tremor = 0
        self.pousou = False                       
        self.derrotado_total = False            
        self.olhando_direita = False
        self._efeitos = []
        self._quadros = self._carregar_quadros()
        self._sprite_antigo = None if self._quadros else visual.carregar_sprite("scorpion.png", (240, 144))

    
    @property
    def derrotado(self):
        return self.vida <= 0

    @property
    def proporcao_vida(self):
        return max(0.0, self.vida / VIDA_CHEFE)

    @property
    def _raiva(self):
        return 0.6 * (1.0 - self.proporcao_vida)

    @staticmethod
    def _carregar_quadros():
        quadros = {}
        for nome, qtd in QUADROS.items():
            for i in range(qtd):
                img = visual.carregar_sprite_escala(f"chefe/{nome}_{i}.png", ESCALA_CHEFE)
                if img is None:
                    return None              
                quadros[(nome, i, False)] = img
                quadros[(nome, i, True)] = pygame.transform.flip(img, True, False)
        return quadros

    def _mudar(self, estado):
        self.estado = estado
        self._inicio_estado = pygame.time.get_ticks()

    def _voltar_a_andar(self, agora):
        self.vel_x = 0
        self._mudar("andando")
        self._prox_ataque = agora + int(random.randint(1800, 2800) * (1.0 - self._raiva * 0.5))

    def _mover_x(self, deslocamento):
        self.x = max(0, min(self.x + deslocamento, self.largura_arena - self.rect.w))
        self.rect.x = round(self.x)

    def _virar_para(self, jogador):
        self.olhando_direita = jogador.rect.centerx > self.rect.centerx

    def atualizar(self, jogador, solidos):
        agora = pygame.time.get_ticks()
        self.pousou = False
        self._efeitos = [e for e in self._efeitos if agora < e["inicio"] + e["dur"]]
        dt = agora - self._inicio_estado
        e = self.estado

        if e == "andando":
            dist = jogador.rect.centerx - self.rect.centerx
            self.olhando_direita = dist > 0
            if abs(dist) > 150:
                self._mover_x((VELOCIDADE_ANDAR * (1 + self._raiva)) * (1 if dist > 0 else -1))
            if agora >= self._prox_ataque:
                self._escolher_ataque(jogador)
        elif e in ("garra_aviso", "cauda_aviso"):
            if dt >= DURACAO[e]:
                self._mudar(e.replace("aviso", "golpe"))
        elif e in ("garra_golpe", "cauda_golpe"):
            if dt >= DURACAO[e]:
                self._mudar("recuo")
        elif e == "recuo":
            if dt >= DURACAO[e]:
                self._voltar_a_andar(agora)
        elif e == "raio_aviso":
            if dt < DURACAO[e] * 0.6:
                self._virar_para(jogador)         
            if dt >= DURACAO[e]:
                self._mudar("raio_disparo")
                self.pousou = True                  
        elif e == "raio_disparo":
            if dt >= DURACAO[e]:
                self._mudar("cansado")
        elif e == "cansado":
            if dt >= DURACAO[e] * (1.0 - self._raiva * 0.5):
                self._voltar_a_andar(agora)
        elif e == "morrendo":
            if agora - self._ultimo_tremor > 400:        
                self._ultimo_tremor = agora
                self.pousou = True
                self._efeito("explosao", self.rect.centerx + random.randint(-70, 70),
                             self.rect.bottom - random.randint(10, 90), 500, (0.8, 1.4), (0.8, 1.4))
            if dt >= DURACAO[e]:
                self.derrotado_total = True

    def _escolher_ataque(self, jogador):
        self._virar_para(jogador)
        if abs(jogador.rect.centerx - self.rect.centerx) < DISTANCIA_CORPO_A_CORPO:
            self._mudar(random.choice(["garra_aviso", "cauda_aviso"]))
        else:
            self._mudar("raio_aviso")

    def _origem_raio(self):
        return self.rect.right - 20 if self.olhando_direita else self.rect.left + 20

    def rect_raio(self):
        if self.estado != "raio_disparo":
            return None
        progresso = min(1.0, (pygame.time.get_ticks() - self._inicio_estado) / TEMPO_CRESCER_RAIO)
        x0 = self._origem_raio()
        ate_a_borda = (self.largura_arena - x0) if self.olhando_direita else x0
        comprimento = int(min(ALCANCE_RAIO, ate_a_borda) * progresso)
        topo = self.chao - CENTRO_RAIO - ALTURA_DANO_RAIO // 2
        if self.olhando_direita:
            return pygame.Rect(x0, topo, comprimento, ALTURA_DANO_RAIO)
        return pygame.Rect(x0 - comprimento, topo, comprimento, ALTURA_DANO_RAIO)

    
    def zonas_de_ataque(self):
        r = self.rect
        zonas = []
        if self.estado == "garra_golpe":
            if self.olhando_direita:
                zonas.append(pygame.Rect(r.right - 10, r.top - 30, 120, r.h + 30))
            else:
                zonas.append(pygame.Rect(r.left - 110, r.top - 30, 120, r.h + 30))
        elif self.estado == "cauda_golpe":
            zonas.append(pygame.Rect(r.right - 10, r.top - 50, 110, r.h + 50))
            zonas.append(pygame.Rect(r.left - 100, r.top - 50, 110, r.h + 50))
        raio = self.rect_raio()
        if raio:
            zonas.append(raio)
        return zonas

    def interagir(self, jogador):
        if self.estado == "morrendo" or self.derrotado_total:
            return None
        j = jogador
        if self.estado != "cansado" and j.rect.colliderect(self.rect):
            return "dano"
        if any(j.rect.colliderect(z) for z in self.zonas_de_ataque()):
            return "dano"
        return None

    def receber_dano(self, quantidade, ponto_x, ponto_y=None):
        if self.estado == "morrendo" or self.derrotado_total:
            return
        agora = pygame.time.get_ticks()
        self.vida = max(0, self.vida - quantidade)
        self._brilho_ate = agora + TEMPO_BRILHO
        y = (ponto_y if ponto_y is not None else self.rect.bottom - 40) + 30
        self._efeito("impacto", ponto_x, y, 260, (0.5, 0.9), (0.5, 0.9))
        if self.derrotado:
            self._ultimo_tremor = agora
            self._mudar("morrendo")


    def _efeito(self, nome, x, y, duracao, esc_x, esc_y):
        self._efeitos.append({"nome": nome, "x": x, "y": y, "inicio": pygame.time.get_ticks(),
                              "dur": duracao, "sx": esc_x, "sy": esc_y})

    def _quadro(self, t):
        e, dt = self.estado, t - self._inicio_estado
        if e == "andando":
            return "andar", (t // 150) % 3
        if e == "garra_aviso":
            return "idle", 2
        if e == "garra_golpe":
            return "garra", 0 if dt < DURACAO[e] // 2 else 1
        if e == "cauda_aviso":
            return "idle", 3
        if e == "cauda_golpe":
            return "cauda", 0
        if e == "raio_aviso":
            return "especial", 0 if dt < DURACAO[e] // 2 else 1     
        if e == "raio_disparo":
            return "raio", 0
        if e == "cansado":
            return "especial", 0
        return "idle", (t // 220) % 4       

    def desenhar(self, tela, cam_x, t):
        if self.derrotado_total:
            return
        r = self.rect.move(-cam_x, 0)
        tremor = int(math.sin(t / 25) * 4) if self.estado == "morrendo" else 0
        if self._quadros:
            nome, i = self._quadro(t)
            vira = self.olhando_direita != (FRENTE_ORIGINAL[nome] == 1)
            imagem = self._quadros[(nome, i, bool(vira))]
            pes_y = int(r.bottom + (ALTURA_QUADRO - PES_NO_QUADRO) * ESCALA_CHEFE)
            alpha = 255
            if self.estado == "morrendo":
                alpha = int(255 * max(0.0, 1 - (t - self._inicio_estado) / DURACAO["morrendo"]))
            elif t < self._brilho_ate:
                alpha = 140                     
            if alpha < 255:
                imagem = imagem.copy()
                imagem.set_alpha(alpha)
            tela.blit(imagem, imagem.get_rect(midbottom=(r.centerx + tremor, pes_y)))
        elif self._sprite_antigo:
            img = self._sprite_antigo if not self.olhando_direita else pygame.transform.flip(self._sprite_antigo, True, False)
            tela.blit(img, img.get_rect(midbottom=(r.centerx + tremor, r.bottom)))
        else:
            self.desenhar_formas(tela, r, t)
        self._desenhar_raio(tela, cam_x, t)
        self._desenhar_efeitos(tela, cam_x, t)

    def _desenhar_raio(self, tela, cam_x, t):
        cabeca = visual.carregar_sprite_escala("efeitos/raio_cabeca.png", ESCALA_RAIO)
        corpo = visual.carregar_sprite_escala("efeitos/raio_corpo.png", ESCALA_RAIO)
        ponta = visual.carregar_sprite_escala("efeitos/raio_ponta.png", ESCALA_RAIO)
        if not (cabeca and corpo and ponta):
            return
        x0 = self._origem_raio() - cam_x
        y = self.chao - CENTRO_RAIO
        dt = t - self._inicio_estado
        if self.estado == "raio_aviso":                   
            p = min(1.0, dt / DURACAO["raio_aviso"])
            tam = (max(1, int(cabeca.get_width() * (0.3 + 0.7 * p))), max(1, int(cabeca.get_height() * (0.3 + 0.7 * p))))
            img = pygame.transform.smoothscale(cabeca, tam)
            img.set_alpha(int(110 + 145 * p) if (t // 70) % 2 == 0 else int(70 + 100 * p))
            if not self.olhando_direita:
                img = pygame.transform.flip(img, True, False)
            tela.blit(img, img.get_rect(center=(int(x0), int(y))))
            return
        raio = self.rect_raio()
        if not raio or raio.w < 6:
            return
        total = raio.w
        largura_corpo = max(1, total - cabeca.get_width() - ponta.get_width())
        pulsar = 1.0 + 0.10 * math.sin(t / 35)                       
        corpo_esticado = pygame.transform.smoothscale(corpo, (largura_corpo, max(1, int(corpo.get_height() * pulsar))))
        altura = max(cabeca.get_height(), corpo_esticado.get_height(), ponta.get_height())
        feixe = pygame.Surface((total, altura), pygame.SRCALPHA)
        feixe.blit(cabeca, (0, (altura - cabeca.get_height()) // 2))
        feixe.blit(corpo_esticado, (cabeca.get_width(), (altura - corpo_esticado.get_height()) // 2))
        feixe.blit(ponta, (total - ponta.get_width(), (altura - ponta.get_height()) // 2))
        if not self.olhando_direita:
            feixe = pygame.transform.flip(feixe, True, False)
        esquerda = x0 if self.olhando_direita else x0 - total
        tela.blit(feixe, (int(esquerda), int(y - altura // 2)))

    def _desenhar_efeitos(self, tela, cam_x, t):
        for ef in self._efeitos:
            p = (t - ef["inicio"]) / ef["dur"]
            if not 0 <= p < 1:
                continue
            base = visual.carregar_sprite_escala(f"efeitos/{ef['nome']}.png", 1.0)
            if base is None:
                continue
            sx = ef["sx"][0] + (ef["sx"][1] - ef["sx"][0]) * p
            sy = ef["sy"][0] + (ef["sy"][1] - ef["sy"][0]) * p
            img = pygame.transform.smoothscale(base, (max(1, int(base.get_width() * sx)), max(1, int(base.get_height() * sy))))
            img.set_alpha(int(255 * (1 - p)))
            tela.blit(img, img.get_rect(midbottom=(ef["x"] - cam_x, ef["y"])))

    def desenhar_formas(self, tela, r, t):
        pygame.draw.rect(tela, (140, 40, 200), r, border_radius=12)
        pygame.draw.polygon(tela, (235, 120, 255), [(r.centerx, r.top + 10), (r.centerx + 12, r.top + 30), (r.centerx, r.top + 50), (r.centerx - 12, r.top + 30)])
