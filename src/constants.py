# ─────────────────────────────────────────────
#  CupFight! — constants.py
# ─────────────────────────────────────────────

# Pantalla
SCREEN_W = 960
SCREEN_H = 540
FPS = 60
TITLE = "CupFight!"

# Suelo
GROUND_Y = SCREEN_H - 110   # Y donde pisan los personajes

# Física
GRAVITY = 0.7
JUMP_FORCE = -16
MOVE_SPEED = 5
FRICTION = 0.75

# Combate
MAX_HP = 100
MAX_ROUNDS = 3             # gana el primero en ganar 2

# Tiempos (en frames a 60fps)
ATTACK_DURATION  = 18
KICK_DURATION    = 20
SPECIAL_DURATION = 28
HIT_STUN         = 20      # frames de hit-stun al recibir golpe
ATTACK_COOLDOWN  = 35      # frames entre ataques
BLOCK_COOLDOWN   = 8

# Daño
DMG_PUNCH   = 10
DMG_KICK    = 14
DMG_SPECIAL = 22
BLOCK_MULT  = 0.15         # % de daño que pasa el bloqueo

# Colores (estilo años 30)
C_SKY_TOP    = (245, 223, 160)
C_SKY_BOT    = (232, 168,  48)
C_GROUND     = (139,  69,   0)
C_GROUND_D   = ( 90,  42,   0)
C_CLOUD      = (255, 255, 230)
C_CLOUD_OUT  = (200, 134,  10)
C_BUILD      = (200, 120,  32)

C_P1_BODY    = (245, 200,  66)   # Copa — amarillo
C_P1_OUTLINE = (139,  69,   0)
C_P1_SHOE    = (204,  68,   0)
C_P1_GLOVE   = (255, 255, 255)

C_P2_BODY    = (122, 212, 232)   # Jarro — azul claro
C_P2_OUTLINE = ( 26,  96, 128)
C_P2_SHOE    = ( 26,  48, 128)
C_P2_GLOVE   = (255, 255, 255)

C_HP_BG      = ( 42,  16,   0)
C_HP_BAR     = (220,  40,  40)
C_HP_BORDER  = (139,  69,   0)
C_TEXT_GOLD  = (245, 200,  66)
C_TEXT_OUT   = (139,  69,   0)
C_HIT_SPARK  = (255,  68,   0)
C_SPECIAL_FX = (255, 238,   0)

C_UI_BG      = ( 26,   8,   0)
C_UI_BORDER  = (200, 134,  10)

# Estados del luchador
class State:
    IDLE    = "idle"
    WALK    = "walk"
    JUMP    = "jump"
    ATTACK  = "attack"
    KICK    = "kick"
    SPECIAL = "special"
    HIT     = "hit"
    BLOCK   = "block"
    KO      = "ko"

# Estados del juego
class GameState:
    TITLE      = "title"
    MENU       = "menu"
    ANNOUNCE   = "announce"
    FIGHT      = "fight"
    ROUND_END  = "round_end"
    GAME_OVER  = "game_over"
    COMING_SOON = "coming_soon"

# Opciones del menú principal
MENU_OPTIONS = [
    {"label": "Historia",      "icon": "libro",   "state": "coming_soon"},
    {"label": "Arcade",        "icon": "joystick","state": "coming_soon"},
    {"label": "Batallas",      "icon": "espadas", "state": "fight"},
    {"label": "Online",        "icon": "red",     "state": "coming_soon"},
    {"label": "Tienda",        "icon": "bolsa",   "state": "coming_soon"},
    {"label": "Configuración", "icon": "engrane", "state": "coming_soon"},
]
