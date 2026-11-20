from PPlay.window import Window
from PPlay.keyboard import Keyboard
from PPlay.mouse import Mouse
import json
import os
from datetime import datetime
from space_jogo import SpaceInvaders

ARQUIVO_RANKING = os.path.join(os.path.dirname(os.path.abspath(__file__)),"ranking.json")

def carregar_ranking():
    try:
        with open(ARQUIVO_RANKING, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if isinstance(dados, list):
            return [item for item in dados if isinstance(item, dict)
                and "nome" in item and "pontos" in item and "data" in item]
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return []

def salvar_resultado(nome, pontos):
    nome = nome.strip() or "Jogador"

    ranking = carregar_ranking()
    ranking.append({"nome": nome[:30], "pontos": int(pontos), "data": datetime.now().strftime("%d/%m/%Y %H:%M")})

    ranking.sort(key=lambda item: item["pontos"], reverse=True)

    arquivo_temporario = ARQUIVO_RANKING + ".tmp"
    with open(arquivo_temporario, "w", encoding="utf-8") as arquivo:
        json.dump(ranking, arquivo, ensure_ascii=False, indent=4)

    os.replace(arquivo_temporario, ARQUIVO_RANKING)

janela = Window(800, 600)
import space_menu
janela.set_title("Space Invaders")

teclado = Keyboard()
mouse = Mouse()
dif = 1
estado_jogo = "MENU"
jogo = SpaceInvaders(janela, teclado)
resultado_registrado = False

while True:
    dt = janela.delta_time()

    if estado_jogo == "MENU":
        novo_estado = space_menu.desenhar_menu(janela, mouse)

        if novo_estado == "JOGO":
            jogo.iniciar_jogo()
            resultado_registrado = False
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

                if not resultado_registrado:
                    print("\n========== FIM DE JOGO ==========")
                    print(f"Pontuação: {jogo.pontos}")
                    try:
                        nome = input("Digite seu nome para salvar no ranking: ")
                    except (EOFError, KeyboardInterrupt):
                        nome = "Jogador"

                    salvar_resultado(nome, jogo.pontos)
                    resultado_registrado = True
            else:
                jogo.desenhar()

    elif estado_jogo == "DIFICULDADE":
        estado_jogo, dif = space_menu.desenhar_dificuldade(janela, teclado, mouse, dif)
    elif estado_jogo == "RANKING":
        ranking_atual = carregar_ranking()
        estado_jogo = space_menu.desenhar_ranking(janela, teclado, ranking_atual)
    elif estado_jogo == "GAME_OVER":
        novo_estado = space_menu.desenhar_game_over(janela, teclado, jogo.pontos)

        if novo_estado == "JOGO":
            jogo.iniciar_jogo()
            resultado_registrado = False
            estado_jogo = "JOGO"
        else:
            estado_jogo = novo_estado

    elif estado_jogo == "SAIR":
        janela.close()
        break

    janela.update()