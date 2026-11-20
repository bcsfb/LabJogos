#SkiFall - configurações e calibragem.

#tudo que costuma ser ajustado durante o balanceamento do jogo está aqui.

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PASTA_IMAGENS = BASE_DIR / "imagens"
PASTA_SONS = BASE_DIR / "sons"
ARQUIVO_RECORDE = BASE_DIR / "recorde.txt"      # formato antigo (só é lido para migrar)
# um ranking por dificuldade
ARQUIVOS_RANKING = {
    "FACIL": BASE_DIR / "ranking_facil.txt",
    "NORMAL": BASE_DIR / "ranking.txt",
    "DIFICIL": BASE_DIR / "ranking_dificil.txt",
}
ARQUIVO_RANKING = ARQUIVOS_RANKING["NORMAL"]
ARQUIVO_OPCOES = BASE_DIR / "opcoes.txt"          # guarda a última dificuldade escolhida
ARQUIVO_CREDITOS = BASE_DIR / "creditos.txt"      # EDITE este arquivo para mudar os créditos

# ----------------------------------------------------------------------------- janela
LARGURA = 1536
ALTURA = 864
TITULO_JANELA = "SkiFall"
FPS_ALVO = 120          # limite de quadros/s (o PPlay não limita sozinho)
DT_MAX = 0.05           # maior passo de simulação aceito (evita "teleporte" após travadas)

# ----------------------------------------------------------------------------- pista
NUM_FAIXAS = 3
LARGURA_PISTA = 780
JOGADOR_CY = ALTURA * 0.25       # o esquiador fica SEMPRE neste y; o mundo é que se move
Y_NASCIMENTO = ALTURA + 150      # objetos nascem abaixo da tela

# ----------------------------------------------------------------------------- velocidade
VELOCIDADE_INICIAL = 300.0
# Teto de velocidade 
VELOCIDADE_MAXIMA_MULTIPLICADOR = 7.5
TEMPO_ATE_VELOCIDADE_MAXIMA = 240.0   # segundos até chegar no teto
PONTOS_POR_SEGUNDO = 10.0

# ----------------------------------------------------------------------------- esquiador
DURACAO_TROCA_FAIXA = 0.16   # segundos para ir de uma faixa à vizinha
TEMPO_REACAO = 0.20          # reação humana considerada na geração "justa" de obstáculos
TEMPO_INVULNERAVEL = 2.2     # depois de usar a vida extra
TEMPO_POSE_SERRA = 0.55
TEMPO_POSE_CARNE = 0.50

# Hitboxes (largura, altura) em pixels - menores que o sprite, para colisões "justas"
HITBOX_JOGADOR = (44, 84)
HITBOX_PINHEIRO = (58, 88)
HITBOX_LOBO = (104, 50)
FATOR_HITBOX_ITEM = 1.0
ALCANCE_SERRA = 35           # px abaixo do esquiador em que a serra já alcança o pinheiro
ALCANCE_CARNE = (46, 40)     # px extras (horizontal, vertical) para o lobo ser "distraído"

# ----------------------------------------------------------------------------- geração
# intervalo entre "linhas" de obstáculos, EM SEGUNDOS (vai do inicial ao final conforme a
# velocidade sobe). Em tempo, e não em pixels, para o jogo continuar justo em alta velocidade.
GAP_INICIAL = (1.0, 1.5)
GAP_FINAL = (0.55, 0.85)

# quantidade de pinheiros por linha (0, 1 ou 2): pesos no início e no fim da curva
PESOS_PINHEIROS_INICIO = (0.26, 0.56, 0.18)
PESOS_PINHEIROS_FIM = (0.08, 0.45, 0.47)

CHANCE_LOBO_INICIO = 0.21
CHANCE_LOBO_FIM = 0.36
TEMPO_PRIMEIRO_LOBO = 15.0
POSSIBILIDADE_LOBO = (0, 2)      # lobos só aparecem nas faixas laterais

