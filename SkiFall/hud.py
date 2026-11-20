#HUD :
#tempo de sobrevivência e pontuação em tempo real;
#inventário
#multiplicador de pontos e redutor de velocidade com o tempo restante;
#indicador de velocidade.
#OBS: paineis e icones pre renderizados

import math

import pygame

import texto
from assets import superficie
from config import (
    ALTURA, COR_DOURADO, COR_TEXTO_SUAVE, DIFICULDADE_CORES, DIFICULDADE_NOMES, LARGURA, NEVASCA_BONUS_PONTOS,
)
from utils import clamp, mistura_cor

TAM_SLOT = 66
ICONE_MAX = 50

def painel(w, h, cor=(14, 30, 62), alpha=170, raio=14, borda=(118, 168, 232, 200)):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (cor[0], cor[1], cor[2], alpha), (0, 0, w, h), border_radius=raio)
    if borda:
        pygame.draw.rect(s, borda, (0, 0, w, h), width=2, border_radius=raio)
    return s

def _icone(nome, maximo, sufixo=""):
    base = superficie(nome + sufixo)
    w, h = base.get_size()
    f = maximo / max(w, h)
    return pygame.transform.scale(base, (max(1, int(w * f)), max(1, int(h * f))))

class Hud:
    SLOTS = ("saw", "meat", "life")
    ARQ = {"saw": "saw", "meat": "meat", "life": "life"}

    def __init__(self):
        self.p_slot = painel(TAM_SLOT, TAM_SLOT, alpha=150, raio=12)
        self.p_esquerda = painel(258, 150)
        self.p_direita = painel(308, 138)
        self.p_badge = painel(168, 78, alpha=185, borda=(255, 214, 90, 220))
        self.p_badge_lama = painel(168, 78, alpha=185, borda=(210, 160, 110, 220))
        self.p_badge_ima = painel(168, 78, alpha=185, borda=(255, 110, 120, 220))
        self.icones = {n: _icone(self.ARQ[n], ICONE_MAX) for n in self.SLOTS}
        self.icones_apagados = {n: _icone(self.ARQ[n], ICONE_MAX, "_apagado") for n in self.SLOTS}
        self.icones_grandes = {n: _icone(self.ARQ[n], int(ICONE_MAX * 1.3)) for n in self.SLOTS}
        self.icone_mult = _icone("multiplier", 46)
        self.icone_lama = _icone("mud", 50)
        self.icone_ima = _icone("ima", 46)

    #posições (para a animação de coleta)
    def posicao_slot(self, nome):
        i = self.SLOTS.index(nome)
        return (30 + i * (TAM_SLOT + 10) + TAM_SLOT // 2, 92 + TAM_SLOT // 2)

    ORDEM_BADGES = ("multiplier", "mud", "ima")

    def posicao_badge(self, tipo, jogo):
        ativos = [t for t, ativo in (("multiplier", jogo.t_mult > 0), ("mud", jogo.t_reducao > 0),
                                     ("ima", jogo.t_ima > 0)) if ativo]
        if tipo not in ativos:
            ativos.append(tipo)
            ativos.sort(key=self.ORDEM_BADGES.index)
        n = len(ativos)
        i = ativos.index(tipo)
        x0 = LARGURA // 2 - (n * 168 + (n - 1) * 14) // 2
        return (x0 + i * (168 + 14) + 84, 16 + 39)

    #HUD da partida
    def desenhar_jogo(self, tela, jogo):
        j = jogo.jogador
        # ---- painel esquerdo: tempo + inventário
        tela.blit(self.p_esquerda, (16, 12))
        segundos = int(jogo.t_corrida)
        texto.desenhar(tela, "TEMPO", 32, 18, 17, COR_TEXTO_SUAVE, borda=1)
        texto.desenhar(tela, f"{segundos // 60:02d}:{segundos % 60:02d}", 32, 34, 40, (255, 255, 255))
        for i, nome in enumerate(self.SLOTS):
            x = 30 + i * (TAM_SLOT + 10)
            y = 92
            tela.blit(self.p_slot, (x, y))
            tem = {"saw": j.serra, "meat": j.carne, "life": j.vida_extra}[nome]
            pulso = jogo.pulsos.get(nome, 0.0)
            if tem:
                icone = self.icones_grandes[nome] if pulso > 0.25 else self.icones[nome]
                tela.blit(icone, icone.get_rect(center=(x + TAM_SLOT // 2, y + TAM_SLOT // 2)))
            else:
                ic = self.icones_apagados[nome]
                tela.blit(ic, ic.get_rect(center=(x + TAM_SLOT // 2, y + TAM_SLOT // 2)))
            if pulso > 0:
                a = clamp(pulso / 0.6, 0, 1)
                cor = mistura_cor((60, 90, 140), COR_DOURADO, a)
                pygame.draw.rect(tela, cor, (x - 2, y - 2, TAM_SLOT + 4, TAM_SLOT + 4), width=3, border_radius=13)

        #pontos, recorde, velocidade
        px = LARGURA - 324
        tela.blit(self.p_direita, (px, 12))
        texto.desenhar(tela, "PONTOS", px + 18, 18, 17, COR_TEXTO_SUAVE, borda=1)
        texto.desenhar(tela, f"{int(jogo.pontuacao):06d}", px + 290, 32, 44, (255, 255, 255), "dir")
        texto.desenhar(tela, f"RECORDE  {jogo.recorde:06d}", px + 290, 82, 17, COR_TEXTO_SUAVE, "dir", borda=1)
        razao = jogo.velocidade_efetiva() / jogo.v0
        frac = clamp((razao - 1.0) / max(0.01, jogo.vmax_mult - 1.0), 0, 1)
        texto.desenhar(tela, "VELOCIDADE", px + 18, 108, 14, COR_TEXTO_SUAVE, borda=1)
        texto.desenhar(tela, f"x{razao:.1f}", px + 290, 104, 18, (255, 255, 255), "dir", borda=1)
        pygame.draw.rect(tela, (8, 18, 40), (px + 18, 126 - 2, 272, 12), border_radius=6)
        if frac > 0:
            cor = mistura_cor((96, 224, 130), (255, 84, 70), frac)
            pygame.draw.rect(tela, cor, (px + 20, 126, max(8, int(268 * frac)), 8), border_radius=4)

        #efeitos ativos (centro, topo)
        if jogo.t_mult > 0:
            x, y = self.posicao_badge("multiplier", jogo)
            self._badge(tela, x, y, self.p_badge, self.icone_mult, f"x{jogo.mult}", (255, 224, 90),
                        jogo.t_mult, jogo.dur_mult, "PONTOS")
        if jogo.t_reducao > 0:
            x, y = self.posicao_badge("mud", jogo)
            self._badge(tela, x, y, self.p_badge_lama, self.icone_lama, f"-{jogo.reducao}%", (236, 196, 140),
                        jogo.t_reducao, jogo.dur_reducao, "VELOCIDADE")

        if jogo.t_ima > 0:
            x, y = self.posicao_badge("ima", jogo)
            self._badge(tela, x, y, self.p_badge_ima, self.icone_ima, "ÍMÃ", (255, 140, 150),
                        jogo.t_ima, jogo.dur_ima, "ATRAI ITENS")

        #avisos de avalanche
        if jogo.avalanche.estado == "aviso":
            piscar = 0.6 + 0.4 * math.sin(jogo.relogio * 14)
            texto.desenhar(tela, "AVALANCHE!", LARGURA // 2, 100, 46, (255, 96, 80), "centro",
                           (80, 8, 8), 4, alpha=int(255 * piscar))
        elif jogo.nevasca.ativa:
            piscar = 0.8 + 0.2 * math.sin(jogo.relogio * 6)
            texto.desenhar(tela, f"NEVASCA  -  PONTOS x{NEVASCA_BONUS_PONTOS:g}", LARGURA // 2, ALTURA - 56, 28,
                           (255, 226, 120), "centro", (40, 70, 130), 3, alpha=int(255 * piscar))

        #dicas
        dica = "M  som: " + ("DESLIGADO" if jogo.audio.mudo else "ligado") + "     P  pausa"
        texto.desenhar(tela, dica, 20, ALTURA - 32, 15, (120, 150, 196), borda=1)
        texto.desenhar(tela, "NÍVEL: " + DIFICULDADE_NOMES[jogo.dificuldade], LARGURA - 20, ALTURA - 34, 17,
                       DIFICULDADE_CORES[jogo.dificuldade], "dir", borda=2)

    def _badge(self, tela, cx, cy, painel, icone, grande, cor, restante, total, legenda):
        x, y = cx - 84, cy - 39
        tela.blit(painel, (x, y))
        tela.blit(icone, icone.get_rect(center=(x + 34, y + 33)))
        texto.desenhar(tela, grande, x + 158, y + 6, 34, cor, "dir")
        texto.desenhar(tela, legenda, x + 158, y + 42, 12, COR_TEXTO_SUAVE, "dir", borda=1)
        frac = clamp(restante / max(0.001, total), 0, 1)
        pygame.draw.rect(tela, (8, 18, 40), (x + 12, y + 62, 144, 9), border_radius=4)
        corbarra = cor if frac > 0.25 or int(restante * 6) % 2 == 0 else (255, 90, 70)
        pygame.draw.rect(tela, corbarra, (x + 13, y + 63, max(2, int(142 * frac)), 7), border_radius=3)
        texto.desenhar(tela, f"{restante:0.0f}s", x + 12, y + 42, 14, (255, 255, 255), borda=1)