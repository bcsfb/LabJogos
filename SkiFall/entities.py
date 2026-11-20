#game objects do SkiFall

#jogador  - posição y fixa; posturas: reto, inclinado p/ direita, inclinado p/ esquerda, sacando a serra, sacando a carne e caído.
#arvore   - pinheiros (n designs), estáticos; só se movem em y (o mundo é que passa).
#lobo     - só nas faixas laterais, mas a ameaça cobre lateral + central (ele salta).
#item     - consumíveis: serra, carne, vida extra, multiplicador, redutor de velocidade, ímã.
#pedra    - obstáculo de pista que a serra NÃO corta (liberado por pontuação).
#gelo     - placa de gelo: deixa a troca de faixa mais lenta (liberado por pontuação).

#todos os objetos do mundo guardam o CENTRO (x, cy); o sprite do PPlay é posicionado a partir dele.

import math
import random

import pygame

import texto
from assets import novo_sprite, reiniciar_animacao
from config import (
    ALCANCE_CARNE, ALCANCE_SERRA, ARQUIVOS_ITENS, DURACAO_TROCA_FAIXA, FATOR_HITBOX_ITEM,
    GELO_FATOR_TROCA, HITBOX_GELO_FATOR, HITBOX_JOGADOR, HITBOX_PEDRA_FATOR, HITBOX_LOBO, HITBOX_PINHEIRO, LOBO_PELAGENS, LOBO_TEMPO_BOTE,
    LOBO_TEMPO_COMENDO, LOBO_VEL_BOTE, NUM_FAIXAS, TEMPO_INVULNERAVEL, TEMPO_POSE_CARNE,
    TEMPO_POSE_SERRA,
)
from utils import clamp, hitbox_centrada, lerp, suave_saida

QUADRO_JOGADOR = 150          # as poses geradas têm 150x150, com o corpo no centro


def _aproximar(valor, alvo, passo):
    if valor < alvo:
        return min(alvo, valor + passo)
    return max(alvo, valor - passo)


