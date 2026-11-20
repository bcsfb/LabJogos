#efeitos visuais do SkiFall
#tudo desenhado direto na superfície da janela do PPlay (janela.get_screen()).
#coisas grandes sao pre-renderizado e reutilizado.

import math
import random

import pygame

import texto
from config import (
    ALTURA, AVALANCHE_ATIVA, AVALANCHE_AVISO, AVALANCHE_INTERVALO, AVALANCHE_PRIMEIRA,
    AVALANCHE_VELOCIDADE, COR_NEVE_LATERAL, LARGURA, NEVASCA_ATIVA, NEVASCA_DURACAO,
    NEVASCA_INTERVALO, NEVASCA_PRIMEIRA, NUM_FAIXAS,
)
from utils import clamp, lerp, mistura_cor, suave_entrada_saida

COR_FUNDO_NEVE = COR_NEVE_LATERAL


#partículas
class _Particula:
    __slots__ = ("x", "y", "vx", "vy", "vida", "vida_max", "cor", "contorno",
                 "raio", "grav", "arrasto", "mundo", "frente")


class Particulas:

    MAXIMO = 450

    def __init__(self):
        self.lista = []

    def emitir(self, x, y, vx, vy, vida, cor, raio, contorno=None, grav=0.0, arrasto=0.0, mundo=0.0,
               frente=True):
        if len(self.lista) >= self.MAXIMO:
            return
        p = _Particula()
        p.x, p.y, p.vx, p.vy = x, y, vx, vy
        p.vida = p.vida_max = vida
        p.cor, p.contorno, p.raio = cor, contorno, raio
        p.grav, p.arrasto, p.mundo = grav, arrasto, mundo
        p.frente = frente        # False = desenhada ATRÁS do esquiador (poeira dos esquis)
        self.lista.append(p)

    # -------- presets
    def explosao_neve(self, x, y, n=16, forca=240.0, mundo=1.0):
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            vel = random.uniform(0.3, 1.0) * forca
            self.emitir(x, y, math.cos(ang) * vel, math.sin(ang) * vel * 0.8,
                        random.uniform(0.35, 0.7), (255, 255, 255), random.uniform(4, 9),
                        (176, 202, 236), arrasto=3.2, mundo=mundo)

    def lascas(self, x, y, n=18, mundo=1.0):
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            vel = random.uniform(120, 420)
            cor = random.choice(((176, 124, 76), (140, 96, 58), (222, 178, 112), (255, 224, 110)))
            self.emitir(x, y, math.cos(ang) * vel, math.sin(ang) * vel - 80,
                        random.uniform(0.4, 0.8), cor, random.uniform(3, 6), (70, 44, 28),
                        grav=700, arrasto=1.2, mundo=mundo)

    def brilho(self, x, y, cor, n=12):
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            vel = random.uniform(80, 260)
            self.emitir(x, y, math.cos(ang) * vel, math.sin(ang) * vel,
                        random.uniform(0.3, 0.6), cor, random.uniform(3, 6), (255, 255, 255),
                        arrasto=3.0)

    def jorro_esqui(self, x, y, lado, forca=1.0):
        #particula troca de faixa
        for _ in range(2):
            self.emitir(x + random.uniform(-6, 6), y, -lado * random.uniform(60, 190) * forca,
                        random.uniform(-70, 30), random.uniform(0.25, 0.5), (255, 255, 255),
                        random.uniform(3, 6), (176, 202, 236), arrasto=2.5, mundo=1.0, frente=False)

    def poeira_descida(self, x, y, vmundo):
        #particula de tras do ski
        if random.random() < 0.55:
            self.emitir(x + random.uniform(-16, 16), y, random.uniform(-25, 25), random.uniform(-30, 10),
                        random.uniform(0.3, 0.55), (255, 255, 255), random.uniform(2.5, 4.5),
                        (190, 212, 240), mundo=1.0, frente=False)

    def atualizar(self, dt, vmundo):
        vivos = []
        for p in self.lista:
            p.vida -= dt
            if p.vida <= 0:
                continue
            p.vx -= p.vx * p.arrasto * dt
            p.vy += p.grav * dt
            p.x += p.vx * dt
            p.y += (p.vy - p.mundo * vmundo) * dt
            vivos.append(p)
        self.lista = vivos

    def desenhar(self, tela, frente=True):
        circulo = pygame.draw.circle
        for p in self.lista:
            if p.frente != frente:
                continue
            f = p.vida / p.vida_max
            r = max(1, int(p.raio * (0.4 + 0.6 * f)))
            pos = (int(p.x), int(p.y))
            esmaecer = (1.0 - f) * 0.65
            if p.contorno is not None:
                circulo(tela, mistura_cor(p.contorno, COR_FUNDO_NEVE, esmaecer), pos, r + 1)
            circulo(tela, mistura_cor(p.cor, COR_FUNDO_NEVE, esmaecer), pos, r)


