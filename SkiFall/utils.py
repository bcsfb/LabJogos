import pygame

from config import FATOR_HITBOX


def clamp(valor, minimo, maximo):
    return max(minimo, min(valor, maximo))


def retangulo_hitbox(sprite):
    """Hitbox deliberadamente menor que o retângulo completo do sprite."""
    reducao_x = sprite.width * (1 - FATOR_HITBOX) / 2
    reducao_y = sprite.height * (1 - FATOR_HITBOX) / 2

    return pygame.Rect(
        int(sprite.x + reducao_x),
        int(sprite.y + reducao_y),
        max(1, int(sprite.width * FATOR_HITBOX)),
        max(1, int(sprite.height * FATOR_HITBOX)),
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
