#telas do SkiFall: menu inicial , pausa, fim de jogo e entrada de iniciais.
#lógica de navegação do menu fica em game.py .

import math

import pygame

import texto
from config import (
    ALTURA, COR_DOURADO, COR_TEXTO_SUAVE, DIFICULDADE_CORES, DIFICULDADE_DESCRICAO, DIFICULDADE_NOMES,
    DIFICULDADES, LARGURA, NEVASCA_BONUS_PONTOS, TAMANHO_RANKING,
)
from hud import _icone, painel
from utils import clamp

MENU_ITENS = ("JOGAR", "DIFICULDADE", "RANKING", "COMO JOGAR", "CRÉDITOS", "SAIR")

CAUSAS = {
    "arvore": "Você bateu em um pinheiro!",
    "pedra": "Você bateu em uma pedra!",
    "lobo": "Um lobo faminto te pegou!",
    "avalanche": "Soterrado por uma avalanche!",
}
CORES_PODIO = ((255, 214, 80), (214, 222, 236), (226, 160, 100))

def quebrar_linhas(txt, tamanho, largura_max):
#quebra o texto para caber na tela
    f = texto.fonte(tamanho)
    palavras = txt.split()
    linhas, atual = [], ""
    for p in palavras:
        tentativa = (atual + " " + p).strip()
        if f.size(tentativa)[0] <= largura_max or not atual:
            atual = tentativa
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas or [""]

