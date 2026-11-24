import math
import random
import sys
import pygame
from settings import LARGURA, ALTURA, FPS, DANO_ATAQUE, VIDAS_INICIAIS, VELOCIDADE_INICIAL, VELOCIDADE_MAXIMA, VELOCIDADE_CHEFE, FASE_CHEFE_ATIVA
from menu import Menu
from levels import Nivel, MAPA_FASE_1, BURACOS_FASE_1, MAPA_CHEFE
from player import Jogador, HUMANO, FANTASMA
from boss import Chefe
from audio import Audio
from ranking import Ranking, TAMANHO_NOME
import visual

TECLAS_PULO = (pygame.K_SPACE, pygame.K_s)      
DURACAO_SUGAR = 1500
DURACAO_ESCURECER = 600
DURACAO_CLAREAR = 600


class Jogo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Spirit: Escape from the Castle")
        self.relogio = pygame.time.Clock()
        self.rodando = True
        self.estado = "menu"   
        self.menu = Menu(["JOGAR", "RANKING", "OPÇÕES", "CRÉDITOS", "SAIR"])
        self.menu_gameover = Menu(["TENTAR NOVAMENTE", "VOLTAR AO MENU"])
        self.audio = Audio()
        self.botao_som = pygame.Rect(LARGURA - 46, 8, 36, 36)
        self.nivel = None
        self.jogador = None
        self.chefe = None
        self.cam_x = 0
        self.ponto_reaparecer = (0, 0)
        self.mensagem = ""
        self.mensagem_ate = 0
        self.tremor_ate = 0
        self.flash_ate = 0
        self.fator_velocidade = 1.0  
        self.maior_x = 0            
        self.transicao_inicio = 0
        self.transicao_origem = (0, 0)
        self.transicao_destino = (0, 0)
        self.fade_ate = 0
        # ranking
        self.ranking = Ranking()
        self.nome_jogador = ""        
        self.nome_digitado = ""       
        self.tempo_inicio = 0         
        self.tempo_final = 0         
        self.posicao_ranking = None  
        self.vitoria_inicio = 0

  
    def novo_jogo(self):
        self.nivel = Nivel(MAPA_FASE_1, BURACOS_FASE_1)
        self.jogador = Jogador(*self.nivel.inicio)
        self.chefe = None
        self.ponto_reaparecer = self.nivel.inicio
        self.cam_x = 0
        self.fator_velocidade = VELOCIDADE_INICIAL
        self.maior_x = 0
        self.tempo_inicio = pygame.time.get_ticks()
        self.estado = "jogando"
        self.audio.musica("musica_fase1")

    def iniciar_chefe(self):

        self.nivel = Nivel(MAPA_CHEFE)
        self.chefe = Chefe(*self.nivel.pos_chefe, largura_arena=self.nivel.largura_px)
        self.jogador.vidas = VIDAS_INICIAIS         
        self.jogador.mudar_forma(HUMANO)
        self.jogador.reaparecer(*self.nivel.inicio)
        self.ponto_reaparecer = self.nivel.inicio
        self.cam_x = 0
        self.fator_velocidade = VELOCIDADE_CHEFE
        self.jogador.pode_trocar_forma = False      
        self.jogador.pode_atacar = True           
        self.audio.musica("musica_chefe")

    def mostrar_mensagem(self, texto, duracao_ms=2500):
        self.mensagem = texto
        self.mensagem_ate = pygame.time.get_ticks() + duracao_ms

    
    def rodar(self):
        while self.rodando:
            self.relogio.tick(int(FPS * (self.fator_velocidade if self.estado == "jogando" else 1.0)))   
            self.tratar_eventos()
            if self.estado == "jogando":
                self.atualizar_jogo()
            elif self.estado == "transicao":
                self.atualizar_transicao()
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
                    self.abrir_tela_nome()
                elif escolha == "RANKING":
                    self.ranking.carregar()
                    self.posicao_ranking = None
                    self.estado = "ranking"
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
                escolha = self.menu_gameover.tratar_evento(evento)
                if escolha == "TENTAR NOVAMENTE":
                    self.novo_jogo()             
                elif escolha == "VOLTAR AO MENU" or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                    self.voltar_ao_menu()
            elif self.estado == "nome":
                self.tratar_evento_nome(evento)
            elif self.estado == "vitoria":
                if (evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE)
                        and pygame.time.get_ticks() - self.vitoria_inicio > 500):
                    self.estado = "ranking"
            elif self.estado == "ranking":
                if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE, pygame.K_SPACE):
                    self.voltar_ao_menu()

    def tratar_eventos_jogo(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in TECLAS_PULO:
                if self.jogador.pular():
                    self.audio.tocar("pulo")
            elif evento.key == pygame.K_x:
                if self.jogador.atacar():
                    self.audio.tocar("ataque")
            elif evento.key == pygame.K_f:
                self.tentar_trocar_forma()
            elif evento.key == pygame.K_ESCAPE:
                self.voltar_ao_menu()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.botao_som.collidepoint(evento.pos):    
                self.audio.alternar_mudo()
        elif evento.type == pygame.KEYUP and evento.key in TECLAS_PULO:
            self.jogador.soltar_pulo()

    def abrir_tela_nome(self):
        self.nome_jogador = ""              
        self.nome_digitado = ""
        self.estado = "nome"
        pygame.key.set_repeat(400, 45)       

    def tratar_evento_nome(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key == pygame.K_ESCAPE:
            pygame.key.set_repeat()         
            self.estado = "menu"
        elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.nome_jogador = self.nome_digitado.strip()  
            pygame.key.set_repeat()       
            self.novo_jogo()
        elif evento.key == pygame.K_BACKSPACE:
            self.nome_digitado = self.nome_digitado[:-1]
        elif evento.unicode and evento.unicode.isprintable() and len(self.nome_digitado) < TAMANHO_NOME:
            self.nome_digitado += evento.unicode

    def vencer(self):
        self.estado = "vitoria"
        self.audio.parar_musica()
        self.audio.tocar("vitoria")
        self.vitoria_inicio = pygame.time.get_ticks()
        self.tempo_final = max(0, (self.vitoria_inicio - self.tempo_inicio) // 1000)
        self.posicao_ranking = self.ranking.adicionar(self.nome_jogador, self.jogador.pontos, self.tempo_final)

    def tentar_trocar_forma(self):
        if self.chefe:          
            return
        if self.jogador.trocar_forma():
            self.flash_ate = pygame.time.get_ticks() + 250
            self.audio.tocar("transformar")

    def voltar_ao_menu(self):
        self.audio.parar_musica()
        self.fator_velocidade = 1.0
        self.estado = "menu"

   
    def atualizar_jogo(self):
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
            self.fim_de_jogo()
        self.atualizar_camera()

    def fim_de_jogo(self):
        self.estado = "gameover"
        self.menu_gameover.indice = 0
        self.audio.parar_musica()
        self.audio.tocar("gameover")

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
                self.audio.tocar("cristal")

    def verificar_inimigos(self):
        j = self.jogador
        for inimigo in self.nivel.inimigos:
            if inimigo.vivo and j.rect.colliderect(inimigo.rect):
                if j.vel_y > 0 and j.rect.bottom - inimigo.rect.top <= 22:
                    inimigo.vivo = False      
                    j.quicar(9)
                    self.audio.tocar("pisar")
                elif j.tomar_dano():
                    self.audio.tocar("dano")

    def verificar_checkpoints(self):
        for ck in self.nivel.checkpoints:
            if not ck["ativo"] and self.jogador.rect.colliderect(ck["rect"]):
                ck["ativo"] = True
                self.ponto_reaparecer = (ck["rect"].x, ck["rect"].bottom - self.jogador.rect.height)
                self.mostrar_mensagem("Checkpoint!", 1200)
                self.audio.tocar("checkpoint")

    def verificar_espelhos(self):
        n, j = self.nivel, self.jogador
        if n.espelho_secreto and not n.espelho_usado and j.rect.colliderect(n.espelho_secreto):
            n.espelho_usado = True
            j.pode_trocar_forma = True
            j.mudar_forma(HUMANO)
            self.flash_ate = pygame.time.get_ticks() + 400
            self.audio.tocar("transformar")
        if FASE_CHEFE_ATIVA and n.grande_espelho and j.rect.colliderect(n.grande_espelho):
            self.iniciar_transicao()     

    def verificar_abismo(self):
        j = self.jogador
        if j.rect.top > ALTURA + 60:             
            j.perder_vida_abismo()
            self.audio.tocar("dano")
            if j.vidas > 0:
                j.reaparecer(*self.ponto_reaparecer)

    def atualizar_chefe(self):
        c, j, n = self.chefe, self.jogador, self.nivel
        c.atualizar(j, n.solidos())
        if c.pousou:
            self.tremor_ate = pygame.time.get_ticks() + 350
        alvo = pygame.Rect(c.rect.x, c.rect.y - 60, c.rect.w, c.rect.h + 60)
        for tiro in j.tiros:
            if tiro.vivo and alvo.colliderect(tiro.rect) and not c.derrotado:
                tiro.vivo = False
                c.receber_dano(DANO_ATAQUE, tiro.rect.centerx, tiro.rect.centery)
                self.audio.tocar("pisar")
                self.tremor_ate = max(self.tremor_ate, pygame.time.get_ticks() + 90)
        if c.interagir(j) == "dano":
            if j.tomar_dano():
                self.audio.tocar("dano")
                lado = 1 if j.rect.centerx > c.rect.centerx else -1
                j.empurrar(lado * 50)
        if c.derrotado_total and not n.portal_aberto:
            n.portal_aberto = True
            self.mostrar_mensagem("O portal de saída se abriu!", 3500)
        if n.portal_aberto and j.rect.colliderect(n.portal):
            self.vencer()

    def iniciar_transicao(self):
        self.estado = "transicao"
        self.transicao_inicio = pygame.time.get_ticks()
        self.transicao_origem = self.jogador.rect.center
        espelho = self.nivel.grande_espelho
        self.transicao_destino = (espelho.centerx, espelho.centery + 20)
        self.audio.tocar("portal")

    def atualizar_transicao(self):
        agora = pygame.time.get_ticks()
        if agora - self.transicao_inicio >= DURACAO_SUGAR + DURACAO_ESCURECER:
            self.iniciar_chefe()                 
            self.estado = "jogando"
            self.fade_ate = agora + DURACAO_CLAREAR


    def desenhar(self):
        t = pygame.time.get_ticks()
        if self.estado == "menu":
            self.desenhar_menu(t)
        elif self.estado == "opcoes":
            self.desenhar_tela_texto(t, "OPÇÕES", [
                "Setas ou A, D e S: andar", "Espaço: pular", "X: atirar um raio (na fase do chefe)",
                "F: trocar de forma (depois do espelho secreto)", "ESC: voltar ao menu", "",
                "Pule em cima dos inimigos para eliminá-los.",
                "Na fase final, esvazie a barra de vida do Scorpion atirando com X.", "Clique no ícone de som para ligar ou desligar.", "(ENTER para voltar)"])
        elif self.estado == "creditos":
            self.desenhar_tela_texto(t, "CRÉDITOS", [
                "Spirit: Escape from the Castle", "Projeto de Programação Orientada a Objetos",
                "Feito em Python + Pygame", "", "Equipe: Isabelle Monteiro e Allan Oliveira", "", "(ENTER para voltar)"])
        elif self.estado == "gameover":
            self.desenhar_gameover(t)
        elif self.estado == "nome":
            self.desenhar_nome(t)
        elif self.estado == "ranking":
            self.desenhar_ranking(t)
        elif self.estado == "vitoria":
            self.desenhar_vitoria(t)     
        else:
            self.desenhar_partida(t)
            if self.estado == "transicao":
                self.desenhar_transicao(t)

    def desenhar_gameover(self, t):
        fundo = visual.carregar_tela_cheia("game_over.png", proporcional=True)
        if fundo:
            self.tela.blit(fundo, (0, 0))
            self.menu_gameover.desenhar(self.tela, [376, 444], largura=356, altura=54, so_destaque=True)
        else:  
            self.desenhar_partida(t)
            self.desenhar_sobreposicao("AS CHAMAS SE APAGARAM...", "", (255, 120, 140))
            self.menu_gameover.desenhar(self.tela, [ALTURA // 2 + 80, ALTURA // 2 + 135])

    def desenhar_partida(self, t):
        cam = self.cam_x
        if t < self.tremor_ate:
            cam += random.randint(-5, 5)
        visual.desenhar_fundo(self.tela, self.cam_x)
        self.nivel.desenhar(self.tela, cam, t)
        if self.chefe:
            self.chefe.desenhar(self.tela, cam, t)
        if self.estado != "transicao":     
            self.jogador.desenhar(self.tela, cam, t)
        self.jogador.desenhar_tiros(self.tela, cam)
        self.desenhar_hud(t)
        if t < self.mensagem_ate:
            visual.desenhar_texto(self.tela, self.mensagem, 22, (255, 245, 200), centro=(LARGURA // 2, 70))
        if t < self.flash_ate:
            flash = pygame.Surface((LARGURA, ALTURA))
            flash.fill((255, 255, 255))
            flash.set_alpha(int(255 * (self.flash_ate - t) / 400))
            self.tela.blit(flash, (0, 0))
        if t < self.fade_ate:       
            veu = pygame.Surface((LARGURA, ALTURA))
            veu.set_alpha(int(255 * (self.fade_ate - t) / DURACAO_CLAREAR))
            self.tela.blit(veu, (0, 0))

    def desenhar_transicao(self, t):
        decorrido = t - self.transicao_inicio
        p = min(1.0, decorrido / DURACAO_SUGAR)
        suave = p * p * (3 - 2 * p)
        ox, oy = self.transicao_origem
        dx, dy = self.transicao_destino
        centro = (ox + (dx - ox) * suave - self.cam_x, oy + (dy - oy) * suave)
        imagem = self.jogador.imagem_atual()
        if imagem is None:
            imagem = pygame.Surface((32, 48))
            imagem.fill((190, 170, 255))
        imagem = pygame.transform.rotozoom(imagem, p * 720, 1.0 - 0.92 * suave)
        self.tela.blit(imagem, imagem.get_rect(center=centro))
        if decorrido > DURACAO_SUGAR:
            veu = pygame.Surface((LARGURA, ALTURA))
            veu.set_alpha(int(255 * min(1.0, (decorrido - DURACAO_SUGAR) / DURACAO_ESCURECER)))
            self.tela.blit(veu, (0, 0))

    def desenhar_hud(self, t):
        j = self.jogador
        for i in range(3):                               
            visual.desenhar_chama(self.tela, 30 + i * 32, 30, i < j.vidas)
        nome = "Fantasma" if j.forma == FANTASMA else "Humano"
        if j.pode_trocar_forma:
            texto = f"Mudar forma: F - {nome}"
        else:
            texto = f"Forma: {nome}"
        visual.desenhar_texto(self.tela, texto, 18, (190, 170, 255), topo_esq=(20, 55))
        if self.chefe and j.pode_atacar:
            visual.desenhar_texto(self.tela, "X: atirar", 18, (190, 170, 255), topo_esq=(20, 80))
        visual.desenhar_icone_som(self.tela, self.botao_som, self.audio.mudo)
        if self.chefe and not self.chefe.derrotado_total:        # barra de vida do Scorpion
            visual.desenhar_texto(self.tela, "SCORPION", 18, (255, 150, 255), topo_dir=(LARGURA - 20, 44))
            barra = pygame.Rect(LARGURA - 280, 72, 260, 18)
            pygame.draw.rect(self.tela, (30, 15, 55), barra, border_radius=5)
            cheio = barra.copy()
            cheio.width = int(barra.width * self.chefe.proporcao_vida)
            if cheio.width > 0:
                pygame.draw.rect(self.tela, (235, 70, 255), cheio, border_radius=5)
            pygame.draw.rect(self.tela, (200, 160, 255), barra, 2, border_radius=5)

    BOTOES_MENU_Y = [258, 300, 342, 384, 426]

    def desenhar_menu(self, t):
        imagem = visual.carregar_sprite("fundo_menu.png", (LARGURA, ALTURA))
        if imagem:
            self.tela.blit(pygame.transform.smoothscale(imagem, (LARGURA, ALTURA)), (0, 0))
            self.menu.desenhar(self.tela, self.BOTOES_MENU_Y, largura=214, altura=36, tamanho_fonte=21)
        else:   
            visual.desenhar_fundo(self.tela, t * 0.05)
            visual.desenhar_texto(self.tela, "Spirit:", 96, (190, 160, 255), centro=(LARGURA // 2, 85))
            visual.desenhar_texto(self.tela, "Escape from the Castle", 40, (215, 195, 255), centro=(LARGURA // 2, 160))
            self.menu.desenhar(self.tela, [240, 290, 340, 390, 440])

    def desenhar_tela_texto(self, t, titulo, linhas):
        visual.desenhar_fundo(self.tela, t * 0.05)
        visual.desenhar_texto(self.tela, titulo, 56, (190, 160, 255), centro=(LARGURA // 2, 70))
        for i, linha in enumerate(linhas):
            visual.desenhar_texto(self.tela, linha, 24, (230, 220, 255), centro=(LARGURA // 2, 150 + i * 36))

    def desenhar_nome(self, t):
        visual.desenhar_fundo(self.tela, t * 0.05)
        visual.desenhar_texto(self.tela, "QUAL É O SEU NOME?", 44, (190, 160, 255), centro=(LARGURA // 2, 130))
        caixa = pygame.Rect(0, 0, 460, 64)
        caixa.center = (LARGURA // 2, 235)
        pygame.draw.rect(self.tela, (20, 12, 50), caixa, border_radius=10)
        pygame.draw.rect(self.tela, (170, 120, 255), caixa, 3, border_radius=10)
        cursor = "|" if (t // 500) % 2 == 0 else " "
        visual.desenhar_texto(self.tela, self.nome_digitado + cursor, 34, (235, 225, 255), topo_esq=(caixa.x + 22, caixa.y + 11))
        visual.desenhar_texto(self.tela, f"Até {TAMANHO_NOME} letras (pode deixar em branco). Seu nome vai aparecer no ranking.", 20, (170, 150, 220), centro=(LARGURA // 2, 300))
        visual.desenhar_texto(self.tela, "ENTER: começar o jogo        ESC: voltar", 22, (235, 225, 255), centro=(LARGURA // 2, 380))

    def desenhar_vitoria(self, t):
        fundo = visual.carregar_tela_cheia("vitoria_fundo.png", proporcional=True)
        geometria = visual.geometria_tela("vitoria_fundo.png")
        if not fundo or not geometria:       
            self.desenhar_partida(t)
            self.desenhar_sobreposicao("VOCÊ ESCAPOU DO CASTELO!",
                                       f"Pontos: {self.jogador.pontos}     (ENTER: ranking)", (170, 255, 200))
            return
        self.tela.blit(fundo, (0, 0))
        escala, desloc_x, desloc_y = geometria
        pes = (desloc_x + 650 * escala, desloc_y + 808 * escala)
        visual.desenhar_heroi_pulando(self.tela, t - self.vitoria_inicio, pes, escala * 0.88, 170 * escala)
        pontos = self.jogador.pontos
        visual.desenhar_texto(self.tela, f"{self.nome_jogador or 'JOGADOR'}   |   Pontos: {pontos}   |   Tempo: {Ranking.formatar_tempo(self.tempo_final)}",
                              22, (235, 225, 255), centro=(LARGURA // 2, 470))
        visual.desenhar_texto(self.tela, "Enter: ver ranking", 18, (255, 235, 150), centro=(LARGURA // 2, 498))

    def desenhar_ranking(self, t):
        visual.desenhar_fundo(self.tela, t * 0.05)
        visual.desenhar_texto(self.tela, "RANKING", 52, (190, 160, 255), centro=(LARGURA // 2, 48))
        registros = self.ranking.melhores()
        if not registros:
            visual.desenhar_texto(self.tela, "Ninguém terminou o jogo ainda.", 26, (230, 220, 255), centro=(LARGURA // 2, 250))
            visual.desenhar_texto(self.tela, "Derrote o Scorpion para entrar aqui!", 22, (170, 150, 220), centro=(LARGURA // 2, 295))
        else:
            col_pos, col_nome, col_pontos, col_tempo = 230, 310, 700, 790
            visual.desenhar_texto(self.tela, "#", 18, (150, 125, 220), topo_esq=(col_pos, 92))
            visual.desenhar_texto(self.tela, "NOME", 18, (150, 125, 220), topo_esq=(col_nome, 92))
            visual.desenhar_texto(self.tela, "PONTOS", 18, (150, 125, 220), topo_dir=(col_pontos, 92))
            visual.desenhar_texto(self.tela, "TEMPO", 18, (150, 125, 220), topo_dir=(col_tempo, 92))
            for i, r in enumerate(registros):
                y = 122 + i * 34
                destaque = self.posicao_ranking == i + 1
                if destaque:      
                    faixa = pygame.Surface((560, 32), pygame.SRCALPHA)
                    faixa.fill((170, 120, 255, 70))
                    self.tela.blit(faixa, (col_pos - 20, y - 4))
                cor = (255, 235, 150) if destaque else (235, 225, 255)
                cor_pos = [(255, 215, 90), (215, 220, 235), (215, 150, 95)][i] if i < 3 else cor
                visual.desenhar_texto(self.tela, f"{i + 1}º", 24, cor_pos, topo_esq=(col_pos, y))
                visual.desenhar_texto(self.tela, r["nome"], 24, cor, topo_esq=(col_nome, y))
                visual.desenhar_texto(self.tela, str(r["pontos"]), 24, cor, topo_dir=(col_pontos, y))
                visual.desenhar_texto(self.tela, Ranking.formatar_tempo(r["tempo"]), 24, cor, topo_dir=(col_tempo, y))
        visual.desenhar_texto(self.tela, "ENTER: voltar ao menu", 20, (170, 150, 220), centro=(LARGURA // 2, 496))

    def desenhar_sobreposicao(self, titulo, subtitulo, cor):
        veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        veu.fill((5, 0, 20, 170))
        self.tela.blit(veu, (0, 0))
        visual.desenhar_texto(self.tela, titulo, 56, cor, centro=(LARGURA // 2, ALTURA // 2 - 20))
        visual.desenhar_texto(self.tela, subtitulo, 24, (235, 225, 255), centro=(LARGURA // 2, ALTURA // 2 + 40))
