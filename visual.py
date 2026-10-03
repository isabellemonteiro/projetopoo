import math
import os
import random
import pygame
from settings import LARGURA, ALTURA

PASTA_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
_cache_sprites = {}
_cache_fontes = {}
_cache_fundo = None


def carregar_sprite(nome, tamanho):
    chave = (nome, tamanho)
    if chave not in _cache_sprites:
        imagem = None
        caminho = os.path.join(PASTA_ASSETS, nome)
        if os.path.exists(caminho):
            try:
                imagem = pygame.image.load(caminho).convert_alpha()
                
                escala = min(tamanho[0] / imagem.get_width(), tamanho[1] / imagem.get_height())
                novo = (max(1, int(imagem.get_width() * escala)), max(1, int(imagem.get_height() * escala)))
                imagem = pygame.transform.smoothscale(imagem, novo)
            except pygame.error:
                imagem = None
        _cache_sprites[chave] = imagem
    return _cache_sprites[chave]


def desenhar_texto(tela, texto, tamanho, cor, centro=None, topo_esq=None, topo_dir=None):
    
    if tamanho not in _cache_fontes:
        _cache_fontes[tamanho] = pygame.font.SysFont("arial", tamanho, bold=True)
    fonte = _cache_fontes[tamanho]
    imagem = fonte.render(texto, True, cor)
    sombra = fonte.render(texto, True, (10, 5, 30))
    ret = imagem.get_rect()
    if centro:
        ret.center = centro
    elif topo_esq:
        ret.topleft = topo_esq
    elif topo_dir:
        ret.topright = topo_dir
    tela.blit(sombra, ret.move(2, 2))
    tela.blit(imagem, ret)



def _criar_fundo():
    fundo = pygame.Surface((LARGURA, ALTURA))
    for y in range(ALTURA):  
        t = y / ALTURA
        pygame.draw.line(fundo, (int(12 + 40 * t), int(8 + 14 * t), int(40 + 60 * t)), (0, y), (LARGURA, y))
    sorteio = random.Random(7)
    for _ in range(80):  
        pygame.draw.circle(fundo, (200, 200, 255), (sorteio.randint(0, LARGURA), sorteio.randint(0, 300)), 1)
    pygame.draw.circle(fundo, (170, 185, 240), (790, 105), 48)  
    pygame.draw.circle(fundo, (150, 165, 225), (775, 95), 9)
    pygame.draw.circle(fundo, (150, 165, 225), (805, 122), 6)
    return fundo


def _silhueta_castelo(tela, x0):
    cor = (34, 24, 70)
    base = ALTURA - 150
    pygame.draw.rect(tela, cor, (x0, base, 480, 150))
    for tx, altura in ((20, 120), (140, 170), (290, 140), (410, 110)):
        pygame.draw.rect(tela, cor, (x0 + tx, base - altura, 50, altura))
        pygame.draw.polygon(tela, cor, [(x0 + tx - 6, base - altura), (x0 + tx + 25, base - altura - 50),
                                         (x0 + tx + 56, base - altura)])
        pygame.draw.rect(tela, (160, 90, 220), (x0 + tx + 20, base - altura + 25, 8, 14))  


