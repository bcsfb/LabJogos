
#SkiFall - loop principal
#estados:  MENU -> JOGANDO <-> QUEDA -> GAME_OVER -> (JOGANDO | MENU)
#OBS: PAUSADO esta por cima de JOGANDO/QUEDA.

#ordem funcionamento PPlay: entrada -> simulação -> desenho -> janela.update()

import math
import random

import pygame
from PPlay.window import Window

import texto
from assets import superficie_escalada
from audio import Audio, VOLUME_MUSICA
from cenario import Cenario
from config import (
    ALTURA, ARQUIVO_CREDITOS, ARQUIVO_OPCOES, ARQUIVOS_RANKING, ARQUIVO_RECORDE, COR_DOURADO, COR_LARANJA, COR_NEVE_LATERAL, COR_VERMELHO,
    CHANCE_CONSUMIVEL_LINHA, CHANCE_GELO_LINHA, CHANCE_LOBO_FIM, CHANCE_LOBO_INICIO, CHANCE_PEDRA, DT_MAX,
    DURACAO_TROCA_FAIXA, GELO_FATOR_TROCA, GELO_PERSISTENCIA, IMA_ALCANCE_Y, IMA_DURACOES, IMA_VELOCIDADE,
    LINHAS_ENTRE_GELOS, NEVASCA_BONUS_PONTOS, PONTUACAO_MINIMA, QUASE_COMBO_MAXIMO, QUASE_DISTANCIA,
    QUASE_PONTOS, QUASE_TEMPO_COMBO,
    DURACOES_EFEITO, FPS_ALVO, GAP_FINAL, GAP_INICIAL, HITBOX_JOGADOR, HITBOX_PINHEIRO, JOGADOR_CY,
    LARGURA, LARGURA_PISTA, DIFICULDADES, DIFICULDADE_AJUSTES, DIFICULDADE_PADRAO,
    MULTIPLICADORES, NUM_FAIXAS, PESOS_MULTIPLICADOR, PESOS_PINHEIROS_FIM, PESOS_PINHEIROS_INICIO,
    PONTOS_POR_SEGUNDO, POSSIBILIDADE_LOBO, REDUTOR_MAX, REDUTOR_MIN, ROTULOS_ITENS,
    TECLA_MUDO, TECLAS_DIREITA, TECLAS_ESQUERDA, TECLAS_PAUSA, TEMPO_ATE_VELOCIDADE_MAXIMA,
    TEMPO_PRIMEIRO_LOBO, TEMPO_REACAO, TITULO_JANELA, VELOCIDADE_INICIAL,
    VELOCIDADE_MAXIMA_MULTIPLICADOR, VELOCIDADE_MINIMA_COM_LAMA, Y_NASCIMENTO,
)
from efeitos import (
    Avalanche, EfeitosTela, Nevasca, NuvemBriga, Particulas, PinheiroCortado, Popup, Projetil,
    Rastro, Sombras, estrelinhas_tontura,
)
from entities import Arvore, COR_HALO, Gelo, Item, Jogador, Lobo, Pedra
from hud import Hud
from opcoes import ler_opcoes, salvar_opcoes
from ranking import Ranking, limpar_nome
from telas import MENU_ITENS, Telas
from utils import clamp, lerp, mistura_cor, suave_entrada_saida

DURACAO_QUEDA = 1.6
DURACAO_QUEDA_REVIVER = 1.25
DURACAO_RETOMADA = 1.0


