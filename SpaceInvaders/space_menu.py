from PPlay.sprite import Sprite

iniciar = Sprite("play.png")
dificuldade = Sprite("dificuldade.png")
ranking = Sprite("ranking.png")
sair = Sprite("sair.png")

facil = Sprite("facil.png")
medio = Sprite("medio.png")
dificil = Sprite("dificil.png")

iniciar.x = 800 / 2 - iniciar.width / 2
iniciar.y = 150

dificuldade.x = 800 / 2 - dificuldade.width / 2
dificuldade.y = 230

ranking.x = 800 / 2 - ranking.width / 2
ranking.y = 310

sair.x = 800 / 2 - sair.width / 2
sair.y = 390

facil.x = 800 / 2 - facil.width / 2
facil.y = 200

medio.x = 800 / 2 - medio.width / 2
medio.y = 280

dificil.x = 800 / 2 - dificil.width / 2
dificil.y = 360


def desenhar_menu(janela, mouse):
    janela.set_background_color((0, 0, 75))

    iniciar.draw()
    dificuldade.draw()
    ranking.draw()
    sair.draw()

    janela.draw_text(f"FPS: {int(janela.get_fps())}", 10, 10, size=22, cor=(255, 255, 255))

    if mouse.is_over_object(iniciar) and mouse.is_button_pressed(1):
        return "JOGO"
    if mouse.is_over_object(dificuldade) and mouse.is_button_pressed(1):
        return "DIFICULDADE"
    if mouse.is_over_object(ranking) and mouse.is_button_pressed(1):
        return "RANKING"
    if mouse.is_over_object(sair) and mouse.is_button_pressed(1):
        return "SAIR"
    return "MENU"


def desenhar_dificuldade(janela, teclado, mouse, dif):
    janela.set_background_color((20, 20, 50))

    janela.draw_text("TELA DE DIFICULDADE", 240, 100, size=32, cor=(255, 255, 255))

    facil.draw()
    medio.draw()
    dificil.draw()

    janela.draw_text(f"FPS: {int(janela.get_fps())}", 10, 10, size=22, cor=(255, 255, 255))

    if mouse.is_over_object(facil) and mouse.is_button_pressed(1):
        dif = 1

    if mouse.is_over_object(medio) and mouse.is_button_pressed(1):
        dif = 2
        
    if mouse.is_over_object(dificil) and mouse.is_button_pressed(1):
        dif = 3

    if teclado.key_pressed("ESC"):
        return "MENU", dif

    return "DIFICULDADE", dif


def desenhar_game_over(janela, teclado):
    janela.set_background_color((20, 0, 0))

    janela.draw_text("GAME OVER", 300, 200, size=48, cor=(255, 255, 255))

    janela.draw_text("Os monstros chegaram ate a nave!", 220, 270, size=24, cor=(255, 255, 255))

    janela.draw_text("ENTER para jogar novamente", 235, 340, size=28, cor=(255, 255, 255))

    janela.draw_text("ESC para voltar ao menu", 255, 390, size=24, cor=(255, 255, 255))

    janela.draw_text(f"FPS: {int(janela.get_fps())}", 10, 10, size=22, cor=(255, 255, 255))

    if teclado.key_pressed("ENTER"):
        return "JOGO"

    if teclado.key_pressed("ESC"):
        return "MENU"

    return "GAME_OVER"
