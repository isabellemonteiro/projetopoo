import pygame
import sys


LARGURA, ALTURA = 800, 600
FPS = 60

pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Spirit: Escape from the Castle")
relogio = pygame.time.Clock()


fonte_titulo = pygame.font.SysFont("Arial", 45, bold=True)
fonte_grande = pygame.font.SysFont("Arial", 55, bold=True)
fonte_ui = pygame.font.SysFont("Arial", 24, bold=True)
fonte_creditos = pygame.font.SysFont("Arial", 20)


class Entidade:
    def __init__(self, x, y, largura, altura):
        self.rect = pygame.Rect(x, y, largura, altura)


class Tiro(Entidade):
    def __init__(self, x, y):
        
        super().__init__(x, y, 15, 8)
        
    def atualizar(self):
        self.rect.x += 14 


class Boss(Entidade):
    def __init__(self):
        
        super().__init__(550, 220, 140, 140)
        self.coracao = pygame.Rect(0, 0, 45, 45)
        self.vida = 5
        self.estado = 'MOVER' 
        self.timer = 0
        self.vel_x = 3
        self.direcao = -1

    def atualizar(self, player_x):
        self.timer += 1
        self.coracao.center = self.rect.center

        if self.estado == 'MOVER':
            self.rect.x += self.vel_x * self.direcao
            if self.rect.x < 250 or self.rect.right > 780:
                self.direcao *= -1
            if self.timer > 150:
                self.estado = 'ALVO'
                self.timer = 0

        elif self.estado == 'ALVO':
            alvo_x = max(250, player_x)
            if self.rect.centerx < alvo_x: self.rect.x += 5
            elif self.rect.centerx > alvo_x: self.rect.x -= 5
            if self.timer > 40:
                self.estado = 'ESMAGAR'
                self.timer = 0

        elif self.estado == 'ESMAGAR':
            self.rect.y += 16
            if self.rect.bottom >= 500:
                self.rect.bottom = 500
                self.estado = 'SUBIR'
                self.timer = 0

        elif self.estado == 'SUBIR':
            if self.timer > 90:
                self.rect.y -= 5
                if self.rect.y <= 220:
                    self.rect.y = 220
                    self.estado = 'MOVER'
                    self.timer = 0