#textos flutuantes
class Popup:
    #testo que aparece e sobe

    def __init__(self, msg, x, y, cor=(255, 255, 255), tamanho=30, vida=1.2, subir=80):
        self.surf = texto.renderizar(msg, tamanho, cor, (12, 24, 52), 3).copy()
        self.x, self.y0 = x, y
        self.t, self.vida, self.subir = 0.0, vida, subir
        self.fim = False

    def atualizar(self, dt):
        self.t += dt
        if self.t >= self.vida:
            self.fim = True

    def desenhar(self, tela):
        p = clamp(self.t / self.vida, 0, 1)
        y = self.y0 - self.subir * (1 - (1 - p) ** 2)
        alpha = 255 if p < 0.6 else int(255 * (1 - (p - 0.6) / 0.4))
        # "pulinho" de escala no começo
        self.surf.set_alpha(max(0, alpha))
        w, h = self.surf.get_size()
        tela.blit(self.surf, (int(self.x - w / 2), int(y - h / 2)))


#pinheiro cortado
def _girar_em_torno_do_pivo(tela, surf, pivo, deslocamento_centro, graus, alpha=255):
    rad = math.radians(graus)
    c, s = math.cos(rad), math.sin(rad)
    ox, oy = deslocamento_centro
    rx = ox * c + oy * s            # rotação anti-horária visual (eixo y para baixo)
    ry = -ox * s + oy * c
    rot = pygame.transform.rotate(surf, graus)
    if alpha < 255:
        rot.set_alpha(int(alpha))
    r = rot.get_rect(center=(pivo[0] + rx, pivo[1] + ry))
    tela.blit(rot, r)


class PinheiroCortado:
    #animacao de partir o pinheiro
    DURACAO = 0.85

    def __init__(self, imagem, cx, cy):
        w, h = imagem.get_size()
        meio = w // 2
        self.esq = imagem.subsurface(pygame.Rect(0, 0, meio, h)).copy()
        self.dir = imagem.subsurface(pygame.Rect(meio, 0, w - meio, h)).copy()
        self.cx, self.cy = cx, cy
        self.w, self.h = w, h
        self.t = 0.0
        self.fim = False

    def atualizar(self, dt, vmundo):
        self.t += dt
        self.cy -= vmundo * dt
        if self.t >= self.DURACAO:
            self.fim = True

    def desenhar(self, tela):
        p = clamp(self.t / self.DURACAO, 0, 1)
        e = 1 - (1 - p) ** 2.2
        ang = 82 * e
        afastar = 46 * e
        alpha = 255 if p < 0.65 else int(255 * (1 - (p - 0.65) / 0.35))
        base_y = self.cy + self.h / 2
        # esquerda: pivô na base, sobre o eixo do tronco, tomba para a esquerda (anti-horário)
        _girar_em_torno_do_pivo(tela, self.esq, (self.cx - afastar, base_y),
                                (-self.w / 4, -self.h / 2), ang, alpha)
        _girar_em_torno_do_pivo(tela, self.dir, (self.cx + afastar, base_y),
                                (self.w / 4, -self.h / 2), -ang, alpha)


