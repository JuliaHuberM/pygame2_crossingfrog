import pygame as pg
from sys import exit

class CruzamentoFazenda:
    def __init__(self):
        pg.init()
        self.janela = pg.display.set_mode((800, 835))
        pg.display.set_caption("Cruzamento da Fazenda")
        self.relogio = pg.time.Clock()

        try:
            # --- Fundo inicial ---
            self.fundo_imagem = pg.image.load("imagens_pygame/fundo_fazenda.png").convert()
            self.fundo_imagem = pg.transform.scale(self.fundo_imagem, (800, 835))

            # --- Sprites da raposa ---
            TAMANHO_RAPOSA = (50, 50)
            img_frente = pg.image.load("imagens_pygame/frente.png").convert_alpha()
            self.sprite_frente = pg.transform.scale(img_frente, TAMANHO_RAPOSA)
            img_costas = pg.image.load("imagens_pygame/costas.png").convert_alpha()
            self.sprite_costas = pg.transform.scale(img_costas, TAMANHO_RAPOSA)
            img_esquerda = pg.image.load("imagens_pygame/LADO_E.png").convert_alpha()
            self.sprite_esquerda = pg.transform.scale(img_esquerda, TAMANHO_RAPOSA)
            img_direita = pg.image.load("imagens_pygame/LADO_D.png").convert_alpha()
            self.sprite_direita = pg.transform.scale(img_direita, TAMANHO_RAPOSA)
            self.sprite_raposa_atual = self.sprite_frente

            # --- JACARÉS ---
            TAMANHO_JACARE = (70, 50)
            self.jacare_frames = [
                pg.transform.scale(pg.image.load(f"imagens_pygame/jac{i}.png").convert_alpha(), TAMANHO_JACARE)
                for i in range(1, 10)
            ]
            print("✅ Jacarés carregados com sucesso!")

            # --- FENOS ---
            TAMANHO_FENO = (60, 60)
            self.feno_frames = [
                pg.transform.scale(pg.image.load(f"imagens_pygame/feno{i}.png").convert_alpha(), TAMANHO_FENO)
                for i in range(1, 10)
            ]
            print("✅ Fenos carregados com sucesso!")

            # --- COBRAS ---
            TAMANHO_COBRA = (160, 50)
            self.cobra_frames = []
            for i in range(1, 9):
                if i == 4:
                    continue
                caminho = f"imagens_pygame/cob{i}.png"
                try:
                    img = pg.transform.scale(pg.image.load(caminho).convert_alpha(), TAMANHO_COBRA)
                    self.cobra_frames.append(img)
                except:
                    print(f"⚠️ Não encontrei {caminho}, pulando...")
            print("✅ Cobras carregadas com sucesso!")

            self.indice_animacao = 0
            self.tempo_animacao = 0.0
            self.vel_animacao = 0.20

        except Exception as e:
            print("❌ ERRO ao carregar imagens:", e)
            pg.quit()
            exit()

        # --- parâmetros gerais ---
        self.pos_raposa = [370, 760]
        self.velocidade = 30
        self.fase = 1

        # --- Plataformas iniciais (Fase 1)
        # 🔥 Removida a primeira linha de jacarés do topo
        self.linhas_das_plataformas = [
            [60, 420, 660],        # fenos (cima)
            [50, 650],             # cobras (cima)
            [50, 250, 450, 800],   # jacarés (meio)
            [120, 360, 720],       # fenos (baixo)
            [0, 700],              # cobras (baixo)
            [100, 250, 700, 800],  # jacarés (fundo)
        ]

        self.tamanho_raposa = self.sprite_frente.get_rect().size
        self.tamanho_jacare = (70, 50)
        self.tamanho_feno = (60, 60)
        self.tamanho_cobra = (160, 50)
        self.ajuste_y_raposa = -35
        self.vidas = 3
        self.game_over = False

        # --- Área da fazenda ---
        self.area_fazenda = pg.Rect(120, 50, 100, 100)
        self.debug_area = True  # mostra o retângulo vermelho

    # -------------------------------------------------------------
    def limpar_janela(self):
        self.janela.blit(self.fundo_imagem, (0, 0))
        if self.debug_area:
            pg.draw.rect(self.janela, (255, 0, 0), self.area_fazenda, 3)

    # -------------------------------------------------------------
    def desenhar_plataformas(self):
        """Desenha jacarés, fenos e cobras animadas com posições diferentes por fase."""
        if self.fase == 1:
            y_posicoes = [195, 295, 395, 495, 595, 695]
        elif self.fase == 2:
            y_posicoes = [300, 400, 500, 600]

        self.tempo_animacao += self.vel_animacao
        if self.tempo_animacao >= 1:
            self.indice_animacao = (self.indice_animacao + 1) % len(self.cobra_frames)
            self.tempo_animacao = 0

        for linha, xs in enumerate(self.linhas_das_plataformas):
            if linha >= len(y_posicoes):
                break
            y = y_posicoes[linha]
            for x in xs:
                if linha in (2, 5) and self.fase == 1 or (linha in (0, 2) and self.fase == 2):
                    jac_img = self.jacare_frames[self.indice_animacao % len(self.jacare_frames)]
                    rect = jac_img.get_rect(center=(x + self.tamanho_jacare[0] // 2, y))
                    self.janela.blit(jac_img, rect)
                elif linha in (0, 3) and self.fase == 1:
                    feno_img = self.feno_frames[self.indice_animacao % len(self.feno_frames)]
                    rect = feno_img.get_rect(center=(x + self.tamanho_feno[0] // 2, y))
                    self.janela.blit(feno_img, rect)
                elif linha in (1, 4) and self.fase == 1:
                    cobra_img = self.cobra_frames[self.indice_animacao % len(self.cobra_frames)]
                    rect = cobra_img.get_rect(center=(x + self.tamanho_cobra[0] // 2, y))
                    self.janela.blit(cobra_img, rect)

    # -------------------------------------------------------------
    def atualizar_plataformas(self):
        """Movimenta as plataformas."""
        for y in range(len(self.linhas_das_plataformas)):
            for i in range(len(self.linhas_das_plataformas[y])):
                if y in (2, 5):  # jacarés
                    self.linhas_das_plataformas[y][i] += 1
                    if self.linhas_das_plataformas[y][i] > 800:
                        self.linhas_das_plataformas[y][i] = -100
                elif y in (0, 3):  # fenos
                    self.linhas_das_plataformas[y][i] -= 2
                    if self.linhas_das_plataformas[y][i] < -120:
                        self.linhas_das_plataformas[y][i] = 800
                elif y in (1, 4):  # cobras
                    self.linhas_das_plataformas[y][i] += 1.5
                    if self.linhas_das_plataformas[y][i] > 850:
                        self.linhas_das_plataformas[y][i] = -300

    # -------------------------------------------------------------
    def raposa_colidiu_com_objeto(self):
        """Detecta colisões com obstáculos."""
        raposa_rect = pg.Rect(
            int(self.pos_raposa[0]),
            int(self.pos_raposa[1] + self.ajuste_y_raposa),
            int(self.tamanho_raposa[0]),
            int(self.tamanho_raposa[1])
        )

        if raposa_rect.colliderect(self.area_fazenda):
            return False

        y_posicoes = [195, 295, 395, 495, 595, 695]

        for linha, xs in enumerate(self.linhas_das_plataformas):
            y_plat = y_posicoes[min(linha, len(y_posicoes) - 1)]
            for x in xs:
                if linha in (2, 5):  # Jacarés
                    plat_rect = pg.Rect(int(x), int(y_plat - self.tamanho_jacare[1] // 2),
                                        int(self.tamanho_jacare[0]), int(self.tamanho_jacare[1]))
                elif linha in (0, 3):  # Fenos
                    plat_rect = pg.Rect(int(x), int(y_plat - self.tamanho_feno[1] // 2),
                                        int(self.tamanho_feno[0]), int(self.tamanho_feno[1]))
                elif linha in (1, 4):  # Cobras
                    plat_rect = pg.Rect(int(x), int(y_plat - self.tamanho_cobra[1] // 2),
                                        int(self.tamanho_cobra[0]), int(self.tamanho_cobra[1]))
                if raposa_rect.colliderect(plat_rect):
                    return True
        return False

    # -------------------------------------------------------------
    def resetar_posicao_raposa(self, colisao=False):
        if colisao:
            self.vidas -= 1
            if self.vidas < 0:
                self.vidas = 0
            som_game_over = pg.mixer.Sound('sons/game_over.mp3')
            print(f"💥 Colidiu! Vidas restantes: {self.vidas}")
            if self.vidas == 0:
                self.game_over = True
        self.pos_raposa = [370, 760]
        self.sprite_raposa_atual = self.sprite_frente

    # -------------------------------------------------------------
    def proxima_fase(self):
        """Muda o cenário e os inimigos conforme a fase."""
        self.fase += 1
        print(f"🌾 Indo para a fase {self.fase}!")

        if self.fase == 2:
            try:
                self.fundo_imagem = pg.image.load("imagens_pygame/fundo_fazenda_2.png").convert()
                self.fundo_imagem = pg.transform.scale(self.fundo_imagem, (800, 835))
                print("🐔 Entrou na fazenda — Fase 2 iniciada!")
            except:
                print("⚠️ Fundo da Fase 2 não encontrado!")

            # mantém apenas as linhas centrais para o novo cenário
            self.linhas_das_plataformas = [
                [50, 250, 450, 800],   # jacarés (meio)
                [120, 360, 720],       # fenos (meio)
                [0, 700],              # cobras (meio)
            ]
            print("⚙️ Linhas ajustadas para o cenário interno da fazenda.")
            self.vel_animacao = 0.25

        elif self.fase == 3:
            print("🚜 Fase 3 iniciada! (ainda sem cenário)")
            self.vel_animacao = 0.3

        else:
            print("🎉 Você zerou o jogo!")
            self.game_over = True

        self.pos_raposa = [370, 760]

    # -------------------------------------------------------------
    def desenhar_raposa(self):
        self.janela.blit(self.sprite_raposa_atual,
                         (self.pos_raposa[0], self.pos_raposa[1] + self.ajuste_y_raposa))

    # -------------------------------------------------------------
    def mover_raposa(self, tecla):
        if self.game_over:
            return
        if tecla == "up":
            self.sprite_raposa_atual = self.sprite_costas
            self.pos_raposa[1] -= self.velocidade
            som_movimento = pg.mixer.Sound('sons/raposa.mp3')
        elif tecla == "down":
            self.sprite_raposa_atual = self.sprite_frente
            self.pos_raposa[1] += self.velocidade
            som_movimento = pg.mixer.Sound('sons/raposa.mp3')
        elif tecla == "left":
            self.sprite_raposa_atual = self.sprite_esquerda
            self.pos_raposa[0] -= self.velocidade
            som_movimento = pg.mixer.Sound('sons/raposa.mp3')
        elif tecla == "right":
            self.sprite_raposa_atual = self.sprite_direita
            self.pos_raposa[0] += self.velocidade
            som_movimento = pg.mixer.Sound('sons/raposa.mp3')
        elif tecla == "r":
            self.__init__()

        # Verifica se encostou na fazenda
        raposa_rect = pg.Rect(
            int(self.pos_raposa[0]),
            int(self.pos_raposa[1] + self.ajuste_y_raposa),
            int(self.tamanho_raposa[0]),
            int(self.tamanho_raposa[1])
        )
        if raposa_rect.colliderect(self.area_fazenda):
            print("🐾 A raposa chegou na fazenda!")
            self.proxima_fase()

    # -------------------------------------------------------------
    def checar_colisoes_e_reagir(self):
        if self.game_over:
            return
        if self.raposa_colidiu_com_objeto():
            self.resetar_posicao_raposa(colisao=True)