#jogador
class Jogador:
    def __init__(self, centros, cy):
        self.centros = centros
        self.cy = cy
        tempo_carne = int(TEMPO_POSE_CARNE * 1000)
        self.sprites = {
            "reto": novo_sprite("player_reto"),
            "direita": novo_sprite("player_direita"),
            "esquerda": novo_sprite("player_esquerda"),
            "caido": novo_sprite("player_caido"),
            "serra": novo_sprite("player_serra", 4, 260),
            "carne_d": novo_sprite("player_carne_d", 3, tempo_carne, loop=False),
            "carne_e": novo_sprite("player_carne_e", 3, tempo_carne, loop=False),
        }
        self.reiniciar()

    def reiniciar(self):
        self.x = float(self.centros[1])
        self.faixa_destino = 1
        self.x_origem = self.x
        self.x_alvo = self.x
        self.prog = 1.0                 # 0..1 durante a troca de faixa
        self.direcao = 0
        self.t_pos_troca = 0.0          # a inclinação "sobra" um instante depois de chegar
        self.acao = None                # "serra" | "carne" | None
        self.t_acao = 0.0
        self.lado_carne = 1
        self.tombado = False
        self.t_tombado = 0.0
        self.invulneravel = 0.0
        self.t_gelo = 0.0               # >0 enquanto está (ou acabou de sair) do gelo
        self.serra = False              # inventário
        self.carne = False
        self.vida_extra = False
        self.relogio = 0.0

    #estado
    @property
    def faixa_atual(self):
        return min(range(NUM_FAIXAS), key=lambda i: abs(self.centros[i] - self.x))

    @property
    def no_gelo(self):
        return self.t_gelo > 0

    @property
    def em_troca(self):
        return self.prog < 1.0

    def mover(self, direcao):
        """Pede troca de faixa (-1 esquerda, +1 direita). Encadeia a partir do destino atual."""
        if self.tombado:
            return False
        destino = int(clamp(self.faixa_destino + direcao, 0, NUM_FAIXAS - 1))
        if destino == self.faixa_destino:
            return False
        self.faixa_destino = destino
        self.x_origem = self.x
        self.x_alvo = float(self.centros[destino])
        self.prog = 0.0
        self.direcao = 1 if self.x_alvo > self.x_origem else -1
        return True

    def acionar_serra(self):
        self.acao = "serra"
        self.t_acao = TEMPO_POSE_SERRA
        reiniciar_animacao(self.sprites["serra"])

    def acionar_carne(self, lado):
        self.acao = "carne"
        self.lado_carne = lado
        self.t_acao = TEMPO_POSE_CARNE
        reiniciar_animacao(self.sprites["carne_d" if lado >= 0 else "carne_e"])

    def tombar(self):
        self.tombado = True
        self.t_tombado = 0.0
        self.acao = None

    def levantar(self):
        self.tombado = False
        self.acao = None
        self.invulneravel = TEMPO_INVULNERAVEL
        # volta para a faixa mais próxima, parado
        f = self.faixa_atual
        self.faixa_destino = f
        self.x = self.x_origem = self.x_alvo = float(self.centros[f])
        self.prog = 1.0

    def postura(self):
        if self.tombado:
            return "caido"
        if self.acao == "serra" and self.t_acao > 0:
            return "serra"
        if self.acao == "carne" and self.t_acao > 0:
            return "carne_d" if self.lado_carne >= 0 else "carne_e"
        if self.prog < 1.0 or self.t_pos_troca > 0:
            return "direita" if self.direcao > 0 else "esquerda"
        return "reto"

    #atualização
    def atualizar(self, dt):
        self.relogio += dt
        if self.t_gelo > 0:
            self.t_gelo -= dt
        if self.prog < 1.0:
            duracao = DURACAO_TROCA_FAIXA * (GELO_FATOR_TROCA if self.t_gelo > 0 else 1.0)
            self.prog = min(1.0, self.prog + dt / duracao)
            self.x = lerp(self.x_origem, self.x_alvo, suave_saida(self.prog))
            if self.prog >= 1.0:
                self.x = self.x_alvo
                self.t_pos_troca = 0.07
        elif self.t_pos_troca > 0:
            self.t_pos_troca -= dt
        if self.t_acao > 0:
            self.t_acao -= dt
            if self.t_acao <= 0:
                self.acao = None
        if self.invulneravel > 0:
            self.invulneravel -= dt
        if self.tombado:
            self.t_tombado += dt
        sprite = self.sprites[self.postura()]
        sprite.update()      # avança a animação (spritesheet) do PPlay

    #colisão
    def hitbox(self):
        return hitbox_centrada(self.x, self.cy, *HITBOX_JOGADOR)

    def alcance_serra(self):

        h = self.hitbox()
        h.height += ALCANCE_SERRA
        return h

    def alcance_carne(self):
        h = self.hitbox()
        return h.inflate(ALCANCE_CARNE[0] * 2, ALCANCE_CARNE[1] * 2)

    def mao(self, lado):

        return (self.x + lado * 46, self.cy + 6)

    #desenho
    def desenhar(self, tela):
        nome = self.postura()
        sprite = self.sprites[nome]
        balanco = 0.0
        if nome == "reto":
            balanco = math.sin(self.relogio * 13) * 1.6
        elif nome == "caido":
            balanco = math.sin(self.t_tombado * 30) * 1.2 * max(0.0, 1.0 - self.t_tombado * 1.6)
        sprite.x = self.x - QUADRO_JOGADOR / 2 + (balanco if nome == "caido" else 0)
        sprite.y = self.cy - QUADRO_JOGADOR / 2 + (balanco if nome != "caido" else 0)
        # piscar enquanto invulnerável
        if self.invulneravel > 0:
            sprite.set_transparency(90 if int(self.relogio * 12) % 2 == 0 else 230)
        else:
            sprite.set_transparency(255)
        sprite.draw()


#objetos do mundo
class ObjetoMundo:
    #Base: guarda o centro (x, cy), anda com o mundo e sabe calcular a hitbox

    tipo = "objeto"

    def __init__(self, x, cy, sprite, caixa):
        self.x = float(x)
        self.cy = float(cy)
        self.cy_ant = float(cy)
        self.sprite = sprite
        self.largura = float(sprite.width)
        self.altura = float(sprite.height)
        self.caixa = caixa
        self.remover = False
        self.quase_gap = 9999.0      # menor folga lateral medida ao passar pelo esquiador ("QUASE!")
        self.quase_pago = False

    def mover(self, dt, vmundo):
        self.cy_ant = self.cy
        self.cy -= vmundo * dt
        if self.cy < -self.altura:
            self.remover = True

    def hitbox(self):
        return hitbox_centrada(self.x, self.cy, *self.caixa)

    def hitbox_varrida(self):
        h = self.hitbox()
        extra = int(self.cy_ant - self.cy)
        if extra > 0:
            h.height += extra
        return h

    def posicionar_sprite(self, desloc_y=0.0):
        self.sprite.x = self.x - self.largura / 2
        self.sprite.y = self.cy - self.altura / 2 + desloc_y


