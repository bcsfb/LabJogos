#carregamento de imagens usando as classes do PPlay (GameImage / Sprite).

import pygame
from PPlay.gameimage import GameImage
from PPlay.sprite import Sprite

from config import PASTA_IMAGENS

_escaladas = {}
_espelhadas = {}

def caminho_imagem(nome):
    return str(PASTA_IMAGENS / f"{nome}.png")


def superficie(nome):

    return GameImage(caminho_imagem(nome)).image


def novo_sprite(nome, frames=1, duracao_ms=None, loop=True):

    sprite = Sprite(caminho_imagem(nome), frames)
    if frames > 1 and duracao_ms:
        sprite.set_total_duration(duracao_ms)
    sprite.set_loop(loop)
    return sprite


def reiniciar_animacao(sprite):
    sprite.frame_atual = 0
    sprite.tempo_acumulado = 0
    sprite.rodando = True


def superficie_escalada(nome, fator):
    chave = (nome, round(fator, 3))
    if chave not in _escaladas:
        base = superficie(nome)
        w = max(1, int(base.get_width() * fator))
        h = max(1, int(base.get_height() * fator))
        _escaladas[chave] = pygame.transform.scale(base, (w, h))  # 'scale' = pixel art nítida
    return _escaladas[chave]


def superficie_espelhada(nome, fator=1.0):
    chave = (nome, round(fator, 3))
    if chave not in _espelhadas:
        _espelhadas[chave] = pygame.transform.flip(superficie_escalada(nome, fator), True, False)
    return _espelhadas[chave]