#nuvem de briga
class NuvemBriga:
    #poira com estrela do ataque de lobo e cair na avalanche

    def __init__(self, x, y, raio=78, duracao=1.4):
        self.x, self.y, self.raio, self.duracao = x, y, raio, duracao
        self.t = 0.0
        rnd = random.Random(11)
        self.bolas = [(rnd.uniform(0, math.tau), rnd.uniform(0.15, 0.85), rnd.uniform(0.28, 0.5),
                       rnd.uniform(0, math.tau)) for _ in range(13)]
        self.estrelas = [(rnd.uniform(0, math.tau), rnd.uniform(0.7, 1.3), rnd.uniform(0, math.tau))
                         for _ in range(6)]
        self.fim = False

    def atualizar(self, dt):
        self.t += dt
        if self.t >= self.duracao:
            self.fim = True

    def desenhar(self, tela):
        cresce = clamp(self.t / 0.22, 0, 1)
        escala = 0.25 + 0.75 * (1 - (1 - cresce) ** 3)
        saida = 1.0 if self.t < self.duracao - 0.25 else clamp((self.duracao - self.t) / 0.25, 0, 1)
        esc = escala * (0.6 + 0.4 * saida)
        r_base = self.raio * esc
        for ang, dist, r, fase in self.bolas:
            tremor = 4 * math.sin(self.t * 38 + fase)
            cx = self.x + math.cos(ang + self.t * 3) * dist * r_base + tremor
            cy = self.y + math.sin(ang + self.t * 3) * dist * r_base * 0.8 + tremor * 0.6
            rr = max(4, int(r * r_base * 1.25))
            pygame.draw.circle(tela, (160, 188, 226), (int(cx), int(cy)), rr + 3)
            pygame.draw.circle(tela, (248, 251, 255), (int(cx), int(cy)), rr)
            pygame.draw.circle(tela, (222, 234, 250), (int(cx + rr * 0.2), int(cy + rr * 0.25)), int(rr * 0.6))
        for ang, dist, fase in self.estrelas:
            a = ang + self.t * 6
            sx = self.x + math.cos(a) * r_base * dist
            sy = self.y + math.sin(a) * r_base * dist * 0.75
            tam = 7 + int(3 * math.sin(self.t * 20 + fase))
            _estrela(tela, sx, sy, tam, (255, 214, 60), (120, 80, 10))
        # riscos de impacto
        for k in range(8):
            a = k * math.tau / 8 + 0.4 + self.t * 2
            d1, d2 = r_base * 1.05, r_base * (1.2 + 0.1 * math.sin(self.t * 25 + k))
            pygame.draw.line(tela, (120, 150, 200),
                             (self.x + math.cos(a) * d1, self.y + math.sin(a) * d1 * 0.8),
                             (self.x + math.cos(a) * d2, self.y + math.sin(a) * d2 * 0.8), 3)


def _estrela(tela, x, y, tam, cor, contorno):
    pts = []
    for i in range(8):
        ang = i * math.pi / 4 - math.pi / 2
        r = tam if i % 2 == 0 else tam * 0.42
        pts.append((x + math.cos(ang) * r, y + math.sin(ang) * r))
    pygame.draw.polygon(tela, contorno, [(px + 1, py + 1) for px, py in pts])
    pygame.draw.polygon(tela, cor, pts)


def estrelinhas_tontura(tela, cx, cy, t, n=3, raio=34):
    #estrelas na cabeça do esquiador
    for i in range(n):
        ang = t * 5.5 + i * math.tau / n
        _estrela(tela, cx + math.cos(ang) * raio, cy + math.sin(ang) * raio * 0.38, 8,
                 (255, 214, 60), (120, 80, 10))


#projétil (carne)
class Projetil:
    """Carne arremessada em arco até o lobo."""

    def __init__(self, superficie, origem, alvo, duracao, ao_chegar, arco=60):
        self.surf = superficie
        self.origem = origem
        self.alvo = alvo            # objeto com .x e .cy (o lobo): o destino acompanha o mundo
        self.dur = duracao
        self.ao_chegar = ao_chegar
        self.arco = arco
        self.t = 0.0
        self.fim = False
        self.x, self.y = origem

    def atualizar(self, dt):
        self.t += dt / self.dur
        p = clamp(self.t, 0, 1)
        self.x = lerp(self.origem[0], self.alvo.x, p)
        self.y = lerp(self.origem[1], self.alvo.cy, p) - math.sin(math.pi * p) * self.arco
        if self.t >= 1.0 and not self.fim:
            self.fim = True
            self.ao_chegar()

    def desenhar(self, tela):
        rot = pygame.transform.rotate(self.surf, self.t * 600)
        tela.blit(rot, rot.get_rect(center=(int(self.x), int(self.y))))


