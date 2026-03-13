# ─────────────────────────────────────────────
#  CupFight! — game.py
# ─────────────────────────────────────────────
import pygame
import math
from src.constants import *
from src.fighter import Fighter
from src.background import Background
from src.hud import HUD


# ── Helpers de texto ───────────────────────────
def _outline_text(surf, font, text, color, outline, cx, cy):
    rendered = font.render(text, True, color)
    outlined = font.render(text, True, outline)
    w, h = rendered.get_size()
    x, y = cx - w // 2, cy - h // 2
    for dx in (-3, 0, 3):
        for dy in (-3, 0, 3):
            if dx or dy:
                surf.blit(outlined, (x + dx, y + dy))
    surf.blit(rendered, (x, y))


def _make_p1() -> Fighter:
    return Fighter(
        x=150, facing=1, is_player=True,
        palette={
            "body":    C_P1_BODY,
            "outline": C_P1_OUTLINE,
            "shoe":    C_P1_SHOE,
            "glove":   C_P1_GLOVE,
            "collar":  C_SKY_BOT,
        },
        name="COPAS",
    )


def _make_p2() -> Fighter:
    return Fighter(
        x=720, facing=-1, is_player=False,
        palette={
            "body":    C_P2_BODY,
            "outline": C_P2_OUTLINE,
            "shoe":    C_P2_SHOE,
            "glove":   C_P2_GLOVE,
            "collar":  (90, 180, 200),
        },
        name="JARRO",
    )


