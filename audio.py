import os
import pygame
from settings import VOLUME_MUSICA, VOLUME_EFEITOS

PASTA_SONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sons")
EXTENSOES = (".ogg", ".mp3", ".wav")  


class Audio:
    def __init__(self):
        self.ativo = True
        self.mudo = False
        self.musica_atual = None
        self._efeitos = {}
        try:
            pygame.mixer.init()
        except pygame.error:
            self.ativo = False     

    def _achar(self, nome):
        for ext in EXTENSOES:
            caminho = os.path.join(PASTA_SONS, nome + ext)
            if os.path.exists(caminho):
                return caminho
        return None

    def tocar(self, nome):
        if not self.ativo or self.mudo:
            return
        if nome not in self._efeitos:
            caminho = self._achar(nome)
            try:
                self._efeitos[nome] = pygame.mixer.Sound(caminho) if caminho else None
            except pygame.error:
                self._efeitos[nome] = None
            if self._efeitos[nome]:
                self._efeitos[nome].set_volume(VOLUME_EFEITOS)
        if self._efeitos[nome]:
            self._efeitos[nome].play()

    def musica(self, nome):
        if not self.ativo or nome == self.musica_atual:
            return
        self.musica_atual = nome
        caminho = self._achar(nome)
        if not caminho:
            pygame.mixer.music.stop()
            return
        try:
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(0 if self.mudo else VOLUME_MUSICA)
            pygame.mixer.music.play(-1)      
        except pygame.error:
            pass

    def parar_musica(self):
        if self.ativo:
            pygame.mixer.music.stop()
        self.musica_atual = None

    def alternar_mudo(self):
        self.mudo = not self.mudo
        if self.ativo:
            pygame.mixer.music.set_volume(0 if self.mudo else VOLUME_MUSICA)
        return self.mudo