#rastro dos esquis
class Rastro:
    #marca dos eskis

    ESPACO = 9.0

    def __init__(self):
        self.esq = []
        self.dir = []
        self.acum = 0.0

    def atualizar(self, dt, vmundo, x, y, ativo):
        mov = vmundo * dt
        for lista in (self.esq, self.dir):
            for ponto in lista:
                ponto[1] -= mov
            while lista and lista[0][1] < -20:
                lista.pop(0)
        self.acum += mov
        if ativo and self.acum >= self.ESPACO:
            self.acum = 0.0
            self.esq.append([x - 11, y])
            self.dir.append([x + 11, y])

    def desenhar(self, tela):
        for lista in (self.esq, self.dir):
            if len(lista) >= 2:
                pygame.draw.lines(tela, (205, 220, 241), False, lista, 5)
                pygame.draw.lines(tela, (176, 200, 232), False, lista, 2)


#tela: tremor e flash
class EfeitosTela:
    def __init__(self):
        self.tremor_t = 0.0
        self.tremor_dur = 0.001
        self.tremor_int = 0.0
        self.flashes = []           # [cor, tempo, duracao, alpha_max]
        self._superficies = {}

    def tremer(self, intensidade, duracao):
        if intensidade >= self.tremor_int * (self.tremor_t / self.tremor_dur if self.tremor_dur else 0):
            self.tremor_int = intensidade
            self.tremor_t = self.tremor_dur = duracao

    def flash(self, cor, duracao=0.2, alpha_max=170):
        self.flashes.append([cor, duracao, duracao, alpha_max])

    def atualizar(self, dt):
        if self.tremor_t > 0:
            self.tremor_t = max(0.0, self.tremor_t - dt)
        for f in self.flashes:
            f[1] -= dt
        self.flashes = [f for f in self.flashes if f[1] > 0]

    def aplicar_tremor(self, tela):
        if self.tremor_t <= 0:
            return
        amp = self.tremor_int * (self.tremor_t / self.tremor_dur)
        dx = int(random.uniform(-amp, amp))
        dy = int(random.uniform(-amp, amp))
        if dx or dy:
            tela.scroll(dx, dy)

    def desenhar_flash(self, tela):
        for cor, restante, total, alpha_max in self.flashes:
            surf = self._superficies.get(cor)
            if surf is None:
                surf = pygame.Surface((LARGURA, ALTURA))
                surf.fill(cor)
                self._superficies[cor] = surf
            surf.set_alpha(int(alpha_max * (restante / total) ** 1.4))
            tela.blit(surf, (0, 0))


#sombras
class Sombras:

    def __init__(self):
        self._cache = {}

    def desenhar(self, tela, cx, cy, largura, altura):
        w = max(8, int(round(largura / 4.0)) * 4)
        h = max(4, int(round(altura / 2.0)) * 2)
        surf = self._cache.get((w, h))
        if surf is None:
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (60, 96, 150, 70), (0, 0, w, h))
            pygame.draw.ellipse(surf, (60, 96, 150, 40), (int(w * 0.12), int(h * 0.15), int(w * 0.76), int(h * 0.7)))
            self._cache[(w, h)] = surf
        tela.blit(surf, (int(cx - w / 2), int(cy - h / 2)))