# ─────────────────────────────────────────────
#  Pantalla de Título
# ─────────────────────────────────────────────
class TitleScreen:
    def __init__(self, fonts):
        self.font_big, self.font_med, self.font_small = fonts
        self.frame = 0
        self._btn_rect = None

    def update(self):
        self.frame += 1

    def draw(self, surf: pygame.Surface):
        f = self.frame
        for row in range(SCREEN_H):
            t = row / SCREEN_H
            r = int(60  * (1 - t) + 15 * t)
            g = int(20  * (1 - t) + 5  * t)
            pygame.draw.line(surf, (r, g, 0), (0, row), (SCREEN_W, row))

        # Líneas decorativas de fondo
        for i in range(0, SCREEN_H, 40):
            pygame.draw.line(surf, (60, 30, 0), (0, i), (SCREEN_W, i), 1)

        # Título
        pulse = 1.0 + math.sin(f * 0.06) * 0.035
        title_base = self.font_big.render("CUP FIGHT!", True, C_TEXT_GOLD)
        w, h = title_base.get_size()
        scaled = pygame.transform.scale(title_base, (int(w * pulse), int(h * pulse)))
        out_base = self.font_big.render("CUP FIGHT!", True, C_TEXT_OUT)
        out_sc = pygame.transform.scale(out_base, scaled.get_size())
        sw, sh = scaled.get_size()
        tx = SCREEN_W // 2 - sw // 2
        ty = 75
        for dx in (-5, 0, 5):
            for dy in (-5, 0, 5):
                if dx or dy:
                    surf.blit(out_sc, (tx + dx, ty + dy))
        surf.blit(scaled, (tx, ty))

        # Subtítulo
        sub = self.font_small.render("★  1930s Cartoon Brawl  ★", True, (220, 168, 60))
        surf.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, ty + sh + 8))

        # Línea decorativa
        lw = 420
        pygame.draw.line(surf, C_UI_BORDER,
                         (SCREEN_W // 2 - lw // 2, ty + sh + 42),
                         (SCREEN_W // 2 + lw // 2, ty + sh + 42), 2)

        # Botón JUGAR
        btn_w, btn_h = 260, 60
        btn_x = SCREEN_W // 2 - btn_w // 2
        btn_y = SCREEN_H // 2 + 35
        bob = int(math.sin(f * 0.09) * 6)

        shadow = pygame.Surface((btn_w + 6, btn_h + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 110), (0, 0, btn_w + 6, btn_h + 6), border_radius=10)
        surf.blit(shadow, (btn_x + 3, btn_y + 8 + bob))

        pygame.draw.rect(surf, C_TEXT_OUT, (btn_x, btn_y + bob, btn_w, btn_h), border_radius=10)
        pygame.draw.rect(surf, C_SKY_BOT,  (btn_x+2, btn_y+2+bob, btn_w-4, btn_h-4), border_radius=8)
        pygame.draw.rect(surf, C_TEXT_OUT, (btn_x, btn_y + bob, btn_w, btn_h), 3, border_radius=10)
        btn_text = self.font_med.render("¡JUGAR!", True, C_UI_BG)
        surf.blit(btn_text, (SCREEN_W // 2 - btn_text.get_width() // 2,
                              btn_y + btn_h // 2 - btn_text.get_height() // 2 + bob))

        self._btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h + 12)

        # Controles rápidos
        controls = [
            "A / D  ·  Moverse     W  ·  Saltar",
            "J  ·  Puñetazo     K  ·  Patada     L  ·  Especial     S  ·  Bloquear",
        ]
        for i, line in enumerate(controls):
            ct = self.font_small.render(line, True, (180, 110, 20))
            surf.blit(ct, (SCREEN_W // 2 - ct.get_width() // 2,
                           btn_y + btn_h + 28 + i * 28))


# ─────────────────────────────────────────────
#  Menú Principal
# ─────────────────────────────────────────────
DESCRIPTIONS = {
    "Historia":      "Sigue la aventura de Copas por el mundo",
    "Arcade":        "Pelea contra enemigos en oleadas infinitas",
    "Batallas":      "Combate rápido contra la IA — ¡disponible!",
    "Online":        "Desafía jugadores de todo el mundo",
    "Tienda":        "Desbloquea personajes, trajes y escenarios",
    "Configuración": "Ajusta controles, volumen y resolución",
}

ACCENTS = {
    "Historia":      (180, 100, 220),
    "Arcade":        (220,  80,  80),
    "Batallas":      (245, 200,  66),
    "Online":        ( 80, 180, 220),
    "Tienda":        ( 80, 220, 140),
    "Configuración": (200, 140,  60),
}

ICONS = {
    "Historia":      "libro",
    "Arcade":        "joystick",
    "Batallas":      "espadas",
    "Online":        "red",
    "Tienda":        "bolsa",
    "Configuración": "engrane",
}


class MainMenu:
    def __init__(self, fonts):
        self.font_big, self.font_med, self.font_small = fonts
        self.frame    = 0
        self.selected = 0
        self.hover    = -1
        self._card_rects: list[pygame.Rect] = []
        self._back_rect = None
        self.enter_anim = float(len(MENU_OPTIONS))

    def update(self):
        self.frame += 1
        if self.enter_anim > 0:
            self.enter_anim = max(0.0, self.enter_anim - 0.18)
        mx, my = pygame.mouse.get_pos()
        self.hover = -1
        for i, r in enumerate(self._card_rects):
            if r.collidepoint(mx, my):
                self.hover = i

    def handle_key(self, key):
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(MENU_OPTIONS)
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(MENU_OPTIONS)
        elif key == pygame.K_LEFT:
            self.selected = (self.selected - 1) % len(MENU_OPTIONS)
        elif key == pygame.K_RIGHT:
            self.selected = (self.selected + 1) % len(MENU_OPTIONS)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            return MENU_OPTIONS[self.selected]["state"]
        elif key == pygame.K_ESCAPE:
            return "title"
        return None

    def handle_click(self, pos):
        for i, r in enumerate(self._card_rects):
            if r.collidepoint(pos):
                self.selected = i
                return MENU_OPTIONS[i]["state"]
        if self._back_rect and self._back_rect.collidepoint(pos):
            return "title"
        return None

    def draw(self, surf: pygame.Surface, bg: Background):
        bg.draw(surf, self.frame)

        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (10, 3, 0, 175), (0, 0, SCREEN_W, SCREEN_H))
        surf.blit(overlay, (0, 0))

        # Título
        _outline_text(surf, self.font_med, "MENÚ PRINCIPAL",
                      C_TEXT_GOLD, C_TEXT_OUT, SCREEN_W // 2, 36)
        lw = 520
        pygame.draw.line(surf, C_UI_BORDER,
                         (SCREEN_W // 2 - lw // 2, 60),
                         (SCREEN_W // 2 + lw // 2, 60), 2)

        # Cuadrícula 3×2
        cols, rows = 3, 2
        card_w, card_h = 245, 158
        gap_x, gap_y   = 22, 18
        grid_w = cols * card_w + (cols - 1) * gap_x
        grid_h = rows * card_h + (rows - 1) * gap_y
        sx = SCREEN_W  // 2 - grid_w // 2
        sy = SCREEN_H  // 2 - grid_h // 2 + 12

        self._card_rects = []

        for i, opt in enumerate(MENU_OPTIONS):
            col = i % cols
            row = i // cols
            slide = max(0.0, min(1.0, 1.0 - (self.enter_anim - i) * 0.22))
            slide_off = int((1.0 - slide) * 55)

            cx_card = sx + col * (card_w + gap_x)
            cy_card = sy + row * (card_h + gap_y) + slide_off
            rect = pygame.Rect(cx_card, cy_card, card_w, card_h)

            is_sel   = (self.selected == i)
            is_hover = (self.hover == i)
            is_active = opt["state"] == "fight"

            if is_sel or is_hover:
                rect = rect.move(0, -6)
            self._card_rects.append(rect)

            accent = ACCENTS.get(opt["label"], C_TEXT_GOLD)
            self._draw_card(surf, rect, opt, is_sel, is_hover, is_active, accent)

        # Descripción
        desc = DESCRIPTIONS.get(MENU_OPTIONS[self.selected]["label"], "")
        ds = self.font_small.render(desc, True, (200, 160, 80))
        surf.blit(ds, (SCREEN_W // 2 - ds.get_width() // 2,
                        sy + grid_h + 16))

        # Botón volver
        bw, bh = 160, 38
        bx = 22
        by = SCREEN_H - bh - 14
        self._back_rect = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(surf, C_TEXT_OUT,  (bx, by, bw, bh), border_radius=6)
        pygame.draw.rect(surf, (55, 20, 0), (bx+2, by+2, bw-4, bh-4), border_radius=5)
        pygame.draw.rect(surf, C_UI_BORDER, (bx, by, bw, bh), 2, border_radius=6)
        bt = self.font_small.render("◀  TÍTULO", True, C_TEXT_GOLD)
        surf.blit(bt, (bx + bw//2 - bt.get_width()//2, by + bh//2 - bt.get_height()//2))

        # Hint teclado
        hint = self.font_small.render(
            "↑↓←→ Navegar   ENTER Seleccionar   ESC Volver",
            True, (140, 90, 20))
        surf.blit(hint, (SCREEN_W - hint.get_width() - 16, SCREEN_H - 26))

    def _draw_card(self, surf, rect, opt, is_sel, is_hover, is_active, accent):
        x, y, w, h = rect

        # Sombra
        sh = pygame.Surface((w + 4, h + 6), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 100), (4, 6, w, h), border_radius=12)
        surf.blit(sh, (x - 2, y))

        # Fondo
        bg_col = (52, 20, 0) if (is_sel or is_hover) else (28, 9, 0)
        pygame.draw.rect(surf, bg_col, rect, border_radius=12)

        # Borde
        bw = 3 if (is_sel or is_hover) else 2
        bc = accent if (is_sel or is_hover) else (80, 35, 0)
        pygame.draw.rect(surf, bc, rect, bw, border_radius=12)

        # Barra superior de color
        bar_col = accent if is_active else tuple(c // 2 for c in accent)
        pygame.draw.rect(surf, bar_col, (x + bw, y + bw, w - bw * 2, 6))

        # Ícono
        icon_key = ICONS.get(opt["label"], "espadas")
        icon_col  = accent if is_active else tuple(max(0, c - 60) for c in accent)
        self._draw_icon(surf, icon_key, x + w // 2, y + 54, icon_col, is_sel or is_hover)

        # Nombre
        lc = accent if is_active else (120, 70, 25)
        ls = self.font_med.render(opt["label"], True, lc)
        surf.blit(ls, (x + w // 2 - ls.get_width() // 2, y + h - 54))

        # Badge
        if not is_active:
            bs = self.font_small.render("PRÓXIMO", True, (100, 55, 18))
            bx2 = x + w // 2 - bs.get_width() // 2
            by2 = y + h - 28
            pygame.draw.rect(surf, (45, 18, 3),
                             (bx2 - 6, by2 - 2, bs.get_width() + 12, bs.get_height() + 4),
                             border_radius=4)
            surf.blit(bs, (bx2, by2))
        else:
            bs = self.font_small.render("▶  JUGAR", True, accent)
            bx2 = x + w // 2 - bs.get_width() // 2
            surf.blit(bs, (bx2, y + h - 28))

        # Glow hover
        if is_sel or is_hover:
            glow = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*accent, 22), (0, 0, w, h), border_radius=12)
            surf.blit(glow, (x, y))

    def _draw_icon(self, surf, icon_key, cx, cy, color, bright):
        dim = tuple(max(0, c - 50) for c in color) if not bright else color

        if icon_key == "libro":
            pygame.draw.rect(surf, dim, (cx - 22, cy - 16, 20, 28), border_radius=2)
            pygame.draw.rect(surf, dim, (cx + 2,  cy - 16, 20, 28), border_radius=2)
            pygame.draw.line(surf, color, (cx, cy - 16), (cx, cy + 12), 3)
            pygame.draw.arc(surf, color,  (cx - 22, cy - 20, 44, 12), 0, math.pi, 2)

        elif icon_key == "joystick":
            pygame.draw.circle(surf, dim,   (cx, cy + 8), 17)
            pygame.draw.circle(surf, color, (cx, cy + 8), 14, 2)
            pygame.draw.line(surf, dim,     (cx, cy - 16), (cx, cy - 2), 5)
            pygame.draw.circle(surf, dim,   (cx, cy - 17), 7)
            pygame.draw.circle(surf, color, (cx, cy - 17), 5)
            for ox in (-9, 9):
                pygame.draw.circle(surf, color, (cx + ox, cy + 6), 3)
            pygame.draw.circle(surf, color, (cx, cy - 2), 3)

        elif icon_key == "espadas":
            for sign in (-1, 1):
                pygame.draw.line(surf, dim,
                                 (cx - sign * 18, cy - 19),
                                 (cx + sign * 18, cy + 19), 5)
                pygame.draw.line(surf, color,
                                 (cx - sign * 18, cy - 19),
                                 (cx + sign * 18, cy + 19), 3)
                gy = cy - sign * 4
                pygame.draw.line(surf, color, (cx - 9, gy), (cx + 9, gy), 4)

        elif icon_key == "red":
            pygame.draw.circle(surf, dim,   (cx, cy), 18)
            pygame.draw.circle(surf, color, (cx, cy), 16, 2)
            pygame.draw.line(surf, color,   (cx - 16, cy), (cx + 16, cy), 2)
            pygame.draw.line(surf, color,   (cx, cy - 16), (cx, cy + 16), 2)
            pygame.draw.arc(surf, color,    (cx - 9, cy - 16, 18, 32), 0, math.pi * 2, 2)

        elif icon_key == "bolsa":
            pygame.draw.rect(surf, dim,   (cx - 14, cy - 6, 28, 22), border_radius=4)
            pygame.draw.rect(surf, color, (cx - 12, cy - 4, 24, 18), border_radius=3)
            pygame.draw.arc(surf, color,  (cx - 9, cy - 19, 18, 18), 0, math.pi, 3)
            ds = self.font_small.render("$", True, color)
            surf.blit(ds, (cx - ds.get_width() // 2, cy - 3))

        elif icon_key == "engrane":
            pygame.draw.circle(surf, dim,   (cx, cy), 17)
            pygame.draw.circle(surf, color, (cx, cy), 14, 2)
            pygame.draw.circle(surf, dim,   (cx, cy), 6)
            for a in range(0, 360, 45):
                rad = math.radians(a)
                ix = cx + int(math.cos(rad) * 17)
                iy = cy + int(math.sin(rad) * 17)
                pygame.draw.circle(surf, color, (ix, iy), 4)


# ─────────────────────────────────────────────
#  Pantalla "Próximamente"
# ─────────────────────────────────────────────
class ComingSoonScreen:
    def __init__(self, fonts, option_name: str):
        self.font_big, self.font_med, self.font_small = fonts
        self.option_name = option_name
        self.frame = 0
        self._back_rect = None
        self.accent = ACCENTS.get(option_name, C_TEXT_GOLD)

    def update(self):
        self.frame += 1

    def draw(self, surf: pygame.Surface, bg: Background):
        bg.draw(surf, self.frame)
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (10, 3, 0, 210), (0, 0, SCREEN_W, SCREEN_H))
        surf.blit(overlay, (0, 0))

        # Círculo grande con ícono
        r = 65 + int(math.sin(self.frame * 0.07) * 6)
        cx, cy_circle = SCREEN_W // 2, SCREEN_H // 2 - 65
        pygame.draw.circle(surf, C_TEXT_OUT,  (cx, cy_circle), r + 5)
        pygame.draw.circle(surf, (45, 15, 0), (cx, cy_circle), r)
        pygame.draw.circle(surf, self.accent,  (cx, cy_circle), r, 3)

        # Ícono en el círculo
        icon_key = ICONS.get(self.option_name, "espadas")
        menu_inst = MainMenu.__new__(MainMenu)
        menu_inst.font_small = self.font_small
        menu_inst._draw_icon(surf, icon_key, cx, cy_circle,
                             self.accent, True)

        _outline_text(surf, self.font_med,
                      self.option_name.upper(),
                      self.accent, C_TEXT_OUT,
                      SCREEN_W // 2, cy_circle + r + 30)

        _outline_text(surf, self.font_big,
                      "PRÓXIMAMENTE",
                      C_TEXT_GOLD, C_TEXT_OUT,
                      SCREEN_W // 2, SCREEN_H // 2 + 40)

        msg = self.font_small.render(
            "Este modo llegará pronto. ¡Estate atento!", True, (200, 140, 50))
        surf.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, SCREEN_H // 2 + 85))

        # Botón volver
        bw, bh = 240, 50
        bx = SCREEN_W // 2 - bw // 2
        by = SCREEN_H - 76
        bob = int(math.sin(self.frame * 0.08) * 4)
        self._back_rect = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(surf, C_TEXT_OUT, (bx, by + bob, bw, bh), border_radius=8)
        pygame.draw.rect(surf, C_SKY_BOT,  (bx+2, by+2+bob, bw-4, bh-4), border_radius=7)
        pygame.draw.rect(surf, C_TEXT_OUT, (bx, by + bob, bw, bh), 2, border_radius=8)
        bt = self.font_small.render("◀  Volver al Menú", True, C_UI_BG)
        surf.blit(bt, (SCREEN_W // 2 - bt.get_width() // 2,
                        by + bh // 2 - bt.get_height() // 2 + bob))

    def handle_click(self, pos):
        if self._back_rect and self._back_rect.collidepoint(pos):
            return "menu"
        return None


# ─────────────────────────────────────────────
#  Clase principal del juego
# ─────────────────────────────────────────────
class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.clock  = pygame.time.Clock()
        self.bg     = Background()
        self.hud    = HUD()

        try:
            self.font_big   = pygame.font.SysFont("impact", 72)
            self.font_med   = pygame.font.SysFont("impact", 40)
            self.font_small = pygame.font.SysFont("impact", 22)
        except Exception:
            self.font_big   = pygame.font.Font(None, 72)
            self.font_med   = pygame.font.Font(None, 40)
            self.font_small = pygame.font.Font(None, 22)

        self._fonts = (self.font_big, self.font_med, self.font_small)
        self._reset_all()

    def _reset_all(self):
        self.state          = GameState.TITLE
        self.frame          = 0
        self._prev_keys     = {}
        self.announce_delay = 0
        self.title_screen   = TitleScreen(self._fonts)
        self.main_menu      = MainMenu(self._fonts)
        self.coming_soon    = None
        self._init_fight()

    def _init_fight(self):
        self.p1        = _make_p1()
        self.p2        = _make_p2()
        self.round_num = 1
        self.p1_wins   = 0
        self.p2_wins   = 0

    # ── Loop ──────────────────────────────────
    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            running = self._handle_events()
            self._update()
            self._draw()
        pygame.quit()

    # ── Eventos ───────────────────────────────
    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self._handle_keydown(event.key) == "quit":
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)
        return True

    def _handle_keydown(self, key):
        if self.state == GameState.TITLE:
            if key == pygame.K_ESCAPE:
                return "quit"
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                self._go_to_menu()

        elif self.state == GameState.MENU:
            result = self.main_menu.handle_key(key)
            if result == "title":
                self.state = GameState.TITLE
            elif result == "fight":
                self._start_battle()
            elif result == "coming_soon":
                label = MENU_OPTIONS[self.main_menu.selected]["label"]
                self.coming_soon = ComingSoonScreen(self._fonts, label)
                self.state = GameState.COMING_SOON

        elif self.state == GameState.COMING_SOON:
            if key == pygame.K_ESCAPE:
                self.state = GameState.MENU

        elif self.state in (GameState.FIGHT, GameState.ROUND_END,
                            GameState.ANNOUNCE, GameState.GAME_OVER):
            if key == pygame.K_ESCAPE:
                self.state = GameState.MENU
            if self.state == GameState.GAME_OVER and key in (
                    pygame.K_RETURN, pygame.K_SPACE):
                self._start_battle()

        return None

    def _handle_click(self, pos):
        if self.state == GameState.TITLE:
            if self.title_screen._btn_rect and \
               self.title_screen._btn_rect.collidepoint(pos):
                self._go_to_menu()

        elif self.state == GameState.MENU:
            result = self.main_menu.handle_click(pos)
            if result == "title":
                self.state = GameState.TITLE
            elif result == "fight":
                self._start_battle()
            elif result == "coming_soon":
                label = MENU_OPTIONS[self.main_menu.selected]["label"]
                self.coming_soon = ComingSoonScreen(self._fonts, label)
                self.state = GameState.COMING_SOON

        elif self.state == GameState.COMING_SOON and self.coming_soon:
            result = self.coming_soon.handle_click(pos)
            if result == "menu":
                self.state = GameState.MENU

    def _go_to_menu(self):
        self.main_menu = MainMenu(self._fonts)
        self.state = GameState.MENU

    def _start_battle(self):
        self._init_fight()
        self.state = GameState.ANNOUNCE
        self.hud.show_announcement(f"ROUND  {self.round_num}\n¡PELEA!", 140)
        self.announce_delay = 145

    # ── Update ────────────────────────────────
    def _update(self):
        self.frame += 1

        if self.state == GameState.TITLE:
            self.title_screen.update()

        elif self.state == GameState.MENU:
            self.main_menu.update()

        elif self.state == GameState.COMING_SOON and self.coming_soon:
            self.coming_soon.update()

        elif self.state == GameState.ANNOUNCE:
            self.hud.update()
            self.announce_delay -= 1
            if self.announce_delay <= 0:
                self.state = GameState.FIGHT

        elif self.state == GameState.FIGHT:
            self.hud.update()
            raw  = pygame.key.get_pressed()
            keys = self._build_keys(raw)
            self.p1.update(self.p2, keys)
            self.p2.update(self.p1, {})
            self.p1.check_hit(self.p2)
            self.p2.check_hit(self.p1)
            self._prev_keys = {k: bool(raw[k])
                               for k in [pygame.K_j, pygame.K_k, pygame.K_l]}
            if self.p1.ko or self.p2.ko:
                self.state = GameState.ROUND_END
                self.announce_delay = 90
                winner = "¡JARRO GANA!" if self.p1.ko else "¡COPAS GANA!"
                self.hud.show_announcement(f"K.O.!\n{winner}", 85)
                if self.p1.ko:
                    self.p2_wins += 1
                else:
                    self.p1_wins += 1

        elif self.state == GameState.ROUND_END:
            self.hud.update()
            self.p1.update(self.p2, {})
            self.p2.update(self.p1, {})
            self.announce_delay -= 1
            if self.announce_delay <= 0:
                if self.p1_wins >= 2 or self.p2_wins >= 2:
                    self.state = GameState.GAME_OVER
                    champ = "¡COPAS\nCAMPEÓN!" if self.p1_wins >= 2 else "¡JARRO\nCAMPEÓN!"
                    self.hud.show_announcement(champ, 9999)
                else:
                    self.round_num += 1
                    self._init_fight()
                    self.state = GameState.ANNOUNCE
                    self.hud.show_announcement(f"ROUND  {self.round_num}\n¡PELEA!", 140)
                    self.announce_delay = 145

        elif self.state == GameState.GAME_OVER:
            self.hud.update()
            self.p1.update(self.p2, {})
            self.p2.update(self.p1, {})

    def _build_keys(self, raw) -> dict:
        keys = {}
        for k in [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s,
                  pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_SPACE]:
            keys[k] = bool(raw[k])
        keys["_punch_just"]   = bool(raw[pygame.K_j]) and not self._prev_keys.get(pygame.K_j, False)
        keys["_kick_just"]    = bool(raw[pygame.K_k]) and not self._prev_keys.get(pygame.K_k, False)
        keys["_special_just"] = bool(raw[pygame.K_l]) and not self._prev_keys.get(pygame.K_l, False)
        return keys

    # ── Draw ──────────────────────────────────
    def _draw(self):
        if self.state == GameState.TITLE:
            self.title_screen.draw(self.screen)

        elif self.state == GameState.MENU:
            self.main_menu.draw(self.screen, self.bg)

        elif self.state == GameState.COMING_SOON and self.coming_soon:
            self.coming_soon.draw(self.screen, self.bg)

        else:
            self.bg.draw(self.screen, self.frame)
            self.p2.draw(self.screen)
            self.p1.draw(self.screen)
            self.hud.draw(self.screen, self.p1, self.p2,
                          self.round_num, self.p1_wins, self.p2_wins)

            if self.state == GameState.GAME_OVER:
                hint = self.font_small.render(
                    "ENTER  ·  Revancha     ESC  ·  Menú",
                    True, (200, 134, 10))
                self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2,
                                        SCREEN_H - 36))
            self._draw_vignette()

        pygame.display.flip()

    def _draw_vignette(self):
        v = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for i in range(50):
            a = int(i * 3)
            r = int(math.sqrt((SCREEN_W//2)**2 + (SCREEN_H//2)**2) - i * 7)
            if r <= 0:
                break
            pygame.draw.ellipse(v, (0, 0, 0, a),
                                (SCREEN_W//2 - r, SCREEN_H//2 - int(r*0.6),
                                 r*2, int(r*1.2)), 8)
        self.screen.blit(v, (0, 0))
