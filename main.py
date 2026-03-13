#!/usr/bin/env python3
# ─────────────────────────────────────────────
#  CupFight! — main.py
#  Juego de peleas 2D estilo años 30 / Cuphead
#  Hecho con Pygame-CE
#
#  Instalar:  pip install pygame-ce
#  Ejecutar:  python main.py
# ─────────────────────────────────────────────
import pygame
from src.constants import SCREEN_W, SCREEN_H, TITLE, FPS
from src.game import Game


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)

    screen = pygame.display.set_mode(
        (SCREEN_W, SCREEN_H),
        pygame.DOUBLEBUF | pygame.HWSURFACE,
    )

    # Ícono de ventana (cup simple dibujado)
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.polygon(icon, (245, 200, 66),
                        [(4, 28), (28, 28), (24, 6), (8, 6)])
    pygame.draw.ellipse(icon, (245, 200, 66), (6, 2, 20, 10))
    pygame.display.set_icon(icon)

    game = Game(screen)
    game.run()


if __name__ == "__main__":
    main()
