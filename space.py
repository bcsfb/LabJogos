from PPlay.window import Window
from PPlay.keyboard import Keyboard
from PPlay.mouse import Mouse
from PPlay.sprite import Sprite
from PPlay.collision import Collision

janela = Window(800, 600)
janela.set_title("Space Invaders")

import space_menu

teclado = Keyboard()
mouse = Mouse()

dif = 1
estado_jogo = "MENU"

nave = Sprite("nave.png")
nave.x = janela.width / 2 - nave.width / 2
nave.y = janela.height - nave.height - 20
velocidade_nave = 350
lista_tiros = []
velocidade_tiro = 500
tempo_recarga = 0.2
cooldown_tiro = tempo_recarga

LINHAS_MONSTROS = 4
COLUNAS_MONSTROS = 6
VELOCIDADE_MONSTROS = 120
DESCIDA_MONSTROS = 20

direcao_monstros = 1
matriz_monstros = []

def criar_matriz_monstros():
    monstro_base = Sprite("monstro.png")

    espaco_x = monstro_base.width / 2
    espaco_y = monstro_base.height / 2
    passo_x = monstro_base.width + espaco_x
    passo_y = monstro_base.height + espaco_y

    largura_total = (monstro_base.width + (COLUNAS_MONSTROS - 1) * passo_x)

    x_inicial = (janela.width - largura_total) / 2
    y_inicial = 60

    matriz = []

    for linha in range(LINHAS_MONSTROS):
        linha_monstros = []
        for coluna in range(COLUNAS_MONSTROS):
            monstro = Sprite("monstro.png")

            monstro.x = x_inicial + coluna * passo_x
            monstro.y = y_inicial + linha * passo_y

            linha_monstros.append(monstro)
        matriz.append(linha_monstros)
    return matriz

def reiniciar_matriz_monstros():
    global matriz_monstros
    global direcao_monstros

    direcao_monstros = 1
    matriz_monstros = criar_matriz_monstros()

reiniciar_matriz_monstros()

def atualizar_monstros(dt):
    global direcao_monstros

    todos = [monstro for linha in matriz_monstros for monstro in linha]

    if not todos:
        return

    monstro_esquerda = min(todos, key=lambda monstro: monstro.x)
    monstro_direita = max(todos, key=lambda monstro: monstro.x + monstro.width)
    movimento_x = (VELOCIDADE_MONSTROS * direcao_monstros * dt)
    proxima_esquerda = (monstro_esquerda.x + movimento_x)
    proxima_direita = (monstro_direita.x + monstro_direita.width + movimento_x)

    vai_bater_esquerda = proxima_esquerda <= 0
    vai_bater_direita = proxima_direita >= janela.width

    if vai_bater_esquerda or vai_bater_direita:
        direcao_monstros *= -1

        for linha in matriz_monstros:
            for monstro in linha:
                monstro.y += DESCIDA_MONSTROS

        movimento_x = (VELOCIDADE_MONSTROS * direcao_monstros* dt)

    for linha in matriz_monstros:
        for monstro in linha:
            monstro.x += movimento_x

    todos = [monstro for linha in matriz_monstros for monstro in linha]

    if not todos:
        return

    menor_x = min(monstro.x for monstro in todos)
    maior_x = max(monstro.x + monstro.width for monstro in todos)

    if menor_x < 0:
        correcao = -menor_x
        for linha in matriz_monstros:
            for monstro in linha:
                monstro.x += correcao

    elif maior_x > janela.width:
        correcao = janela.width - maior_x
        for linha in matriz_monstros:
            for monstro in linha:
                monstro.x += correcao

def monstro_colidiu_com_nave():
    for linha in matriz_monstros:
        for monstro in linha:
            if Collision.collided(monstro, nave):
                return True

    return False

def monstro_mais_baixo_atingiu_jogador():
    todos = [monstro for linha in matriz_monstros for monstro in linha]

    if not todos:
        return False

    maior_y = max(monstro.y + monstro.height for monstro in todos)

    return maior_y >= nave.y

