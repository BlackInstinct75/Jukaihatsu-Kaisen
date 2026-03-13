# ─────────────────────────────────────────────
#  CupFight! — hud.py
# ─────────────────────────────────────────────
import pygame
import math
from src.constants import *


def _outline_text(surf, font, text, color, outline_color, x, y, center=True):
    """Dibuja texto con contorno grueso (estilo años 30)."""
    rendered_outline = font.render(text, True, outline_color)
    rendered_text    = font.render(text, True, color)
    w, h = rendered_text.get_size()
    ox = x - w // 2 if center else x
    oy = y - h // 2 if center else y
    for dx in (-2, 0, 2):
        for dy in (-2, 0, 2):
            if dx != 0 or dy != 0:
                surf.blit(rendered_outline, (ox + dx, oy + dy))
    surf.blit(rendered_text, (ox, oy))


class HUD:
    """
    Muestra las barras de vida, nombres, rondas y anuncios.
    """

    def __init__(self):
        pygame.font.init()
        # Intentar cargar fuentes del sistema; fallback a la por defecto
        try:
            self.font_big   = pygame.font.SysFont("impact", 52)
            self.font_med   = pygame.font.SysFont("impact", 32)
            self.font_small = pygame.font.SysFont("impact", 22)
        except Exception:
            self.font_big   = pygame.font.Font(None, 52)
            self.font_med   = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 22)

        # Estado de anuncio
        self.announce_text  = ""
        self.announce_timer = 0
        self.announce_alpha = 0

    # ── Anuncio central ───────────────────────────
    def show_announcement(self, text: str, duration: int = 120):
        self.announce_text  = text
        self.announce_timer = duration

    # ── Update ────────────────────────────────────
    def update(self):
        if self.announce_timer > 0:
            self.announce_timer -= 1
            fade_frames = 15
            if self.announce_timer > fade_frames:
                self.announce_alpha = 255
            else:
                self.announce_alpha = int(255 * self.announce_timer / fade_frames)

    # ── Draw ──────────────────────────────────────
    def draw(self, surf: pygame.Surface, p1, p2, round_num: int,
             p1_wins: int, p2_wins: int):

        self._draw_player_hud(surf, p1, left=True,  wins=p1_wins)
        self._draw_player_hud(surf, p2, left=False, wins=p2_wins)
        self._draw_round(surf, round_num)

        if self.announce_timer > 0:
            self._draw_announcement(surf)

    def _draw_player_hud(self, surf, player, left: bool, wins: int):
        pad = 18
        bar_w = 320
        bar_h = 22

        x = pad if left else SCREEN_W - pad - bar_w
        y = 14

        # Panel de fondo
        panel = pygame.Surface((bar_w + 10, 70), pygame.SRCALPHA)
        pygame.draw.rect(panel, (26, 8, 0, 180), (0, 0, bar_w + 10, 70), border_radius=6)
        surf.blit(panel, (x - 5, y - 5))

        # Nombre
        name_x = x if left else x + bar_w
        _outline_text(surf, self.font_small, player.name,
                      C_TEXT_GOLD, C_TEXT_OUT,
                      name_x, y + 2, center=False)

        # Barra de vida
        by = y + 26
        pygame.draw.rect(surf, C_HP_BG,     (x, by, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(surf, C_HP_BORDER, (x, by, bar_w, bar_h), 3, border_radius=4)

        hp_pct = max(0.0, player.hp / player.max_hp)
        hp_color = (
            C_HP_BAR if hp_pct > 0.4
            else (255, 165, 0) if hp_pct > 0.2
            else (255, 50, 50)
        )
        inner_w = max(0, int((bar_w - 4) * hp_pct))
        if inner_w > 0:
            inner_x = x + 2 if left else x + 2 + (bar_w - 4 - inner_w)
            pygame.draw.rect(surf, hp_color,
                             (inner_x, by + 2, inner_w, bar_h - 4),
                             border_radius=3)
            # Brillo
            shine_w = max(0, inner_w - 8)
            if shine_w > 0:
                shine = pygame.Surface((shine_w, 5), pygame.SRCALPHA)
                shine.fill((255, 255, 255, 60))
                surf.blit(shine, (inner_x + 4, by + 3))

        # Puntos de ronda (estrellitas)
        for i in range(wins):
            sx = x + 4 + i * 20 if left else x + bar_w - 4 - i * 20
            self._draw_small_star(surf, sx, by + bar_h + 10, C_TEXT_GOLD)

    def _draw_small_star(self, surf, cx, cy, color):
        pts = []
        for i in range(10):
            r = 7 if i % 2 == 0 else 3
            a = i * math.pi / 5 - math.pi / 2
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        pygame.draw.polygon(surf, C_TEXT_OUT, pts)
        inner = [(cx + (r - 1.5) * math.cos(i * math.pi / 5 - math.pi / 2),
                  cy + (r - 1.5) * math.sin(i * math.pi / 5 - math.pi / 2))
                 for i, r in [(j, 7 if j % 2 == 0 else 3) for j in range(10)]]
        pygame.draw.polygon(surf, color, inner)

    def _draw_round(self, surf, round_num):
        _outline_text(surf, self.font_small,
                      f"ROUND  {round_num}",
                      C_TEXT_GOLD, C_TEXT_OUT,
                      SCREEN_W // 2, 20)

    def _draw_announcement(self, surf):
        a = self.announce_alpha
        lines = self.announce_announce_text if hasattr(self, 'announce_announce_text') \
            else self.announce_text.split("\n")

        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

        total_h = len(lines) * 72
        start_y = SCREEN_H // 2 - total_h // 2

        for i, line in enumerate(lines):
            # Efecto de escala en entrada
            scale = 1.0
            if self.announce_timer > 100:
                scale = 1.0 + (self.announce_timer - 100) * 0.015

            font = self.font_big
            rendered = font.render(line, True, C_TEXT_GOLD)
            if scale != 1.0:
                new_w = int(rendered.get_width() * scale)
                new_h = int(rendered.get_height() * scale)
                rendered = pygame.transform.scale(rendered, (new_w, new_h))

            w, h = rendered.get_size()
            x = SCREEN_W // 2 - w // 2
            y = start_y + i * 72 - h // 2

            # Contorno
            outline_r = font.render(line, True, C_TEXT_OUT)
            if scale != 1.0:
                outline_r = pygame.transform.scale(outline_r, (w, h))
            outline_r.set_alpha(a)

            for dx in (-3, 0, 3):
                for dy in (-3, 0, 3):
                    if dx or dy:
                        surf.blit(outline_r, (x + dx, y + dy))

            rendered.set_alpha(a)
            surf.blit(rendered, (x, y))

    # Sobrescribir para soportar multilínea correctamente
    @property
    def announce_text(self):
        return self._announce_text

    @announce_text.setter
    def announce_text(self, val):
        self._announce_text = val
