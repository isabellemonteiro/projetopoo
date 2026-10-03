import math
import random
import sys
import pygame
from settings import LARGURA, ALTURA, FPS, GOLPES_PARA_VENCER, VELOCIDADE_INICIAL, VELOCIDADE_MAXIMA, VELOCIDADE_CHEFE, FASE_CHEFE_ATIVA
from menu import Menu
from levels import Nivel, MAPA_FASE_1, BURACOS_FASE_1, MAPA_CHEFE
from player import Jogador, HUMANO, FANTASMA
from boss import Chefe
import visual


class Jogo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Spirit: Escape from the Castle")
        self.relogio = pygame.time.Clock()
        self.rodando = True
        self.estado = "menu"   
        self.menu = Menu(["JOGAR", "OPÇÕES", "CRÉDITOS", "SAIR"])
        self.nivel = None
        self.jogador = None
        self.chefe = None
        self.cam_x = 0
        self.ponto_reaparecer = (0, 0)
        self.mensagem = ""
        self.mensagem_ate = 0
        self.tremor_ate = 0
        self.flash_ate = 0
        self.pausado = False
        self.fator_velocidade = 1.0  
        self.maior_x = 0            

  
    def novo_jogo(self):
        self.nivel = Nivel(MAPA_FASE_1, BURACOS_FASE_1)
        self.jogador = Jogador(*self.nivel.inicio)
        self.chefe = None
        self.ponto_reaparecer = self.nivel.inicio
        self.cam_x = 0
        self.pausado = False
        self.fator_velocidade = VELOCIDADE_INICIAL
        self.maior_x = 0
        self.estado = "jogando"

    def iniciar_chefe(self):

        self.nivel = Nivel(MAPA_CHEFE)
        self.chefe = Chefe(*self.nivel.pos_chefe)
        self.jogador.mudar_forma(HUMANO)
        self.jogador.reaparecer(*self.nivel.inicio)
        self.ponto_reaparecer = self.nivel.inicio
        self.cam_x = 0
        self.fator_velocidade = VELOCIDADE_CHEFE
        self.flash_ate = pygame.time.get_ticks() + 400

    def mostrar_mensagem(self, texto, duracao_ms=2500):
        self.mensagem = texto
        self.mensagem_ate = pygame.time.get_ticks() + duracao_ms

    
    def rodar(self):
        while self.rodando:
            self.relogio.tick(int(FPS * (self.fator_velocidade if self.estado == "jogando" else 1.0)))   
            self.tratar_eventos()
            if self.estado == "jogando":
                self.atualizar_jogo()
            self.desenhar()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    def tratar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            elif self.estado == "menu":
                escolha = self.menu.tratar_evento(evento)
                if escolha == "JOGAR":
                    self.novo_jogo()
                elif escolha == "OPÇÕES":
                    self.estado = "opcoes"
                elif escolha == "CRÉDITOS":
                    self.estado = "creditos"
                elif escolha == "SAIR":
                    self.rodando = False
            elif self.estado in ("opcoes", "creditos"):
                if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    self.estado = "menu"
            elif self.estado == "jogando":
                self.tratar_eventos_jogo(evento)
            elif self.estado == "gameover":
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN:
                        self.novo_jogo()          # volta ao início do jogo
                    elif evento.key == pygame.K_ESCAPE:
                        self.estado = "menu"
            elif self.estado == "vitoria":
                if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    self.estado = "menu"

    def tratar_eventos_jogo(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and not self.pausado:
                self.jogador.pular()
            elif evento.key == pygame.K_f and not self.pausado:
                self.tentar_trocar_forma()
            elif evento.key == pygame.K_p:
                self.pausado = not self.pausado
            elif evento.key == pygame.K_ESCAPE:
                self.estado = "menu"
        elif evento.type == pygame.KEYUP and evento.key == pygame.K_SPACE:
            self.jogador.soltar_pulo()

    def tentar_trocar_forma(self):
        if self.jogador.trocar_forma():
            self.flash_ate = pygame.time.get_ticks() + 250

   
    def atualizar_jogo(self):
        if self.pausado:
            return
        j = self.jogador
        teclas = pygame.key.get_pressed()
        self.nivel.atualizar(j)                      
        j.atualizar(teclas, self.nivel.solidos())
        j.limitar(0, self.nivel.largura_px)

        self.verificar_cristais()
        self.verificar_inimigos()
        self.verificar_checkpoints()
        self.verificar_espelhos()
        if self.chefe:
            self.atualizar_chefe()
        self.verificar_abismo()

        self.atualizar_dificuldade()
        if j.vidas <= 0:
            self.estado = "gameover"
        self.atualizar_camera()

    def atualizar_dificuldade(self):
        
        if self.chefe or not self.nivel.grande_espelho:
            return
        self.maior_x = max(self.maior_x, self.jogador.rect.x)
        progresso = min(1.0, self.maior_x / self.nivel.grande_espelho.x)
        self.fator_velocidade = VELOCIDADE_INICIAL + (VELOCIDADE_MAXIMA - VELOCIDADE_INICIAL) * progresso

    def atualizar_camera(self):
        alvo = self.jogador.rect.centerx - LARGURA // 2
        self.cam_x = max(0, min(alvo, self.nivel.largura_px - LARGURA))

    def verificar_cristais(self):
        for cristal in self.nivel.cristais[:]:
            if self.jogador.rect.colliderect(cristal):
                self.nivel.cristais.remove(cristal)
                self.jogador.coletar_cristal()

    def verificar_inimigos(self):
        j = self.jogador
        for inimigo in self.nivel.inimigos:
            if inimigo.vivo and j.rect.colliderect(inimigo.rect):
                if j.vel_y > 0 and j.rect.bottom - inimigo.rect.top <= 22:
                    inimigo.vivo = False      
                    j.quicar(9)
                else:
                    j.tomar_dano()

    def verificar_checkpoints(self):
        for ck in self.nivel.checkpoints:
            if not ck["ativo"] and self.jogador.rect.colliderect(ck["rect"]):
                ck["ativo"] = True
                self.ponto_reaparecer = (ck["rect"].x, ck["rect"].bottom - self.jogador.rect.height)
                self.mostrar_mensagem("Checkpoint!", 1200)

    def verificar_espelhos(self):
        n, j = self.nivel, self.jogador
        if n.espelho_secreto and not n.espelho_usado and j.rect.colliderect(n.espelho_secreto):
            n.espelho_usado = True
            j.pode_trocar_forma = True
            j.mudar_forma(HUMANO)
            self.flash_ate = pygame.time.get_ticks() + 400
        if FASE_CHEFE_ATIVA and n.grande_espelho and j.rect.colliderect(n.grande_espelho):
            self.iniciar_chefe()     

    def verificar_abismo(self):
        j = self.jogador
        if j.rect.top > ALTURA + 60:             
            j.perder_vida_abismo()
            if j.vidas > 0:
                j.reaparecer(*self.ponto_reaparecer)

    def atualizar_chefe(self):
        c, j, n = self.chefe, self.jogador, self.nivel
        c.atualizar(j, n.solidos())
        if c.pousou:
            self.tremor_ate = pygame.time.get_ticks() + 350
        resultado = c.interagir(j)
        if resultado == "dano":
            if j.tomar_dano():
                lado = 1 if j.rect.centerx > c.rect.centerx else -1
                j.empurrar(lado * 50)
        elif resultado == "golpe":
            j.quicar(13)
            self.tremor_ate = pygame.time.get_ticks() + 250
        elif resultado == "pisou":
            j.quicar(8)
        elif resultado == "fantasma":
            j.quicar(8)
        if c.derrotado_total and not n.portal_aberto:
            n.portal_aberto = True
        if n.portal_aberto and j.rect.colliderect(n.portal):
            self.estado = "vitoria"


    def desenhar(self):
        t = pygame.time.get_ticks()
        if self.estado == "menu":
            self.desenhar_menu(t)
        elif self.estado == "opcoes":
            self.desenhar_tela_texto(t, "OPÇÕES", [
                "Setas esquerda/direita: andar", "Espaço: pular (segure para pular mais alto)",
                "F: trocar de forma (depois do espelho secreto)", "ESC: voltar ao menu", "",
                "Pule em cima dos inimigos para eliminá-los.",
                "Só o HUMANO quebra o cristal do Scorpion.", "", "(ENTER para voltar)"])
        elif self.estado == "creditos":
            self.desenhar_tela_texto(t, "CRÉDITOS", [
                "Spirit: Escape from the Castle", "Projeto de Programação Orientada a Objetos",
                "Feito em Python + Pygame", "", "Equipe: Isabelle Monteiro e Allan Oliveira", "", "(ENTER para voltar)"])
        else:
            self.desenhar_partida(t)
            if self.estado == "gameover":
                self.desenhar_sobreposicao("AS CHAMAS SE APAGARAM...",
                                           "ENTER: recomeçar do início    ESC: menu", (255, 120, 140))
            elif self.estado == "vitoria":
                self.desenhar_sobreposicao("VOCÊ ESCAPOU DO CASTELO!",
                                           f"Pontos: {self.jogador.pontos}     (ENTER: menu)", (170, 255, 200))

    def desenhar_partida(self, t):
        cam = self.cam_x
        if t < self.tremor_ate:
            cam += random.randint(-5, 5)
        visual.desenhar_fundo(self.tela, self.cam_x)
        self.nivel.desenhar(self.tela, cam, t)
        if self.chefe:
            self.chefe.desenhar(self.tela, cam, t)
        self.jogador.desenhar(self.tela, cam, t)
        self.desenhar_hud(t)
        if t < self.mensagem_ate:
            visual.desenhar_texto(self.tela, self.mensagem, 22, (255, 245, 200), centro=(LARGURA // 2, 70))
        if t < self.flash_ate:
            flash = pygame.Surface((LARGURA, ALTURA))
            flash.fill((255, 255, 255))
            flash.set_alpha(int(255 * (self.flash_ate - t) / 400))
            self.tela.blit(flash, (0, 0))
        if self.pausado:
            self.desenhar_sobreposicao("PAUSADO", "P para continuar", (255, 255, 255))

    def desenhar_hud(self, t):
        j = self.jogador
        for i in range(3):                                  # Chamas de Vida
            visual.desenhar_chama(self.tela, 30 + i * 32, 30, i < j.vidas)
        visual.desenhar_texto(self.tela, f"Pontos: {j.pontos}", 24, (200, 230, 255), topo_dir=(LARGURA - 20, 12))
        nome = "Fantasma" if j.forma == FANTASMA else "Humano"
        visual.desenhar_texto(self.tela, f"Forma: {nome}", 18, (190, 170, 255), topo_esq=(20, 55))
        if not self.chefe:
            visual.desenhar_texto(self.tela, f"Velocidade: x{self.fator_velocidade:.1f}", 18, (190, 170, 255), topo_esq=(20, 78))
        if self.chefe and not self.chefe.derrotado:
            restantes = GOLPES_PARA_VENCER - self.chefe.acertos
            visual.desenhar_texto(self.tela, "SCORPION", 18, (255, 150, 255), topo_dir=(LARGURA - 20, 44))
            for i in range(GOLPES_PARA_VENCER):
                cor = (235, 70, 255) if i < restantes else (70, 50, 90)
                x = LARGURA - 30 - i * 26
                pygame.draw.polygon(self.tela, cor, [(x, 78), (x + 9, 90), (x, 102), (x - 9, 90)])

    
    BOTOES_MENU_Y = [270, 315, 355, 397]

    def desenhar_menu(self, t):
        imagem = visual.carregar_sprite("fundo_menu.png", (LARGURA, ALTURA))
        if imagem:
            self.tela.blit(pygame.transform.smoothscale(imagem, (LARGURA, ALTURA)), (0, 0))
            self.menu.desenhar(self.tela, self.BOTOES_MENU_Y, largura=214, altura=38, tamanho_fonte=22)
        else:   
            visual.desenhar_fundo(self.tela, t * 0.05)
            visual.desenhar_texto(self.tela, "Spirit:", 96, (190, 160, 255), centro=(LARGURA // 2, 85))
            visual.desenhar_texto(self.tela, "Escape from the Castle", 40, (215, 195, 255), centro=(LARGURA // 2, 160))
            self.menu.desenhar(self.tela, [250, 308, 366, 424])

    def desenhar_tela_texto(self, t, titulo, linhas):
        visual.desenhar_fundo(self.tela, t * 0.05)
        visual.desenhar_texto(self.tela, titulo, 56, (190, 160, 255), centro=(LARGURA // 2, 70))
        for i, linha in enumerate(linhas):
            visual.desenhar_texto(self.tela, linha, 24, (230, 220, 255), centro=(LARGURA // 2, 150 + i * 36))

    def desenhar_sobreposicao(self, titulo, subtitulo, cor):
        veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        veu.fill((5, 0, 20, 170))
        self.tela.blit(veu, (0, 0))
        visual.desenhar_texto(self.tela, titulo, 56, cor, centro=(LARGURA // 2, ALTURA // 2 - 20))
        visual.desenhar_texto(self.tela, subtitulo, 24, (235, 225, 255), centro=(LARGURA // 2, ALTURA // 2 + 40))