class Telas:
    LARGURA_CREDITOS = 760
    ALTURA_CREDITOS = 480

    def __init__(self):
        self.escuro = pygame.Surface((LARGURA, ALTURA))
        self.escuro.fill((6, 14, 34))
        self.p_titulo = painel(740, 206, alpha=150, raio=24)
        self.p_opcoes = painel(580, 376, alpha=205, raio=22)
        self.p_pausa = painel(560, 330, alpha=215, raio=24)
        self.p_fim = painel(540, 470, alpha=215, raio=26, borda=(255, 120, 100, 220))
        self.p_rank_fim = painel(440, 470, alpha=215, raio=26, borda=(255, 214, 90, 220))
        self.p_rank_menu = painel(330, 292, alpha=185, raio=20, borda=(255, 214, 90, 200))
        self.p_dif = painel(330, 292, alpha=185, raio=20)
        self.p_iniciais = painel(700, 400, alpha=235, raio=28, borda=(255, 214, 90, 230))
        self.p_como = painel(1100, 640, alpha=225, raio=26)
        self.p_ranking_tela = painel(820, 600, alpha=225, raio=26, borda=(255, 214, 90, 220))
        self.p_creditos = painel(860, 700, alpha=228, raio=26, borda=(255, 214, 90, 220))
        self.icones = {n: _icone(n, 32) for n in ("saw", "meat", "life", "multiplier", "mud")}
        self.icones_novidade = {"pedra": _icone("pedra_obs1", 34), "ima": _icone("ima", 34),
                                "gelo": _icone("gelo", 40)}

    #ranking (reutilizado)
    def _desenhar_ranking(self, tela, x, y, largura, entradas, relogio, destaque=-1, tam=26, passo=46):
        """Lista o top N. 'destaque' = índice da linha recém-inserida (pisca)."""
        for i in range(TAMANHO_RANKING):
            yy = y + i * passo
            if i == destaque and int(relogio * 3) % 2 == 0:
                pygame.draw.rect(tela, (255, 214, 80), (x - 12, yy - 4, largura + 24, passo - 4), width=3, border_radius=10)
            cor = CORES_PODIO[i] if i < 3 else (230, 238, 252)
            if i < len(entradas):
                nome, pontos = entradas[i]
                texto.desenhar(tela, f"{i + 1}.", x, yy, tam, cor)
                texto.desenhar(tela, nome, x + int(tam * 1.7), yy, tam, (255, 255, 255))
                texto.desenhar(tela, f"{pontos:06d}", x + largura, yy, tam, cor, "dir")
            else:
                dim = (120, 144, 186)
                texto.desenhar(tela, f"{i + 1}.", x, yy, tam, dim, borda=1)
                texto.desenhar(tela, "---", x + int(tam * 1.7), yy, tam, dim, borda=1)
                texto.desenhar(tela, "000000", x + largura, yy, tam, dim, "dir", borda=1)

    #menu
    def desenhar_menu(self, tela, jogo):
        if jogo.menu_tela == "PRINCIPAL":
            self._menu_principal(tela, jogo)
            return
        self.escuro.set_alpha(150)
        tela.blit(self.escuro, (0, 0))
        if jogo.menu_tela == "RANKING":
            self._menu_ranking(tela, jogo)
        elif jogo.menu_tela == "COMO_JOGAR":
            self._menu_como_jogar(tela, jogo)
        else:
            self._menu_creditos(tela, jogo)

    #menu principal
    def _menu_principal(self, tela, jogo):
        t = jogo.relogio
        cx = LARGURA // 2
        flutua = math.sin(t * 2.0) * 5
        tela.blit(self.p_titulo, (cx - 370, 30))
        texto.desenhar(tela, "SKIFALL", cx, 44 + flutua, 112, (255, 255, 255), "centro", (24, 70, 150), 7, True)
        texto.desenhar(tela, "Desça a montanha. Desvie. Sobreviva.", cx, 182, 26, COR_TEXTO_SUAVE, "centro")

        #opções
        tela.blit(self.p_opcoes, (cx - 290, 250))
        for i, item in enumerate(MENU_ITENS):
            y = 268 + i * 58
            sel = i == jogo.menu_idx
            if sel:
                pygame.draw.rect(tela, (34, 66, 128), (cx - 268, y - 4, 536, 50), border_radius=12)
                pygame.draw.rect(tela, COR_DOURADO, (cx - 268, y - 4, 536, 50), width=3, border_radius=12)
            cor = COR_DOURADO if sel else (255, 255, 255)
            if item == "DIFICULDADE":
                texto.desenhar(tela, "DIFICULDADE", cx - 246, y + 4, 30, cor)
                nome = DIFICULDADE_NOMES[jogo.dificuldade]
                valor = f"<  {nome}  >" if sel else nome
                texto.desenhar(tela, valor, cx + 250, y + 4, 30, DIFICULDADE_CORES[jogo.dificuldade], "dir")
            else:
                texto.desenhar(tela, item, cx - 246, y + 4, 30, cor)
        texto.desenhar(tela, "W / S  ou  CIMA / BAIXO  escolhe      ENTER / ESPAÇO  confirma      "
                             "A / D  ou  ESQ / DIR  muda o nível      ESC  sai",
                       cx, 640, 18, COR_TEXTO_SUAVE, "centro", borda=1)

        #TOP 5 do nível atual (esquerda)
        tela.blit(self.p_rank_menu, (24, 236))
        texto.desenhar(tela, "TOP 5", 24 + 165, 244, 28, COR_DOURADO, "centro")
        texto.desenhar(tela, DIFICULDADE_NOMES[jogo.dificuldade], 24 + 165, 274, 18,
                       DIFICULDADE_CORES[jogo.dificuldade], "centro", borda=1)
        self._desenhar_ranking(tela, 44, 304, 290, jogo.ranking.entradas, jogo.relogio, tam=21, passo=42)

        #descrição do nível atual (direita)
        xd = LARGURA - 24 - 330
        tela.blit(self.p_dif, (xd, 236))
        cor_n = DIFICULDADE_CORES[jogo.dificuldade]
        texto.desenhar(tela, "NÍVEL", xd + 165, 246, 18, COR_TEXTO_SUAVE, "centro", borda=1)
        texto.desenhar(tela, DIFICULDADE_NOMES[jogo.dificuldade], xd + 165, 268, 40, cor_n, "centro", (12, 24, 52), 3)
        y = 326
        for linha in DIFICULDADE_DESCRICAO[jogo.dificuldade]:
            for parte in quebrar_linhas(linha, 20, 286):
                texto.desenhar(tela, parte, xd + 22, y, 20, (255, 255, 255), borda=1)
                y += 28
            y += 6

    #ranking (todos os níveis)
    def _menu_ranking(self, tela, jogo):
        cx = LARGURA // 2
        tela.blit(self.p_ranking_tela, (cx - 410, 130))
        texto.desenhar(tela, "RANKING", cx, 142, 60, (255, 255, 255), "centro", (24, 70, 150), 6, True)
        for i, nome_dif in enumerate(DIFICULDADES):
            x = cx - 354 + i * 242
            ativa = i == jogo.rank_aba
            cor = DIFICULDADE_CORES[nome_dif]
            pygame.draw.rect(tela, (34, 66, 128) if ativa else (14, 30, 62), (x, 236, 226, 52), border_radius=12)
            pygame.draw.rect(tela, cor if ativa else (90, 120, 170), (x, 236, 226, 52), width=3 if ativa else 2,
                             border_radius=12)
            texto.desenhar(tela, DIFICULDADE_NOMES[nome_dif], x + 113, 244, 28, cor if ativa else (150, 176, 214), "centro")
        texto.desenhar(tela, "A / D  ou  SETAS  -  troca o nível", cx, 300, 20, COR_TEXTO_SUAVE, "centro", borda=1)
        entradas = jogo.rankings[DIFICULDADES[jogo.rank_aba]].entradas
        self._desenhar_ranking(tela, cx - 300, 350, 600, entradas, jogo.relogio, -1, 34, 62)
        texto.desenhar(tela, "ESC / ENTER  -  voltar", cx, 696, 22, COR_TEXTO_SUAVE, "centro")

    #como jogar
    def _menu_como_jogar(self, tela, jogo):
        cx = LARGURA // 2
        tela.blit(self.p_como, (cx - 550, 110))
        texto.desenhar(tela, "COMO JOGAR", cx, 122, 56, (255, 255, 255), "centro", (24, 70, 150), 6, True)
        x1, x2 = cx - 520, cx + 20
        texto.desenhar(tela, "CONTROLES", x1, 212, 24, COR_DOURADO)
        linhas = [
            "A / D  ou  SETAS  -  trocar de faixa",
            "P / ESC  -  pausar",
            "M  -  ligar / desligar o som",
            "Passe rente nos obstáculos: bônus QUASE!",
            f"Durante a nevasca os pontos valem x{NEVASCA_BONUS_PONTOS:g}!".replace(".", ","),
        ]
        for i, l in enumerate(linhas):
            texto.desenhar(tela, l, x1, 252 + i * 38, 20, (255, 255, 255), borda=2)
        texto.desenhar(tela, "ITENS", x2, 212, 24, COR_DOURADO)
        itens = [
            ("saw", "Serra: parte o próximo pinheiro"),
            ("meat", "Carne: distrai o lobo"),
            ("life", "Vida extra: você volta ao jogo"),
            ("multiplier", "Estrela: multiplica os pontos"),
            ("mud", "Redutor: obstáculos mais lentos"),
        ]
        for i, (nome, desc) in enumerate(itens):
            ic = self.icones[nome]
            yy = 250 + i * 38
            tela.blit(ic, ic.get_rect(center=(x2 + 20, yy + 16)))
            texto.desenhar(tela, desc, x2 + 52, yy + 2, 20, (255, 255, 255), borda=2)

        nivel = DIFICULDADE_NOMES[jogo.dificuldade]
        texto.desenhar(tela, f"NOVIDADES POR PONTUAÇÃO  (nível {nivel})", x1, 468, 24, COR_DOURADO)
        novidades = [
            ("pedra", "pedra", "Pedras: a serra NÃO corta, é preciso desviar"),
            ("ima", "ima", "Ímã: atrai os itens de todas as faixas"),
            ("gelo", "gelo", "Gelo: a troca de faixa fica mais lenta"),
        ]
        for i, (chave, icone, desc) in enumerate(novidades):
            ic = self.icones_novidade[icone]
            yy = 512 + i * 46
            tela.blit(ic, ic.get_rect(center=(x1 + 24, yy + 16)))
            texto.desenhar(tela, f"a partir de {int(jogo._limiar(chave))} pts", x1 + 64, yy + 2, 20, COR_DOURADO, borda=2)
            texto.desenhar(tela, desc, x1 + 330, yy + 2, 20, (255, 255, 255), borda=2)
        texto.desenhar(tela, "ESC / ENTER  -  voltar", cx, 706, 22, COR_TEXTO_SUAVE, "centro")

    #créditos (creditos.txt)
    def montar_creditos(self, linhas):
        #converte cretitos.txt em uma imagem para o jogo
        L = self.LARGURA_CREDITOS
        blocos = []     # (superfície, y)
        y = 0
        espaco = 0
        for bruta in linhas:
            linha = bruta.strip()
            if linha.startswith("//"):
                continue
            if not linha:
                espaco += 24
                continue
            if linha.startswith("#"):
                y += 46 + espaco if blocos else 0
                espaco = 0
                for parte in quebrar_linhas(linha.lstrip("#").strip(), 34, L):
                    surf = texto.renderizar(parte, 34, COR_DOURADO, (80, 50, 0), 4)
                    blocos.append((surf, y))
                    y += surf.get_height() + 4
                y += 10
            else:
                y += espaco
                espaco = 0
                for parte in quebrar_linhas(linha, 26, L):
                    surf = texto.renderizar(parte, 26, (255, 255, 255), (12, 24, 52), 2)
                    blocos.append((surf, y))
                    y += surf.get_height() + 6
        total = pygame.Surface((L, max(40, y + 20)), pygame.SRCALPHA)
        for surf, yy in blocos:
            total.blit(surf, ((L - surf.get_width()) // 2, yy))
        return total

    def _menu_creditos(self, tela, jogo):
        cx = LARGURA // 2
        tela.blit(self.p_creditos, (cx - 430, 80))
        texto.desenhar(tela, "CRÉDITOS", cx, 92, 60, (255, 255, 255), "centro", (24, 70, 150), 6, True)
        x, y0, h = cx - self.LARGURA_CREDITOS // 2, 186, self.ALTURA_CREDITOS
        pygame.draw.line(tela, (255, 214, 80), (x, y0 - 4), (x + self.LARGURA_CREDITOS, y0 - 4), 2)
        pygame.draw.line(tela, (255, 214, 80), (x, y0 + h + 4), (x + self.LARGURA_CREDITOS, y0 + h + 4), 2)
        # janela rolante: mostra as linhas [scroll, scroll + h) da imagem dos créditos
        surf = jogo.surf_creditos
        scroll = int(jogo.creditos_scroll)
        ini = max(0, scroll)
        fim = min(surf.get_height(), scroll + h)
        if fim > ini:
            tela.blit(surf, (x, y0 + (ini - scroll)), (0, ini, self.LARGURA_CREDITOS, fim - ini))
        texto.desenhar(tela, "ESC / ENTER  -  voltar          BAIXO  acelera          CIMA  volta", cx, 702, 20,
                       COR_TEXTO_SUAVE, "centro")

    #pausa
    def desenhar_pausa(self, tela, jogo):
        self.escuro.set_alpha(130)
        tela.blit(self.escuro, (0, 0))
        cx, cy = LARGURA // 2, ALTURA // 2
        tela.blit(self.p_pausa, (cx - 280, cy - 165))
        texto.desenhar(tela, "PAUSADO", cx, cy - 140, 70, (255, 255, 255), "centro", (24, 70, 150), 6, True)
        texto.desenhar(tela, "P / ESC  -  continuar", cx, cy - 30, 28, COR_DOURADO, "centro")
        texto.desenhar(tela, "R  -  recomeçar", cx, cy + 20, 26, (255, 255, 255), "centro")
        texto.desenhar(tela, "Q  -  voltar ao menu", cx, cy + 62, 26, (255, 255, 255), "centro")
        texto.desenhar(tela, "M  -  som " + ("DESLIGADO" if jogo.audio.mudo else "ligado"), cx, cy + 104, 22,
                       COR_TEXTO_SUAVE, "centro")

    #fim de jogo
    def desenhar_game_over(self, tela, jogo):
        a = clamp(jogo.t_estado / 0.6, 0, 1)
        self.escuro.set_alpha(int(170 * a))
        tela.blit(self.escuro, (0, 0))
        if a < 0.35:
            return
        if jogo.entrando_iniciais:
            self._desenhar_iniciais(tela, jogo)
            return
        k = clamp((a - 0.35) / 0.65, 0, 1)
        alpha = int(255 * k)
        cx = LARGURA // 2
        desloc = int((1 - k) * 40)
        topo = ALTURA // 2 - 235 + desloc

        #painel de resultado
        xp = cx - 500
        self.p_fim.set_alpha(alpha)
        tela.blit(self.p_fim, (xp, topo))
        mid = xp + 270
        texto.desenhar(tela, "FIM DE JOGO", mid, topo + 24, 66, (255, 120, 104), "centro", (80, 10, 10), 6, True, alpha)
        texto.desenhar(tela, CAUSAS.get(jogo.causa_morte, ""), mid, topo + 108, 26, COR_TEXTO_SUAVE, "centro", alpha=alpha)
        texto.desenhar(tela, "NÍVEL: " + DIFICULDADE_NOMES[jogo.dificuldade], mid, topo + 140, 20,
                       DIFICULDADE_CORES[jogo.dificuldade], "centro", alpha=alpha)
        seg = int(jogo.t_corrida)
        l, r = xp + 36, xp + 504
        texto.desenhar(tela, "PONTUAÇÃO", l, topo + 188, 20, COR_TEXTO_SUAVE, alpha=alpha)
        texto.desenhar(tela, f"{int(jogo.pontuacao):06d}", r, topo + 172, 54, (255, 255, 255), "dir", alpha=alpha)
        texto.desenhar(tela, "TEMPO", l, topo + 248, 20, COR_TEXTO_SUAVE, alpha=alpha)
        texto.desenhar(tela, f"{seg // 60:02d}:{seg % 60:02d}", r, topo + 240, 40, (255, 255, 255), "dir", alpha=alpha)
        texto.desenhar(tela, "RECORDE", l, topo + 302, 20, COR_TEXTO_SUAVE, alpha=alpha)
        texto.desenhar(tela, f"{jogo.recorde:06d}", r, topo + 296, 40, COR_DOURADO, "dir", alpha=alpha)
        if jogo.novo_recorde and int(jogo.relogio * 3) % 2 == 0:
            texto.desenhar(tela, "NOVO RECORDE!", mid, topo + 352, 38, COR_DOURADO, "centro", (80, 50, 0), 4, alpha=alpha)
        elif jogo.posicao_ranking > 0 and int(jogo.relogio * 3) % 2 == 0:
            texto.desenhar(tela, f"{jogo.posicao_ranking + 1}º LUGAR NO RANKING!", mid, topo + 356, 28, COR_DOURADO,
                           "centro", (80, 50, 0), 4, alpha=alpha)
        if jogo.t_estado > 0.9:
            texto.desenhar(tela, "ESPAÇO  -  jogar de novo", mid, topo + 404, 26, (255, 255, 255), "centro")
            texto.desenhar(tela, "ESC  -  menu", mid, topo + 438, 20, COR_TEXTO_SUAVE, "centro")

        #painel do ranking (do nível jogado)
        xr = cx + 60
        self.p_rank_fim.set_alpha(alpha)
        tela.blit(self.p_rank_fim, (xr, topo))
        texto.desenhar(tela, "TOP 5", xr + 220, topo + 22, 56, COR_DOURADO, "centro", (80, 50, 0), 5, True, alpha)
        self._desenhar_ranking(tela, xr + 36, topo + 120, 366, jogo.ranking.entradas, jogo.relogio,
                               jogo.posicao_ranking, 30, 62)

    #iniciais
    def _desenhar_iniciais(self, tela, jogo):
        cx, cy = LARGURA // 2, ALTURA // 2
        tela.blit(self.p_iniciais, (cx - 350, cy - 200))
        texto.desenhar(tela, "NOVO NO RANKING!", cx, cy - 184, 56, COR_DOURADO, "centro", (80, 50, 0), 5, True)
        pos = jogo.ranking.posicao_para(int(jogo.pontuacao)) + 1
        texto.desenhar(tela, f"{pos}º lugar  -  {int(jogo.pontuacao):06d} pontos  -  {DIFICULDADE_NOMES[jogo.dificuldade]}",
                       cx, cy - 98, 28, (255, 255, 255), "centro")
        for i in range(3):
            x = cx - 150 + i * 106
            ativo = i == len(jogo.iniciais)
            cor_borda = COR_DOURADO if ativo else (118, 168, 232)
            pygame.draw.rect(tela, (10, 22, 50), (x, cy - 46, 92, 116), border_radius=14)
            pygame.draw.rect(tela, cor_borda, (x, cy - 46, 92, 116), width=4, border_radius=14)
            if i < len(jogo.iniciais):
                texto.desenhar(tela, jogo.iniciais[i], x + 46, cy - 36, 84, (255, 255, 255), "centro", titulo=True)
            elif ativo and int(jogo.relogio * 2.5) % 2 == 0:
                pygame.draw.rect(tela, COR_DOURADO, (x + 20, cy + 52, 52, 8))
        texto.desenhar(tela, "Digite suas iniciais  (A - Z)", cx, cy + 96, 24, COR_TEXTO_SUAVE, "centro")
        texto.desenhar(tela, "BACKSPACE  apaga          ENTER  confirma", cx, cy + 132, 22, (255, 255, 255), "centro")
