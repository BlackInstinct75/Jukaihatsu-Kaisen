# ─────────────────────────────────────────────
#  CupFight! — background.py
# ─────────────────────────────────────────────
import pygame
import math
from src.constants import *


class Background:
    """
    Fondo estilo años 30 / Cuphead.
    Se renderiza a una superficie estática y se actualiza sólo
    lo que es dinámico (nubes).
    """

    def __init__(self):
        self.clouds = [
            {"x": 80,  "y": 60,  "scale": 1.1, "speed": 0.04},
            {"x": 300, "y": 40,  "scale": 0.8, "speed": 0.03},
            {"x": 560, "y": 70,  "scale": 1.2, "speed": 0.05},
            {"x": 780, "y": 50,  "scale": 0.7, "speed": 0.06},
        ]
        self._static = None   # caché del fondo sin nubes

    def _build_static(self) -> pygame.Surface:
        surf = pygame.Surface((SCREEN_W, SCREEN_H))

        # Cielo degradado (línea a línea)
        sky_h = SCREEN_H - 110
        for row in range(sky_h):
            t = row / sky_h
            r = int(C_SKY_TOP[0] + (C_SKY_BOT[0] - C_SKY_TOP[0]) * t)
            g = int(C_SKY_TOP[1] + (C_SKY_BOT[1] - C_SKY_TOP[1]) * t)
            b = int(C_SKY_TOP[2] + (C_SKY_BOT[2] - C_SKY_TOP[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, row), (SCREEN_W, row))

        # Edificios en silueta
        buildings = [
            (30,  SCREEN_H - 200, 90, 170),
            (160, SCREEN_H - 230, 70, 200),
            (270, SCREEN_H - 190, 55, 160),
            (620, SCREEN_H - 210, 85, 180),
            (750, SCREEN_H - 190, 65, 160),
            (860, SCREEN_H - 215, 80, 185),
        ]
        for bx, by, bw, bh in buildings:
            self._draw_building(surf, bx, by, bw, bh)

        # Suelo
        pygame.draw.rect(surf, C_GROUND, (0, GROUND_Y, SCREEN_W, SCREEN_H - GROUND_Y))

        # Borde superior del suelo (accidentado)
        for i in range(0, SCREEN_W, 28):
            h = 5 + math.sin(i * 0.3) * 3
            pygame.draw.ellipse(surf, (160, 90, 10),
                                (i, GROUND_Y - int(h), 30, int(h) * 2))

        # Franja del suelo
        pygame.draw.line(surf, C_GROUND_D, (0, GROUND_Y + 30), (SCREEN_W, GROUND_Y + 30), 3)

        # Puntos decorativos del suelo
        for i in range(20, SCREEN_W, 55):
            pygame.draw.ellipse(surf, C_GROUND_D, (i - 4, GROUND_Y + 42, 8, 6))

        return surf

    def _draw_building(self, surf, x, y, w, h):
        # Cuerpo del edificio
        pygame.draw.rect(surf, C_BUILD, (x, y, w, h))

        # Ventanas
        win_color = (160, 90, 10)
        for wy in range(y + 15, y + h - 20, 28):
            for wx in range(x + 10, x + w - 10, 20):
                pygame.draw.rect(surf, win_color, (wx, wy, 9, 11))

        # Tejado / remate
        pygame.draw.rect(surf, (180, 100, 20),
                         (x - 4, y - 8, w + 8, 12), border_radius=3)

    def draw(self, surf: pygame.Surface, frame: int):
        # Construir caché estático una sola vez
        if self._static is None:
            self._static = self._build_static()

        surf.blit(self._static, (0, 0))

        # Nubes animadas (se mueven lentamente)
        for c in self.clouds:
            ox = (c["x"] + frame * c["speed"]) % (SCREEN_W + 220) - 110
            self._draw_cloud(surf, ox, c["y"], c["scale"])

    def _draw_cloud(self, surf, x, y, scale):
        blobs = [
            (-20,  0,  34, 22),
            ( 10, -14, 28, 20),
            ( 36,  4,  30, 20),
            ( 55,  0,  22, 18),
            ( -5,  8,  40, 18),
        ]
        for bx, by, bw, bh in blobs:
            rx = int(x + bx * scale)
            ry = int(y + by * scale)
            rw = max(4, int(bw * scale))
            rh = max(4, int(bh * scale))
            pygame.draw.ellipse(surf, C_CLOUD_OUT, (rx - 2, ry - 2, rw + 4, rh + 4))
            pygame.draw.ellipse(surf, C_CLOUD,     (rx, ry, rw, rh))