#pinheiro
class Arvore(ObjetoMundo):
    tipo = "arvore"
    VARIANTES = (1, 2, 3, 4)       # tree1/tree2 (originais) e tree3/tree4 (com neve)

    def __init__(self, x, cy, variante=None):
        self.variante = variante or random.choice(self.VARIANTES)
        self.nome = f"tree{self.variante}"
        super().__init__(x, cy, novo_sprite(self.nome), HITBOX_PINHEIRO)

    def desenhar(self, tela, sombras):
        sombras.desenhar(tela, self.x, self.cy + self.altura * 0.40, self.largura * 0.72, 20)
        self.posicionar_sprite()
        self.sprite.draw()


#pedra
class Pedra(ObjetoMundo):

    tipo = "pedra"
    VARIANTES = (1, 2)

    def __init__(self, x, cy, variante=None):
        self.variante = variante or random.choice(self.VARIANTES)
        self.nome = f"pedra_obs{self.variante}"
        sprite = novo_sprite(self.nome)
        caixa = (sprite.width * HITBOX_PEDRA_FATOR[0], sprite.height * HITBOX_PEDRA_FATOR[1])
        super().__init__(x, cy, sprite, caixa)

    def desenhar(self, tela, sombras):
        sombras.desenhar(tela, self.x, self.cy + self.altura * 0.36, self.largura * 0.85, 16)
        self.posicionar_sprite()
        self.sprite.draw()


#gelo
class Gelo(ObjetoMundo):

    tipo = "gelo"

    def __init__(self, x, cy):
        sprite = novo_sprite("gelo")
        caixa = (sprite.width * HITBOX_GELO_FATOR[0], sprite.height * HITBOX_GELO_FATOR[1])
        super().__init__(x, cy, sprite, caixa)
        self.fase = random.uniform(0, math.tau)

    def desenhar(self, tela, relogio):
        self.posicionar_sprite()
        self.sprite.draw()
        # brilhos piscando
        for i, (ox, oy) in enumerate(((-62, -22), (58, 14), (-8, 30))):
            if math.sin(relogio * 5 + self.fase + i * 2.1) > 0.35:
                cx, cy = int(self.x + ox), int(self.cy + oy)
                pygame.draw.line(tela, (255, 255, 255), (cx - 6, cy), (cx + 6, cy), 3)
                pygame.draw.line(tela, (255, 255, 255), (cx, cy - 6), (cx, cy + 6), 3)