# chance, POR LINHA gerada, de aparecer cada consumível (vida extra é a mais rara).
CHANCE_CONSUMIVEL_LINHA = {
    "life": 0.015,
    "saw": 0.05,
    "meat": 0.035,
    "multiplier": 0.063,
    "mud": 0.063,       # "redutor de velocidade"
    "ima": 0.030,       # só aparece depois de PONTUACAO_MINIMA["ima"]
}

# multiplicador de pontos: quanto maior, mais raro (números ainda não definidos no GDD)
MULTIPLICADORES = (2, 3, 5, 8)
PESOS_MULTIPLICADOR = (5, 2, 3, 1)
DURACOES_EFEITO = (5, 8, 10, 12, 15, 20)

# redutor de velocidade (retarda a aproximação dos obstáculos)
REDUTOR_MIN = 10
REDUTOR_MAX = 50
VELOCIDADE_MINIMA_COM_LAMA = 0.25   # fração da velocidade inicial: piso do redutor

# ----------------------------------------------------------------------------- lobo
LOBO_TEMPO_BOTE = 0.55       # quando faltar este tempo para alcançar o esquiador, o lobo salta
LOBO_VEL_BOTE = 1500.0       # px/s do salto lateral (atravessa uma faixa em ~0,17 s)
LOBO_TEMPO_COMENDO = 1.9
LOBO_PELAGENS = ("cinza", "marrom", "branco", "negro")

# ----------------------------------------------------------------------------- eventos de clima
NEVASCA_ATIVA = True          
NEVASCA_PRIMEIRA = 35.0       # s de corrida até a 1ª nevasca
NEVASCA_INTERVALO = (28.0, 48.0)
NEVASCA_DURACAO = (8.0, 13.0)

AVALANCHE_ATIVA = True        
AVALANCHE_PRIMEIRA = 55.0
AVALANCHE_INTERVALO = (32.0, 52.0)
AVALANCHE_AVISO = 2.1         # segundos de aviso (rugido + alerta) antes de descer
AVALANCHE_VELOCIDADE = 1650.0

#pontuação mínima para cada novidade começar a aparecer
PONTUACAO_MINIMA = {
    "pedra": 2000,
    "ima": 1250,
    "gelo": 2750,
}

#"QUASE!"
QUASE_DISTANCIA = 150        # px: folga lateral máxima entre o esquiador e o obstáculo para valer (100 = bem rente)
QUASE_PONTOS = 50            # pontos do 1º "quase"; combos seguidos valem 2x, 3x ... (até o máximo)
QUASE_COMBO_MAXIMO = 10
QUASE_TEMPO_COMBO = 6.0      # s sem outro "quase" para o combo zerar

#pedra
CHANCE_PEDRA = 0.35          # chance de um "pinheiro sorteado" virar pedra (depois de liberada)
HITBOX_PEDRA_FATOR = (0.74, 0.62)

NEVASCA_BONUS_PONTOS = 1.5  

#imã
IMA_DURACOES = (6, 8, 10)    # segundos (sorteado ao nascer)
IMA_ALCANCE_Y = 640          # px à frente do esquiador em que os itens já são atraídos
IMA_VELOCIDADE = 1100.0      # px/s de atração lateral

#gelo escorregadio
CHANCE_GELO_LINHA = 0.18     # chance por linha (depois de liberado)
LINHAS_ENTRE_GELOS = 4
GELO_FATOR_TROCA = 1.9       # a troca de faixa leva 1,9x mais tempo sobre o gelo
GELO_PERSISTENCIA = 0.30     # s que o "escorrega" continua depois de sair do gelo
HITBOX_GELO_FATOR = (0.78, 0.66)

#ranking
TAMANHO_RANKING = 5
PONTUACAO_MINIMA_RANKING = 1000