def desenhar_fundo(tela, cam_x):

    global _cache_fundo
    if _cache_fundo is None:
        _cache_fundo = _criar_fundo()
    tela.blit(_cache_fundo, (0, 0))
    deslocamento = -(cam_x * 0.25) % 480
    for i in range(-1, LARGURA // 480 + 2):
        _silhueta_castelo(tela, deslocamento + i * 480)



def desenhar_bloco(tela, r):
    pygame.draw.rect(tela, (58, 48, 92), r)
    pygame.draw.rect(tela, (34, 28, 60), r, 2)
    pygame.draw.line(tela, (34, 28, 60), (r.x, r.centery), (r.right, r.centery), 2)
    pygame.draw.line(tela, (34, 28, 60), (r.centerx, r.y), (r.centerx, r.centery), 2)
    pygame.draw.line(tela, (100, 88, 160), (r.x + 2, r.y + 2), (r.right - 3, r.y + 2), 2)


def desenhar_cristal(tela, r, t):
    balanco = int(math.sin(t / 250 + r.x) * 3)
    cx, cy = r.centerx, r.centery + balanco
    pygame.draw.polygon(tela, (70, 170, 255), [(cx, cy - 13), (cx + 9, cy), (cx, cy + 13), (cx - 9, cy)])
    pygame.draw.polygon(tela, (200, 240, 255), [(cx, cy - 13), (cx + 3, cy - 2), (cx, cy + 4), (cx - 6, cy - 2)])


def desenhar_chama(tela, x, y, acesa, escala=1.0):
    cor = (150, 100, 255) if acesa else (60, 50, 90)
    pontos = [(0, -18), (10, -2), (7, 10), (0, 14), (-7, 10), (-10, -2)]
    pygame.draw.polygon(tela, cor, [(x + px * escala, y + py * escala) for px, py in pontos])
    if acesa:
        pygame.draw.circle(tela, (210, 240, 255), (int(x), int(y + 4 * escala)), max(2, int(4 * escala)))


def desenhar_tocha(tela, r, acesa, t):
    pygame.draw.rect(tela, (90, 80, 120), (r.centerx - 4, r.bottom - 34, 8, 34))
    pygame.draw.rect(tela, (120, 105, 160), (r.centerx - 9, r.bottom - 38, 18, 6))
    desenhar_chama(tela, r.centerx, r.bottom - 52, acesa, 0.8 + 0.1 * math.sin(t / 90))


def desenhar_plataforma_movel(tela, r):
    pygame.draw.line(tela, (120, 110, 150), (r.x + 6, r.y), (r.x + 6, r.y - 40), 3)
    pygame.draw.line(tela, (120, 110, 150), (r.right - 6, r.y), (r.right - 6, r.y - 40), 3)
    pygame.draw.rect(tela, (80, 70, 120), r)
    pygame.draw.rect(tela, (140, 125, 200), r, 2)


def desenhar_espelho(tela, r, t, brilho=True):
    pygame.draw.rect(tela, (110, 70, 200), r, border_radius=10)
    interior = r.inflate(-12, -12)
    luz = 150 + int(60 * math.sin(t / 300)) if brilho else 90
    pygame.draw.ellipse(tela, (luz, luz - 30, 255), interior)
    pygame.draw.line(tela, (230, 220, 255), (interior.x + 8, interior.y + 14), (interior.x + 18, interior.y + 6), 2)


def desenhar_grande_espelho(tela, r, t):
    sprite = carregar_sprite("grande_espelho.png", (r.w + 40, r.h))
    if sprite:
        tela.blit(sprite, sprite.get_rect(midbottom=r.midbottom))
    else:
        desenhar_espelho(tela, r, t)


def desenhar_portal(tela, r, t):
    for i in range(5):
        raio_x = r.w // 2 - i * 5
        raio_y = r.h // 2 - i * 9
        cor = (90 + i * 30, 60 + i * 30, 255)
        pygame.draw.ellipse(tela, cor, (r.centerx - raio_x, r.centery - raio_y + int(math.sin(t / 200 + i) * 3),
                                        raio_x * 2, raio_y * 2), 3)


def desenhar_fantasma(tela, r, direita, t):
    cor = (205, 220, 255)
    brilho = pygame.Surface((r.w + 20, r.h + 20), pygame.SRCALPHA)
    pygame.draw.ellipse(brilho, (120, 150, 255, 70), brilho.get_rect())
    tela.blit(brilho, (r.x - 10, r.y - 10))
    pygame.draw.ellipse(tela, cor, (r.x, r.y, r.w, int(r.h * 0.65)))
    pygame.draw.rect(tela, cor, (r.x, r.y + int(r.h * 0.3), r.w, int(r.h * 0.45)))
    for i in range(4):  # barra ondulada do "lençol"
        pygame.draw.circle(tela, cor, (r.x + 4 + i * 8, r.bottom - 8 + int(math.sin(t / 140 + i * 1.5) * 3)), 6)
    lado = 4 if direita else -4
    for ox in (-6, 6):
        pygame.draw.circle(tela, (25, 20, 60), (r.centerx + lado + ox, r.y + 16), 4)


def desenhar_humano(tela, r, direita, t):
    pygame.draw.rect(tela, (60, 60, 110), (r.x + 4, r.y + 20, r.w - 8, r.h - 32))       
    pygame.draw.rect(tela, (40, 40, 80), (r.x + 6, r.bottom - 14, 8, 14))               
    pygame.draw.rect(tela, (40, 40, 80), (r.right - 14, r.bottom - 14, 8, 14))
    pygame.draw.circle(tela, (240, 200, 170), (r.centerx, r.y + 12), 11)                 
    pygame.draw.rect(tela, (30, 25, 50), (r.centerx - 11, r.y, 22, 8))                 
    pygame.draw.rect(tela, (140, 70, 200), (r.x + 2, r.y + 22, r.w - 4, 6))            
    ponta = r.x - 10 if direita else r.right
    pygame.draw.polygon(tela, (140, 70, 200), [(ponta, r.y + 24), (ponta + 10, r.y + 24),
                                               (ponta + 5, r.y + 36 + int(math.sin(t / 120) * 3))])
    pygame.draw.circle(tela, (10, 10, 10), (r.centerx + (4 if direita else -4), r.y + 12), 2)


def desenhar_esqueleto(tela, r, t):
    osso = (235, 235, 225)
    pygame.draw.circle(tela, osso, (r.centerx, r.y + 11), 10)
    pygame.draw.circle(tela, (20, 10, 30), (r.centerx - 4, r.y + 10), 3)
    pygame.draw.circle(tela, (20, 10, 30), (r.centerx + 4, r.y + 10), 3)
    pygame.draw.line(tela, osso, (r.centerx, r.y + 20), (r.centerx, r.y + 32), 3)
    for i in range(3):
        pygame.draw.line(tela, osso, (r.centerx - 8, r.y + 22 + i * 4), (r.centerx + 8, r.y + 22 + i * 4), 2)
    passo = int(math.sin(t / 120) * 5)
    pygame.draw.line(tela, osso, (r.centerx, r.y + 32), (r.centerx - 6 + passo, r.bottom), 3)
    pygame.draw.line(tela, osso, (r.centerx, r.y + 32), (r.centerx + 6 - passo, r.bottom), 3)


def desenhar_morcego(tela, r, t):
    bater = int(math.sin(t / 80) * 8)
    cor = (110, 50, 170)
    pygame.draw.polygon(tela, cor, [(r.centerx - 4, r.centery), (r.x - 6, r.centery - 6 - bater), (r.x + 4, r.centery + 8)])
    pygame.draw.polygon(tela, cor, [(r.centerx + 4, r.centery), (r.right + 6, r.centery - 6 - bater), (r.right - 4, r.centery + 8)])
    pygame.draw.ellipse(tela, (80, 30, 130), (r.centerx - 8, r.centery - 8, 16, 18))
    pygame.draw.circle(tela, (255, 80, 80), (r.centerx - 3, r.centery - 2), 2)
    pygame.draw.circle(tela, (255, 80, 80), (r.centerx + 3, r.centery - 2), 2)
