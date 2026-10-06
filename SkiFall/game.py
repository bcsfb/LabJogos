import math
import random

import pygame
from PPlay.keyboard import Keyboard
from PPlay.sprite import Sprite
from PPlay.window import Window

from config import (
    ALTURA,
    ARQUIVOS,
    ARQUIVO_RECORDE,
    CHANCE_CARNE,
    CHANCE_CONSUMIVEL,
    CHANCE_LAMA,
    CHANCE_LOBO,
    CHANCE_MULTIPLICADOR,
    CHANCE_PINHEIRO,
    CHANCE_SERRA,
    CHANCE_VIDA,
    COR_BRANCO,
    COR_DIVISA,
    COR_DOURADO,
    COR_FLORESTA,
    COR_FLORESTA_ESCURA,
    COR_LAMA,
    COR_NEVE,
    COR_PISTA,
    DISTANCIA_MAX_ENTRE_LINHAS,
    DISTANCIA_MIN_ENTRE_LINHAS,
    DURACOES_EFEITO,
    LARGURA,
    MULTIPLICADORES,
    PESOS_MULTIPLICADOR,
    PONTOS_POR_SEGUNDO,
    POSSIBILIDADE_LOBO,
    REDUTOR_MAX,
    REDUTOR_MIN,
    TECLAS_DIREITA,
    TECLAS_ESQUERDA,
    VELOCIDADE_INICIAL,
    VELOCIDADE_MAXIMA_MULTIPLICADOR,
    VELOCIDADE_MINIMA_COM_LAMA,
    VELOCIDADE_TROCA_FAIXA,
    TEMPO_ATE_VELOCIDADE_MAXIMA,
)
from entities import Objeto, Player
from utils import clamp, ler_recorde, retangulo_hitbox, salvar_recorde