#lobo
class Lobo(ObjetoMundo):
    #estados: espreita -> bote -> (desviado -> comendo -> saindo)  ou  (atacando).
    #nasce numa faixa lateral e, quando está perto, SALTA até a faixa central

    tipo = "lobo"

    def __init__(self, faixa, centros, cy):
        self.faixa = faixa
        self.lado = -1 if faixa == 0 else 1          # -1: lado esquerdo da pista, +1: direito
        self.x_lateral = float(centros[faixa])
        self.x_centro = float(centros[1])
        self.pelagem = random.choice(LOBO_PELAGENS)
        # o sprite original olha para a esquerda: o lobo da esquerda precisa olhar para a direita
        sufixo = "d" if self.lado < 0 else "e"
        super().__init__(self.x_lateral, cy, novo_sprite(f"lobo_{self.pelagem}_{sufixo}"), HITBOX_LOBO)
        self.estado = "espreita"
        self.t_estado = 0.0
        self.relogio = random.uniform(0, 6)
        self.sinal = None            # "bote": avisa o jogo para tocar o rosnado

    def mudar(self, estado):
        self.estado = estado
        self.t_estado = 0.0

    @property
    def perigoso(self):
        return self.estado in ("espreita", "bote")

    def comer(self):
        #chama quando carne chega ao lobo
        self.mudar("comendo")
        self.sinal = "mastigar"

    def atualizar(self, dt, vmundo, jogador):
        self.t_estado += dt
        self.relogio += dt
        if self.estado != "atacando":
            self.mover(dt, vmundo)
        if self.estado == "espreita":
            dist = self.cy - jogador.cy
            if dist > 0 and vmundo > 1.0 and dist / vmundo <= LOBO_TEMPO_BOTE:
                self.mudar("bote")
                self.sinal = "bote"
        elif self.estado == "bote":
            self.x = _aproximar(self.x, self.x_centro, LOBO_VEL_BOTE * dt)
        elif self.estado == "desviado":
            self.x = _aproximar(self.x, self.x_lateral, 1400 * dt)
        elif self.estado == "comendo":
            self.x = _aproximar(self.x, self.x_lateral, 700 * dt)
            if self.t_estado >= LOBO_TEMPO_COMENDO:
                self.mudar("saindo")
        elif self.estado == "saindo":
            self.x += self.lado * 520 * dt
            if abs(self.x - self.x_centro) > 900:
                self.remover = True

    def desenhar(self, tela, sombras, relogio_global):
        desloc = 0.0
        if self.estado in ("espreita", "bote", "desviado", "saindo"):
            desloc = math.sin(self.relogio * 19) * 3.2                       # trote
        elif self.estado == "comendo":
            desloc = abs(math.sin(self.relogio * 13)) * 5.0                  # mastigando
        sombras.desenhar(tela, self.x, self.cy + self.altura * 0.40, self.largura * 0.8, 16)
        self.posicionar_sprite(desloc)
        self.sprite.draw()
        # "!" de alerta quando o salto está para acontecer
        if self.estado == "espreita" and self.cy < 760:
            piscar = int(relogio_global * 8) % 2 == 0
            if piscar:
                texto.desenhar(tela, "!", self.x, self.cy - self.altura / 2 - 34, 36,
                               (255, 80, 70), "centro", (90, 10, 10), 3)


#consumíveis
_halos = {}


def _halo(cor, raio):
    chave = (cor, raio)
    surf = _halos.get(chave)
    if surf is None:
        surf = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        for r in range(raio, 0, -2):
            a = int(120 * (1 - r / raio) ** 1.6)
            pygame.draw.circle(surf, (cor[0], cor[1], cor[2], a), (raio, raio), r)
        _halos[chave] = surf
    return surf


COR_HALO = {
    "saw": (255, 150, 50),
    "meat": (255, 90, 110),
    "life": (255, 80, 90),
    "multiplier": (255, 214, 70),
    "mud": (190, 140, 90),
    "ima": (255, 100, 110),
}


class Item(ObjetoMundo):
    tipo = "item"

    def __init__(self, subtipo, x, cy, valor=0, duracao=0):
        self.subtipo = subtipo
        self.valor = valor            # multiplicador (2,5,8) ou % de redução
        self.duracao = duracao        # segundos do efeito (multiplicador / redutor)
        sprite = novo_sprite(ARQUIVOS_ITENS[subtipo])
        caixa = (sprite.width * FATOR_HITBOX_ITEM, sprite.height * FATOR_HITBOX_ITEM)
        super().__init__(x, cy, sprite, caixa)
        self.fase = random.uniform(0, math.tau)

    def desenhar(self, tela, relogio):
        flutuar = math.sin(relogio * 4.2 + self.fase) * 5.0
        raio = int(max(self.largura, self.altura) * 0.95)
        halo = _halo(COR_HALO[self.subtipo], raio)
        pulso = 0.65 + 0.35 * math.sin(relogio * 5 + self.fase)
        halo.set_alpha(int(255 * pulso))
        tela.blit(halo, (int(self.x - raio), int(self.cy - raio + flutuar)))
        self.posicionar_sprite(flutuar)
        self.sprite.draw()
        rotulo = None
        if self.subtipo == "multiplier":
            rotulo = (f"x{self.valor}", (255, 224, 90))
        elif self.subtipo == "mud":
            rotulo = (f"-{self.valor}%", (236, 196, 140))
        if rotulo:
            texto.desenhar(tela, rotulo[0], self.x, self.cy - self.altura / 2 - 30 + flutuar, 26,
                           rotulo[1], "centro", (12, 24, 52), 3)