#DIFICULDADE
DIFICULDADES = ("FACIL", "NORMAL", "DIFICIL")   
DIFICULDADE_PADRAO = "NORMAL"
DIFICULDADE_NOMES = {"FACIL": "FÁCIL", "NORMAL": "NORMAL", "DIFICIL": "DIFÍCIL"}
DIFICULDADE_CORES = {"FACIL": (120, 230, 140), "NORMAL": (255, 214, 80), "DIFICIL": (255, 100, 90)}

DIFICULDADE_AJUSTES = {
    "FACIL": dict(
        velocidade_inicial=0.90,    # x VELOCIDADE_INICIAL
        velocidade_maxima=0.90,     # x VELOCIDADE_MAXIMA_MULTIPLICADOR (o teto)
        tempo_ate_maximo=1.15,      # x TEMPO_ATE_VELOCIDADE_MAXIMA (>1 = acelera mais devagar)
        intervalo_obstaculos=1.1,   # x espaço (em segundos) entre linhas de obstáculos
        obstaculos=0.75,            # x chance de a linha ter 1 ou 2 obstáculos
        lobos=0.75,                 # x chance de lobo
        itens=1.25,                 # x chance de consumíveis
        novidades=1.25,             # x PONTUACAO_MINIMA (pedra/ímã/gelo aparecem mais tarde)
        vida_extra_inicial=1,       # 1 = começa a partida com uma vida extra
    ),
    "NORMAL": dict(
        velocidade_inicial=1.0, velocidade_maxima=1.0, tempo_ate_maximo=1.0, intervalo_obstaculos=1.0,
        obstaculos=1.0, lobos=1.0, itens=1.0, novidades=1.0, vida_extra_inicial=0,
    ),
    "DIFICIL": dict(
        velocidade_inicial=1.10,
        velocidade_maxima=1.10,
        tempo_ate_maximo=0.85,
        intervalo_obstaculos=0.90,
        obstaculos=1.25,
        lobos=1.25,
        itens=0.75,
        novidades=0.75,
        vida_extra_inicial=0,
    ),
}

#texto painel de descrição
DIFICULDADE_DESCRICAO = {
    "FACIL": ["Começa com 1 vida extra", "Obstáculos mais lentos e espaçados", "Menos lobos, mais itens",
              "Pedras, ímã e gelo demoram mais"],
    "NORMAL": ["A experiência padrão do jogo", "Velocidade e obstáculos equilibrados", "Itens e novidades como definidos",
               "em config.py"],
    "DIFICIL": ["Mais rápido e acelera depressa", "Obstáculos mais próximos e frequentes", "Mais lobos, menos itens",
                "Pedras, ímã e gelo chegam cedo"],
}

#teclas
TECLAS_ESQUERDA = ("A", "LEFT")
TECLAS_DIREITA = ("D", "RIGHT")
TECLAS_PAUSA = ("P", "ESC")
TECLA_MUDO = "M"

#cores
COR_NEVE_LATERAL = (232, 241, 252)
COR_PISTA = (246, 250, 255)
COR_PISTA_SOMBRA = (214, 228, 246)
COR_LINHA_FAIXA = (165, 197, 236)
COR_BORDA_PISTA = (122, 165, 220)
COR_BRANCO = (255, 255, 255)
COR_DOURADO = (255, 210, 60)
COR_VERMELHO = (232, 64, 64)
COR_LARANJA = (255, 150, 50)
COR_MARROM_LAMA = (170, 122, 80)
COR_AZUL_ESCURO = (12, 24, 52)
COR_PAINEL = (14, 30, 62)
COR_TEXTO_SUAVE = (186, 208, 238)

#arquivos
ARQUIVOS_ITENS = {
    "saw": "saw",
    "meat": "meat",
    "life": "life",
    "multiplier": "multiplier",
    "mud": "mud",
    "ima": "ima",
}
ROTULOS_ITENS = {
    "saw": "SERRA",
    "meat": "CARNE",
    "life": "VIDA EXTRA",
    "multiplier": "MULTIPLICADOR",
    "mud": "REDUTOR",
    "ima": "ÍMÃ",
}