class SkiFall:
    #inicialização
    def __init__(self):
        self.janela = Window(LARGURA, ALTURA, TITULO_JANELA, resizavel=True, pixel_art=True)
        self.janela.set_background_color(COR_NEVE_LATERAL)
        self.teclado = self.janela.keyboard
        self.tela = Window.get_screen()
        texto.preaquecer((12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 54, 70, 78),
                         (56, 60, 66, 70, 84, 112))

        self.limitador = pygame.time.Clock()   # o PPlay não limita o FPS sozinho
        self.dt_suave = 1.0 / 60.0

        # geometria da pista
        self.x_pista = (LARGURA - LARGURA_PISTA) / 2
        self.lw = LARGURA_PISTA / NUM_FAIXAS
        self.centros = [self.x_pista + self.lw * (i + 0.5) for i in range(NUM_FAIXAS)]

        # sistemas
        self.audio = Audio()
        self.cenario = Cenario(self.x_pista, LARGURA_PISTA)
        self.hud = Hud()
        self.telas = Telas()
        self.particulas = Particulas()
        self.fx = EfeitosTela()
        self.sombras = Sombras()
        self.rastro = Rastro()
        self.nevasca = Nevasca()
        self.avalanche = Avalanche(self.centros, self.lw, self.x_pista)
        self.jogador = Jogador(self.centros, JOGADOR_CY)
        self.jogador_menu = Jogador(self.centros, 772)   # o esquiador do menu desce por baixo das opções

        # alerta vermelho (lobo se aproximando):
        self.surf_alerta = pygame.Surface((int(self.lw * 2), 150), pygame.SRCALPHA)
        for y in range(150):
            pygame.draw.line(self.surf_alerta, (232, 54, 54, int(130 * (y / 150) ** 1.3)), (0, y),
                             (int(self.lw * 2), y))

        #ranking por dificuldade
        self.rankings = {nome: Ranking(ARQUIVOS_RANKING[nome], ARQUIVO_RECORDE if nome == "NORMAL" else None)
                         for nome in DIFICULDADES}
        escolhida = ler_opcoes(ARQUIVO_OPCOES).get("dificuldade", DIFICULDADE_PADRAO).upper()
        self._aplicar_dificuldade(escolhida if escolhida in DIFICULDADES else DIFICULDADE_PADRAO)
        self.ultimas_iniciais = ""
        #navegação do menu inicial
        self.menu_tela = "PRINCIPAL"      # PRINCIPAL | RANKING | COMO_JOGAR | CREDITOS
        self.menu_idx = 0
        self.rank_aba = DIFICULDADES.index(self.dificuldade)
        self.surf_creditos = None
        self.creditos_scroll = 0.0
        self.relogio = 0.0
        self.pausado = False
        self.hit_stop = 0.0
        self.mostrar_fps = False
        self.t_demo = 1.0
        self.acum_poeira = 0.0
        self.acum_jorro = 0.0
        self._zerar_partida()
        self.estado = "MENU"
        self.t_estado = 0.0
        self.audio.musica_iniciar(0, 0.40)

    #dificuldade
    def _aplicar_dificuldade(self, nome):
        """Calcula os valores da partida a partir de config.py (NORMAL) + os ajustes do nível."""
        self.dificuldade = nome
        self.adj = DIFICULDADE_AJUSTES[nome]
        self.v0 = VELOCIDADE_INICIAL * self.adj["velocidade_inicial"]
        self.vmax_mult = max(1.0, VELOCIDADE_MAXIMA_MULTIPLICADOR * self.adj["velocidade_maxima"])
        self.t_max = TEMPO_ATE_VELOCIDADE_MAXIMA * self.adj["tempo_ate_maximo"]
        self.ranking = self.rankings[nome]
        self.recorde = self.ranking.melhor()

    def _limiar(self, novidade):
        """Pontuação mínima (já ajustada pela dificuldade) para a novidade aparecer."""
        return PONTUACAO_MINIMA[novidade] * self.adj["novidades"]

    def _mudar_dificuldade(self, passo):
        i = (DIFICULDADES.index(self.dificuldade) + passo) % len(DIFICULDADES)
        self._aplicar_dificuldade(DIFICULDADES[i])
        salvar_opcoes(ARQUIVO_OPCOES, {"dificuldade": self.dificuldade})
        self.audio.tocar("blip")

    def _zerar_partida(self):
        self.t_corrida = 0.0
        self.pontuacao = 0.0
        self.novo_recorde = False
        self.causa_morte = None
        self.objetos = []
        self.cortes = []
        self.projeteis = []
        self.voando = []
        self.popups = []
        self.nuvens = []
        self.pulsos = {}
        self.mult, self.t_mult, self.dur_mult = 1, 0.0, 1.0
        self.reducao, self.t_reducao, self.dur_reducao = 0, 0.0, 1.0
        self.fator_mundo = 1.0
        self.t_retomada = DURACAO_RETOMADA
        self.y_ultima_linha = Y_NASCIMENTO - 150
        self.gap_px_proximo = 400.0
        self.livres_anteriores = {0, 1, 2}
        self.linhas_desde_lobo = 9
        self.reviver = False
        self.lobo_atacante = None
        self.t_ima, self.dur_ima = 0.0, 1.0
        self.combo_quase, self.t_combo_quase = 0, 0.0
        self.linhas_desde_gelo = 9
        self.gelo_na_linha_anterior = False
        self.t_som_gelo = 0.0
        self.novidades_avisadas = set()
        self.entrando_iniciais = False
        self.iniciais = ""
        self.posicao_ranking = -1

    #loop
    def rodar(self):
        try:
            while True:
                self.passo()
        except SystemExit:
            self._salvar_se_recorde()
            raise

    def passo(self):
        dt = self._calcular_dt()
        self._entrada_global()
        if not self.pausado:
            self.relogio += dt

        if self.estado == "MENU":
            self._atualizar_menu(dt)
            self._desenhar_menu()
        elif self.estado in ("JOGANDO", "QUEDA"):
            if not self.pausado:
                self._atualizar_partida(dt)
            self._desenhar_partida()
            if self.pausado:
                self.telas.desenhar_pausa(self.tela, self)
        else:  # GAME_OVER
            self._atualizar_game_over(dt)
            self._desenhar_partida()
            self.telas.desenhar_game_over(self.tela, self)

        # música acompanha a velocidade
        if not self.pausado:
            desejado = 0
            if self.estado in ("JOGANDO", "QUEDA"):
                desejado = self.audio.andamento_para_progresso(self._progresso())
            self.audio.musica_atualizar(dt, desejado)
        if self.mostrar_fps:
            texto.desenhar(self.tela, f"FPS {self.janela.get_fps():5.1f}", LARGURA // 2, ALTURA - 40, 18,
                           (255, 255, 255), "centro")

        self.janela.update()                 # por último no quadro
        self.limitador.tick(FPS_ALVO)

    def _calcular_dt(self):
        bruto = clamp(self.janela.delta_time(), 0.0, DT_MAX)
        if bruto > 0:
            # suaviza oscilações
            if abs(bruto - self.dt_suave) < 0.012:
                self.dt_suave += (bruto - self.dt_suave) * 0.25
            else:
                self.dt_suave = bruto
        return self.dt_suave

    #entrada global
    def _entrada_global(self):
        if not self.entrando_iniciais and self.teclado.key_down(TECLA_MUDO):
            self.audio.alternar_mudo()
        if self.teclado.key_down(pygame.K_F3):
            self.mostrar_fps = not self.mostrar_fps
        perdeu_foco = getattr(pygame, "WINDOWFOCUSLOST", None)
        if perdeu_foco is not None and self.estado in ("JOGANDO", "QUEDA") and not self.pausado:
            if any(ev.type == perdeu_foco for ev in self.janela.eventos):
                self._alternar_pausa()
        if self.estado in ("JOGANDO", "QUEDA"):
            if any(self.teclado.key_down(k) for k in TECLAS_PAUSA):
                self._alternar_pausa()
            elif self.pausado:
                if self.teclado.key_down("R"):
                    self._alternar_pausa()
                    self.iniciar_partida()
                elif self.teclado.key_down("Q"):
                    self._alternar_pausa()
                    self._voltar_ao_menu()

    def _alternar_pausa(self):
        self.pausado = not self.pausado
        self.audio.musica_pausar(self.pausado)
        self.audio.tocar("blip")

    #menu
    def _atualizar_menu(self, dt):
        self.t_estado += dt
        v = VELOCIDADE_INICIAL * 1.5
        self.cenario.atualizar(dt, v)
        demo = self.jogador_menu
        demo.atualizar(dt)
        self.t_demo -= dt
        if self.t_demo <= 0:
            d = random.choice((-1, 1))
            if not demo.mover(d):
                demo.mover(-d)
            self.t_demo = random.uniform(0.9, 1.8)
        self.rastro.atualizar(dt, v, demo.x, demo.cy + 30, True)
        self.acum_poeira += dt
        while self.acum_poeira >= 0.03:
            self.acum_poeira -= 0.03
            self.particulas.poeira_descida(demo.x, demo.cy + 36, v)
        self.particulas.atualizar(dt, v)
        self.audio.vento_parar()

        if self.menu_tela == "PRINCIPAL":
            self._menu_principal(dt)
        elif self.menu_tela == "RANKING":
            self._menu_ranking()
        elif self.menu_tela == "CREDITOS":
            self._menu_creditos(dt)
        else:                                   # COMO_JOGAR
            if self._confirmou() or self._voltou():
                self._ir_para_menu("PRINCIPAL")

    #menu: entradas
    def _alguma(self, *teclas):
        return any(self.teclado.key_down(t) for t in teclas)

    def _confirmou(self):
        return self._alguma("ENTER", "SPACE")

    def _voltou(self):
        return self._alguma("ESC")

    def _ir_para_menu(self, tela):
        self.menu_tela = tela
        self.audio.tocar("blip")

    def _menu_principal(self, dt):
        n = len(MENU_ITENS)
        if self._alguma("UP", "W"):
            self.menu_idx = (self.menu_idx - 1) % n
            self.audio.tocar("blip")
        elif self._alguma("DOWN", "S"):
            self.menu_idx = (self.menu_idx + 1) % n
            self.audio.tocar("blip")
        item = MENU_ITENS[self.menu_idx]
        if item == "DIFICULDADE":
            if self._alguma("LEFT", "A"):
                self._mudar_dificuldade(-1)
            elif self._alguma("RIGHT", "D"):
                self._mudar_dificuldade(1)
        if self._confirmou():
            if item == "JOGAR":
                self.iniciar_partida()
            elif item == "DIFICULDADE":
                self._mudar_dificuldade(1)
            elif item == "RANKING":
                self.rank_aba = DIFICULDADES.index(self.dificuldade)
                self._ir_para_menu("RANKING")
            elif item == "COMO JOGAR":
                self._ir_para_menu("COMO_JOGAR")
            elif item == "CRÉDITOS":
                self._abrir_creditos()
            elif item == "SAIR":
                self.janela.close()
        elif self._voltou():
            self.janela.close()

    def _menu_ranking(self):
        if self._alguma("LEFT", "A"):
            self.rank_aba = (self.rank_aba - 1) % len(DIFICULDADES)
            self.audio.tocar("blip")
        elif self._alguma("RIGHT", "D"):
            self.rank_aba = (self.rank_aba + 1) % len(DIFICULDADES)
            self.audio.tocar("blip")
        elif self._confirmou() or self._voltou():
            self._ir_para_menu("PRINCIPAL")

    #menu: créditos (creditos.txt)
    def _abrir_creditos(self):
        """Lê creditos.txt a cada abertura: dá para editar o arquivo sem reiniciar o jogo."""
        try:
            linhas = ARQUIVO_CREDITOS.read_text(encoding="utf-8").splitlines()
        except (FileNotFoundError, OSError):
            linhas = ["# SKIFALL", "Crie o arquivo creditos.txt", "para editar estes créditos"]
        self.surf_creditos = self.telas.montar_creditos(linhas)
        self.creditos_scroll = -float(self.telas.ALTURA_CREDITOS)
        self._ir_para_menu("CREDITOS")

    def _menu_creditos(self, dt):
        vel = 60.0
        if self.teclado.key_pressed("DOWN"):
            vel = 260.0
        elif self.teclado.key_pressed("UP"):
            vel = -140.0
        self.creditos_scroll += vel * dt
        altura = self.surf_creditos.get_height()
        if self.creditos_scroll > altura + 40:                 # acabou: recomeça de baixo
            self.creditos_scroll = -float(self.telas.ALTURA_CREDITOS)
        elif self.creditos_scroll < -float(self.telas.ALTURA_CREDITOS):
            self.creditos_scroll = -float(self.telas.ALTURA_CREDITOS)
        if self._confirmou() or self._voltou():
            self._ir_para_menu("PRINCIPAL")

    def _desenhar_menu(self):
        tela = self.tela
        self.cenario.desenhar(tela, 1.4)
        self.rastro.desenhar(tela)
        self.sombras.desenhar(tela, self.jogador_menu.x, self.jogador_menu.cy + 48, 56, 16)
        self.particulas.desenhar(tela, False)
        self.jogador_menu.desenhar(tela)
        self.particulas.desenhar(tela, True)
        self.telas.desenhar_menu(tela, self)

    def _voltar_ao_menu(self):
        self.menu_tela = "PRINCIPAL"
        self.menu_idx = 0
        self.rank_aba = DIFICULDADES.index(self.dificuldade)
        self.estado = "MENU"
        self.t_estado = 0.0
        self.pausado = False
        self.particulas.lista = []
        self.rastro = Rastro()
        self.nevasca.reiniciar()
        self.audio.vento_parar()
        self.audio.musica_iniciar(0, 0.40)

    #início da partida
    def iniciar_partida(self):
        self._zerar_partida()
        self.estado = "JOGANDO"
        self.t_estado = 0.0
        self.pausado = False
        self.hit_stop = 0.0
        self.jogador.reiniciar()
        self.jogador.vida_extra = bool(self.adj["vida_extra_inicial"])
        self.particulas.lista = []
        self.rastro = Rastro()
        self.nevasca.reiniciar()
        self.avalanche.reiniciar()
        self.fx.flashes = []
        self.audio.tocar("inicio")
        self.audio.musica_iniciar(0, VOLUME_MUSICA)

    #velocidade
    def _progresso(self):
        return clamp(self.t_corrida / self.t_max, 0.0, 1.0)

    def _velocidade_base(self):
        """Velocidade com que os obstáculos se aproximam do esquiador (cresce com o tempo)."""
        return self.v0 * (1.0 + (self.vmax_mult - 1.0) * self._progresso())

    def velocidade_efetiva(self):
        v = self._velocidade_base()
        if self.t_reducao > 0:
            v = max(v * (1.0 - self.reducao / 100.0), self.v0 * VELOCIDADE_MINIMA_COM_LAMA)
        return v * self.fator_mundo

    #atualização da partida
    def _atualizar_partida(self, dt):
        if self.hit_stop > 0:                 # "hit stop": congela uma fração de segundo no impacto
            self.hit_stop -= dt
            self.fx.atualizar(dt)
            return
        self.t_estado += dt
        jogando = self.estado == "JOGANDO"
        j = self.jogador

        #desacelera na queda, acelera suavemente ao recomeçar
        if jogando:
            if self.t_retomada > 0:
                self.t_retomada = max(0.0, self.t_retomada - dt)
            self.fator_mundo = lerp(0.45, 1.0, suave_entrada_saida(1.0 - self.t_retomada / DURACAO_RETOMADA))
        else:
            self.fator_mundo = max(0.0, 1.0 - self.t_estado / 0.55) ** 2

        #relógios do jogador
        if jogando:
            self.t_corrida += dt
            bonus_nevasca = NEVASCA_BONUS_PONTOS if self.nevasca.ativa else 1.0
            self.pontuacao += PONTOS_POR_SEGUNDO * self.mult * bonus_nevasca * dt
            self._checar_novidades()
            if self.t_mult > 0:
                self.t_mult -= dt
                if self.t_mult <= 0:
                    self.mult, self.t_mult = 1, 0.0
            if self.t_reducao > 0:
                self.t_reducao -= dt
                if self.t_reducao <= 0:
                    self.reducao, self.t_reducao = 0, 0.0
            if self.t_ima > 0:
                self.t_ima = max(0.0, self.t_ima - dt)
            if self.t_combo_quase > 0:
                self.t_combo_quase -= dt
            if self.t_som_gelo > 0:
                self.t_som_gelo -= dt
        for nome in list(self.pulsos):
            self.pulsos[nome] -= dt
            if self.pulsos[nome] <= 0:
                del self.pulsos[nome]

        if jogando:
            self._entrada_jogo()

        v = self.velocidade_efetiva()
        j.atualizar(dt)
        self.cenario.atualizar(dt, v)

        #geração de obstáculos
        if jogando:
            self.y_ultima_linha -= v * dt
            if self.y_ultima_linha + self.gap_px_proximo <= Y_NASCIMENTO:
                self._gerar_linha()

        #objetos do mundo
        for o in self.objetos:
            if o.tipo == "lobo":
                o.atualizar(dt, v, j)
                self._tratar_sinal_lobo(o)
            else:
                o.mover(dt, v)
        if self.lobo_atacante is not None and self.estado == "QUEDA":
            lb = self.lobo_atacante
            lb.x = j.x + math.sin(self.t_estado * 34) * 4
            lb.cy = j.cy + 8
        self.objetos = [o for o in self.objetos if not o.remover]

        #clima
        self.nevasca.atualizar(dt, self.t_corrida, v)
        self.audio.vento_atualizar(self.nevasca.intensidade)
        if jogando or self.estado == "QUEDA":
            for ev in self.avalanche.atualizar(dt, self.t_corrida, self._escolher_faixa_avalanche):
                self._evento_avalanche(ev)
            if self.avalanche.ativa:
                self.avalanche.emitir_poeira(self.particulas)

        #ímã
        if jogando and self.t_ima > 0:
            self._aplicar_ima(dt)

        #colisões
        if jogando:
            self._resolver_colisoes()

        #efeitos
        self.rastro.atualizar(dt, v, j.x, j.cy + 30, ativo=not j.tombado)
        if jogando:
            self.acum_poeira += dt
            while self.acum_poeira >= 0.03:
                self.acum_poeira -= 0.03
                self.particulas.poeira_descida(j.x, j.cy + 36, v)
            if j.em_troca:
                self.acum_jorro += dt
                while self.acum_jorro >= 0.02:
                    self.acum_jorro -= 0.02
                    self.particulas.jorro_esqui(j.x, j.cy + 34, j.direcao)
        self.particulas.atualizar(dt, v)
        for c in self.cortes:
            c.atualizar(dt, v)
        self.cortes = [c for c in self.cortes if not c.fim]
        for p in self.projeteis:
            p.atualizar(dt)
        self.projeteis = [p for p in self.projeteis if not p.fim]
        for n in self.nuvens:
            n.atualizar(dt)
        self.nuvens = [n for n in self.nuvens if not n.fim]
        for p in self.popups:
            p.atualizar(dt)
        self.popups = [p for p in self.popups if not p.fim]
        self._atualizar_voando(dt)
        self.fx.atualizar(dt)

        #fim da queda
        if self.estado == "QUEDA":
            dur = DURACAO_QUEDA_REVIVER if self.reviver else DURACAO_QUEDA
            if self.t_estado >= dur:
                if self.reviver:
                    self._reviver_jogador()
                else:
                    self._fim_de_jogo()

    #entrada durante o jogo
    def _entrada_jogo(self):
        esq = any(self.teclado.key_down(k) for k in TECLAS_ESQUERDA)
        dire = any(self.teclado.key_down(k) for k in TECLAS_DIREITA)
        direcao = -1 if (esq and not dire) else 1 if (dire and not esq) else 0
        if direcao and self.jogador.mover(direcao):
            self.audio.tocar("troca_faixa")
            self.particulas.jorro_esqui(self.jogador.x, self.jogador.cy + 34, direcao, 1.6)

    #geração
    def _faixa_de(self, x):
        return min(range(NUM_FAIXAS), key=lambda i: abs(self.centros[i] - x))

    @staticmethod
    def _alcanca(anteriores, novas, alcance):
        return any(abs(a - b) <= alcance for a in anteriores for b in novas)

    def _faixa_protegida(self):
        return self.avalanche.faixa_livre if self.avalanche.ativa else None

    def _gerar_linha(self):
        p = self._progresso()
        vb = self._velocidade_base()
        y = max(Y_NASCIMENTO, self.y_ultima_linha + self.gap_px_proximo)
        #quantas faixas o jogador consegue atravessar entre a linha anterior e esta? O tempo útil é a
        #distância entre as linhas MENOS a "espessura" dos obstáculos (enquanto um pinheiro passa pelo
        #esquiador a faixa dele fica bloqueada), descontando 1 reação e então 1 troca por faixa.
        espessura = HITBOX_PINHEIRO[1] + HITBOX_JOGADOR[1]
        tempo_util = max(0.0, (y - self.y_ultima_linha - espessura) / max(vb, 1.0))
        duracao_troca = DURACAO_TROCA_FAIXA
        if self.gelo_na_linha_anterior:       # depois de uma placa de gelo a troca de faixa é mais lenta
            duracao_troca *= GELO_FATOR_TROCA
            tempo_util = max(0.0, tempo_util - GELO_PERSISTENCIA)
        alcance = int(max(0.0, tempo_util - TEMPO_REACAO) / duracao_troca)
        protegida = self._faixa_protegida()
        todas = set(range(NUM_FAIXAS))
        livres = set(todas)
        self.linhas_desde_lobo += 1
        self.linhas_desde_gelo += 1
        faixa_gelo = None

        #lobo?
        chance_lobo = lerp(CHANCE_LOBO_INICIO, CHANCE_LOBO_FIM, p) * self.adj["lobos"]
        virou_lobo = False
        if (self.t_corrida >= TEMPO_PRIMEIRO_LOBO and self.linhas_desde_lobo >= 3 and protegida is None
                and random.random() < chance_lobo):
            opcoes = list(POSSIBILIDADE_LOBO)
            random.shuffle(opcoes)
            for faixa in opcoes:
                oposta = 2 - faixa
                if self._alcanca(self.livres_anteriores, {oposta}, alcance):
                    lead = 0.9 * vb          # nasce mais longe: dá tempo do aviso (uivo + alerta)
                    y_lobo = y + lead
                    self.objetos.append(Lobo(faixa, self.centros, y_lobo))
                    self.audio.tocar("uivo")
                    livres = {oposta}
                    y = y_lobo
                    virou_lobo = True
                    self.linhas_desde_lobo = 0
                    break

        #pinheiros / pedras / gelo
        if not virou_lobo:
            pesos = [lerp(a, b, p) for a, b in zip(PESOS_PINHEIROS_INICIO, PESOS_PINHEIROS_FIM)]
            pesos[1] *= self.adj["obstaculos"]       # dificuldade: mais/menos linhas com obstáculos
            pesos[2] *= self.adj["obstaculos"]
            n = random.choices((0, 1, 2), weights=pesos)[0]
            escolhidas = set(random.sample(range(NUM_FAIXAS), n))
            if protegida is not None:
                escolhidas.discard(protegida)
            # placa de gelo (liberada por pontuação): a faixa dela fica sem obstáculo
            if (self.pontuacao >= self._limiar("gelo") and self.linhas_desde_gelo >= LINHAS_ENTRE_GELOS
                    and random.random() < CHANCE_GELO_LINHA):
                faixa_gelo = random.choice(range(NUM_FAIXAS))
                escolhidas.discard(faixa_gelo)
            # nunca deixa a linha intransponível dado o tempo que o jogador tem para reagir
            while escolhidas and not self._alcanca(self.livres_anteriores, todas - escolhidas, alcance):
                escolhidas.discard(random.choice(tuple(escolhidas)))
            pedras_liberadas = self.pontuacao >= self._limiar("pedra")
            for f in escolhidas:
                if pedras_liberadas and random.random() < CHANCE_PEDRA:
                    self.objetos.append(Pedra(self.centros[f], y))
                else:
                    self.objetos.append(Arvore(self.centros[f], y))
            if faixa_gelo is not None:
                self.objetos.append(Gelo(self.centros[faixa_gelo], y))
                self.linhas_desde_gelo = 0
            livres = todas - escolhidas

        #consumível (no máximo um por linha, numa faixa livre)
        self._sortear_consumivel(y, livres)

        self.livres_anteriores = livres
        self.gelo_na_linha_anterior = faixa_gelo is not None
        self.y_ultima_linha = y
        gap_s_prox = random.uniform(lerp(GAP_INICIAL[0], GAP_FINAL[0], p), lerp(GAP_INICIAL[1], GAP_FINAL[1], p))
        gap_s_prox *= self.adj["intervalo_obstaculos"]
        self.gap_px_proximo = gap_s_prox * vb

    def _tipos_permitidos(self):
        #itens ja no inventario e power-ups ja em uso nao aparecem
        j = self.jogador
        bloqueados = set()
        if j.serra:
            bloqueados.add("saw")
        if j.carne:
            bloqueados.add("meat")
        if j.vida_extra:
            bloqueados.add("life")
        if self.t_mult > 0:
            bloqueados.add("multiplier")
        if self.t_reducao > 0:
            bloqueados.add("mud")
        if self.t_ima > 0 or self.pontuacao < self._limiar("ima"):
            bloqueados.add("ima")
        for o in self.objetos:
            if o.tipo == "item":
                bloqueados.add(o.subtipo)
        return [t for t in CHANCE_CONSUMIVEL_LINHA if t not in bloqueados]

    def _sortear_consumivel(self, y, livres):
        if not livres:
            return
        tipos = self._tipos_permitidos()
        random.shuffle(tipos)
        for tipo in tipos:
            if random.random() < CHANCE_CONSUMIVEL_LINHA[tipo] * self.adj["itens"]:
                faixa = random.choice(sorted(livres))
                valor, duracao = 0, 0
                if tipo == "multiplier":
                    valor = random.choices(MULTIPLICADORES, weights=PESOS_MULTIPLICADOR)[0]
                    duracao = random.choice(DURACOES_EFEITO)
                elif tipo == "mud":
                    valor = random.randint(REDUTOR_MIN, REDUTOR_MAX)
                    duracao = random.choice(DURACOES_EFEITO)
                elif tipo == "ima":
                    duracao = random.choice(IMA_DURACOES)
                self.objetos.append(Item(tipo, self.centros[faixa], y, valor, duracao))
                return

    #avalanche
    def _escolher_faixa_avalanche(self):
        #pelo menos uma faixa livre de obstaculos
        j = self.jogador
        livres = []
        for f in range(NUM_FAIXAS):
            ocupada = False
            for o in self.objetos:
                if o.cy < j.cy - 120:
                    continue
                if o.tipo in ("arvore", "pedra") and self._faixa_de(o.x) == f:
                    ocupada = True
                elif o.tipo == "lobo" and o.perigoso and f in (o.faixa, 1):
                    ocupada = True
            if not ocupada:
                livres.append(f)
        if not livres:
            return None
        diferentes = [f for f in livres if f != j.faixa_destino]
        if diferentes and random.random() < 0.7:
            return random.choice(diferentes)
        return random.choice(livres)

    def _evento_avalanche(self, ev):
        if ev == "aviso":
            self.audio.tocar("avalanche_alerta")
            self.fx.tremer(3, 1.8)
        elif ev == "desce":
            self.audio.tocar("avalanche_passa")
            self.fx.tremer(9, 0.8)

    #lobos (sinais)
    def _tratar_sinal_lobo(self, lobo):
        if lobo.sinal == "bote":
            self.audio.tocar("rosnado")
        elif lobo.sinal == "mastigar":
            self.audio.tocar("mastigar")
            self.particulas.brilho(lobo.x, lobo.cy - 10, (255, 120, 120), 8)
        lobo.sinal = None

    #colisões
    def _resolver_colisoes(self):
        j = self.jogador
        hb = j.hitbox()
        invulneravel = j.invulneravel > 0
        for o in self.objetos:
            if o.remover:
                continue
            if o.tipo == "item":
                if hb.colliderect(o.hitbox_varrida()):
                    self._coletar(o)
            elif o.tipo == "gelo":
                if hb.colliderect(o.hitbox()):
                    self._pisar_gelo()
            elif invulneravel:
                continue
            elif o.tipo == "arvore":
                hv = o.hitbox_varrida()
                if j.serra and j.alcance_serra().colliderect(hv):
                    self._cortar_arvore(o)
                elif hv.colliderect(hb):
                    self._iniciar_queda("arvore", o)
                    return
                else:
                    self._verificar_quase(o, hb, hv)
            elif o.tipo == "pedra":            # a serra NÃO corta pedra
                hv = o.hitbox_varrida()
                if hv.colliderect(hb):
                    self._iniciar_queda("pedra", o)
                    return
                self._verificar_quase(o, hb, hv)
            elif o.tipo == "lobo" and o.perigoso:
                hv = o.hitbox_varrida()
                if j.carne and j.alcance_carne().colliderect(hv):
                    self._usar_carne(o)
                elif hv.colliderect(hb):
                    self._iniciar_queda("lobo", o)
                    return
                else:
                    self._verificar_quase(o, hb, hv)
        if not invulneravel:
            for r in self.avalanche.rects_perigo():
                if hb.colliderect(r):
                    self._iniciar_queda("avalanche", None)
                    return

    #"QUASE!"
    def _verificar_quase(self, o, hb, hv):
        #verifica se a distancia player-obstaculo foi pequena o suficiente e se o player passou vivo do obstaculo
        if o.quase_pago:
            return
        if hv.bottom > hb.top and hv.top < hb.bottom:         # está passando pela altura do esquiador
            folga = max(hb.left - hv.right, hv.left - hb.right, 0)
            if folga < o.quase_gap:
                o.quase_gap = folga
        elif hv.bottom <= hb.top:                              # já passou
            o.quase_pago = True
            if o.quase_gap <= QUASE_DISTANCIA:
                self._dar_quase()

    def _dar_quase(self):
        j = self.jogador
        if self.t_combo_quase > 0:
            self.combo_quase = min(self.combo_quase + 1, QUASE_COMBO_MAXIMO)
        else:
            self.combo_quase = 1
        self.t_combo_quase = QUASE_TEMPO_COMBO
        pontos = QUASE_PONTOS * self.combo_quase
        self.pontuacao += pontos
        msg = f"QUASE!  +{pontos}" if self.combo_quase == 1 else f"QUASE! x{self.combo_quase}  +{pontos}"
        self.popups.append(Popup(msg, j.x, j.cy - 118, (120, 235, 255), 32, 1.0, 50))
        self.particulas.brilho(j.x, j.cy, (170, 240, 255), 10)
        self.audio.tocar("quase")

    #gelo
    def _pisar_gelo(self):
        j = self.jogador
        j.t_gelo = GELO_PERSISTENCIA
        if self.t_som_gelo <= 0:
            self.t_som_gelo = 1.6
            self.audio.tocar("gelo")
            self.popups.append(Popup("GELO!", j.x, j.cy - 112, (170, 225, 255), 32, 0.9, 40))
        if random.random() < 0.35:
            self.particulas.brilho(j.x, j.cy + 40, (205, 238, 255), 2)

    #ímã
    def _aplicar_ima(self, dt):
        j = self.jogador
        passo = IMA_VELOCIDADE * dt
        for o in self.objetos:
            if o.tipo == "item" and j.cy - 40 < o.cy < j.cy + IMA_ALCANCE_Y:
                dx = j.x - o.x
                if abs(dx) > 1.0:
                    o.x += math.copysign(min(abs(dx), passo), dx)
                    if random.random() < 9 * dt:
                        self.particulas.brilho(o.x, o.cy, (255, 120, 130), 1)

    def _desenhar_aura_ima(self, tela):
        j = self.jogador
        if self.t_ima <= 0 or (self.t_ima < 2.0 and int(self.relogio * 8) % 2 == 0):
            return
        fase = (self.relogio * 1.5) % 1.0
        for k in (0.0, 0.5):
            f = (fase + k) % 1.0
            raio = int(165 - 125 * f)                  # anéis que se fecham: "puxando" para o esquiador
            cor = mistura_cor((255, 100, 112), COR_NEVE_LATERAL, f * 0.75)
            pygame.draw.circle(tela, cor, (int(j.x), int(j.cy)), raio, 4)

    #novidades por pontuação
    NOVIDADES = {
        "pedra": "PEDRAS!  Serra não consegue cortar!",
        "ima": "ÍMÃ!  Atrai os itens!",
        "gelo": "GELO!  Troca de faixa mais lenta!",
    }

    def _checar_novidades(self):
        for chave, msg in self.NOVIDADES.items():
            if chave not in self.novidades_avisadas and self.pontuacao >= self._limiar(chave):
                self.novidades_avisadas.add(chave)
                abertos = sum(1 for pu in self.popups if getattr(pu, "novidade", False))   # empilha se coincidirem
                aviso = Popup(msg, LARGURA // 2, 140 + 44 * abertos, COR_DOURADO, 34, 3.2, 10)
                aviso.novidade = True
                self.popups.append(aviso)
                self.audio.tocar("blip")

    #consumíveis
    def _coletar(self, item):
        j = self.jogador
        tipo = item.subtipo
        item.remover = True
        rotulo = ROTULOS_ITENS[tipo]
        cor = COR_HALO[tipo]
        som = {"life": "vida", "multiplier": "multiplicador", "mud": "redutor", "ima": "ima"}.get(tipo, "coleta")
        self.audio.tocar(som)
        self.particulas.brilho(item.x, item.cy, cor, 14)
        self.popups.append(Popup(rotulo + "!", item.x, item.cy - 56, cor, 28, 1.1, 60))
        if tipo == "saw":
            j.serra = True
            destino = ("slot", "saw")
        elif tipo == "meat":
            j.carne = True
            destino = ("slot", "meat")
        elif tipo == "life":
            j.vida_extra = True
            destino = ("slot", "life")
        elif tipo == "multiplier":
            self.mult, self.t_mult = item.valor, float(item.duracao)
            self.dur_mult = float(item.duracao)
            destino = ("badge", "multiplier")
        elif tipo == "mud":
            self.reducao, self.t_reducao = item.valor, float(item.duracao)
            self.dur_reducao = float(item.duracao)
            destino = ("badge", "mud")
        else:  # ímã
            self.t_ima = self.dur_ima = float(item.duracao)
            destino = ("badge", "ima")
        icone = {"saw": self.hud.icones.get("saw"), "meat": self.hud.icones.get("meat"),
                 "life": self.hud.icones.get("life"), "multiplier": self.hud.icone_mult,
                 "mud": self.hud.icone_lama, "ima": self.hud.icone_ima}[tipo]
        self.voando.append({"surf": icone, "x0": item.x, "y0": item.cy, "destino": destino, "t": 0.0})

    def _atualizar_voando(self, dt):
        vivos = []
        for f in self.voando:
            f["t"] += dt / 0.5
            if f["t"] >= 1.0:
                if f["destino"][0] == "slot":
                    self.pulsos[f["destino"][1]] = 0.6
                continue
            vivos.append(f)
        self.voando = vivos

    def _desenhar_voando(self):
        for f in self.voando:
            if f["destino"][0] == "slot":
                alvo = self.hud.posicao_slot(f["destino"][1])
            else:
                alvo = self.hud.posicao_badge(f["destino"][1], self)
            e = suave_entrada_saida(f["t"])
            x = lerp(f["x0"], alvo[0], e)
            y = lerp(f["y0"], alvo[1], e) - math.sin(math.pi * e) * 80
            surf = f["surf"]
            self.tela.blit(surf, surf.get_rect(center=(int(x), int(y))))

    def _cortar_arvore(self, arvore):
        j = self.jogador
        j.serra = False
        j.acionar_serra()
        arvore.remover = True
        self.cortes.append(PinheiroCortado(arvore.sprite.image, arvore.x, arvore.cy))
        self.particulas.lascas(arvore.x, arvore.cy, 24)
        self.particulas.explosao_neve(arvore.x, arvore.cy - 20, 10, 200)
        self.fx.tremer(5, 0.25)
        self.audio.tocar("serra")
        self.audio.tocar("estalo")
        self.popups.append(Popup("SERRA!", j.x, j.cy - 112, COR_LARANJA, 36, 1.0, 50))

    def _usar_carne(self, lobo):
        j = self.jogador
        j.carne = False
        lado = lobo.lado
        j.acionar_carne(lado)
        lobo.mudar("desviado")
        self.projeteis.append(Projetil(superficie_escalada("meat", 0.62), j.mao(lado), lobo, 0.30, lobo.comer))
        self.audio.tocar("metal")
        self.fx.tremer(3, 0.15)
        self.popups.append(Popup("CARNE!", j.x, j.cy - 100, (255, 130, 130), 36, 1.0, 60))

    #queda / revive / fim
    def _iniciar_queda(self, causa, origem):
        j = self.jogador
        self.estado = "QUEDA"
        self.t_estado = 0.0
        self.causa_morte = causa
        self.reviver = j.vida_extra
        if self.reviver:
            j.vida_extra = False
            self.pulsos["life"] = 0.0
        j.tombar()
        self.hit_stop = 0.07
        self.audio.tocar("batida")
        self.fx.tremer(14, 0.5)
        self.fx.flash((255, 255, 255), 0.2, 150)
        self.particulas.explosao_neve(j.x, j.cy + 24, 24, 320)
        if causa == "lobo" and origem is not None:
            origem.mudar("atacando")
            self.lobo_atacante = origem
            self.nuvens.append(NuvemBriga(j.x, j.cy + 6, 86, (DURACAO_QUEDA_REVIVER if self.reviver else DURACAO_QUEDA) - 0.1))
            self.audio.tocar("rosnado")
        elif causa == "avalanche":
            self.nuvens.append(NuvemBriga(j.x, j.cy + 10, 120, 1.2))
        if self.reviver:
            self.popups.append(Popup("VIDA EXTRA!", j.x, j.cy - 110, (255, 120, 130), 40, 1.3, 70))

    def _reviver_jogador(self):
        j = self.jogador
        j.levantar()
        self.estado = "JOGANDO"
        self.t_estado = 0.0
        self.t_retomada = 1.3
        # limpa a zona logo abaixo do esquiador (com um "poof" de neve) para ele não cair de novo
        for o in self.objetos:
            if o.tipo in ("arvore", "pedra", "lobo") and j.cy - 170 < o.cy < j.cy + 520:
                if o.tipo == "lobo" and o.estado == "atacando":
                    o.mudar("saindo")
                    continue
                o.remover = True
                self.particulas.explosao_neve(o.x, o.cy, 10, 220)
        if self.lobo_atacante is not None:
            self.lobo_atacante.mudar("saindo")
            self.lobo_atacante = None
        self.audio.tocar("vida")
        self.fx.flash((255, 230, 230), 0.25, 110)
        self.popups.append(Popup("DE VOLTA!", j.x, j.cy - 100, COR_DOURADO, 38, 1.2, 60))

    def _fim_de_jogo(self):
        self.estado = "GAME_OVER"
        self.t_estado = 0.0
        pontos = int(self.pontuacao)
        self.novo_recorde = pontos > self.ranking.melhor()
        if self.novo_recorde:
            self.recorde = pontos
        self.posicao_ranking = -1
        self.iniciais = ""
        self.entrando_iniciais = self.ranking.qualifica(pontos)   # entra no top N? pede as iniciais
        self.audio.musica_parar(0.6)
        self.audio.vento_parar()
        if self.novo_recorde:
            self.audio.tocar("recorde")
        else:
            self.audio.tocar("vida" if self.entrando_iniciais else "fim")

    def _confirmar_iniciais(self):
        nome = self.iniciais or self.ultimas_iniciais or "AAA"
        self.posicao_ranking = self.ranking.inserir(nome, int(self.pontuacao))
        self.ultimas_iniciais = limpar_nome(nome)
        self.recorde = self.ranking.melhor()
        self.entrando_iniciais = False
        self.audio.tocar("blip")

    def _entrada_iniciais(self):
        #digitação das iniciais
        for i in range(26):
            if self.teclado.key_down(pygame.K_a + i) and len(self.iniciais) < 3:
                self.iniciais += chr(65 + i)
                self.audio.tocar("blip")
        if self.teclado.key_down(pygame.K_BACKSPACE) and self.iniciais:
            self.iniciais = self.iniciais[:-1]
        enter = self.teclado.key_down("ENTER")
        kp = getattr(pygame, "K_KP_ENTER", None)
        if kp is not None and self.teclado.key_down(kp):
            enter = True
        if enter:
            self._confirmar_iniciais()

    def _salvar_se_recorde(self):
        try:
            if self.entrando_iniciais:
                self.ranking.inserir(self.iniciais or self.ultimas_iniciais or "???", int(self.pontuacao))
            elif self.estado in ("JOGANDO", "QUEDA") and self.ranking.qualifica(int(self.pontuacao)):
                self.ranking.inserir(self.ultimas_iniciais or "???", int(self.pontuacao))
        except Exception:  # noqa: BLE001 - nunca impedir o jogo de fechar
            pass

    #game over
    def _atualizar_game_over(self, dt):
        self.t_estado += dt
        self.fator_mundo = 0.0
        self.jogador.atualizar(dt)
        self.particulas.atualizar(dt, 0.0)
        self.nuvens = [n for n in self.nuvens if not n.fim]
        for n in self.nuvens:
            n.atualizar(dt)
        for p in self.popups:
            p.atualizar(dt)
        self.popups = [p for p in self.popups if not p.fim]
        self.fx.atualizar(dt)
        if self.entrando_iniciais:
            if self.t_estado > 0.5:
                self._entrada_iniciais()
        elif self.t_estado > 0.9:
            if self.teclado.key_down("SPACE") or self.teclado.key_down("ENTER"):
                self.iniciar_partida()
            elif self.teclado.key_down("ESC"):
                self._voltar_ao_menu()

    #desenho da partida
    def _desenhar_alerta_lobos(self):
        for o in self.objetos:
            if o.tipo == "lobo" and o.estado == "espreita" and o.cy > ALTURA + 20:
                piscar = 0.55 + 0.45 * math.sin(self.relogio * 16)
                x0 = int(self.centros[o.faixa] - self.lw / 2) if o.faixa == 0 else int(self.centros[1] - self.lw / 2)
                self.surf_alerta.set_alpha(int(255 * piscar))
                self.tela.blit(self.surf_alerta, (x0, ALTURA - 150))
                cx = int(self.centros[o.faixa])
                pygame.draw.polygon(self.tela, (110, 18, 18), [(cx, ALTURA - 112), (cx - 32, ALTURA - 56), (cx + 32, ALTURA - 56)])
                pygame.draw.polygon(self.tela, (255, 206, 52), [(cx, ALTURA - 104), (cx - 25, ALTURA - 61), (cx + 25, ALTURA - 61)])
                texto.desenhar(self.tela, "!", cx, ALTURA - 100, 36, (110, 18, 18), "centro", None, 0)

    def _desenhar_partida(self):
        tela = self.tela
        j = self.jogador
        razao = self.velocidade_efetiva() / VELOCIDADE_INICIAL
        self.cenario.desenhar(tela, razao)
        for o in self.objetos:                       # gelo é terreno: fica por baixo de tudo
            if o.tipo == "gelo" and -140 < o.cy < ALTURA + 140:
                o.desenhar(tela, self.relogio)
        self.rastro.desenhar(tela)
        self._desenhar_alerta_lobos()

        for o in sorted(self.objetos, key=lambda ob: ob.cy):
            if o.cy > ALTURA + 140 or o.cy < -140 or o.tipo == "gelo":
                continue
            if o.tipo in ("arvore", "pedra"):
                o.desenhar(tela, self.sombras)
            elif o.tipo == "lobo":
                o.desenhar(tela, self.sombras, self.relogio)
            else:
                o.desenhar(tela, self.relogio)
        for c in self.cortes:
            c.desenhar(tela)
        for p in self.projeteis:
            p.desenhar(tela)

        self.sombras.desenhar(tela, j.x, j.cy + 48, 56, 16)
        self.particulas.desenhar(tela, False)        # poeira dos esquis fica atrás do esquiador
        self._desenhar_aura_ima(tela)
        j.desenhar(tela)
        if j.tombado and self.causa_morte in ("arvore", "pedra"):
            estrelinhas_tontura(tela, j.x, j.cy - 34, j.t_tombado)
        for n in self.nuvens:
            n.desenhar(tela)
        self.particulas.desenhar(tela, True)
        self.avalanche.desenhar(tela, self.relogio)
        self.nevasca.desenhar(tela)
        self.fx.aplicar_tremor(tela)
        for p in self.popups:
            p.desenhar(tela)
        self.fx.desenhar_flash(tela)
        self.hud.desenhar_jogo(tela, self)
        self._desenhar_voando()