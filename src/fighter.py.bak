# ─────────────────────────────────────────────
#  CupFight! — fighter.py
# ─────────────────────────────────────────────
import pygame
import math
import random
from src.constants import *


class Particle:
    """Chispa / estrella al recibir golpe."""
    def __init__(self, x, y, kind="spark"):
        self.x = x
        self.y = y
        self.vx = random.uniform(-6, 6)
        self.vy = random.uniform(-8, -2)
        self.life = random.randint(20, 35)
        self.max_life = self.life
        self.angle = random.uniform(0, math.pi * 2)
        self.rot = random.uniform(-0.3, 0.3)
        self.kind = kind   # "spark" | "star"
        self.size = random.randint(4, 8)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.35
        self.life -= 1
        self.angle += self.rot
        return self.life > 0

    def draw(self, surf):
        alpha = int(255 * self.life / self.max_life)
        if self.kind == "star":
            color = (*C_SPECIAL_FX, alpha)
            self._draw_star(surf, color)
        else:
            color = (*C_HIT_SPARK, alpha)
            pygame.draw.ellipse(surf, color[:3],
                                (int(self.x) - self.size // 2,
                                 int(self.y) - self.size // 4,
                                 self.size, self.size // 2))

    def _draw_star(self, surf, color):
        pts = 5
        r_out, r_in = self.size, self.size // 2
        points = []
        for i in range(pts * 2):
            r = r_out if i % 2 == 0 else r_in
            a = self.angle + i * math.pi / pts
            points.append((self.x + r * math.cos(a),
                           self.y + r * math.sin(a)))
        if len(points) >= 3:
            pygame.draw.polygon(surf, color[:3], points)


# ─────────────────────────────────────────────
class Fighter:
    """
    Luchador estilo rubber-hose (años 30).
    Todo se dibuja con pygame.draw — sin sprites externos.
    """

    def __init__(self, x: int, facing: int, is_player: bool,
                 palette: dict, name: str):
        # Posición y física
        self.x = float(x)
        self.y = float(GROUND_Y - 110)
        self.vx = 0.0
        self.vy = 0.0

        # Lógica
        self.facing   = facing      # +1 = derecha, -1 = izquierda
        self.is_player = is_player
        self.pal       = palette
        self.name      = name

        # Combate
        self.max_hp      = MAX_HP
        self.hp          = MAX_HP
        self.state       = State.IDLE
        self.atk_timer   = 0        # frames restantes del ataque
        self.atk_damage  = 0
        self.hit_cool    = 0        # cooldown entre ataques
        self.hit_stun    = 0        # frames de hit-stun
        self.hit_flash   = 0        # parpadeo al ser golpeado
        self.block_cool  = 0
        self.is_blocking = False
        self.on_ground   = True
        self.ko          = False

        # Hitbox activa de ataque (Rect o None)
        self.attack_hb: pygame.Rect | None = None

        # Partículas
        self.particles: list[Particle] = []

        # Animación
        self.frame  = 0
        self.ftimer = 0           # contador para avanzar frame

        # IA
        self.ai_timer  = 0
        self.ai_action = None     # "left" | "right" | "block" | None

    # ── Hitbox del cuerpo ──────────────────────────
    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), 68, 110)

    @property
    def cx(self) -> float:
        return self.x + 34

    @property
    def feet(self) -> float:
        return self.y + 110

    # ── Helpers de estado ──────────────────────────
    def is_attacking(self) -> bool:
        return self.state in (State.ATTACK, State.KICK, State.SPECIAL)

    def is_busy(self) -> bool:
        return self.is_attacking() or self.state == State.HIT

    # ── Update principal ───────────────────────────
    def update(self, other: "Fighter", keys_held: dict):
        if self.ko:
            self._update_ko()
            return

        # Input o IA
        if self.is_player:
            self._handle_input(keys_held)
        else:
            self._handle_ai(other)

        # Física
        self._apply_physics()

        # Timers
        self.atk_timer  = max(0, self.atk_timer  - 1)
        self.hit_cool   = max(0, self.hit_cool   - 1)
        self.hit_stun   = max(0, self.hit_stun   - 1)
        self.hit_flash  = max(0, self.hit_flash  - 1)
        self.block_cool = max(0, self.block_cool - 1)

        # Actualizar hitbox de ataque
        self._update_attack_hb()

        # Actualizar estado (sólo si no está ocupado)
        if not self.is_attacking() and self.state != State.HIT:
            if not self.on_ground:
                self.state = State.JUMP
            elif abs(self.vx) > 0.5:
                self.state = State.WALK
            elif self.is_blocking:
                self.state = State.BLOCK
            else:
                self.state = State.IDLE

        if self.state == State.HIT and self.hit_stun == 0:
            self.state = State.IDLE

        # Orientar hacia el oponente
        if not self.is_attacking():
            self.facing = 1 if other.cx > self.cx else -1

        # Partículas
        self.particles = [p for p in self.particles if p.update()]

        # Animación
        self.ftimer += 1
        if self.ftimer >= 6:
            self.ftimer = 0
            self.frame += 1

    def _update_ko(self):
        self.vy += GRAVITY
        self.y = min(self.y + self.vy, GROUND_Y - 110)
        if self.y >= GROUND_Y - 110:
            self.vy = 0
        self.particles = [p for p in self.particles if p.update()]

    def _apply_physics(self):
        self.vy += GRAVITY
        self.x  += self.vx
        self.y  += self.vy

        # Suelo
        if self.y >= GROUND_Y - 110:
            self.y = GROUND_Y - 110
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Fricción en suelo
        if self.on_ground:
            self.vx *= FRICTION

        # Límites de pantalla
        self.x = max(10.0, min(float(SCREEN_W - 78), self.x))

    # ── Hitbox de ataque ───────────────────────────
    def _update_attack_hb(self):
        if self.atk_timer > 0:
            reach = {"attack": 75, "kick": 90, "special": 120}.get(self.state, 75)
            hy = int(self.y + (70 if self.state == State.KICK else 38))
            hx = int(self.cx) if self.facing == 1 else int(self.cx - reach)
            self.attack_hb = pygame.Rect(hx, hy, reach, 32)
        else:
            self.attack_hb = None

    # ── Comprobar si golpea al oponente ───────────
    def check_hit(self, other: "Fighter"):
        if not self.attack_hb:
            return
        if not self.attack_hb.colliderect(other.rect):
            return

        dmg = self.atk_damage
        if other.is_blocking:
            dmg = max(1, int(dmg * BLOCK_MULT))
        else:
            other.hit_stun = HIT_STUN
            other.state    = State.HIT
            other.vx       = self.facing * 6
            other.vy       = -5
            # Partículas
            kind = "star" if self.state == State.SPECIAL else "spark"
            for _ in range(6):
                other.particles.append(Particle(other.cx, other.y + 40, kind))

        other.hp = max(0, other.hp - dmg)
        other.hit_flash = 14
        self.attack_hb = None   # un golpe por swing
        self.atk_timer = 0

        if other.hp <= 0:
            other.ko    = True
            other.state = State.KO
            other.vy    = -10

    # ── Input del jugador ─────────────────────────
    def _handle_input(self, keys: dict):
        if self.is_busy():
            return

        # Bloquear
        self.is_blocking = keys.get(pygame.K_s) and self.on_ground

        if self.is_blocking:
            self.vx    = 0
            self.state = State.BLOCK
            return

        # Movimiento
        self.vx = 0
        if keys.get(pygame.K_a) or keys.get(pygame.K_LEFT):
            self.vx = -MOVE_SPEED
        if keys.get(pygame.K_d) or keys.get(pygame.K_RIGHT):
            self.vx = MOVE_SPEED

        # Salto
        if (keys.get(pygame.K_w) or keys.get(pygame.K_SPACE)) and self.on_ground:
            self.vy = JUMP_FORCE

        # Ataques (un único disparo por pulsación — gestionado en Game)
        if keys.get("_punch_just"):
            self._start_attack(State.ATTACK, ATTACK_DURATION,  DMG_PUNCH)
        elif keys.get("_kick_just"):
            self._start_attack(State.KICK,   KICK_DURATION,    DMG_KICK)
        elif keys.get("_special_just"):
            self._start_attack(State.SPECIAL, SPECIAL_DURATION, DMG_SPECIAL)

    def _start_attack(self, kind: str, duration: int, damage: int):
        if self.hit_cool > 0:
            return
        self.state      = kind
        self.atk_timer  = duration
        self.atk_damage = damage
        self.hit_cool   = ATTACK_COOLDOWN
        self.vx         = 0

    # ── IA ────────────────────────────────────────
    def _handle_ai(self, other: "Fighter"):
        self.ai_timer -= 1
        dist = other.cx - self.cx
        abs_dist = abs(dist)

        self.is_blocking = False

        if self.ai_timer <= 0:
            self.ai_timer = random.randint(15, 40)
            r = random.random()

            if abs_dist < 95 and r < 0.22:
                self.ai_action = "block"
            elif abs_dist < 100 and not self.is_busy() and r < 0.80:
                roll = random.random()
                if roll < 0.45:
                    self._start_attack(State.ATTACK,  ATTACK_DURATION,  DMG_PUNCH)
                elif roll < 0.75:
                    self._start_attack(State.KICK,    KICK_DURATION,    DMG_KICK)
                else:
                    self._start_attack(State.SPECIAL, SPECIAL_DURATION, DMG_SPECIAL)
                self.ai_action = None
            else:
                self.ai_action = "right" if dist > 0 else "left"

            # Salto aleatorio
            if random.random() < 0.12 and self.on_ground:
                self.vy = JUMP_FORCE

        if not self.is_busy():
            self.vx = 0
            if self.ai_action == "right":
                self.vx = MOVE_SPEED * 0.85
            elif self.ai_action == "left":
                self.vx = -MOVE_SPEED * 0.85
            elif self.ai_action == "block":
                self.is_blocking = True
                self.state = State.BLOCK

    # ── Dibujado ──────────────────────────────────
    def draw(self, surf: pygame.Surface):
        # Parpadeo al recibir golpe
        if self.hit_flash > 0 and self.hit_flash % 3 == 0:
            return

        # Sombra
        shadow_surf = pygame.Surface((70, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, 70, 20))
        surf.blit(shadow_surf, (int(self.x), GROUND_Y - 12))

        # Dibujar en superficie con flip
        tmp = pygame.Surface((200, 160), pygame.SRCALPHA)
        self._draw_character(tmp)

        if self.facing == -1:
            tmp = pygame.transform.flip(tmp, True, False)

        surf.blit(tmp, (int(self.cx) - 100, int(self.y) - 10))

        # Partículas (en pantalla directa)
        for p in self.particles:
            p.draw(surf)

        # Debug hitbox (comentar en producción)
        # if self.attack_hb:
        #     pygame.draw.rect(surf, (255,0,0), self.attack_hb, 2)

    def _draw_character(self, surf: pygame.Surface):
        """Dibuja todo el personaje en la superficie temporal (100,50 = punto de los pies)."""
        cx, fy = 100, 140   # centro X, pies Y dentro del tmp

        t = self.frame
        walk_cycle = math.sin(t * 0.5) if self.state == State.WALK else 0
        idle_bob   = math.sin(t * 0.25) * 1.5 if self.state == State.IDLE else 0
        jump_sq    = 1.1 if (not self.on_ground and self.vy < 0) else (0.9 if not self.on_ground else 1.0)

        body_h  = int(52 * jump_sq)
        body_y  = fy - body_h - 24 + int(idle_bob)
        body_x  = cx - 22

        is_atk  = self.is_attacking()
        is_kick = self.state == State.KICK
        is_spec = self.state == State.SPECIAL
        is_blk  = self.is_blocking or self.state == State.BLOCK
        is_hit  = self.state == State.HIT
        is_ko   = self.ko

        p = self.pal

        # ── Piernas ──
        self._draw_limb(surf, cx, fy, walk_cycle * 20,
                        is_kick, "leg", p)
        self._draw_limb(surf, cx, fy, -walk_cycle * 20,
                        False, "leg", p)

        # ── Cuerpo ──
        body_rect = pygame.Rect(body_x, body_y, 44, body_h)
        pygame.draw.rect(surf, p["outline"], body_rect.inflate(4, 4), border_radius=10)
        pygame.draw.rect(surf, p["body"],    body_rect, border_radius=8)
        # Collar
        pygame.draw.rect(surf, p.get("collar", p["body"]),
                         (body_x, body_y, 44, 14), border_radius=6)

        # ── Brazos ──
        arm_fwd  = 40 + (30 if is_atk and not is_kick else 0) + (40 if is_spec else 0)
        arm_back = -30

        self._draw_limb(surf, cx - 16, body_y + 12,
                        arm_fwd if is_atk else (15 + walk_cycle * 18),
                        is_spec, "arm", p)
        self._draw_limb(surf, cx + 16, body_y + 12,
                        arm_back if is_atk else (-15 - walk_cycle * 18),
                        False, "arm", p)

        # ── Cabeza ──
        self._draw_head(surf, cx, body_y, p, is_blk, is_hit, is_ko, is_atk, is_spec)

    def _draw_limb(self, surf, ox, oy, angle_deg, special, kind, p):
        """Dibuja un miembro estilo rubber-hose con bezier simulado."""
        is_leg  = kind == "leg"
        length  = 32 if is_leg else 26
        thick   = 9  if is_leg else 7

        rad = math.radians(angle_deg)
        ex  = ox + math.sin(rad) * length
        ey  = oy + math.cos(rad) * length

        # Dibujamos la manguera como línea gruesa (aproximación)
        mid_x = (ox + ex) / 2 + math.cos(rad) * (length * 0.3)
        mid_y = (oy + ey) / 2

        # Contorno (sombra)
        for pts, color, w in [
            ([(ox, oy), (int(mid_x), int(mid_y)), (int(ex), int(ey))],
             p["outline"], thick + 3),
            ([(ox, oy), (int(mid_x), int(mid_y)), (int(ex), int(ey))],
             p["body"], thick),
        ]:
            if len(pts) >= 2:
                pygame.draw.lines(surf, color, False, pts, w)

        # Extremo
        if is_leg:
            # Zapato
            pygame.draw.ellipse(surf, p["outline"],
                                (int(ex) - 14, int(ey) - 4, 26, 16))
            pygame.draw.ellipse(surf, p["shoe"],
                                (int(ex) - 13, int(ey) - 3, 24, 14))
        else:
            # Guante
            pygame.draw.circle(surf, p["outline"], (int(ex), int(ey)), 11)
            pygame.draw.circle(surf, p["glove"],   (int(ex), int(ey)), 9)
            # Nudillos
            for i in range(-1, 2):
                pygame.draw.line(surf, (200, 200, 200),
                                 (int(ex) + i * 3, int(ey) - 4),
                                 (int(ex) + i * 3, int(ey) + 2), 2)
            if special:
                glow = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 220, 0, 100), (20, 20), 18)
                surf.blit(glow, (int(ex) - 20, int(ey) - 20))

    def _draw_head(self, surf, cx, body_y, p, is_blk, is_hit, is_ko, is_atk, is_spec):
        hx = cx
        hy = body_y - 34
        tilt = (5 if is_blk else (-12 if is_hit else (8 if is_atk else 0)))

        # Superficie temporal para rotar la cabeza
        head_tmp = pygame.Surface((80, 80), pygame.SRCALPHA)
        hcx, hcy = 40, 40

        is_p1 = p["body"] == C_P1_BODY

        if is_p1:
            # Copa (trapezoide redondeado)
            pts = [(hcx - 16, hcy + 18), (hcx + 16, hcy + 18),
                   (hcx + 20, hcy - 18), (hcx - 20, hcy - 18)]
            pygame.draw.polygon(head_tmp, p["outline"], pts)
            inner = [(hcx - 14, hcy + 16), (hcx + 14, hcy + 16),
                     (hcx + 17, hcy - 16), (hcx - 17, hcy - 16)]
            pygame.draw.polygon(head_tmp, p["body"], inner)
            # Borde superior (rim)
            pygame.draw.ellipse(head_tmp, p["outline"],
                                (hcx - 22, hcy - 24, 44, 14))
            pygame.draw.ellipse(head_tmp, p["body"],
                                (hcx - 20, hcy - 22, 40, 12))
            # Asa
            pygame.draw.arc(head_tmp, p["outline"],
                            (hcx + 18, hcy - 10, 20, 24),
                            -0.8, 0.9, 4)
        else:
            # Jarro (mug rectangular)
            pygame.draw.rect(head_tmp, p["outline"],
                             (hcx - 20, hcy - 22, 40, 44), border_radius=7)
            pygame.draw.rect(head_tmp, p["body"],
                             (hcx - 18, hcy - 20, 36, 40), border_radius=5)
            # Franja
            stripe_color = tuple(max(0, c - 30) for c in p["body"])
            pygame.draw.line(head_tmp, stripe_color,
                             (hcx - 18, hcy + 2), (hcx + 18, hcy + 2), 5)
            # Asa
            pygame.draw.arc(head_tmp, p["outline"],
                            (hcx + 16, hcy - 8, 20, 22),
                            -0.9, 0.9, 4)

        # Cara
        self._draw_face(head_tmp, hcx, hcy, is_blk, is_hit, is_ko, is_atk)

        # Rotar y pegar cabeza
        rotated = pygame.transform.rotate(head_tmp, -tilt)
        rw, rh  = rotated.get_size()
        surf.blit(rotated, (hx - rw // 2, hy - rh // 2))

    def _draw_face(self, surf, cx, cy, is_blk, is_hit, is_ko, is_atk):
        eye_y = cy - 8

        if is_ko:
            # Ojos X
            for ex in [cx - 9, cx + 9]:
                pygame.draw.line(surf, (50,50,50), (ex-5, eye_y-5), (ex+5, eye_y+5), 3)
                pygame.draw.line(surf, (50,50,50), (ex+5, eye_y-5), (ex-5, eye_y+5), 3)
            # Boca torcida
            pygame.draw.arc(surf, (50,50,50),
                            (cx - 8, cy + 4, 16, 10), 0, math.pi, 3)

        elif is_hit:
            # Ojos apretados
            for ex in [cx - 9, cx + 9]:
                pygame.draw.ellipse(surf, (50,50,50), (ex-5, eye_y-2, 10, 4))
            # Boca abierta (susto)
            pygame.draw.ellipse(surf, (50,50,50), (cx-6, cy+4, 12, 10))

        elif is_atk:
            # Ojos enojados
            for i, ex in enumerate([cx - 9, cx + 9]):
                pygame.draw.ellipse(surf, (50,50,50), (ex-4, eye_y-5, 8, 10))
                # Cejas
                sign = 1 if i == 0 else -1
                pygame.draw.line(surf, (50,50,50),
                                 (ex - 5, eye_y - 8),
                                 (ex + 5, eye_y - 6 + sign * 2), 3)
            # Dientes
            pygame.draw.rect(surf, (255,255,255), (cx-8, cy+5, 16, 6), border_radius=2)
            pygame.draw.rect(surf, (50,50,50), (cx-8, cy+5, 16, 6), 2, border_radius=2)
            for i in range(-2, 3):
                pygame.draw.line(surf, (50,50,50),
                                 (cx + i*3, cy+5), (cx + i*3, cy+11), 1)
        else:
            # Ojos normales
            for ex in [cx - 9, cx + 9]:
                pygame.draw.ellipse(surf, (255,255,255), (ex-5, eye_y-6, 10, 12))
                pygame.draw.ellipse(surf, (50,50,50),   (ex-5, eye_y-6, 10, 12), 2)
                pygame.draw.ellipse(surf, (30,30,30),   (ex-2, eye_y-3,  6, 8))
                pygame.draw.circle(surf, (255,255,255), (ex+2, eye_y-1),  2)

            # Boca
            if is_blk:
                pygame.draw.line(surf, (50,50,50),
                                 (cx-7, cy+7), (cx+7, cy+7), 3)
            else:
                pygame.draw.arc(surf, (50,50,50),
                                (cx - 8, cy + 2, 16, 10),
                                math.pi, 2*math.pi, 3)
