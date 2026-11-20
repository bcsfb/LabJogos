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

    janela.draw_text(f"FPS: {int(janela.get_fps())}",10, 10, size=22, cor=(255, 255, 255))

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
    janela.draw_text("TELA DE DIFICULDADE",240, 100, size=32, cor=(255, 255, 255))

    facil.draw()
    medio.draw()
    dificil.draw()

    janela.draw_text(f"FPS: {int(janela.get_fps())}",10, 10, size=22, cor=(255, 255, 255))

    if mouse.is_over_object(facil) and mouse.is_button_pressed(1):
        dif = 1
    if mouse.is_over_object(medio) and mouse.is_button_pressed(1):
        dif = 2
    if mouse.is_over_object(dificil) and mouse.is_button_pressed(1):
        dif = 3

    if teclado.key_pressed("ESC"):
        return "MENU", dif

    return "DIFICULDADE", dif

def desenhar_ranking(janela, teclado, ranking_lista):
    janela.set_background_color((10, 10, 30))

    janela.draw_text("RANKING - MELHORES 5",220, 65, size=34, cor=(255, 255, 255))

    janela.draw_text("POS.", 105, 150, size=22, cor=(255, 220, 100))
    janela.draw_text("NOME", 190, 150, size=22, cor=(255, 220, 100))
    janela.draw_text("PONTOS", 430, 150, size=22, cor=(255, 220, 100))
    janela.draw_text("DATA", 555, 150, size=22, cor=(255, 220, 100))

    melhores = sorted(ranking_lista,key=lambda item: int(item.get("pontos", 0)),reverse=True)[:5]

    if not melhores:
        janela.draw_text("Ainda nao ha partidas registradas.",190, 230, size=22, cor=(220, 220, 220))
    else:
        for indice, resultado in enumerate(melhores):
            y = 200 + indice * 55
            nome = str(resultado.get("nome", "Jogador"))[:18]
            pontos = int(resultado.get("pontos", 0))
            data = str(resultado.get("data", "-"))

            janela.draw_text(str(indice + 1), 115, y,size=22, cor=(255, 255, 255))
            janela.draw_text(nome, 190, y,size=22, cor=(255, 255, 255))
            janela.draw_text(str(pontos), 445, y,size=22, cor=(255, 255, 255))
            janela.draw_text(data, 555, y,size=18, cor=(255, 255, 255))

    janela.draw_text("ESC para voltar ao menu",275, 530, size=22, cor=(220, 220, 220))
    janela.draw_text(f"FPS: {int(janela.get_fps())}",10, 10, size=22, cor=(255, 255, 255))

    if teclado.key_pressed("ESC"):
        return "MENU"

    return "RANKING"


def desenhar_game_over(janela, teclado, pontos=0):
    janela.set_background_color((20, 0, 0))

    janela.draw_text("GAME OVER",300, 170, size=48, cor=(255, 255, 255))
    janela.draw_text("Os monstros chegaram ate a nave!",220, 240, size=24, cor=(255, 255, 255))
    janela.draw_text(f"Pontuacao final: {pontos}",285, 295, size=26, cor=(255, 220, 100))
    janela.draw_text("ENTER para jogar novamente",235, 360, size=28, cor=(255, 255, 255))
    janela.draw_text("ESC para voltar ao menu",255, 410, size=24, cor=(255, 255, 255))
    janela.draw_text(f"FPS: {int(janela.get_fps())}",10, 10, size=22, cor=(255, 255, 255))

    if teclado.key_pressed("ENTER"):
        return "JOGO"
    if teclado.key_pressed("ESC"):
        return "MENU"

    return "GAME_OVER"