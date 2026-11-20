def ler_opcoes(caminho):
    opcoes = {}
    try:
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            if "=" in linha:
                chave, valor = linha.split("=", 1)
                opcoes[chave.strip().lower()] = valor.strip()
    except (FileNotFoundError, OSError):
        pass
    return opcoes

def salvar_opcoes(caminho, opcoes):
    try:
        caminho.write_text("\n".join(f"{k}={v}" for k, v in opcoes.items()), encoding="utf-8")
    except OSError:
        pass