def processar_colisao_tiros():
    for tiro in lista_tiros[:]:
        tiro_atingiu_monstro = False

        for linha in matriz_monstros:
            for monstro in linha[:]:
                if tiro.collided(monstro):
                    linha.remove(monstro)
                    lista_tiros.remove(tiro)
                    tiro_atingiu_monstro = True
                    break

            if tiro_atingiu_monstro:
                break

def desenhar_monstros():
    for linha in matriz_monstros:
        for monstro in linha:
            monstro.draw()

def iniciar_jogo():
    global lista_tiros
    global cooldown_tiro
    global estado_jogo

    nave.x = janela.width / 2 - nave.width / 2
    nave.y = janela.height - nave.height - 20
    lista_tiros = []
    cooldown_tiro = tempo_recarga

    reiniciar_matriz_monstros()

    estado_jogo = "JOGO"

def atualizar_jogo(dt):
    global cooldown_tiro
    global tempo_recarga
    global estado_jogo

    if dif == 1:
        tempo_recarga = 0.2
    elif dif == 2:
        tempo_recarga = 0.3
    elif dif == 3:
        tempo_recarga = 0.4

    cooldown_tiro += dt

    if teclado.key_pressed("LEFT") and nave.x > 0:
        nave.x -= velocidade_nave * dt
    if teclado.key_pressed("RIGHT") and nave.x + nave.width < janela.width:
        nave.x += velocidade_nave * dt
    if nave.x < 0:
        nave.x = 0
    if nave.x + nave.width > janela.width:
        nave.x = janela.width - nave.width

    if (teclado.key_pressed("SPACE") and cooldown_tiro >= tempo_recarga):
        tiro = Sprite("tiro.png")
        tiro.x = (nave.x + nave.width / 2 - tiro.width / 2)
        tiro.y = nave.y - tiro.height
        lista_tiros.append(tiro)
        cooldown_tiro = 0

    for tiro in lista_tiros[:]:
        tiro.y -= velocidade_tiro * dt

        if tiro.y + tiro.height < 0:
            lista_tiros.remove(tiro)

    atualizar_monstros(dt)
    processar_colisao_tiros()

    if (monstro_colidiu_com_nave() or monstro_mais_baixo_atingiu_jogador()):
        estado_jogo = "GAME_OVER"

def desenhar_jogo():
    janela.set_background_color((0, 0, 75))
    desenhar_monstros()

    for tiro in lista_tiros:
        tiro.draw()

    nave.draw()
    janela.draw_text(f"FPS: {int(janela.get_fps())}", 10, 10, size=22, cor=(255, 255, 255))

while True:
    dt = janela.delta_time()

    if estado_jogo == "MENU": 
        novo_estado = space_menu.desenhar_menu (janela,mouse)
        if novo_estado == "JOGO":
            iniciar_jogo()
        else:
            estado_jogo = novo_estado

    elif estado_jogo == "JOGO":
        if teclado.key_pressed("ESC"):
            estado_jogo = "MENU"
        else:
            atualizar_jogo(dt)
            desenhar_jogo()

    elif estado_jogo == "DIFICULDADE":
        estado_jogo, dif = space_menu.desenhar_dificuldade (janela,teclado,mouse,dif)

    elif estado_jogo == "RANKING":

        janela.set_background_color((10, 10, 30))
        janela.draw_text("RANKING", 330, 200, size=40, cor=(255, 255, 255))
        janela.draw_text(f"FPS: {int(janela.get_fps())}", 10, 10, size=22, cor=(255, 255, 255))

        if teclado.key_pressed("ESC"):
            estado_jogo = "MENU"

    elif estado_jogo == "GAME_OVER":

        novo_estado = space_menu.desenhar_game_over (janela,teclado)
        if novo_estado == "JOGO":
            iniciar_jogo()
        else:
            estado_jogo = novo_estado

    elif estado_jogo == "SAIR":
        janela.close()

    janela.update()