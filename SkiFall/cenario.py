
#background do SkiFall

#tudo que é cenário rola na mesma direção e na mesma

import random
import pygame

from assets import superficie, superficie_escalada, superficie_espelhada
from config import (
    ALTURA, COR_BORDA_PISTA, COR_LINHA_FAIXA, COR_NEVE_LATERAL, COR_PISTA, COR_PISTA_SOMBRA,
    LARGURA, NUM_FAIXAS,
)
from utils import clamp

ESPACO_POSTES = 250
TAMANHO_TRACO = 46
TAMANHO_VAO = 38


class Cenario:
    def __init__(self, x_pista, largura_pista, semente=3):
        self.x_pista = x_pista
        self.lp = largura_pista
        self.lw = largura_pista / NUM_FAIXAS
        self.rnd = random.Random(semente)
        self.dist = 0.0          # distância total rolada (sem limite): base de tudo que se repete
        self.tile = self._criar_tile()
        self._preparar_decoracao()
        self.decor = []
        self._popular_inicial()
        self.riscos = [[self.rnd.uniform(0, LARGURA), self.rnd.uniform(0, ALTURA),
                        self.rnd.uniform(70, 170)] for _ in range(18)]

    #chão
    def _criar_tile(self):
        rnd = random.Random(21)
        s = pygame.Surface((LARGURA, ALTURA))
        s.fill(COR_NEVE_LATERAL)
        xi, xf = int(self.x_pista), int(self.x_pista + self.lp)
        pygame.draw.rect(s, COR_PISTA, (xi, 0, xf - xi, ALTURA))

        def marcar(x, y, w, h, cor_sombra, cor):
            for dy in (0, -ALTURA, ALTURA):          # repete nas emendas -> o tile é "sem costura"
                yy = y + dy
                if yy + h < 0 or yy > ALTURA:
                    continue
                pygame.draw.ellipse(s, cor_sombra, (x, yy + 3, w, h))
                pygame.draw.ellipse(s, cor, (x, yy, w, h))

        # montinhos de neve nas laterais
        for _ in range(170):
            x = rnd.choice((rnd.uniform(-20, xi - 30), rnd.uniform(xf + 10, LARGURA - 10)))
            marcar(int(x), int(rnd.uniform(0, ALTURA)), rnd.randint(16, 54), rnd.randint(7, 18),
                   (210, 224, 244), (248, 251, 255))
        # irregularidades discretas na pista
        for _ in range(60):
            marcar(int(rnd.uniform(xi + 10, xf - 60)), int(rnd.uniform(0, ALTURA)), rnd.randint(14, 40),
                   rnd.randint(5, 11), (228, 238, 252), (255, 255, 255))
        # brilhos
        for _ in range(240):
            x = int(rnd.uniform(0, LARGURA))
            y = int(rnd.uniform(0, ALTURA))
            cor = (255, 255, 255) if rnd.random() < 0.7 else (200, 220, 246)
            pygame.draw.rect(s, cor, (x, y, 3, 3))
        # bordas da pista (sombra suave + linha)
        for x0, sinal in ((xi, -1), (xf, 1)):
            pygame.draw.rect(s, COR_PISTA_SOMBRA, (x0 - (12 if sinal < 0 else 0), 0, 12, ALTURA))
            pygame.draw.rect(s, COR_BORDA_PISTA, (x0 - 2, 0, 4, ALTURA))
        return s.convert()

    #decoração
    def _preparar_decoracao(self):
        arvores = []
        for nome in ("tree1", "tree2", "tree3", "tree4"):
            for fator in (0.5, 0.65, 0.8, 0.95):
                arvores.append(superficie_escalada(nome, fator))
        self.tipos = [
            ("arvore", arvores, 0.50),
            ("pedra", [superficie("pedra1"), superficie("pedra2"), superficie("pedra3")], 0.22),
            ("moita", [superficie("moita")], 0.12),
            ("tronco", [superficie("tronco")], 0.06),
            ("lagoa", [superficie("lagoa")], 0.10),
        ]
        self.poste_v = superficie("poste_vermelho")
        self.poste_a = superficie("poste_azul")
        self.poste_v_esp = superficie_espelhada("poste_vermelho")
        self.poste_a_esp = superficie_espelhada("poste_azul")

    def _escolher(self):
        r = self.rnd.random()
        acum = 0.0
        for _, imagens, peso in self.tipos:
            acum += peso
            if r <= acum:
                return self.rnd.choice(imagens)
        return self.rnd.choice(self.tipos[0][1])

    def _livre(self, x, y, w, h, ignorar=None):
        r = pygame.Rect(int(x) - 8, int(y) - 8, int(w) + 16, int(h) + 16)
        for d in self.decor:
            if d is ignorar:
                continue
            if r.colliderect(pygame.Rect(int(d["x"]), int(d["y"]), d["w"], d["h"])):
                return False
        return True

    def _posicionar(self, d, y_min, y_max):
        w, h = d["w"], d["h"]
        for _ in range(40):
            esquerda = self.rnd.random() < 0.5
            if esquerda:
                x = self.rnd.uniform(4, max(5, self.x_pista - 22 - w))
            else:
                x = self.rnd.uniform(self.x_pista + self.lp + 22, max(self.x_pista + self.lp + 23, LARGURA - 4 - w))
            y = self.rnd.uniform(y_min, y_max)
            if self._livre(x, y, w, h, d):
                d["x"], d["y"] = x, y
                return True
        d["x"], d["y"] = x, y        # sem espaço: aceita sobreposição leve
        return False

    def _popular_inicial(self):
        for _ in range(26):
            img = self._escolher()
            d = {"img": img, "w": img.get_width(), "h": img.get_height(), "x": 0, "y": 0}
            self._posicionar(d, -120, ALTURA + 40)
            self.decor.append(d)

    #atualização / desenho
    def atualizar(self, dt, vmundo):
        mov = vmundo * dt
        self.dist += mov
        for d in self.decor:
            d["y"] -= mov
            if d["y"] + d["h"] < -10:
                d["img"] = self._escolher()
                d["w"], d["h"] = d["img"].get_width(), d["img"].get_height()
                self._posicionar(d, ALTURA + 10, ALTURA + 220)
        for r in self.riscos:
            r[1] -= mov * 1.7
            if r[1] + r[2] < 0:
                r[0] = self.rnd.uniform(0, LARGURA)
                r[1] = ALTURA + self.rnd.uniform(0, 200)
                r[2] = self.rnd.uniform(70, 170)

    def desenhar(self, tela, razao_velocidade=1.0):
        off = int(self.dist) % ALTURA
        tela.blit(self.tile, (0, -off))
        if off:
            tela.blit(self.tile, (0, ALTURA - off))

        # divisórias tracejadas das faixas (rolam com o mundo)
        passo = TAMANHO_TRACO + TAMANHO_VAO
        deslocamento = int(self.dist) % passo
        for i in range(1, NUM_FAIXAS):
            x = int(self.x_pista + self.lw * i) - 2
            y = -deslocamento
            while y < ALTURA:
                pygame.draw.rect(tela, COR_LINHA_FAIXA, (x, y, 5, TAMANHO_TRACO))
                y += passo

        # postes com bandeira nas bordas da pista
        rolado = int(self.dist)
        base = -(rolado % (ESPACO_POSTES * 2))
        k = 0
        y = base
        while y < ALTURA + ESPACO_POSTES:
            vermelho = (k % 2 == 0)
            esq = self.poste_v if vermelho else self.poste_a
            dir_ = self.poste_v_esp if vermelho else self.poste_a_esp
            tela.blit(esq, (int(self.x_pista - 34), int(y)))
            tela.blit(dir_, (int(self.x_pista + self.lp + 8), int(y)))
            y += ESPACO_POSTES
            k += 1

        # árvores, pedras, lagoas
        for d in sorted(self.decor, key=lambda d: d["y"] + d["h"]):
            if -d["h"] < d["y"] < ALTURA:
                tela.blit(d["img"], (int(d["x"]), int(d["y"])))

        # riscos de velocidade
        intensidade = clamp((razao_velocidade - 1.8) / 2.5, 0.0, 1.0)
        if intensidade > 0:
            quantos = int(len(self.riscos) * intensidade)
            for x, y, comp in self.riscos[:quantos]:
                pygame.draw.line(tela, (206, 222, 245), (int(x), int(y)), (int(x), int(y + comp)), 3)