from config import PONTUACAO_MINIMA_RANKING, TAMANHO_RANKING

def limpar_nome(nome):
    letras = "".join(c for c in str(nome).upper() if "A" <= c <= "Z")
    return letras[:3]

class Ranking:
    def __init__(self, caminho, caminho_antigo=None, tamanho=TAMANHO_RANKING):
        self.caminho = caminho
        self.tamanho = tamanho
        self.entradas = []          # [(nome, pontos)] em ordem decrescente
        self._carregar(caminho_antigo)
    #arquivo
    def _carregar(self, caminho_antigo):
        try:
            for linha in self.caminho.read_text(encoding="utf-8").splitlines():
                partes = linha.strip().split(";")
                if len(partes) != 2:
                    continue
                nome = limpar_nome(partes[0]) or "???"
                try:
                    pontos = int(partes[1])
                except ValueError:
                    continue
                if pontos > 0:
                    self.entradas.append((nome, pontos))
        except (FileNotFoundError, OSError):
            pass
        if not self.entradas and caminho_antigo is not None:
            try:
                antigo = int(caminho_antigo.read_text(encoding="utf-8").strip())
                if antigo > 0:
                    self.entradas = [("EQP", antigo)]
                    self.salvar()
            except (FileNotFoundError, ValueError, OSError):
                pass
        self.entradas.sort(key=lambda e: -e[1])
        self.entradas = self.entradas[: self.tamanho]

    def salvar(self):
        try:
            texto = "\n".join(f"{n};{p}" for n, p in self.entradas)
            self.caminho.write_text(texto, encoding="utf-8")
        except OSError:
            pass

    #consultas
    def melhor(self):
        return self.entradas[0][1] if self.entradas else 0

    def posicao_para(self, pontos):
        i = 0
        while i < len(self.entradas) and self.entradas[i][1] >= pontos:
            i += 1
        return i

    def qualifica(self, pontos):
        return pontos >= max(1, PONTUACAO_MINIMA_RANKING) and self.posicao_para(pontos) < self.tamanho

    def inserir(self, nome, pontos):
        pontos = int(pontos)
        if not self.qualifica(pontos):
            return -1
        pos = self.posicao_para(pontos)
        self.entradas.insert(pos, (limpar_nome(nome) or "???", pontos))
        self.entradas = self.entradas[: self.tamanho]
        self.salvar()
        return pos
