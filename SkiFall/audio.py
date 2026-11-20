
#audios do SkiFall.

#efeitos sonoros: classe Sound do PPlay.

import pygame
from PPlay.sound import Sound, SoundManager

from config import PASTA_SONS, VELOCIDADE_INICIAL, VELOCIDADE_MAXIMA_MULTIPLICADOR

EFEITOS = (
    "uivo", "metal", "serra", "estalo", "batida", "coleta", "vida", "multiplicador",
    "redutor", "mastigar", "rosnado", "troca_faixa", "inicio", "fim", "recorde", "blip",
    "avalanche_alerta", "avalanche_passa", "quase", "ima", "gelo",
)
NUM_ANDAMENTOS = 4
NUM_SEGMENTOS = 4
VOLUME_MUSICA = 0.55

class Audio:
    def __init__(self):
        self.ativo = False
        self.mudo = False
        self.sfx = {}
        self.musica = []          # musica[andamento][segmento] -> pygame.mixer.Sound
        self.tocando = False
        self.seg_na_fila = 1
        self.andamento_atual = 0
        self.volume_musica = VOLUME_MUSICA
        self.fade = None          # (tempo_restante, duracao) durante o fade-out
        self.vento = None
        self.canal_musica = None
        self.canal_vento = None
        try:
            SoundManager.inicializar()
            if not pygame.mixer.get_init():
                raise RuntimeError("mixer não inicializado")
            pygame.mixer.set_num_channels(24)
            pygame.mixer.set_reserved(2)       # canal 0 = música, canal 1 = vento da nevasca
            self.canal_musica = pygame.mixer.Channel(0)
            self.canal_vento = pygame.mixer.Channel(1)
            self._carregar()
            self.ativo = True
        except Exception as erro:  
            print(f"[SkiFall] Áudio desativado: {erro}")

    #carga
    def _carregar(self):
        for nome in EFEITOS:
            self.sfx[nome] = Sound(str(PASTA_SONS / f"{nome}.wav"))
        for a in range(NUM_ANDAMENTOS):
            segmentos = []
            for s in range(NUM_SEGMENTOS):
                caminho = PASTA_SONS / "musica" / f"t{a}_s{s}.wav"
                segmentos.append(pygame.mixer.Sound(str(caminho)))
            self.musica.append(segmentos)
        self.vento = pygame.mixer.Sound(str(PASTA_SONS / "nevasca.wav"))

    #efeitos
    def tocar(self, nome):
        if not self.ativo or self.mudo:
            return
        som = self.sfx.get(nome)
        if som is not None:
            try:
                som.play()
            except Exception:  # noqa: BLE001
                pass

    #música
    @staticmethod
    def andamento_para_velocidade(velocidade):

        razao = velocidade / VELOCIDADE_INICIAL
        alcance = VELOCIDADE_MAXIMA_MULTIPLICADOR - 1.0
        progresso = (razao - 1.0) / alcance if alcance > 0 else 0.0
        if progresso < 0.18:
            return 0
        if progresso < 0.42:
            return 1
        if progresso < 0.70:
            return 2
        return 3

    @staticmethod
    def andamento_para_progresso(progresso):

        if progresso < 0.18:
            return 0
        if progresso < 0.42:
            return 1
        if progresso < 0.70:
            return 2
        return 3

    def musica_iniciar(self, andamento=0, volume=VOLUME_MUSICA):
        if not self.ativo:
            return
        self.volume_musica = volume
        self.fade = None
        self.andamento_atual = andamento
        self.canal_musica.stop()
        self.canal_musica.set_volume(0.0 if self.mudo else volume)
        self.canal_musica.play(self.musica[andamento][0])
        self.canal_musica.queue(self.musica[andamento][1])
        self.seg_na_fila = 1
        self.tocando = True

    def musica_atualizar(self, dt, andamento_desejado):

        if not self.ativo or not self.tocando:
            return
        if self.fade is not None:
            restante, total = self.fade
            restante -= dt
            if restante <= 0:
                self.canal_musica.stop()      # stop() também limpa a fila
                self.tocando = False
                self.fade = None
                return
            self.fade = (restante, total)
            if not self.mudo:
                self.canal_musica.set_volume(self.volume_musica * restante / total)
            return
        if self.canal_musica.get_queue() is None:
            # o segmento que estava na fila começou a tocar -> enfileira o seguinte
            self.seg_na_fila = (self.seg_na_fila + 1) % NUM_SEGMENTOS
            self.andamento_atual = andamento_desejado
            self.canal_musica.queue(self.musica[self.andamento_atual][self.seg_na_fila])

    def musica_parar(self, fade_s=0.7):
        if self.ativo and self.tocando:
            self.fade = (fade_s, fade_s)

    def musica_pausar(self, pausar):
        if not self.ativo:
            return
        if pausar:
            self.canal_musica.pause()
            self.canal_vento.pause()
        else:
            self.canal_musica.unpause()
            self.canal_vento.unpause()

    #vento da nevasca
    def vento_atualizar(self, intensidade):
        if not self.ativo:
            return
        if intensidade > 0.02 and not self.canal_vento.get_busy():
            self.canal_vento.play(self.vento, loops=-1)
        if intensidade <= 0.02:
            if self.canal_vento.get_busy():
                self.canal_vento.stop()
            return
        self.canal_vento.set_volume(0.0 if self.mudo else min(1.0, intensidade))

    def vento_parar(self):
        if self.ativo:
            self.canal_vento.stop()

    #mudo
    def alternar_mudo(self):
        self.mudo = not self.mudo
        if not self.ativo:
            return
        SoundManager.set_sfx_volume(0 if self.mudo else 100)
        if self.canal_musica is not None:
            self.canal_musica.set_volume(0.0 if self.mudo else self.volume_musica)
        if self.mudo and self.canal_vento is not None:
            self.canal_vento.set_volume(0.0)
