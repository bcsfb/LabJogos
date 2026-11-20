#para evitar os travamentos com o draw_text do PPlay que cria uma fonte nova a cada chamada 
#aqui as fontes são criadas uma única vez e cada texto é renderizado uma vez e memorizado.

import pygame

_NOMES_TEXTO = "arial,verdana,dejavusans,freesans"
_NOMES_TITULO = "arialblack,impact,arial,dejavusans,freesans"

_fontes = {}
_cache = {}
_TAMANHO_MAX_CACHE = 700

def fonte(tamanho, titulo=False):
    chave = (tamanho, titulo)
    if chave not in _fontes:
        try:
            if titulo:
                f = pygame.font.SysFont(_NOMES_TITULO, tamanho)
            else:
                f = pygame.font.SysFont(_NOMES_TEXTO, tamanho, bold=True)
        except Exception:
            f = pygame.font.Font(None, int(tamanho * 1.25))
        _fontes[chave] = f
    return _fontes[chave]

def preaquecer(tamanhos, titulo_tamanhos=()):
#cria as fontes antes do jogo começar
    for t in tamanhos:
        fonte(t)
    for t in titulo_tamanhos:
        fonte(t, True)


def _montar(texto, tamanho, cor, contorno, borda, titulo):
    f = fonte(tamanho, titulo)
    base = f.render(texto, True, cor)
    if borda <= 0 or contorno is None:
        return base
    w, h = base.get_size()
    s = pygame.Surface((w + 2 * borda, h + 2 * borda), pygame.SRCALPHA)
    traco = f.render(texto, True, contorno)
    for dx in range(-borda, borda + 1):
        for dy in range(-borda, borda + 1):
            if dx == 0 and dy == 0:
                continue
            if dx * dx + dy * dy <= borda * borda + 1:
                s.blit(traco, (borda + dx, borda + dy))
    s.blit(base, (borda, borda))
    return s


def renderizar(texto, tamanho, cor=(255, 255, 255), contorno=(12, 24, 52), borda=2, titulo=False):
    chave = (texto, tamanho, cor, contorno, borda, titulo)
    surf = _cache.get(chave)
    if surf is None:
        if len(_cache) > _TAMANHO_MAX_CACHE:
            _cache.clear()
        surf = _montar(texto, tamanho, cor, contorno, borda, titulo)
        _cache[chave] = surf
    return surf


def desenhar(tela, texto, x, y, tamanho=28, cor=(255, 255, 255), ancora="esq",
             contorno=(12, 24, 52), borda=2, titulo=False, alpha=255):
#desenha o texto
    surf = renderizar(str(texto), tamanho, cor, contorno, borda, titulo)
    w, h = surf.get_size()
    if ancora == "centro":
        x -= w // 2
    elif ancora == "dir":
        x -= w
    if alpha < 255:
        surf = surf.copy()
        surf.set_alpha(int(alpha))
    tela.blit(surf, (int(x), int(y)))
    return w, h
