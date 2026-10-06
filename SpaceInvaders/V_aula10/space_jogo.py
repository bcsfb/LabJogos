from PPlay.sprite import Sprite
from PPlay.collision import Collision
import random

class SpaceInvaders:
    def __init__(self, janela, teclado):
        self.janela = janela
        self.teclado = teclado

        self.velocidade_nave = 350

        self.velocidade_tiro = 500
        self.tempo_recarga = 0.2
        self.cooldown_tiro = self.tempo_recarga

        self.linhas_monstros = 4
        self.colunas_monstros = 6
        self.velocidade_monstros = 120
        self.descida_monstros = 20

        self.direcao_monstros = 1
        self.matriz_monstros = []

        self.lista_tiros = []

        self.vidas = 3

        self.velocidade_tiro_monstro = 230
        self.tempo_recarga_tiro_monstro = 1.2
        self.cooldown_tiro_monstro = self._novo_intervalo_tiro_monstro()

        self.tempo_invulnerabilidade = 0.0
        self.tempo_piscar = 0.0
        self.player_visivel = True

        self.game_over = False

        self.nave = Sprite("nave.png")
        self.lista_tiros_monstros = []

        self.nave.x = self.janela.width / 2 - self.nave.width / 2
        self.nave.y = self.janela.height - self.nave.height - 20

        self.reiniciar_matriz_monstros()

    def _novo_intervalo_tiro_monstro(self):
        return self.tempo_recarga_tiro_monstro * random.uniform(0.80, 1.20)

    def _todos_monstros(self):
        return [monstro for linha in self.matriz_monstros for monstro in linha]

    def criar_matriz_monstros(self):
        monstro_base = Sprite("monstro.png")

        if self.linhas_monstros <= 3:
            raise ValueError("linhas_monstros precisa ser maior que 3.")

        if self.colunas_monstros <= 5:
            raise ValueError("colunas_monstros precisa ser maior que 5.")

        espaco_x = monstro_base.width / 2
        espaco_y = monstro_base.height / 2

        passo_x = monstro_base.width + espaco_x
        passo_y = monstro_base.height + espaco_y

        largura_total = (monstro_base.width + (self.colunas_monstros - 1) * passo_x)

        x_inicial = (self.janela.width - largura_total) / 2
        y_inicial = 60

        matriz = []

        for linha in range(self.linhas_monstros):
            linha_monstros = []

            for coluna in range(self.colunas_monstros):
                monstro = Sprite("monstro.png")

                monstro.x = x_inicial + coluna * passo_x
                monstro.y = y_inicial + linha * passo_y

                linha_monstros.append(monstro)

            matriz.append(linha_monstros)

        return matriz

    def reiniciar_matriz_monstros(self):
        self.direcao_monstros = 1
        self.matriz_monstros = self.criar_matriz_monstros()

    def iniciar_jogo(self):
        self.nave.x = self.janela.width / 2 - self.nave.width / 2
        self.nave.y = self.janela.height - self.nave.height - 20

        self.lista_tiros = []
        self.lista_tiros_monstros = []

        self.cooldown_tiro = self.tempo_recarga
        self.cooldown_tiro_monstro = self._novo_intervalo_tiro_monstro()

        self.vidas = 3

        self.tempo_invulnerabilidade = 0.0
        self.tempo_piscar = 0.0
        self.player_visivel = True
        self.nave.unhide()

        self.game_over = False

        self.reiniciar_matriz_monstros()

    def parar_jogo(self):
        self.lista_tiros = []
        self.lista_tiros_monstros = []
        self.tempo_invulnerabilidade = 0.0
        self.tempo_piscar = 0.0
        self.player_visivel = True
        self.nave.unhide()

    def atualizar_monstros(self, dt):
        todos = self._todos_monstros()

        if not todos:
            return

        monstro_esquerda = min(todos, key=lambda monstro: monstro.x)
        monstro_direita = max(todos, key=lambda monstro: monstro.x + monstro.width)

        movimento_x = (self.velocidade_monstros* self.direcao_monstros* dt)

        proxima_esquerda = monstro_esquerda.x + movimento_x
        proxima_direita = (monstro_direita.x + monstro_direita.width + movimento_x)

        vai_bater_esquerda = proxima_esquerda <= 0
        vai_bater_direita = proxima_direita >= self.janela.width

        if vai_bater_esquerda or vai_bater_direita:
            self.direcao_monstros *= -1

            for linha in self.matriz_monstros:
                for monstro in linha:
                    monstro.y += self.descida_monstros

            movimento_x = (self.velocidade_monstros* self.direcao_monstros* dt)

        for linha in self.matriz_monstros:
            for monstro in linha:
                monstro.x += movimento_x

        todos = self._todos_monstros()

        if not todos:
            return

        menor_x = min(monstro.x for monstro in todos)
        maior_x = max(monstro.x + monstro.width for monstro in todos)

        if menor_x < 0:
            correcao = -menor_x

            for linha in self.matriz_monstros:
                for monstro in linha:
                    monstro.x += correcao

        elif maior_x > self.janela.width:
            correcao = self.janela.width - maior_x

            for linha in self.matriz_monstros:
                for monstro in linha:
                    monstro.x += correcao

    def iniciar_tiro_player(self):
        tiro = Sprite("tiro.png")
        tiro.x = (self.nave.x + self.nave.width / 2 - tiro.width / 2)
        tiro.y = self.nave.y - tiro.height

        self.lista_tiros.append(tiro)
        self.cooldown_tiro = 0

    def atualizar_tiro_player(self, dt):
        for tiro in self.lista_tiros[:]:
            tiro.y -= self.velocidade_tiro * dt

            if tiro.y + tiro.height < 0:
                self.lista_tiros.remove(tiro)

    def processar_colisao_tiros_player(self):
        for tiro in self.lista_tiros[:]:
            tiro_atingiu_monstro = False

            for linha in self.matriz_monstros:
                for monstro in linha[:]:
                    if tiro.collided(monstro):
                        linha.remove(monstro)
                        self.lista_tiros.remove(tiro)
                        tiro_atingiu_monstro = True
                        break

                if tiro_atingiu_monstro:
                    break

    def tentar_disparar_monstro(self, dt, dif):
        self.cooldown_tiro_monstro -= dt

        if self.cooldown_tiro_monstro > 0:
            return

        todos = self._todos_monstros()

        if not todos:
            self.cooldown_tiro_monstro = self._novo_intervalo_tiro_monstro()
            return

        monstro = random.choice(todos)
        tiro = Sprite("tiros_monstros.png")

        tiro.x = (monstro.x + monstro.width / 2 - tiro.width / 2)
        tiro.y = monstro.y + monstro.height

        self.lista_tiros_monstros.append(tiro)
        multiplicador_dificuldade = {1: 1.0, 2: 0.90, 3: 0.80}.get(dif, 1.0)
        self.cooldown_tiro_monstro = ( self._novo_intervalo_tiro_monstro()* multiplicador_dificuldade)

    def atualizar_tiros_monstros(self, dt):
        for tiro in self.lista_tiros_monstros[:]:
            tiro.y += self.velocidade_tiro_monstro * dt

            if tiro.y > self.janela.height:
                self.lista_tiros_monstros.remove(tiro)

    def iniciar_invulnerabilidade(self):
        self.tempo_invulnerabilidade = 2.0
        self.tempo_piscar = 0.0
        self.player_visivel = True
        self.nave.unhide()

    def atualizar_invulnerabilidade(self, dt):
        if self.tempo_invulnerabilidade <= 0:
            return

        self.tempo_invulnerabilidade -= dt
        self.tempo_piscar += dt

        if self.tempo_piscar >= 0.10:
            self.tempo_piscar = 0.0
            self.player_visivel = not self.player_visivel

            if self.player_visivel:
                self.nave.unhide()
            else:
                self.nave.hide()

        if self.tempo_invulnerabilidade <= 0:
            self.tempo_invulnerabilidade = 0.0
            self.tempo_piscar = 0.0
            self.player_visivel = True
            self.nave.unhide()

    def processar_colisao_tiros_monstros_com_player(self):
        if self.tempo_invulnerabilidade > 0:
            return

        for tiro in self.lista_tiros_monstros[:]:
            if Collision.collided(tiro, self.nave):
                self.lista_tiros_monstros.remove(tiro)
                self.vidas -= 1

                if self.vidas <= 0:
                    self.vidas = 0
                    self.game_over = True
                    return

                self.nave.x = self.janela.width / 2 - self.nave.width / 2
                self.nave.y = self.janela.height - self.nave.height - 20
                self.iniciar_invulnerabilidade()
                break

    def monstro_colidiu_com_nave(self):
        for linha in self.matriz_monstros:
            for monstro in linha:
                if Collision.collided(monstro, self.nave):
                    return True
        return False

    def monstro_mais_baixo_atingiu_jogador(self):
        todos = self._todos_monstros()
        if not todos:
            return False

        maior_y = max(monstro.y + monstro.height for monstro in todos)
        return maior_y >= self.nave.y

    def atualizar(self, dt, dif):
        if self.game_over:
            return
        if dif == 1:
            self.tempo_recarga = 0.2
        elif dif == 2:
            self.tempo_recarga = 0.3
        elif dif == 3:
            self.tempo_recarga = 0.4

        self.cooldown_tiro += dt

        if self.teclado.key_pressed("LEFT"):
            self.nave.x -= self.velocidade_nave * dt
        if self.teclado.key_pressed("RIGHT"):
            self.nave.x += self.velocidade_nave * dt
        if self.nave.x < 0:
            self.nave.x = 0
        if self.nave.x + self.nave.width > self.janela.width:
            self.nave.x = self.janela.width - self.nave.width

        if (self.teclado.key_pressed("SPACE") and self.cooldown_tiro >= self.tempo_recarga):
            self.iniciar_tiro_player()

        self.atualizar_tiro_player(dt)
        self.atualizar_monstros(dt)
        self.processar_colisao_tiros_player()

        self.tentar_disparar_monstro(dt, dif)
        self.atualizar_tiros_monstros(dt)

        self.atualizar_invulnerabilidade(dt)
        self.processar_colisao_tiros_monstros_com_player()

        if self.game_over:
            return
        if self.monstro_colidiu_com_nave():
            self.game_over = True
            return
        if self.monstro_mais_baixo_atingiu_jogador():
            self.game_over = True

    def desenhar_monstros(self):
        for linha in self.matriz_monstros:
            for monstro in linha:
                monstro.draw()

    def desenhar(self):
        self.janela.set_background_color((0, 0, 75))

        self.desenhar_monstros()

        for tiro in self.lista_tiros:
            tiro.draw()
        for tiro in self.lista_tiros_monstros:
            tiro.draw()

        if self.player_visivel:
            self.nave.draw()

        self.janela.draw_text(f"Vidas: {self.vidas}", 10, 40, size=24, cor=(255, 255, 255))
        self.janela.draw_text(f"FPS: {int(self.janela.get_fps())}", 10, 10, size=22, cor=(255, 255, 255))