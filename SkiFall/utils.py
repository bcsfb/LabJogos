#matemáticas, hitbox e recorde).
import pygame

def clamp(valor, minimo, maximo):
    return max(minimo, min(valor, maximo))

def lerp(a, b, t):
    return a + (b - a) * t

def suave_saida(t):
    #suaviza a troca de faixa
    t = clamp(t, 0.0, 1.0)
    return 1.0 - (1.0 - t) ** 2.6

def suave_entrada_saida(t):
    t = clamp(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)

def mistura_cor(c1, c2, t):
    t = clamp(t, 0.0, 1.0)
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

def hitbox_centrada(cx, cy, largura, altura):
    #retangulos de colisao
    return pygame.Rect(
        int(cx - largura / 2), int(cy - altura / 2), max(1, int(largura)), max(1, int(altura))
    )

def ler_recorde(caminho):
    try:
        return max(0, int(caminho.read_text(encoding="utf-8").strip()))
    except (FileNotFoundError, ValueError, OSError):
        return 0

def salvar_recorde(caminho, recorde):
    try:
        caminho.write_text(str(int(recorde)), encoding="utf-8")
    except OSError:
        pass