import pygame
import sys
from screens import GameStateManager, Start, End  # Traz as telas
from classes.game import CruzamentoFazenda
from classes.hud import HUD

pygame.init()
SCREENWIDTH, SCREENHEIGHT = 900, 935
FPS = 60
pygame.mixer.init()  # Inicializa o mixer de áudio

# Carregar música de fundo
try:
    pygame.mixer.music.load('sons/trilha.mp3')
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Erro ao carregar música de fundo: {e}")

# Carregar efeitos sonoros
try:
    som_movimento = pygame.mixer.Sound('sons/raposa.mp3')
    som_start = pygame.mixer.Sound('sons/start.mp3')
    som_troca_fase = pygame.mixer.Sound('sons/fases.mp3')
    som_game_over = pygame.mixer.Sound('sons/game_over.mp3')
except pygame.error as e:
    print(f"Erro ao carregar sons: {e}")

# --- Estado do jogo ---
STATE = "menu"  # menu → jogo → end
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption("Running Fox Game")

# --- Inicializações ---
gsm = GameStateManager("start")
menu_start = Start(screen, gsm)
menu_end = End(screen, gsm)

# Jogo principal (raposa)
jogo = CruzamentoFazenda()
hud = HUD(jogo.janela, jogo)

# --- Loop principal ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Menu inicial
        if STATE == "menu":
            menu_start.handle_event(event)
            if gsm.get_state() == "level":
                som_start.play()
                STATE = "jogo"
        
        # Tela final
        elif STATE == "end":
            menu_end.handle_event(event)
            if gsm.get_state() == "start":
                jogo = CruzamentoFazenda()
                hud = HUD(jogo.janela, jogo)
                STATE = "menu"
                pygame.mixer.music.play(-1)  # Reinicie a trilha ao voltar ao menu

        # Jogo da raposa
        elif STATE == "jogo":
            jogo.handle_event = None
            if event.type == pygame.KEYDOWN:
                tecla = pygame.key.name(event.key)
                jogo.mover_raposa(tecla)
                if tecla == "escape":
                    STATE = "end"

    # --- Atualizações ---
    if STATE == "menu":
        menu_start.run()

    elif STATE == "jogo":
        jogo.relogio.tick(60)
        jogo.atualizar_plataformas()
        jogo.checar_colisoes_e_reagir()
        jogo.limpar_janela()
        jogo.desenhar_plataformas()
        jogo.desenhar_raposa()
        hud.desenhar_vidas()
        pygame.display.update()

        # Vai pra tela final quando acabar as vidas
        if jogo.vidas <= 0 or jogo.game_over:
            pygame.mixer.music.stop()
            som_game_over.play()
            STATE = "end"

    elif STATE == "end":
        menu_end.run()

    pygame.display.update()
    clock.tick(FPS)
