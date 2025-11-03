import pygame
import sys
import os

# --- CONFIGURAÇÕES GERAIS ---
SCREENWIDTH, SCREENHEIGHT = 900, 935
FPS = 60

# --- FUNÇÃO AUXILIAR PARA CAMINHOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def get_asset_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)

# --- CLASSE BASE ---
class BaseScreen:
    def __init__(self, display, gsm, bg_path):
        self.display = display
        self.gsm = gsm

        # carrega o fundo
        full_bg_path = get_asset_path(bg_path)
        self.bg = pygame.image.load(full_bg_path).convert()
        self.bg = pygame.transform.scale(self.bg, (SCREENWIDTH, SCREENHEIGHT))
        self.font_title = pygame.font.SysFont(None, 72)
        self.font_text = pygame.font.SysFont(None, 36)

    def draw_centered(self, text, font, y):
        surface = font.render(text, True, (255, 255, 255))
        rect = surface.get_rect(center=(SCREENWIDTH // 2, y))
        self.display.blit(surface, rect)
        return rect


# --- TELA DE INÍCIO ---
class Start(BaseScreen):
    def __init__(self, display, gsm):
        super().__init__(display, gsm, "imagens_pygame/imagem_start.png")
        button_image_path = get_asset_path("imagens_pygame/botao_start.png")

        self.start_button_image = pygame.image.load(button_image_path).convert_alpha()

        # redimensiona o botão
        target_width = 400
        original_width, original_height = self.start_button_image.get_size()
        new_height = int(original_height * (target_width / original_width))/2
        self.start_button_image = pygame.transform.scale(self.start_button_image, (target_width, new_height))

        # cria efeito hover
        self.start_button_hover_image = self.start_button_image.copy()
        self.start_button_hover_image.fill((50, 50, 50, 0), special_flags=pygame.BLEND_RGB_SUB)
        self.start_button_rect = None

        # Carrega as 4 imagens do nome do jogo para animação
        TAMANHO_NOME = (600, 100)
        try:
            self.game_name_images = [
                pygame.transform.scale(pygame.image.load(get_asset_path(f"imagens_pygame/nome_jogo_{i}.png")).convert_alpha(), TAMANHO_NOME)
                for i in range(1, 5)
            ]
        except pygame.error as e:
            print(f"Erro ao carregar imagens do nome do jogo: {e}")
            # Fallback: se não carregar, usa uma superfície vazia ou texto simples
            fallback_surface = self.font_title.render("Running Fox Game", True, (255, 255, 255))
            self.game_name_images = [fallback_surface] * 4  # Repete a mesma imagem 4 vezes


        # Contador para animação
        self.animation_frame = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.start_button_rect and self.start_button_rect.collidepoint(event.pos):
                self.gsm.set_state('level')

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.gsm.set_state('level')

    def run(self):
        self.display.blit(self.bg, (0, 0))
        
        # Animação do nome do jogo
        if self.game_name_images:
            current_image = self.game_name_images[self.animation_frame % len(self.game_name_images)]
            img_rect = current_image.get_rect(center=(SCREENWIDTH // 2, SCREENHEIGHT // 3))  # Posição acima do botão
            self.display.blit(current_image, img_rect)
        
        # Incrementa o contador de animação (ajuste para velocidade: % 16 para mais lento)
        self.animation_frame += 1

        # Desenha o botão
        button_y_pos = SCREENHEIGHT * 5 // 6
        mouse_pos = pygame.mouse.get_pos()
        current_button_image = self.start_button_image
        self.start_button_rect = current_button_image.get_rect(center=(SCREENWIDTH // 2, button_y_pos))

        if self.start_button_rect.collidepoint(mouse_pos):
            current_button_image = self.start_button_hover_image

        self.display.blit(current_button_image, self.start_button_rect)


# --- TELA DO JOGO ---
class Level(BaseScreen):
    def __init__(self, display, gsm):
        super().__init__(display, gsm, "imagens_pygame/level_1.png")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            self.gsm.set_state('end')

    def run(self):
        self.display.blit(self.bg, (0, 0))
        self.draw_centered("LEVEL - Pressione [E] para encerrar", self.font_text, SCREENHEIGHT - 100)


# --- TELA FINAL ---
class End(BaseScreen):
    def __init__(self, display, gsm):
        super().__init__(display, gsm, "imagens_pygame/game_over.png")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.gsm.set_state('start')
            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    def run(self):
        self.display.blit(self.bg, (0, 0))
        self.draw_centered("FIM DE JOGO", self.font_title, SCREENHEIGHT // 3)
        self.draw_centered("Pressione [R] para reiniciar ou [Q] para sair", self.font_text, SCREENHEIGHT // 2)


# --- GERENCIADOR DE ESTADOS ---
class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState

    def get_state(self):
        return self.currentState

    def set_state(self, state):
        self.currentState = state


# --- EXECUÇÃO PRINCIPAL ---
class Game:
    def __init__(self):
        pygame.init()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))  # garante o diretório correto
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        pygame.display.set_caption("Running Fox Game")
        self.clock = pygame.time.Clock()

        # inicializa estados
        self.gameStateManager = GameStateManager('start')
        self.start = Start(self.screen, self.gameStateManager)
        self.level = Level(self.screen, self.gameStateManager)
        self.end = End(self.screen, self.gameStateManager)
        self.states = {'start': self.start, 'level': self.level, 'end': self.end}

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.states[self.gameStateManager.get_state()].handle_event(event)

            self.states[self.gameStateManager.get_state()].run()
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()