#nevasca
class Nevasca:
    #tempestade de neve

    BANDAS = 14
    ALPHA_MAX = 125

    def __init__(self):
        self.intensidade = 0.0
        self.ativa = False
        self.t_proxima = NEVASCA_PRIMEIRA
        self.t_fim = 0.0
        rnd = random.Random(5)
        self.flocos = [[rnd.uniform(0, LARGURA), rnd.uniform(0, ALTURA), rnd.uniform(0.6, 1.4)]
                       for _ in range(130)]
        altura_banda = ALTURA // self.BANDAS + 1
        self.bandas = []
        for _ in range(self.BANDAS):
            s = pygame.Surface((LARGURA, altura_banda))
            s.fill((246, 250, 255))
            self.bandas.append(s)
        self.altura_banda = ALTURA // self.BANDAS

    def reiniciar(self):
        self.intensidade = 0.0
        self.ativa = False
        self.t_proxima = NEVASCA_PRIMEIRA

    def atualizar(self, dt, t_corrida, vmundo):
        if NEVASCA_ATIVA:
            if not self.ativa and t_corrida >= self.t_proxima:
                self.ativa = True
                self.t_fim = t_corrida + random.uniform(*NEVASCA_DURACAO)
            elif self.ativa and t_corrida >= self.t_fim:
                self.ativa = False
                self.t_proxima = t_corrida + random.uniform(*NEVASCA_INTERVALO)
        alvo = 1.0 if self.ativa else 0.0
        passo = dt * 0.55
        if self.intensidade < alvo:
            self.intensidade = min(alvo, self.intensidade + passo)
        elif self.intensidade > alvo:
            self.intensidade = max(alvo, self.intensidade - passo)
        if self.intensidade > 0.01:
            for f in self.flocos:
                f[0] -= (430 + 380 * f[2]) * dt
                f[1] += (140 + 120 * f[2]) * dt - vmundo * 0.12 * dt
                if f[0] < -20:
                    f[0] += LARGURA + 40
                if f[1] > ALTURA + 10:
                    f[1] -= ALTURA + 20
                elif f[1] < -10:
                    f[1] += ALTURA + 20

    def desenhar(self, tela):
        if self.intensidade <= 0.01:
            return
        for i, banda in enumerate(self.bandas):
            frac = (i + 1) / self.BANDAS
            banda.set_alpha(int(self.ALPHA_MAX * (frac ** 1.25) * self.intensidade))
            tela.blit(banda, (0, i * self.altura_banda))
        n = int(len(self.flocos) * self.intensidade)
        for f in self.flocos[:n]:
            x, y = int(f[0]), int(f[1])
            comp = int(10 + 9 * f[2])
            pygame.draw.line(tela, (176, 200, 234), (x + 1, y + 1), (x + comp // 2 + 1, y + 1 + comp // 6), 3)
            pygame.draw.line(tela, (255, 255, 255), (x, y), (x + comp // 2, y + comp // 6), 3)


#avalanche
class Avalanche:

    ALTURA_CORPO = 440

    def __init__(self, centros, largura_faixa, x_pista):
        self.centros = centros
        self.lw = largura_faixa
        self.x_pista = x_pista
        self.reiniciar()
        self._aviso = pygame.Surface((int(largura_faixa), 150), pygame.SRCALPHA)
        for y in range(150):
            a = int(120 * (1 - y / 150) ** 1.4)
            pygame.draw.line(self._aviso, (232, 64, 64, a), (0, y), (int(largura_faixa), y))

    def reiniciar(self):
        self.estado = "espera"
        self.t = 0.0
        self.t_proxima = AVALANCHE_PRIMEIRA
        self.faixa_livre = None
        self.y_frente = -30.0
        self._tentando_desde = None

    @property
    def ativa(self):
        return self.estado in ("aviso", "descendo")

    def faixas_ocupadas(self):
        if self.faixa_livre is None:
            return []
        return [f for f in range(NUM_FAIXAS) if f != self.faixa_livre]

    def rects_perigo(self):
        #retangulos de perigo da avalanche
        if self.estado != "descendo":
            return []
        topo = self.y_frente - self.ALTURA_CORPO
        return [pygame.Rect(int(self.centros[f] - self.lw / 2), int(topo), int(self.lw), self.ALTURA_CORPO)
                for f in self.faixas_ocupadas()]

    def atualizar(self, dt, t_corrida, escolher_faixa):
        #retorna lista de eventos
        eventos = []
        if not AVALANCHE_ATIVA:
            return eventos
        if self.estado == "espera":
            if t_corrida >= self.t_proxima:
                faixa = escolher_faixa()
                if faixa is not None:
                    self.faixa_livre = faixa
                    self.estado = "aviso"
                    self.t = 0.0
                    self._tentando_desde = None
                    eventos.append("aviso")
                else:   # nenhuma faixa vazia agora: espera um pouco (sem nunca ser injusta)
                    if self._tentando_desde is None:
                        self._tentando_desde = t_corrida
                    if t_corrida - self._tentando_desde > 8.0:
                        self._tentando_desde = None
                        self.t_proxima = t_corrida + random.uniform(*AVALANCHE_INTERVALO)
        elif self.estado == "aviso":
            self.t += dt
            if self.t >= AVALANCHE_AVISO:
                self.estado = "descendo"
                self.y_frente = -30.0
                eventos.append("desce")
        elif self.estado == "descendo":
            self.y_frente += AVALANCHE_VELOCIDADE * dt
            if self.y_frente - self.ALTURA_CORPO > ALTURA + 40:
                self.estado = "espera"
                self.faixa_livre = None
                self.t_proxima = t_corrida + random.uniform(*AVALANCHE_INTERVALO)
                eventos.append("fim")
        return eventos

    def emitir_poeira(self, particulas):
        if self.estado == "aviso":
            for f in self.faixas_ocupadas():
                if random.random() < 0.5:
                    particulas.emitir(self.centros[f] + random.uniform(-self.lw / 2, self.lw / 2), -4,
                                      random.uniform(-30, 30), random.uniform(120, 300), random.uniform(0.4, 0.8),
                                      (255, 255, 255), random.uniform(4, 9), (176, 202, 236))
        elif self.estado == "descendo":
            for f in self.faixas_ocupadas():
                for _ in range(2):
                    particulas.emitir(self.centros[f] + random.uniform(-self.lw / 2, self.lw / 2),
                                      self.y_frente + random.uniform(-10, 30), random.uniform(-90, 90),
                                      random.uniform(100, 380), random.uniform(0.4, 0.9),
                                      (255, 255, 255), random.uniform(5, 11), (176, 202, 236))

    def desenhar(self, tela, relogio):
        if self.estado == "aviso":
            piscar = 0.55 + 0.45 * math.sin(relogio * 14)
            self._aviso.set_alpha(int(255 * piscar))
            for f in self.faixas_ocupadas():
                x = int(self.centros[f] - self.lw / 2)
                tela.blit(self._aviso, (x, 0))
                cx = int(self.centros[f])
                pygame.draw.polygon(tela, (120, 20, 20), [(cx, 24), (cx - 34, 84), (cx + 34, 84)])
                pygame.draw.polygon(tela, (255, 206, 52), [(cx, 32), (cx - 27, 79), (cx + 27, 79)])
                texto.desenhar(tela, "!", cx, 42, 40, (120, 20, 20), "centro", None, 0)
        elif self.estado == "descendo":
            for f in self.faixas_ocupadas():
                x = int(self.centros[f] - self.lw / 2)
                topo = int(self.y_frente - self.ALTURA_CORPO)
                # corpo: degradê em faixas (mais escuro/azulado perto da frente) + ondulações
                faixas = 8
                alt = self.ALTURA_CORPO // faixas
                for k in range(faixas):
                    cor = mistura_cor((226, 237, 252), (176, 202, 238), (k / (faixas - 1)) ** 1.5)
                    pygame.draw.rect(tela, cor, (x, topo + k * alt, int(self.lw), alt + 1))
                for k in range(6):
                    yy = topo + 40 + k * 66
                    pygame.draw.line(tela, (140, 172, 222), (x + 8, yy), (x + self.lw - 8, yy + 16), 5)
                    pygame.draw.line(tela, (255, 255, 255), (x + 14, yy - 6), (x + self.lw - 30, yy + 6), 4)
                # frente: bolas de neve rolando (contorno forte, para destacar do chão claro)
                n = 7
                for k in range(n):
                    cx = x + (k + 0.5) * self.lw / n
                    r = int(38 + 14 * math.sin(k * 2.1 + relogio * 12))
                    pygame.draw.circle(tela, (92, 128, 190), (int(cx), int(self.y_frente)), r + 4)
                for k in range(n):
                    cx = x + (k + 0.5) * self.lw / n
                    r = int(38 + 14 * math.sin(k * 2.1 + relogio * 12))
                    pygame.draw.circle(tela, (240, 246, 255), (int(cx), int(self.y_frente)), r)
                    pygame.draw.circle(tela, (200, 218, 244), (int(cx + r * 0.2), int(self.y_frente + r * 0.25)), int(r * 0.6))