class SkiFall:
    def __init__(self):
        # PPlay controla a janela, o buffer virtual, os eventos e o update.
        self.janela = Window(
            LARGURA,
            ALTURA,
            "SkiFall - Beta",
            pixel_art=True,
        )

        self.teclado = Keyboard()

        # Superfície virtual do PPlay; pygame.draw desenha no buffer do PPlay.
        self.surface = Window.get_screen()

        self.estado = "MENU"
        self.player = None
        self.objetos = []

        self.tempo_run = 0.0
        self.pontuacao = 0.0
        self.recorde = ler_recorde(ARQUIVO_RECORDE)

        self.velocidade_atual = VELOCIDADE_INICIAL
        self.multiplicador = 1
        self.tempo_multiplicador = 0.0
        self.reducao_lama = 0
        self.tempo_lama = 0.0

        self.distancia_proxima_linha = 160

        self.tempo_morte = 0.0
        self.posicao_morte_x = 0.0
        self.posicao_morte_y = 0.0

        largura_pista = 780
        self.pista_x = (LARGURA - largura_pista) / 2
        self.pista_largura = largura_pista
        self.centros_faixas = [
            self.pista_x + largura_pista * 1 / 6,
            self.pista_x + largura_pista * 3 / 6,
            self.pista_x + largura_pista * 5 / 6,
        ]

        self.iniciar_rodada()

    def iniciar_rodada(self):
        # Esquiador nasce na parte superior.
        self.player = Player(1, ALTURA * 0.20)
        self.player.definir_posicoes_faixas(self.centros_faixas)
        self.objetos = []

        self.tempo_run = 0.0
        self.pontuacao = 0.0
        self.velocidade_atual = VELOCIDADE_INICIAL

        self.multiplicador = 1
        self.tempo_multiplicador = 0.0
        self.reducao_lama = 0
        self.tempo_lama = 0.0

        self.distancia_proxima_linha = 160
        self.tempo_morte = 0.0

    def calcular_velocidade(self):
        progresso = clamp(
            self.tempo_run / TEMPO_ATE_VELOCIDADE_MAXIMA,
            0,
            1,
        )
        return VELOCIDADE_INICIAL * (
            1 + (VELOCIDADE_MAXIMA_MULTIPLICADOR - 1) * progresso
        )

    def velocidade_efetiva(self):
        velocidade = self.velocidade_atual

        if self.tempo_lama > 0:
            fator = 1 - self.reducao_lama / 100
            velocidade *= fator
            velocidade = max(
                velocidade,
                VELOCIDADE_INICIAL * VELOCIDADE_MINIMA_COM_LAMA,
            )

        return velocidade

    def criar_sprite(self, arquivo):
        return Sprite(str(arquivo))

    def linha_tem_objeto(self, y):
        return any(abs(obj.sprite.y - y) < 70 for obj in self.objetos)

    def adicionar_objeto(self, tipo, faixa, y):
        if tipo == "tree":
            arquivo = random.choice((ARQUIVOS["tree1"], ARQUIVOS["tree2"]))
        elif tipo in ARQUIVOS:
            arquivo = ARQUIVOS[tipo]
        else:
            return

        sprite = self.criar_sprite(arquivo)
        sprite.x = self.centros_faixas[faixa] - sprite.width / 2
        self.objetos.append(Objeto(sprite, faixa, y, tipo))

    def escolher_consumivel(self):
        candidatos = []
        pesos = []

        if not self.player.vida_extra:
            candidatos.append("life")
            pesos.append(CHANCE_VIDA)
        if not self.player.serra:
            candidatos.append("saw")
            pesos.append(CHANCE_SERRA)
        if not self.player.carne:
            candidatos.append("meat")
            pesos.append(CHANCE_CARNE)
        if self.tempo_multiplicador <= 0:
            candidatos.append("multiplier")
            pesos.append(CHANCE_MULTIPLICADOR)
        if self.tempo_lama <= 0:
            candidatos.append("mud")
            pesos.append(CHANCE_LAMA)

        if not candidatos:
            return None

        return random.choices(candidatos, weights=pesos, k=1)[0]

    def gerar_linha(self):
        # Agora os objetos nascem abaixo da tela.
        y = ALTURA + 120

        if self.linha_tem_objeto(y):
            return

        if random.random() < CHANCE_LOBO:
            lado = random.choice(POSSIBILIDADE_LOBO)
            faixa_livre = 2 if lado == 0 else 0

            self.adicionar_objeto("wolf", lado, y)

            # Nunca colocamos árvore na única faixa livre quando há lobo.
            if random.random() < CHANCE_CONSUMIVEL:
                consumivel = self.escolher_consumivel()
                if consumivel:
                    self.adicionar_objeto(
                        consumivel,
                        faixa_livre,
                        y + random.randint(-15, 15),
                    )
            return

        faixas = [0, 1, 2]
        random.shuffle(faixas)
        quantidade = 2 if random.random() < 0.50 else 1
        ocupadas = []

        for faixa in faixas[:quantidade]:
            if random.random() <= CHANCE_PINHEIRO:
                self.adicionar_objeto("tree", faixa, y)
                ocupadas.append(faixa)

        if random.random() < CHANCE_CONSUMIVEL:
            livres = [f for f in range(3) if f not in ocupadas]
            if livres:
                consumivel = self.escolher_consumivel()
                if consumivel:
                    self.adicionar_objeto(
                        consumivel,
                        random.choice(livres),
                        y + random.randint(-15, 15),
                    )

    # ---------------------------- INPUT ----------------------------

    def _pressionou(self, teclas):
        return any(self.teclado.key_down(tecla) for tecla in teclas)

    def processar_input_menu(self):
        if self.teclado.key_down("SPACE"):
            self.iniciar_rodada()
            self.estado = "JOGANDO"

    def processar_input_jogo(self):
        if self._pressionou(TECLAS_ESQUERDA):
            if self.player.faixa_atual > 0:
                self.player.mover_para(self.player.faixa_atual - 1)

        if self._pressionou(TECLAS_DIREITA):
            if self.player.faixa_atual < 2:
                self.player.mover_para(self.player.faixa_atual + 1)

    def processar_input_game_over(self):
        if self.teclado.key_down("SPACE"):
            self.iniciar_rodada()
            self.estado = "JOGANDO"

    # ------------------------- COLISÕES ----------------------------

    def processar_lobo(self, objeto):
        if objeto.lobo_atacando or objeto.foi_processado:
            return False

        if self.player.faixa_atual not in {objeto.faixa, 1}:
            return False

        if self.player.carne:
            self.player.carne = False
            objeto.lobo_atacando = True
            objeto.alvo_faixa = self.player.faixa_atual
            objeto.foi_processado = True
            return True

        self.iniciar_morte()
        return True

    def processar_colisoes(self):
        hitbox_player = retangulo_hitbox(self.player.sprite)

        for objeto in self.objetos:
            if objeto.removido:
                continue

            if not hitbox_player.colliderect(retangulo_hitbox(objeto.sprite)):
                continue

            if objeto.tipo == "tree":
                if self.player.serra:
                    self.player.serra = False
                    objeto.removido = True
                else:
                    self.iniciar_morte()
                    return

            elif objeto.tipo == "wolf":
                self.processar_lobo(objeto)
                if self.estado != "JOGANDO":
                    return

            elif objeto.tipo == "saw":
                if not self.player.serra:
                    self.player.serra = True
                objeto.removido = True

            elif objeto.tipo == "meat":
                if not self.player.carne:
                    self.player.carne = True
                objeto.removido = True

            elif objeto.tipo == "life":
                if not self.player.vida_extra:
                    self.player.vida_extra = True
                objeto.removido = True

            elif objeto.tipo == "multiplier":
                self.multiplicador = random.choices(
                    MULTIPLICADORES,
                    weights=PESOS_MULTIPLICADOR,
                    k=1,
                )[0]
                self.tempo_multiplicador = random.choice(DURACOES_EFEITO)
                objeto.removido = True

            elif objeto.tipo == "mud":
                self.reducao_lama = random.randint(REDUTOR_MIN, REDUTOR_MAX)
                self.tempo_lama = random.choice(DURACOES_EFEITO)
                objeto.removido = True

    # ---------------------------- MORTE ----------------------------

    def iniciar_morte(self):
        if self.estado != "JOGANDO":
            return

        if self.player.vida_extra:
            self.player.vida_extra = False
            self.player.faixa_atual = 1
            self.player.faixa_destino = 1
            self.player.em_movimento = False
            self.player.angulo_visual = 0
            self.player.sprite.x = self.centros_faixas[1] - self.player.sprite.width / 2
            self.objetos = [
                obj for obj in self.objetos
                if obj.sprite.y < self.player.sprite.y - 100
                or obj.sprite.y > self.player.sprite.y + 200
            ]
            return

        self.estado = "MORTE"
        self.tempo_morte = 0.0
        self.posicao_morte_x = self.player.sprite.x
        self.posicao_morte_y = self.player.sprite.y

        if self.pontuacao > self.recorde:
            self.recorde = int(self.pontuacao)
            salvar_recorde(ARQUIVO_RECORDE, self.recorde)

    def atualizar_morte(self, dt):
        self.tempo_morte += dt
        direcao = -1 if self.player.faixa_atual == 0 else 1
        self.posicao_morte_x += direcao * 330 * dt
        self.posicao_morte_y -= 270 * dt

        self.player.sprite.x = self.posicao_morte_x
        self.player.sprite.y = self.posicao_morte_y

        if self.tempo_morte >= 1.25:
            self.estado = "GAME_OVER"

    # ---------------------------- UPDATE ---------------------------

    def atualizar_jogo(self, dt):
        self.tempo_run += dt
        self.velocidade_atual = self.calcular_velocidade()

        self.pontuacao += PONTOS_POR_SEGUNDO * self.multiplicador * dt

        if self.tempo_multiplicador > 0:
            self.tempo_multiplicador -= dt
            if self.tempo_multiplicador <= 0:
                self.tempo_multiplicador = 0
                self.multiplicador = 1

        if self.tempo_lama > 0:
            self.tempo_lama -= dt
            if self.tempo_lama <= 0:
                self.tempo_lama = 0
                self.reducao_lama = 0

        self.player.atualizar(dt)
        velocidade = self.velocidade_efetiva()

        self.distancia_proxima_linha -= velocidade * dt
        if self.distancia_proxima_linha <= 0:
            self.gerar_linha()
            fator = self.velocidade_atual / VELOCIDADE_INICIAL
            intervalo_base = random.uniform(
                DISTANCIA_MIN_ENTRE_LINHAS,
                DISTANCIA_MAX_ENTRE_LINHAS,
            )
            self.distancia_proxima_linha = max(
                intervalo_base / math.sqrt(fator),
                120,
            )

        for objeto in self.objetos:
            objeto.atualizar(dt, velocidade, self.player)

        self.processar_colisoes()
        self.objetos = [obj for obj in self.objetos if not obj.removido]

    # -------------------------- DESENHO ----------------------------

    def desenhar_background(self):
        self.janela.set_background_color(COR_NEVE)

        pygame.draw.rect(
            self.surface,
            COR_FLORESTA,
            (0, 0, int(self.pista_x), ALTURA),
        )
        pygame.draw.rect(
            self.surface,
            COR_FLORESTA,
            (
                int(self.pista_x + self.pista_largura),
                0,
                int(LARGURA - (self.pista_x + self.pista_largura)),
                ALTURA,
            ),
        )
        pygame.draw.rect(
            self.surface,
            COR_PISTA,
            (int(self.pista_x), 0, int(self.pista_largura), ALTURA),
        )

        largura_faixa = self.pista_largura / 3
        for i in (1, 2):
            x = int(self.pista_x + largura_faixa * i)
            pygame.draw.line(
                self.surface,
                COR_DIVISA,
                (x, 0),
                (x, ALTURA),
                5,
            )

        # Elementos decorativos também sobem.
        deslocamento = int(
            (self.tempo_run * self.velocidade_efetiva() * 0.6) % 150
        )
        for lado in (0, 1):
            base_x = 60 if lado == 0 else int(LARGURA - 110)
            for i in range(-1, 8):
                y = i * 150 - deslocamento - 100
                self.desenhar_arvore_decorativa(base_x, y)

    def desenhar_arvore_decorativa(self, x, y):
        pygame.draw.rect(
            self.surface,
            (105, 70, 42),
            (x + 25, y + 45, 16, 45),
        )
        pygame.draw.polygon(
            self.surface,
            COR_FLORESTA_ESCURA,
            [(x + 33, y), (x, y + 58), (x + 66, y + 58)],
        )
        pygame.draw.polygon(
            self.surface,
            COR_FLORESTA_ESCURA,
            [(x + 33, y + 24), (x + 5, y + 78), (x + 61, y + 78)],
        )

    def desenhar_inventario(self):
        base_x = 20
        base_y = 65
        tamanho = 62
        espaco = 12

        pygame.draw.rect(
            self.surface,
            (245, 250, 255),
            (base_x - 10, base_y - 10, 3 * tamanho + 2 * espaco + 20, tamanho + 20),
        )

        itens = (
            ("saw", self.player.serra),
            ("meat", self.player.carne),
            ("life", self.player.vida_extra),
        )

        for i, (tipo, ativo) in enumerate(itens):
            x = base_x + i * (tamanho + espaco)
            pygame.draw.rect(
                self.surface,
                (205, 220, 235),
                (x, base_y, tamanho, tamanho),
                3,
            )

            if ativo:
                sprite = Sprite(str(ARQUIVOS[tipo]))
                sprite.width = tamanho - 12
                sprite.height = tamanho - 12
                sprite.x = x + 6
                sprite.y = base_y + 6
                sprite.draw()

            self.janela.draw_text(
                "1" if ativo else "0",
                x + tamanho - 18,
                base_y + tamanho - 24,
                size = 22,
                cor = COR_BRANCO,
            )

    def desenhar_hud(self):
        minutos = int(self.tempo_run // 60)
        segundos = int(self.tempo_run % 60)

        self.janela.draw_text(
            f"TEMPO  {minutos:02d}:{segundos:02d}",
            20,
            18,
            size = 30,
            cor = COR_BRANCO,
        )

        self.janela.draw_text(
            f"PONTOS  {int(self.pontuacao)}",
            LARGURA - 240,
            18,
            size = 30,
            cor = COR_BRANCO,
        )

        self.janela.draw_text(
            f"VELOCIDADE {self.velocidade_atual / VELOCIDADE_INICIAL:.2f}x",
            LARGURA - 240,
            56,
            size = 22,
            cor = COR_BRANCO,
        )

        self.desenhar_inventario()

        if self.tempo_multiplicador > 0:
            self.janela.draw_text(
                f"{self.multiplicador}X  {self.tempo_multiplicador:04.1f}s",
                LARGURA // 2 - 70,
                45,
                size = 40,
                cor = COR_DOURADO,
                bold=True,
            )

        if self.tempo_lama > 0:
            self.janela.draw_text(
                f"LAMA -{self.reducao_lama}%  {self.tempo_lama:04.1f}s",
                LARGURA // 2 - 110,
                95,
                size = 40,
                cor = COR_LAMA,
                bold=True,
            )

    @staticmethod
    def camada_escura(surface, alpha):
        camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        camada.fill((0, 0, 0, alpha))
        surface.blit(camada, (0, 0))

    def desenhar_menu(self):
        self.desenhar_background()
        self.player.sprite.draw()
        self.camada_escura(self.surface, 105)

        self.janela.draw_text(
            "SKIFALL",
            LARGURA // 2 - 115,
            ALTURA // 2 - 140,
            size = 64,
            cor = COR_BRANCO,
            bold=True,
        )
        self.janela.draw_text(
            "COMEÇAR A ESQUIAR",
            LARGURA // 2 - 170,
            ALTURA // 2 - 35,
            size = 40,
            cor = COR_BRANCO,
            bold=True,
        )
        self.janela.draw_text(
            "SPACE para começar",
            LARGURA // 2 - 105,
            ALTURA // 2 + 35,
            size = 30,
            cor = COR_BRANCO,
        )
        self.janela.draw_text(
            "W/S ou ↑/↓ para trocar de faixa",
            LARGURA // 2 - 150,
            ALTURA // 2 + 100,
            size = 22,
            cor = COR_BRANCO,
        )
        self.janela.draw_text(
            f"Recorde: {self.recorde}",
            LARGURA // 2 - 70,
            ALTURA // 2 + 135,
            size = 22,
            cor = COR_BRANCO,
        )

    def desenhar_morte(self):
        self.desenhar_background()
        for objeto in self.objetos:
            objeto.desenhar()
        self.player.draw()

        alpha = int(clamp((self.tempo_morte - 0.75) / 0.5, 0, 1) * 100)
        self.camada_escura(self.surface, alpha)

    def desenhar_game_over(self):
        self.desenhar_background()
        self.camada_escura(self.surface, 130)

        self.janela.draw_text(
            "VOCÊ MORREU",
            LARGURA // 2 - 150,
            ALTURA // 2 - 130,
            size = 64,
            cor = COR_BRANCO,
            bold=True,
        )
        self.janela.draw_text(
            f"Pontuação: {int(self.pontuacao)}",
            LARGURA // 2 - 100,
            ALTURA // 2 - 20,
            size = 30,
            cor = COR_BRANCO,
        )

        minutos = int(self.tempo_run // 60)
        segundos = int(self.tempo_run % 60)

        self.janela.draw_text(
            f"Tempo: {minutos:02d}:{segundos:02d}",
            LARGURA // 2 - 80,
            ALTURA // 2 + 30,
            size = 30,
            cor = COR_BRANCO,
        )
        self.janela.draw_text(
            f"Recorde: {self.recorde}",
            LARGURA // 2 - 70,
            ALTURA // 2 + 75,
            size = 30,
            cor = COR_BRANCO,
        )
        self.janela.draw_text(
            "SPACE para jogar novamente",
            LARGURA // 2 - 150,
            ALTURA // 2 + 135,
            size = 40,
            cor = COR_BRANCO,
            bold=True,
        )

    # ---------------------------- LOOP -----------------------------

    def rodar(self):
        """Loop principal. Window.update() é deliberadamente o último comando."""
        while True:
            dt = min(self.janela.delta_time(), 0.033)

            if self.estado == "MENU":
                self.processar_input_menu()
                self.desenhar_menu()

            elif self.estado == "JOGANDO":
                self.processar_input_jogo()
                self.atualizar_jogo(dt)

                self.desenhar_background()
                for objeto in self.objetos:
                    objeto.desenhar()
                self.player.draw()
                self.desenhar_hud()

            elif self.estado == "MORTE":
                self.atualizar_morte(dt)
                self.desenhar_morte()

            elif self.estado == "GAME_OVER":
                self.processar_input_game_over()
                self.desenhar_game_over()

            self.janela.update()
