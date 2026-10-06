import math

from PPlay.sprite import Sprite

from config import (
    ALTURA,
    ARQUIVOS,
    VELOCIDADE_TROCA_FAIXA,
)
from utils import clamp


class Objeto:
    def __init__(self, sprite, faixa, y, tipo):
        self.sprite = sprite
        self.faixa = faixa
        self.tipo = tipo
        self.sprite.y = y

        self.removido = False
        self.foi_processado = False

        self.velocidade_ataque = 850.0
        self.lobo_atacando = False
        self.alvo_faixa = None

    def atualizar(self, dt, velocidade_mundo, player):
        if self.tipo == "wolf" and self.lobo_atacando:
            alvo_x = player.sprite.x + player.sprite.width / 2
            centro_x = self.sprite.x + self.sprite.width / 2
            diferenca = alvo_x - centro_x
            distancia = self.velocidade_ataque * dt

            if abs(diferenca) <= distancia:
                self.sprite.x += diferenca
                self.lobo_atacando = False
            else:
                self.sprite.x += math.copysign(distancia, diferenca)

        self.sprite.y -= velocidade_mundo * dt

        if self.sprite.y < -self.sprite.height - 80:
            self.removido = True

    def desenhar(self):
        self.sprite.draw()


class Player:
    def __init__(self, faixa_inicial, y_fixo):
        self.sprite = Sprite(str(ARQUIVOS["player"]))

        self.faixa_atual = faixa_inicial
        self.faixa_destino = faixa_inicial
        self.centros_faixas = []

        self.y_fixo = y_fixo
        self.sprite.y = y_fixo
        self.em_movimento = False

        # Inventário do GDD: serra, proteção contra lobo (carne) e vida extra.
        self.serra = False
        self.carne = False
        self.vida_extra = False

        self.angulo_visual = 0

    def definir_posicoes_faixas(self, centros_faixas):
        self.centros_faixas = centros_faixas
        self.sprite.x = centros_faixas[self.faixa_atual] - self.sprite.width / 2

    def mover_para(self, nova_faixa):
        nova_faixa = int(clamp(nova_faixa, 0, 2))

        if nova_faixa == self.faixa_destino:
            return

        self.faixa_destino = nova_faixa
        self.em_movimento = True

        if self.faixa_destino > self.faixa_atual:
            self.angulo_visual = 12
        else:
            self.angulo_visual = -12

    def atualizar(self, dt):
        if not self.centros_faixas:
            return

        alvo_x = self.centros_faixas[self.faixa_destino] - self.sprite.width / 2
        diferenca = alvo_x - self.sprite.x
        distancia_maxima = VELOCIDADE_TROCA_FAIXA * dt

        if abs(diferenca) <= distancia_maxima:
            self.sprite.x = alvo_x
            self.faixa_atual = self.faixa_destino
            self.em_movimento = False
            self.angulo_visual = 0
        else:
            self.sprite.x += math.copysign(distancia_maxima, diferenca)

        self.sprite.y = self.y_fixo

    def draw(self):
        self.sprite.draw()