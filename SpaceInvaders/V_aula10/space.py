from PPlay.window import Window
from PPlay.keyboard import Keyboard
from PPlay.mouse import Mouse

janela = Window(800, 600)
janela.set_title("Space Invaders")

import space_menu
from space_jogo import SpaceInvaders

teclado = Keyboard()
mouse = Mouse()

dif = 1
estado_jogo = "MENU"

jogo = SpaceInvaders(janela, teclado)

while True:
    dt = janela.delta_time()

    if estado_jogo == "MENU":
        novo_estado = space_menu.desenhar_menu(janela, mouse)

        if novo_estado == "JOGO":
            jogo.iniciar_jogo()
            estado_jogo = "JOGO"
        else:
            estado_jogo = novo_estado

    elif estado_jogo == "JOGO":
        if teclado.key_pressed("ESC"):
            estado_jogo = "MENU"
            jogo.parar_jogo()
        else:
            jogo.atualizar(dt, dif)

            if jogo.game_over:
                estado_jogo = "GAME_OVER"
            else:
                jogo.desenhar()

    elif estado_jogo == "DIFICULDADE":
        estado_jogo, dif = space_menu.desenhar_dificuldade(janela, teclado, mouse, dif)

    elif estado_jogo == "RANKING":
        janela.set_background_color((10, 10, 30))
        janela.draw_text("RANKING", 330, 200, size=40, cor=(255, 255, 255))
        janela.draw_text(f"FPS: {int(janela.get_fps())}", 10, 10, size=22, cor=(255, 255, 255))

        if teclado.key_pressed("ESC"):
            estado_jogo = "MENU"

    elif estado_jogo == "GAME_OVER":
        novo_estado = space_menu.desenhar_game_over(janela, teclado)

        if novo_estado == "JOGO":
            jogo.iniciar_jogo()
            estado_jogo = "JOGO"
        else:
            estado_jogo = novo_estado

    elif estado_jogo == "SAIR":
        janela.close()

    janela.update()
