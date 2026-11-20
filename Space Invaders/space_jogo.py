from PPlay.sprite import Sprite
from PPlay.collision import Collision
import random
import pygame

class SpaceInvaders:
    def __init__(self, janela, teclado):
        self.janela = janela
        self.teclado = teclado

        self.velocidade_nave = 350
        self.velocidade_tiro = 500
        self.tempo_recarga = 0.2
        self.cooldown_tiro = self.tempo_recarga

        self.linhas_monstros = 6
        self.colunas_monstros = 8

        self.velocidade_monstros_base = 90
        self.descida_monstros_base = 15
        self.velocidade_tiro_monstro_base = 150
        self.tempo_recarga_tiro_monstro_base = 1.5

        self.velocidade_monstros = self.velocidade_monstros_base
        self.descida_monstros = self.descida_monstros_base
        self.velocidade_tiro_monstro = self.velocidade_tiro_monstro_base
        self.tempo_recarga_tiro_monstro = self.tempo_recarga_tiro_monstro_base

        self.fase = 1
        self.direcao_monstros = 1
        self.matriz_monstros = []
        self.lista_tiros = []
        self.lista_tiros_monstros = []

        self.monstro_especial = None
        self.tempo_piscar_especial = 0
        self.especial_visivel = True

        self.vidas = 5
        self.pontos = 0

        self.cooldown_tiro_monstro = self._novo_intervalo_tiro_monstro()

        self.tempo_invulnerabilidade = 0.0
        self.tempo_piscar = 0.0
        self.player_visivel = True
        self.game_over = False

        self.nave = Sprite("nave.png")
        self.nave.x = self.janela.width / 2 - self.nave.width / 2
        self.nave.y = self.janela.height - self.nave.height - 20

        self.reiniciar_matriz_monstros()

    def _novo_intervalo_tiro_monstro(self):
        return self.tempo_recarga_tiro_monstro * random.uniform(0.80, 1.20)

    def _todos_monstros(self):
        return [monstro for linha in self.matriz_monstros for monstro in linha]

    def sortear_monstro_especial(self):
        todos = self._todos_monstros()
        if not todos:
            self.monstro_especial = None
            return

        self.monstro_especial = random.choice(todos)
        self.monstro_especial.image = self.monstro_especial.image.copy()
        self.monstro_especial.image.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        self.tempo_piscar_especial = 0.0
        self.especial_visivel = True

    def atualizar_monstro_especial(self, dt):
        if self.monstro_especial is None:
            return

        self.tempo_piscar_especial += dt*0.5
        if self.tempo_piscar_especial >= 0.18:
            self.tempo_piscar_especial = 0.0
            self.especial_visivel = not self.especial_visivel

    def criar_matriz_monstros(self):
        monstro_base = Sprite("monstro.png")

        passo_x = monstro_base.width * 1.5
        passo_y = monstro_base.height * 1.5

        largura_total = (monstro_base.width + (self.colunas_monstros - 1) * passo_x)

        if largura_total > self.janela.width:
            raise ValueError("A matriz de monstros nao cabe na largura da janela.")

        x_inicial = (self.janela.width - largura_total) / 2
        y_inicial = 10

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
        self.sortear_monstro_especial()

    def iniciar_jogo(self):
        self.nave.x = self.janela.width / 2 - self.nave.width / 2
        self.nave.y = self.janela.height - self.nave.height - 20

        self.lista_tiros = []
        self.lista_tiros_monstros = []

        self.cooldown_tiro = self.tempo_recarga
        self.vidas = 5
        self.pontos = 0
        self.fase = 1

        self.velocidade_monstros = self.velocidade_monstros_base
        self.descida_monstros = self.descida_monstros_base
        self.velocidade_tiro_monstro = self.velocidade_tiro_monstro_base
        self.tempo_recarga_tiro_monstro = self.tempo_recarga_tiro_monstro_base
        self.cooldown_tiro_monstro = self._novo_intervalo_tiro_monstro()

        self.tempo_invulnerabilidade = 0.0
        self.tempo_piscar = 0.0
        self.player_visivel = True
        self.nave.unhide()
        self.game_over = False
        self.tempo_piscar_especial = 0.0
        self.especial_visivel = True

        self.reiniciar_matriz_monstros()

    def parar_jogo(self):
        self.lista_tiros = []
        self.lista_tiros_monstros = []
        self.tempo_invulnerabilidade = 0.0
        self.tempo_piscar = 0.0
        self.player_visivel = True
        self.nave.unhide()

    def proxima_fase(self):
        self.fase += 1

        self.velocidade_monstros *= 1.1
        self.velocidade_tiro_monstro *= 1.1
        self.tempo_recarga_tiro_monstro = max(0.45, self.tempo_recarga_tiro_monstro * 0.95)

        self.lista_tiros = []
        self.lista_tiros_monstros = []
        self.cooldown_tiro_monstro = self._novo_intervalo_tiro_monstro()

        self.reiniciar_matriz_monstros()

    def atualizar_monstros(self, dt):
        todos = self._todos_monstros()
        if not todos:
            return

        monstro_esquerda = min(todos, key=lambda monstro: monstro.x)
        monstro_direita = max(todos, key=lambda monstro: monstro.x + monstro.width)

        movimento_x = (self.velocidade_monstros * self.direcao_monstros * dt)

        proxima_esquerda = monstro_esquerda.x + movimento_x
        proxima_direita = (monstro_direita.x + monstro_direita.width + movimento_x)

        if proxima_esquerda <= 0 or proxima_direita >= self.janela.width:
            self.direcao_monstros *= -1

            for linha in self.matriz_monstros:
                for monstro in linha:
                    monstro.y += self.descida_monstros

            movimento_x = (self.velocidade_monstros * self.direcao_monstros * dt)

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
            tiro_esquerda = tiro.x
            tiro_direita = tiro.x + tiro.width
            tiro_topo = tiro.y
            tiro_base = tiro.y + tiro.height
            tiro_atingiu_monstro = False

            for linha in self.matriz_monstros:
                if not linha:
                    continue

                topo_bloco = min(monstro.y for monstro in linha)
                base_bloco = max(monstro.y + monstro.height for monstro in linha)

                if tiro_base < topo_bloco or tiro_topo > base_bloco:
                    continue

                for monstro in linha[:]:
                    if (tiro_direita < monstro.x or tiro_esquerda > monstro.x + monstro.width
                        or tiro_base < monstro.y or tiro_topo > monstro.y + monstro.height):
                        continue

                    if tiro.collided(monstro):
                        if monstro is self.monstro_especial:
                            self.pontos += 10 * len(linha)
                            linha.clear()
                            self.monstro_especial = None
                            self.sortear_monstro_especial()
                        else:
                            linha.remove(monstro)
                            self.pontos += 10

                        if tiro in self.lista_tiros:
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
            return

        monstro = random.choice(todos)
        tiro = Sprite("tiros_monstros.png")
        tiro.x = (monstro.x + monstro.width / 2 - tiro.width / 2)
        tiro.y = monstro.y + monstro.height
        self.lista_tiros_monstros.append(tiro)

        multiplicador_dificuldade = {1: 1.0, 2: 0.8, 3: 0.6}.get(dif, 1.0)

        self.cooldown_tiro_monstro = (self._novo_intervalo_tiro_monstro() * multiplicador_dificuldade)

    def atualizar_tiros_monstros(self, dt):
        for tiro in self.lista_tiros_monstros[:]:
            tiro.y += self.velocidade_tiro_monstro * dt
            if tiro.y > self.janela.height:
                self.lista_tiros_monstros.remove(tiro)

    def iniciar_invulnerabilidade(self):
        self.tempo_invulnerabilidade = 2.5
        self.tempo_piscar = 0.0
        self.player_visivel = True
        self.nave.unhide()

    def atualizar_invulnerabilidade(self, dt):
        if self.tempo_invulnerabilidade <= 0:
            return

        self.tempo_invulnerabilidade -= dt
        self.tempo_piscar += dt

        if self.tempo_piscar >= 0.20:
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

        self.nave.x = max(0, min(self.nave.x, self.janela.width - self.nave.width))

        if (self.teclado.key_pressed("SPACE") and self.cooldown_tiro >= self.tempo_recarga):
            self.iniciar_tiro_player()

        self.atualizar_tiro_player(dt)
        self.atualizar_monstros(dt)
        self.atualizar_monstro_especial(dt)
        self.processar_colisao_tiros_player()

        if not self._todos_monstros():
            self.proxima_fase()
            return

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
                if monstro is self.monstro_especial and not self.especial_visivel:
                    continue
                monstro.draw()

    def desenhar(self):
        self.janela.set_background_color((100, 150, 255))
        self.desenhar_monstros()

        for tiro in self.lista_tiros:
            tiro.draw()
        for tiro in self.lista_tiros_monstros:
            tiro.draw()

        if self.player_visivel:
            self.nave.draw()

        self.janela.draw_text(f"FPS: {int(self.janela.get_fps())}",10, 10, size=22, cor=(255, 255, 255))
        self.janela.draw_text(f"Vidas: {self.vidas}",10, 40, size=24, cor=(255, 255, 255))
        self.janela.draw_text(f"Pontos: {self.pontos}",10, 70, size=24, cor=(255, 255, 255))
        self.janela.draw_text(f"Fase: {self.fase}",10, 100, size=24, cor=(255, 255, 255))