def rodar_jogo():
    px, py = 50, 400
    p_rect = pygame.Rect(px, py, 30, 50)
    vy = 0
    no_chao = False
    vidas = 3
    forma = 'FANTASMA'
    
    tiros = []
    boss = None
    cooldown_tiro = 0
    
    plataformas_fase1 = [
        pygame.Rect(0, 500, 300, 100),
        pygame.Rect(450, 500, 350, 100),
    ]
    
    plataformas_boss = [
        pygame.Rect(0, 500, 800, 100)
    ]
    
    inimigos = [
        {"rect": pygame.Rect(180, 470, 30, 30), "tipo": "morcego"},
        {"rect": pygame.Rect(250, 470, 30, 30), "tipo": "esqueleto"},
        {"rect": pygame.Rect(520, 470, 30, 30), "tipo": "morcego"},
        {"rect": pygame.Rect(620, 470, 30, 30), "tipo": "esqueleto"},
    ]
    
    portal = pygame.Rect(720, 400, 40, 100)

    while True:
        relogio.tick(FPS)
        if cooldown_tiro > 0:
            cooldown_tiro -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if no_chao and forma != 'VITORIA':
                        vy = -14 if forma == 'FANTASMA' else -10
                        no_chao = False
                
                if event.key in [pygame.K_z, pygame.K_x]:
                    if forma == 'HUMANO' and cooldown_tiro == 0:
                        tiros.append(Tiro(p_rect.right, p_rect.centery - 5))
                        cooldown_tiro = 12 
                
                if event.key == pygame.K_ESCAPE:
                    return

        keys = pygame.key.get_pressed()
        vx = 0
        if forma != 'VITORIA':
            vel_player = 5 if forma == 'FANTASMA' else 4
            if keys[pygame.K_LEFT]: vx = -vel_player
            if keys[pygame.K_RIGHT]: vx = vel_player

        if forma == 'VITORIA':
            vx = 0
            if no_chao:
                vy = -8
                no_chao = False

        gravidade = 0.3 if forma == 'FANTASMA' else 0.6
        vy += gravidade
        if vy > 12: vy = 12

        plats_atuais = plataformas_fase1 if forma == 'FANTASMA' else plataformas_boss

        p_rect.x += vx
        for plat in plats_atuais:
            if p_rect.colliderect(plat):
                if vx > 0: p_rect.right = plat.left
                if vx < 0: p_rect.left = plat.right

        p_rect.y += vy
        no_chao = False
        for plat in plats_atuais:
            if p_rect.colliderect(plat):
                if vy > 0:
                    p_rect.bottom = plat.top
                    vy = 0
                    no_chao = True
                if vy < 0:
                    p_rect.top = plat.bottom
                    vy = 0

        if p_rect.y > ALTURA:
            return 

        if forma == 'FANTASMA':
            for inimigo in inimigos[:]:
                if p_rect.colliderect(inimigo["rect"]):
                    vidas -= 1
                    inimigos.remove(inimigo)
                    if vidas <= 0: return

            if p_rect.colliderect(portal):
                forma = 'HUMANO'
                p_rect.x, p_rect.y = 50, 400
                boss = Boss()

        elif forma == 'HUMANO':
            if boss is not None:
                boss.atualizar(p_rect.x)
                
                if p_rect.colliderect(boss.rect):
                    vidas -= 1
                    p_rect.x, p_rect.y = 50, 400 
                    if vidas <= 0: return

                for tiro in tiros[:]:
                    tiro.atualizar()
                    if tiro.rect.colliderect(boss.coracao):
                        boss.vida -= 1
                        tiros.remove(tiro)
                        if boss.vida <= 0:
                            forma = 'VITORIA'
                    elif tiro.rect.x > LARGURA:
                        tiros.remove(tiro)

        
        tela.fill((15, 15, 25))

        for plat in plats_atuais:
            pygame.draw.rect(tela, (50, 50, 60), plat)

        if forma == 'FANTASMA':
            pygame.draw.ellipse(tela, (0, 255, 200), portal, 4)
            for inimigo in inimigos:
                cor = (140, 70, 180) if inimigo["tipo"] == "morcego" else (210, 210, 210)
                pygame.draw.rect(tela, cor, inimigo["rect"])
            pygame.draw.ellipse(tela, (150, 220, 255), p_rect)

        elif forma == 'HUMANO' or forma == 'VITORIA':
            cor_portao = (0, 255, 0) if forma == 'VITORIA' else (120, 70, 20)
            pygame.draw.rect(cor_portao, (720, 380, 60, 120)) 
            for tiro in tiros:
                pygame.draw.rect(tela, (255, 255, 0), tiro.rect)

            pygame.draw.rect(tela, (220, 50, 50), p_rect)

            if forma == 'HUMANO' and boss is not None:
                pygame.draw.rect(tela, (70, 70, 80), boss.rect)
                pygame.draw.rect(tela, (255, 0, 50), boss.coracao)

        
        texto_vida = fonte_ui.render("Chamas de Vida: ", True, (255, 255, 255))
        tela.blit(texto_vida, (20, 20))
        for i in range(vidas):
            pygame.draw.circle(tela, (255, 100, 0), (180 + (i * 25), 32), 10)

        if forma == 'VITORIA':
            texto_vitoria = fonte_grande.render("VITÓRIA!", True, (0, 255, 100))
            tela.blit(texto_vitoria, (LARGURA // 2 - 120, ALTURA // 2 - 50))

        pygame.display.flip()


def main():
    estado_atual = "MENU" 
    opcao_selecionada = 0 
    opcoes_menu = ["JOGAR", "CREDITOS", "SAIR"]

    while True:
        relogio.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if estado_atual == "MENU":
                    if event.key == pygame.K_UP:
                        opcao_selecionada = (opcao_selecionada - 1) % len(opcoes_menu)
                    elif event.key == pygame.K_DOWN:
                        opcao_selecionada = (opcao_selecionada + 1) % len(opcoes_menu)
                    elif event.key == pygame.K_RETURN: 
                        if opcao_selecionada == 0:
                            rodar_jogo() 
                        elif opcao_selecionada == 1:
                            estado_atual = "CREDITOS"
                        elif opcao_selecionada == 2:
                            pygame.quit()
                            sys.exit()
                            
                elif estado_atual == "CREDITOS":
                    if event.key in [pygame.K_ESCAPE, pygame.K_RETURN]:
                        estado_atual = "MENU"

        
        if estado_atual == "MENU":
            tela.fill((10, 10, 20)) 
            
            titulo_txt = fonte_titulo.render("SPIRIT: ESCAPE FROM THE CASTLE", True, (150, 100, 255))
            tela.blit(titulo_txt, (LARGURA // 2 - titulo_txt.get_width() // 2, 100))
            
            for indice, texto_opcao in enumerate(opcoes_menu):
                if indice == opcao_selecionada:
                    cor = (0, 255, 200)
                    render_txt = fonte_grande.render(f"> {texto_opcao} <", True, cor)
                else:
                    cor = (255, 255, 255)
                    render_txt = fonte_grande.render(texto_opcao, True, cor)
                    
                pos_y = 260 + (indice * 80)
                tela.blit(render_txt, (LARGURA // 2 - render_txt.get_width() // 2, pos_y))

        elif estado_atual == "CREDITOS":
            tela.fill((15, 10, 20))
            
            sub_titulo = fonte_titulo.render("CRÉDITOS", True, (255, 215, 0))
            tela.blit(sub_titulo, (LARGURA // 2 - sub_titulo.get_width() // 2, 80))
            
            linhas_credito = [
                "Desenvolvido pela Equipe Spirit",
                "",
                "Design de Níveis",
                "Programação da Física & Engine",
                "Padrões do Boss Scorpion",
                "",
                "Pressione ENTER para voltar."
            ]
            
            for i, linha in enumerate(linhas_credito):
                cor_linha = (200, 200, 200) if i != len(linhas_credito)-1 else (0, 255, 200)
                txt_c = fonte_creditos.render(linha, True, cor_linha)
                tela.blit(txt_c, (LARGURA // 2 - txt_c.get_width() // 2, 220 + (i * 35)))

        pygame.display.flip()

if __name__ == "__main__":
    main()
