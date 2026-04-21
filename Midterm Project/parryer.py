import pygame
import random
import sys
import os
import math

pygame.init()

# --- 에셋 경로 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def _asset(*parts): return os.path.join(BASE_DIR, *parts)




def load_sprites(file_path, frames_count, orig_w, orig_h, target_w, target_h, cols=None):
    sheet = pygame.image.load(file_path).convert_alpha()

    if cols is None:
        cols = frames_count

    frames = []
    for i in range(frames_count):
        row, col = divmod(i, cols)
        rect = pygame.Rect(col * orig_w, row * orig_h, orig_w, orig_h)
        frame = sheet.subsurface(rect)
        scaled_frame = pygame.transform.scale(frame, (target_w, target_h))
        frames.append(scaled_frame)
    return frames

# --- 기본 설정 (원래 크기 800x600으로 복구) ---
WIDTH, HEIGHT = 800, 600
FPS = 60

PLAYER_W, PLAYER_H = 50, 50
PIXEL_SCALE = PLAYER_W / 8
PARRY_SIZE = int(16 * PIXEL_SCALE)
ENEMY_W, ENEMY_H = 30, 30
E_SHIP_W, E_SHIP_H = 40, 40
M_SHIP_W, M_SHIP_H = 96, 96
BOSS_W, BOSS_H = 128, 128
PARRY_RADIUS = (math.hypot(PLAYER_W, PLAYER_H) / 2) * 1.4

# --- 운석 랜더링 계산 ---
ORIG_METEOR_W, ORIG_METEOR_H = 38, 32
RATIO_W, RATIO_H = ORIG_METEOR_W / 96, ORIG_METEOR_H / 96
OFFSET_RATIO_X, OFFSET_RATIO_Y = 29 / 96, 33 / 96
METEOR_RENDER_W = int(ENEMY_W / RATIO_W)
METEOR_RENDER_H = int(ENEMY_H / RATIO_H)
METEOR_DRAW_OFFSET_X = int(METEOR_RENDER_W * OFFSET_RATIO_X)
METEOR_DRAW_OFFSET_Y = int(METEOR_RENDER_H * OFFSET_RATIO_Y)

WHITE  = (255, 255, 255)
GRAY   = (40,  40,  40)
RED    = (220, 50,  50)
YELLOW = (240, 200, 0)
GREEN  = (100, 255, 100)
CYAN   = (0, 255, 255)
MAGENTA= (255, 0, 255)

# ⭐ --- 전체화면 및 800x600 가상 해상도 설정 --- ⭐
# 1. 실제 모니터 해상도로 전체화면 생성
info = pygame.display.Info() # 현재 모니터의 해상도 정보를 가져옵니다.
MONITOR_W, MONITOR_H = info.current_w, info.current_h
# pygame.NOFRAME을 사용하여 테두리가 없는 창을 화면 크기만큼 띄웁니다.
real_screen = pygame.display.set_mode((MONITOR_W, MONITOR_H), pygame.NOFRAME)
pygame.display.set_caption("Parryer")

# 2. 게임의 모든 논리가 그려질 800x600 가상 도화지 생성
screen = pygame.Surface((WIDTH, HEIGHT))

# 3. 화면 비율(Aspect Ratio) 유지용 레터박스 계산
scale_x = MONITOR_W / WIDTH
scale_y = MONITOR_H / HEIGHT
SCALE = min(scale_x, scale_y) # 4:3 비율을 유지하도록 더 작은 배율 적용

SCALED_W = int(WIDTH * SCALE)
SCALED_H = int(HEIGHT * SCALE)
OFFSET_X = (MONITOR_W - SCALED_W) // 2
OFFSET_Y = (MONITOR_H - SCALED_H) // 2

clock = pygame.time.Clock()

def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0: return font
    return pygame.font.SysFont(None, size)

# 폰트 크기 원상 복구
font = get_korean_font(24)
font_big = get_korean_font(48)
font_title = get_korean_font(80)

# --- 화면 흔들림 설정 ---
shake_amount = 0

def get_shake_offset():
    global shake_amount
    if shake_amount > 0:
        ox = random.randint(-shake_amount, shake_amount)
        oy = random.randint(-shake_amount, shake_amount)
        shake_amount = max(0, shake_amount - 1)
        return ox, oy
    return 0, 0

def trigger_shake(amount=15): # 흔들림 강도 원상 복구
    global shake_amount
    shake_amount = amount

def get_virtual_mouse():
    mx, my = pygame.mouse.get_pos()
    return int((mx - OFFSET_X) / SCALE), int((my - OFFSET_Y) / SCALE)

def draw_button(surface, rect, text, fnt, hovered, base_color=(50, 50, 120)):
    color = tuple(min(255, c + 50) for c in base_color) if hovered else base_color
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=8)
    txt = fnt.render(text, True, WHITE)
    surface.blit(txt, txt.get_rect(center=rect.center))

# 이미지 초기화 (크기 원상 복구)
try:
    PLAYER_IMAGES = load_sprites(_asset("sprites", "player.png"), 3, 8, 8, PLAYER_W, PLAYER_H)
    FLAME_IMAGES  = load_sprites(_asset("sprites", "flame.png"), 4, 8, 8, PLAYER_W, PLAYER_H)
    PARRY_IMAGES  = load_sprites(_asset("sprites", "parry.png"), 4, 16, 16, PARRY_SIZE, PARRY_SIZE)
    METEOR_IMAGES = load_sprites(_asset("sprites", "meteor.png"), 8, 96, 96, METEOR_RENDER_W, METEOR_RENDER_H, cols=8)
    ENEMY_SHIP_IMAGES = load_sprites(_asset("sprites", "enemy_ship1.png"), 3, 8, 8, E_SHIP_W, E_SHIP_H, cols=3)
    MISSILE_SHIP_IMAGES  = load_sprites(_asset("sprites", "missile_ship.png"), 12, 64, 64, M_SHIP_W, M_SHIP_H, cols=12)
    MISSILE_FLAME_IMAGES = load_sprites(_asset("sprites", "missile_ship_flame.png"), 8, 64, 64, M_SHIP_W, M_SHIP_H, cols=8)

    EXPLOSION_IMAGES = load_sprites(_asset("sprites", "enemy_boom.png"), 6, 8, 8, 40, 40, cols=3)
    ORANGE_EXP = EXPLOSION_IMAGES[0:3]
    BLUE_EXP = EXPLOSION_IMAGES[3:6]

    ATTACK_W, ATTACK_H = 20, 20
    attack_img_raw = pygame.image.load(_asset("sprites", "enemy_attack1.png")).convert_alpha()
    ATTACK_IMG = pygame.transform.scale(attack_img_raw, (ATTACK_W, ATTACK_H))
    MISSILE_IMGS = load_sprites(_asset("sprites", "missile.png"), 3, 9, 24, 14, 36, cols=3)
    BANG_IMG = pygame.image.load(_asset("sprites", "bang.png")).convert_alpha()
    _BOSS_BOOM_SZ = int(M_SHIP_W * 0.75)
    BOSS_BOOM_IMAGES = load_sprites(_asset("sprites", "boss_boom.png"), 8, 32, 32, _BOSS_BOOM_SZ, _BOSS_BOOM_SZ, cols=8)

    BOSS_IMAGES         = load_sprites(_asset("sprites", "boss.png"),         34, 128, 128, BOSS_W, BOSS_H, cols=34)
    BOSS_DIE_IMAGES     = load_sprites(_asset("sprites", "boss_die.png"),     18, 128, 128, BOSS_W, BOSS_H, cols=18)
    BOSS_FLAME_IMAGES   = load_sprites(_asset("sprites", "boss_flame.png"),    8, 128, 128, BOSS_W, BOSS_H, cols=8)
    BOSS_ABILITY_IMAGES = load_sprites(_asset("sprites", "boss_ability.png"),  8, 128, 128, BOSS_W, BOSS_H, cols=8)
    LASER_IMGS_BOSS     = load_sprites(_asset("sprites", "laser.png"),         4,  18,  38, 18, 38, cols=4)

    ENEMY_ATTACK_SOUND = pygame.mixer.Sound(_asset("sounds", "laserSmall_002.ogg"))

    METEOR_SOUND = pygame.mixer.Sound(_asset("sounds", "meteor_boom.ogg"))
    METEOR_SOUND.set_volume(0.3)

    PARRY_SOUND = pygame.mixer.Sound(_asset("sounds", "parry.mp3"))

    EXPLOSION_SOUND = pygame.mixer.Sound(_asset("sounds", "enemy_boom.mp3"))
    EXPLOSION_SOUND.set_volume(0.5)
except NameError:
    pass

# --- 패럴랙스 배경 레이어 ---
def _load_bg(name):
    img = pygame.image.load(_asset("backgrounds", name)).convert_alpha()
    return pygame.transform.scale(img, (WIDTH, HEIGHT))

_bg_img      = _load_bg("Background.png")
_neb_img     = _load_bg("nebulae.png")
_neb_flip    = pygame.transform.flip(_neb_img, False, True)
_planet_imgs = [_load_bg(f"planets{i}.png") for i in range(1, 6)]
_dust_img    = _load_bg("dust.png")
_dust_flip   = pygame.transform.flip(_dust_img, False, True)

# 레이어 순서: Background → nebulae → planets → dust
# type "single" : 동일 이미지 반복
# type "flip"   : 교대로 상하좌우 반전하여 이음새 없이 반복
# type "random" : 5종 이미지 중 무작위 선택하여 반복
BG_LAYERS = [
    {"y": 0.0, "speed": 0.3, "type": "single", "img": _bg_img},
    {"y": 0.0, "speed": 0.6, "type": "flip",   "img": _neb_img,  "top": _neb_flip},
    {"y": float(-HEIGHT), "speed": 1.6, "type": "planet", "imgs": _planet_imgs,
     "cur": random.choice(_planet_imgs)},
    {"y": 0.0, "speed": 1.0, "type": "flip",   "img": _dust_img, "top": _dust_flip},
]

def update_bg_layers():
    for L in BG_LAYERS:
        L["y"] += L["speed"]
        if L["type"] == "planet":
            if L["y"] > HEIGHT:
                L["y"] = float(-HEIGHT)
                L["cur"] = random.choice(L["imgs"])
        elif L["y"] >= HEIGHT:
            L["y"] -= HEIGHT
            if L["type"] == "flip":
                L["img"], L["top"] = L["top"], L["img"]

def draw_bg_layers():
    for L in BG_LAYERS:
        y = int(L["y"])
        if L["type"] == "single":
            screen.blit(L["img"], (0, y - HEIGHT))
            screen.blit(L["img"], (0, y))
        elif L["type"] == "flip":
            screen.blit(L["top"], (0, y - HEIGHT))
            screen.blit(L["img"], (0, y))
        elif L["type"] == "planet":
            screen.blit(L["cur"], (0, y))

PARRY_SEQ = [3, 3, 3, 3, 2, 2, 2, 1, 1, 0]

DIFF_SETTINGS = {"spawn": 40, "attack_min": 1, "attack_max": 8, "proj_speed": 1.0,
                 "m_attack_min": 8, "m_attack_max": 16, "m_proj_speed": 1.0, "m_hp": 5, "boss_hp": 15, "boss_attack_interval": 16, "boss_rotation_interval": 6}

LEVELS = [
    {"min_speed": 3, "max_speed": 5,  "spawn": 40, "label": "Stage: 1"}, # 속도 원상 복구
]

# --- 파괴 애니메이션(폭발) 클래스 ---
class Explosion:
    def __init__(self, center, frames):
        self.frames = frames
        self.frame_idx = 0
        self.timer = 0
        self.delay = int(0.05 * FPS)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=center)
        self.active = True

    def update(self):
        self.timer += 1
        if self.timer >= self.delay:
            self.timer = 0
            self.frame_idx += 1
            if self.frame_idx < len(self.frames):
                self.image = self.frames[self.frame_idx]
            else:
                self.active = False

    def draw(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)

# --- 운석 클래스 ---
class Meteor:
    def __init__(self, x, y, w, h, speed):
        self.rect = pygame.Rect(x, y, w, h)
        self.speed = speed
        self.active = True
        self.frame = 0
        self.anim_timer = 0
        self.frame_delay = int(0.05 * FPS)

    def destroy(self):
        self.active = False
        self.frame = 1

    def update(self):
        if self.active:
            self.rect.y += self.speed
        else:
            self.anim_timer += 1
            if self.anim_timer >= self.frame_delay:
                self.anim_timer = 0
                self.frame += 1

    def draw(self, surface):
        draw_pos = (self.rect.x - METEOR_DRAW_OFFSET_X, self.rect.y - METEOR_DRAW_OFFSET_Y)
        if self.frame < 8:
            surface.blit(METEOR_IMAGES[self.frame], draw_pos)

# --- 적 우주선 클래스 ---
class EnemyShip:
    def __init__(self, target_x, target_y, spawn_delay=0):
        self.w = E_SHIP_W
        self.h = E_SHIP_H
        self.x = (WIDTH / 2) - (self.w / 2)
        self.y = -self.h
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 4 # 속도 원상 복구
        self.rect = pygame.Rect(int(self.x), int(self.y), self.w, self.h)
        self.frame = 1
        self.spawn_delay = spawn_delay
        self.is_in_position = False
        self.attack_timer = random.randint(DIFF_SETTINGS["attack_min"] * FPS, DIFF_SETTINGS["attack_max"] * FPS)
        self.invincible = 0

    def update(self):
        if self.spawn_delay > 0:
            self.spawn_delay -= 1
            return
        if self.invincible > 0:
            self.invincible -= 1

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist > self.speed:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        else:
            self.x = self.target_x
            self.y = self.target_y
            self.is_in_position = True

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if self.x < self.target_x - 1:
            self.frame = 2
        elif self.x > self.target_x + 1:
            self.frame = 0
        else:
            self.frame = 1

    def ready_to_attack(self):
        if self.is_in_position:
            if self.attack_timer > 0:
                self.attack_timer -= 1
                return False
            else:
                self.attack_timer = random.randint(DIFF_SETTINGS["attack_min"] * FPS, DIFF_SETTINGS["attack_max"] * FPS)
                return True
        return False

    def draw(self, surface):
        surface.blit(ENEMY_SHIP_IMAGES[self.frame], self.rect)

# --- 미사일 함선 클래스 ---
class MissileShip:
    def __init__(self, target_x, target_y, spawn_delay=0):
        self.w = M_SHIP_W
        self.h = M_SHIP_H
        self.x = float(target_x)
        self.y = float(-self.h)
        self.spawn_delay = spawn_delay
        self.target_x = float(target_x)
        self.target_y = float(target_y)
        self.speed = 3
        self.hb_ox = 0
        self.hb_oy = round(M_SHIP_H * 17 / 64)
        self.hb_w  = M_SHIP_W
        self.hb_h  = M_SHIP_H - self.hb_oy - round(M_SHIP_H * 19 / 64)
        self.rect = pygame.Rect(int(self.x) + self.hb_ox, int(self.y) + self.hb_oy, self.hb_w, self.hb_h)
        self.is_in_position = False
        self.flame_frame = 0
        self.flame_timer = 0
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_playing = False
        self.fire_event = False
        self.missile_target_left  = None
        self.missile_target_right = None
        self.max_hp = DIFF_SETTINGS["m_hp"]
        self.hp = self.max_hp
        self.invincible = 0
        self.hp_bar_timer = 0
        self.attack_timer = random.randint(
            DIFF_SETTINGS["m_attack_min"] * FPS,
            DIFF_SETTINGS["m_attack_max"] * FPS
        )

    def update(self):
        self.fire_event = False
        if self.spawn_delay > 0:
            self.spawn_delay -= 1
            return
        if self.invincible > 0:
            self.invincible -= 1
        if self.hp_bar_timer > 0:
            self.hp_bar_timer -= 1

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > self.speed:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        else:
            self.x = self.target_x
            self.y = self.target_y
            self.is_in_position = True
        self.rect.x = int(self.x) + self.hb_ox
        self.rect.y = int(self.y) + self.hb_oy

        self.flame_timer += 1
        if self.flame_timer >= 3:
            self.flame_timer = 0
            self.flame_frame = (self.flame_frame + 1) % 8

        if self.anim_playing:
            self.anim_timer += 1
            if self.anim_timer >= 11:
                self.anim_timer = 0
                self.anim_frame += 1
                if self.anim_frame in (5, 8, 11):
                    self.fire_event = True
                if self.anim_frame > 11:
                    self.anim_frame = 0
                    self.anim_playing = False
                    self.attack_timer = random.randint(
                        DIFF_SETTINGS["m_attack_min"] * FPS,
                        DIFF_SETTINGS["m_attack_max"] * FPS
                    )
        elif self.is_in_position:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.anim_frame = 1
                self.anim_timer = 0
                self.anim_playing = True

    def draw(self, surface):
        flame_img = MISSILE_FLAME_IMAGES[self.flame_frame]
        surface.blit(flame_img, (int(self.x), int(self.y) - M_SHIP_H + 96))
        surface.blit(MISSILE_SHIP_IMAGES[self.anim_frame], (int(self.x), int(self.y)))
        if not self.anim_playing and self.is_in_position and self.attack_timer <= 2 * FPS:
            if (self.attack_timer // 30) % 2 != 0:
                surface.blit(BANG_IMG, BANG_IMG.get_rect(centerx=self.rect.centerx, bottom=self.rect.top + 60))
        if self.hp_bar_timer > 0:
            bar_w = self.hb_w
            bar_h = 6
            bar_x = self.rect.x
            bar_y = self.rect.bottom + 4
            pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_w, bar_h))
            green_w = int(bar_w * self.hp / self.max_hp)
            if green_w > 0:
                pygame.draw.rect(surface, GREEN, (bar_x, bar_y, green_w, bar_h))

# --- 미사일 투사체 클래스 ---
class Missile:
    def __init__(self, x, y, tx, ty):
        self.w, self.h = 14, 36
        self.x, self.y = float(x), float(y)
        self.rect = pygame.Rect(int(self.x), int(self.y), self.w, self.h)
        speed = 6 * 0.75 * DIFF_SETTINGS["m_proj_speed"]
        angle = math.atan2(ty - y, tx - x)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.active = True
        self.reflected = False
        self.frame = 0
        self.frame_timer = 0

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.topleft = (int(self.x), int(self.y))
        if self.y > HEIGHT + 50 or self.y < -50 or self.x < -50 or self.x > WIDTH + 50:
            self.active = False
        self.frame_timer += 1
        if self.frame_timer >= 6:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % 3

    def draw(self, surface):
        img = MISSILE_IMGS[self.frame]
        angle = -(math.degrees(math.atan2(self.dy, self.dx)) + 90)
        rotated = pygame.transform.rotate(img, angle)
        surface.blit(rotated, rotated.get_rect(center=self.rect.center))

# --- 보스 클래스 ---
class Boss:
    def __init__(self):
        self.w = BOSS_W
        self.h = BOSS_H
        self.x = float(WIDTH // 2 - self.w // 2)
        self.y = float(-self.h)
        self.target_x = float(WIDTH // 2 - self.w // 2)
        self.target_y = 60.0
        self.speed = 2.0
        self.hb_ox = 25
        self.hb_oy = 12
        self.hb_w  = BOSS_W - 50
        self.hb_h  = BOSS_H - 25
        self.rect = pygame.Rect(int(self.x) + self.hb_ox, int(self.y) + self.hb_oy, self.hb_w, self.hb_h)
        self.is_in_position = False

        self.max_hp = DIFF_SETTINGS["boss_hp"]
        self.hp = self.max_hp
        self.invincible = 0

        self.anim_frame = 0
        self.anim_timer = 0
        self.flame_frame = 0
        self.flame_timer = 0
        self.hp_bar_timer = 0

        self.attack_phase = 'idle'
        self.attack_timer = DIFF_SETTINGS["boss_attack_interval"] * FPS
        self.boss_draw_angle = 0.0
        self.rotation_timer = 0
        self.fire_angle = math.pi / 2
        self.laser_timer = 0
        self.laser_frame = 0
        self.laser_frame_timer = 0

        self.dying = False
        self.die_frame = 0
        self.die_timer = 0
        self.active = True

        self.summon_timer = 0
        self.ability_frame = 0
        self.ability_timer = 0
        self.summon_event = False

    def _laser_exit(self, cx, cy, angle):
        dx, dy = math.cos(angle), math.sin(angle)
        candidates = []
        if abs(dx) > 1e-6:
            candidates.append(((WIDTH - cx) / dx) if dx > 0 else (-cx / dx))
        if abs(dy) > 1e-6:
            candidates.append(((HEIGHT - cy) / dy) if dy > 0 else (-cy / dy))
        t = min((t for t in candidates if t >= 0), default=0)
        return cx + dx * t, cy + dy * t

    def update(self, player_rect):
        if not self.active:
            return
        self.summon_event = False
        if self.invincible > 0:
            self.invincible -= 1
        if self.hp_bar_timer > 0:
            self.hp_bar_timer -= 1

        if not self.is_in_position:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.hypot(dx, dy)
            if dist > self.speed:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
            else:
                self.x = self.target_x
                self.y = self.target_y
                self.is_in_position = True
        self.rect.x = int(self.x) + self.hb_ox
        self.rect.y = int(self.y) + self.hb_oy

        if self.dying:
            self.die_timer += 1
            if self.die_timer >= 10:
                self.die_timer = 0
                self.die_frame += 1
                if self.die_frame >= 18:
                    self.active = False
            return

        self.flame_timer += 1
        if self.flame_timer >= 3:
            self.flame_timer = 0
            self.flame_frame = (self.flame_frame + 1) % 8

        if not self.is_in_position:
            return

        # 공격 상태머신
        if self.attack_phase == 'idle':
            self.rotation_timer += 1
            if self.rotation_timer >= 6:
                self.rotation_timer = 0
                if abs(self.boss_draw_angle) > 0.5:
                    self.boss_draw_angle -= 1.0 if self.boss_draw_angle > 0 else -1.0
                else:
                    self.boss_draw_angle = 0.0

            if self.summon_timer > 0:
                self.summon_timer -= 1
                if self.summon_timer == 0:
                    self.attack_phase = 'ability'
                    self.ability_frame = 0
                    self.ability_timer = 0
            else:
                self.attack_timer -= 1
                if self.attack_timer <= 0:
                    self.attack_phase = 'aiming'
                    self.anim_frame = 1
                    self.anim_timer = 0
                    self.rotation_timer = 0

        elif self.attack_phase == 'aiming':
            # 0.2초(12프레임)마다 1도씩 플레이어 방향으로 회전
            cx = int(self.x) + BOSS_W // 2
            cy = int(self.y) + BOSS_H // 2
            px, py = player_rect.center
            target_angle = 90 - math.degrees(math.atan2(py - cy, px - cx))
            self.rotation_timer += 1
            if self.rotation_timer >= DIFF_SETTINGS["boss_rotation_interval"]:
                self.rotation_timer = 0
                diff = target_angle - self.boss_draw_angle
                while diff > 180: diff -= 360
                while diff < -180: diff += 360
                if abs(diff) > 0.5:
                    self.boss_draw_angle += 1.0 if diff > 0 else -1.0
            self.anim_timer += 1
            if self.anim_timer >= 10:
                self.anim_timer = 0
                self.anim_frame += 1
                if self.anim_frame >= 21:
                    self.anim_frame = 21
                    self.fire_angle = math.radians(90 - self.boss_draw_angle)
                    self.laser_timer = 45
                    self.attack_phase = 'firing'

        elif self.attack_phase == 'firing':
            self.laser_frame_timer += 1
            if self.laser_frame_timer >= 6:
                self.laser_frame_timer = 0
                self.laser_frame = (self.laser_frame + 1) % 4
            self.laser_timer -= 1
            if self.laser_timer <= 0:
                self.attack_phase = 'recovering'
                self.anim_frame = 22
                self.anim_timer = 0

        elif self.attack_phase == 'recovering':
            self.laser_frame_timer += 1
            if self.laser_frame_timer >= 6:
                self.laser_frame_timer = 0
                self.laser_frame = (self.laser_frame + 1) % 4
            self.anim_timer += 1
            if self.anim_timer >= 8:
                self.anim_timer = 0
                self.anim_frame += 1
                if self.anim_frame >= 34:
                    self.anim_frame = 0
                    self.rotation_timer = 0
                    self.attack_phase = 'idle'
                    self.attack_timer = DIFF_SETTINGS["boss_attack_interval"] * FPS
                    self.summon_timer = 6 * FPS

        elif self.attack_phase == 'ability':
            self.ability_timer += 1
            if self.ability_timer >= 6:
                self.ability_timer = 0
                self.ability_frame += 1
                if self.ability_frame >= 8:
                    self.ability_frame = 7
                    self.summon_event = True
                    self.attack_phase = 'idle'

    def take_damage(self, dmg=1):
        if self.invincible > 0 or self.dying:
            return False
        self.hp -= dmg
        self.invincible = 30
        self.hp_bar_timer = 3 * FPS
        if self.hp <= 0:
            self.hp = 0
            self.dying = True
            return True
        return False

    def draw(self, surface):
        if not self.active:
            return
        sprite_cx = int(self.x) + BOSS_W // 2
        sprite_cy = int(self.y) + BOSS_H // 2

        if self.attack_phase == 'ability':
            ability_img = pygame.transform.rotate(BOSS_ABILITY_IMAGES[self.ability_frame], self.boss_draw_angle)
            surface.blit(ability_img, ability_img.get_rect(center=(sprite_cx, sprite_cy)))

        if not self.dying:
            flame_img = pygame.transform.rotate(BOSS_FLAME_IMAGES[self.flame_frame], self.boss_draw_angle)
            surface.blit(flame_img, flame_img.get_rect(center=(sprite_cx, sprite_cy)))

        if self.dying:
            if self.die_frame < 18:
                die_img = pygame.transform.rotate(BOSS_DIE_IMAGES[self.die_frame], self.boss_draw_angle)
                surface.blit(die_img, die_img.get_rect(center=(sprite_cx, sprite_cy)))
        else:
            boss_img = pygame.transform.rotate(BOSS_IMAGES[self.anim_frame], self.boss_draw_angle)
            surface.blit(boss_img, boss_img.get_rect(center=(sprite_cx, sprite_cy)))

        if self.attack_phase in ('firing', 'recovering'):
            laser_img = LASER_IMGS_BOSS[self.laser_frame]
            cannon_reach = self.hb_oy + self.hb_h - BOSS_H // 2 -10
            theta = math.radians(self.boss_draw_angle)
            cx = int(sprite_cx + cannon_reach * math.sin(theta))
            cy = int(sprite_cy + cannon_reach * math.cos(theta))
            ex, ey = self._laser_exit(cx, cy, self.fire_angle)
            beam_len = int(math.hypot(ex - cx, ey - cy)) + 1
            if beam_len > 0:
                beam_surf = pygame.Surface((18, beam_len), pygame.SRCALPHA)
                for i in range(0, beam_len, 38):
                    beam_surf.blit(laser_img, (0, i))
                rot_angle = 90 - math.degrees(self.fire_angle)
                rotated = pygame.transform.rotate(beam_surf, rot_angle)
                surface.blit(rotated, rotated.get_rect(center=((cx + ex) // 2, (cy + ey) // 2)))

        if self.hp_bar_timer > 0:
            bar_w = self.hb_w
            bar_h = 6
            bar_x = self.rect.x
            bar_y = self.rect.bottom + 4
            pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_w, bar_h))
            green_w = int(bar_w * self.hp / self.max_hp)
            if green_w > 0:
                pygame.draw.rect(surface, GREEN, (bar_x, bar_y, green_w, bar_h))

# --- 적 투사체 클래스 ---
class EnemyAttack:
    def __init__(self, ship):
        self.ship = ship
        self.w = ATTACK_W
        self.h = ATTACK_H

        self.x = ship.rect.centerx - self.w // 2
        self.y = ship.rect.bottom
        self.rect = pygame.Rect(int(self.x), int(self.y), self.w, self.h)

        self.charge_timer = 1 * FPS
        self.dx = 0
        self.dy = 0
        self.speed = 6 * DIFF_SETTINGS["proj_speed"]
        self.active = True
        self.reflected = False

    def update(self, current_player_rect):
        if self.charge_timer > 0:
            self.charge_timer -= 1
            if self.ship in enemy_ships:
                self.x = self.ship.rect.centerx - self.w // 2
                self.y = self.ship.rect.bottom
            self.rect.topleft = (int(self.x), int(self.y))

            if self.charge_timer == 0:
                if self.ship not in enemy_ships:
                    self.active = False
                else:
                    px, py = current_player_rect.center
                    angle = math.atan2(py - self.rect.centery, px - self.rect.centerx)
                    self.dx = math.cos(angle) * self.speed
                    self.dy = math.sin(angle) * self.speed
                    ENEMY_ATTACK_SOUND.play()
        else:
            self.x += self.dx
            self.y += self.dy
            self.rect.topleft = (int(self.x), int(self.y))

            if self.y > HEIGHT + 50 or self.y < -50 or self.x < -50 or self.x > WIDTH + 50:
                self.active = False

    def draw(self, surface):
        surface.blit(ATTACK_IMG, self.rect)

def draw_hud(score, level_cfg, lives, parry_cooldown):
    score_text = font.render(f"Score: {score}", True, WHITE)
    stage_text = font.render(f"{level_cfg['label']}", True, YELLOW)
    screen.blit(score_text, (10, 10))
    screen.blit(stage_text, (10, 50))

    lives_text = font.render(f"{'♥ ' * lives}", True, RED)
    screen.blit(lives_text, lives_text.get_rect(right=WIDTH - 10, top=10))

    cd_sec = (parry_cooldown + FPS - 1) // FPS
    if cd_sec == 0:
        cd_text = font.render("Parry: Ready (F)", True, GREEN)
    else:
        cd_text = font.render(f"Parry: {cd_sec}s", True, WHITE)
    screen.blit(cd_text, cd_text.get_rect(right=WIDTH - 10, top=50))

def title_screen():
    btn_start = pygame.Rect(WIDTH//2 - 100, HEIGHT//2,      200, 50)
    btn_exit  = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 70, 200, 50)
    while True:
        clock.tick(FPS)
        update_bg_layers()
        draw_bg_layers()
        mx, my = get_virtual_mouse()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn_start.collidepoint(mx, my): return
                if btn_exit.collidepoint(mx, my):  pygame.quit(); sys.exit()
        title_surf = font_title.render("Parryer", True, WHITE)
        shadow_surf = font_title.render("Parryer", True, (80, 80, 80))
        screen.blit(shadow_surf, shadow_surf.get_rect(center=(WIDTH//2 + 3, HEIGHT//3 + 3)))
        screen.blit(title_surf,  title_surf.get_rect(center=(WIDTH//2, HEIGHT//3)))
        draw_button(screen, btn_start, "Start", font, btn_start.collidepoint(mx, my))
        draw_button(screen, btn_exit,  "Exit",  font, btn_exit.collidepoint(mx, my),  (100, 40, 40))
        real_screen.fill((0, 0, 0))
        real_screen.blit(pygame.transform.scale(screen, (SCALED_W, SCALED_H)), (OFFSET_X, OFFSET_Y))
        pygame.display.flip()

def difficulty_screen():
    btn_easy   = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 80, 200, 50)
    btn_normal = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 10, 200, 50)
    btn_hard   = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 50)
    diffs = {
        "easy":   {"spawn": 40, "attack_min": 1, "attack_max": 12, "proj_speed": 0.75, "m_attack_min": 5,  "m_attack_max": 15, "m_proj_speed": 0.75, "m_hp": 3, "boss_hp": 10, "boss_attack_interval": 19, "boss_rotation_interval": 12, "difficulty": "easy"},
        "normal": {"spawn": 27, "attack_min": 1, "attack_max": 8,  "proj_speed": 1.0,  "m_attack_min": 4,  "m_attack_max": 12, "m_proj_speed": 1.0,  "m_hp": 5, "boss_hp": 15, "boss_attack_interval": 16, "boss_rotation_interval": 6,  "difficulty": "normal"},
        "hard":   {"spawn": 20, "attack_min": 1, "attack_max": 4,  "proj_speed": 1.25, "m_attack_min": 3,  "m_attack_max": 9,  "m_proj_speed": 1.25, "m_hp": 7, "boss_hp": 20, "boss_attack_interval": 13, "boss_rotation_interval": 3,  "difficulty": "hard"},
    }
    while True:
        clock.tick(FPS)
        update_bg_layers()
        draw_bg_layers()
        mx, my = get_virtual_mouse()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn_easy.collidepoint(mx, my):   return diffs["easy"]
                if btn_normal.collidepoint(mx, my): return diffs["normal"]
                if btn_hard.collidepoint(mx, my):   return diffs["hard"]
        sel_surf = font_big.render("Select Difficulty", True, WHITE)
        screen.blit(sel_surf, sel_surf.get_rect(center=(WIDTH//2, HEIGHT//4)))
        draw_button(screen, btn_easy,   "Easy",   font, btn_easy.collidepoint(mx, my),   (30, 100, 30))
        draw_button(screen, btn_normal, "Normal", font, btn_normal.collidepoint(mx, my), (100, 100, 30))
        draw_button(screen, btn_hard,   "Hard",   font, btn_hard.collidepoint(mx, my),   (120, 30, 30))
        real_screen.fill((0, 0, 0))
        real_screen.blit(pygame.transform.scale(screen, (SCALED_W, SCALED_H)), (OFFSET_X, OFFSET_Y))
        pygame.display.flip()

def stage_select_screen():
    btn_s1 = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 80, 200, 50)
    btn_s2 = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 10, 200, 50)
    btn_s3 = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 50)
    while True:
        clock.tick(FPS)
        update_bg_layers()
        draw_bg_layers()
        mx, my = get_virtual_mouse()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn_s1.collidepoint(mx, my): return 1
                if btn_s2.collidepoint(mx, my): return 2
                if btn_s3.collidepoint(mx, my): return 3
        sel_surf = font_big.render("Select Stage", True, WHITE)
        screen.blit(sel_surf, sel_surf.get_rect(center=(WIDTH//2, HEIGHT//4)))
        draw_button(screen, btn_s1, "Stage 1", font, btn_s1.collidepoint(mx, my), (30,  60, 120))
        draw_button(screen, btn_s2, "Stage 2", font, btn_s2.collidepoint(mx, my), (80,  40, 120))
        draw_button(screen, btn_s3, "Stage 3", font, btn_s3.collidepoint(mx, my), (120, 30,  80))
        real_screen.fill((0, 0, 0))
        real_screen.blit(pygame.transform.scale(screen, (SCALED_W, SCALED_H)), (OFFSET_X, OFFSET_Y))
        pygame.display.flip()

def game_over_screen(score):
    screen.fill(GRAY)

    # 텍스트들을 800x600 가상 화면 정중앙을 기준으로 동적 정렬
    t1 = font_big.render("GAME OVER", True, RED)
    t2 = font.render(f"Score: {score}", True, WHITE)
    t3 = font.render("R: Restart   Q/ESC: Quit", True, WHITE)

    screen.blit(t1, t1.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
    screen.blit(t2, t2.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
    screen.blit(t3, t3.get_rect(center=(WIDTH//2, HEIGHT//2 + 70)))

    # 레터박스 렌더링 적용
    real_screen.fill((0, 0, 0))
    scaled_surface = pygame.transform.scale(screen, (SCALED_W, SCALED_H))
    real_screen.blit(scaled_surface, (OFFSET_X, OFFSET_Y))
    pygame.display.flip()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key in (pygame.K_q, pygame.K_ESCAPE): pygame.quit(); sys.exit()

def main(start_stage=1):
    global enemy_ships

    # 시작 Y 좌표 원상 복구
    player_rect = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 100, PLAYER_W, PLAYER_H)
    meteors = []
    enemy_ships = []
    enemy_attacks = []
    explosions = []
    missile_ships = []
    missiles = []
    bosses = []
    god_mode = False

    score = 0
    lives = 5
    invincible = 0

    stage = 1
    stage_timer = 0
    stage_clear_timer = 0
    ships_spawned = 0
    stage2_spawned = False
    stage2_missile_timer = 0
    meteor_spawn_timer = 0

    parry_cooldown = 0
    parry_anim_idx = -1
    parry_anim_timer = 0
    parry_active_timer = 0

    show_hitbox = False
    level_cfg = {"min_speed": 3, "max_speed": 5, "spawn": DIFF_SETTINGS["spawn"], "label": "Stage: 1"}

    def spawn_missile_ships_stage2():
        ty = 64
        missile_ships.append(MissileShip(WIDTH // 6 - M_SHIP_W // 2,     ty, FPS))
        missile_ships.append(MissileShip(WIDTH // 2 - M_SHIP_W // 2,     ty, FPS))
        missile_ships.append(MissileShip(WIDTH * 5 // 6 - M_SHIP_W // 2, ty, FPS))

    def spawn_stage2():
        nonlocal stage, stage2_spawned
        stage = 2
        stage2_spawned = True
        level_cfg["label"] = "Stage: 2"

        ty = 64
        cx_left   = WIDTH // 6
        cx_center = WIDTH // 2
        cx_right  = WIDTH * 5 // 6
        for cx in (
            cx_left + (cx_center - cx_left) // 3,
            cx_left + 2 * (cx_center - cx_left) // 3,
            cx_center + (cx_right - cx_center) // 3,
            cx_center + 2 * (cx_right - cx_center) // 3,
        ):
            enemy_ships.append(EnemyShip(cx - E_SHIP_W // 2, ty))
        ref_x = cx_center
        ref_y = ty + M_SHIP_H // 2
        enemy_ships.append(EnemyShip(ref_x - 256 - E_SHIP_W // 2, ref_y + 32))
        enemy_ships.append(EnemyShip(ref_x + 256 - E_SHIP_W // 2, ref_y + 32))

        spawn_missile_ships_stage2()

    def spawn_stage3():
        nonlocal stage
        stage = 3
        level_cfg["label"] = "Stage: 3"

    if start_stage >= 2:
        ships_spawned = 8
        spawn_stage2()
    if start_stage >= 3:
        spawn_stage3()

    bosses.append(Boss())  # 테스트용: Stage 1 시작 시 보스 스폰

    while True:
        clock.tick(FPS)
        update_bg_layers()
        draw_bg_layers()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if e.key == pygame.K_d:
                    show_hitbox = not show_hitbox
                if e.key == pygame.K_h:
                    god_mode = not god_mode
                if e.key == pygame.K_f and parry_cooldown <= 0:
                    parry_cooldown = int(5.5 * FPS)
                    parry_active_timer = int(0.4 * FPS)
                    parry_anim_idx = 0
                    parry_anim_timer = 0
                    PARRY_SOUND.play()

        stage_timer += 1

        if parry_cooldown > 0: parry_cooldown -= 1
        if parry_active_timer > 0: parry_active_timer -= 1

        if parry_anim_idx >= 0:
            parry_anim_timer += 1
            if parry_anim_timer >= 3:
                parry_anim_idx += 1
                parry_anim_timer = 0
                if parry_anim_idx >= len(PARRY_SEQ):
                    parry_anim_idx = -1

        keys = pygame.key.get_pressed()

        current_image = PLAYER_IMAGES[1]
        flame_offset_x = 0

        # 플레이어 이동속도 원상 복구
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.x -= 5
            current_image = PLAYER_IMAGES[0]
            flame_offset_x = -PIXEL_SCALE
        elif keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
            player_rect.x += 5
            current_image = PLAYER_IMAGES[2]
            flame_offset_x = PIXEL_SCALE

        if keys[pygame.K_UP] and player_rect.top > 0: player_rect.y -= 5
        if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT: player_rect.y += 5

        # --- 적 우주선 생성 로직 (Stage 1) ---
        if stage == 1:
            if stage_timer >= 5 * FPS and ships_spawned < 8:
                if (stage_timer - 5 * FPS) % int(0.5 * FPS) == 0:
                    pair_idx = ships_spawned // 2
                    left_target_x  = (WIDTH / 9) * (pair_idx + 1) - (E_SHIP_W / 2)
                    right_target_x = (WIDTH / 9) * (8 - pair_idx) - (E_SHIP_W / 2)
                    enemy_ships.append(EnemyShip(left_target_x,  80))
                    enemy_ships.append(EnemyShip(right_target_x, 80))
                    ships_spawned += 2

            if ships_spawned >= 8 and len(enemy_ships) == 0:
                stage_clear_timer += 1
                if stage_clear_timer >= 5 * FPS:
                    spawn_stage2()

        if stage == 2 and stage2_missile_timer > 0:
            stage2_missile_timer -= 1
            if stage2_missile_timer == 0:
                spawn_missile_ships_stage2()

        # --- 운석 생성 로직 ---
        meteor_spawn_timer += 1
        if meteor_spawn_timer >= level_cfg["spawn"]:
            meteor_spawn_timer = 0
            x = random.randint(0, WIDTH - ENEMY_W)
            speed = random.randint(level_cfg["min_speed"], level_cfg["max_speed"])
            meteors.append(Meteor(x, -ENEMY_H, ENEMY_W, ENEMY_H, speed))

        # --- 위치 및 애니메이션 업데이트 ---
        for ms in missile_ships:
            ms.update()
            if ms.fire_event:
                if ms.anim_frame == 5:
                    ms.missile_target_left  = (player_rect.left,  player_rect.centery)
                    ms.missile_target_right = (player_rect.right, player_rect.centery)
                tl = ms.missile_target_left
                tr = ms.missile_target_right
                missiles.append(Missile(ms.rect.left,  ms.rect.centery, tl[0], tl[1]))
                missiles.append(Missile(ms.rect.right, ms.rect.centery, tr[0], tr[1]))

        for mis in missiles:
            mis.update()
        missiles = [mis for mis in missiles if mis.active]

        for ship in enemy_ships:
            ship.update()
            if ship.ready_to_attack():
                enemy_attacks.append(EnemyAttack(ship))

        for atk in enemy_attacks:
            atk.update(player_rect)
        enemy_attacks = [atk for atk in enemy_attacks if atk.active]

        for exp in explosions:
            exp.update()
        explosions = [exp for exp in explosions if exp.active]

        for boss in bosses:
            boss.update(player_rect)
        bosses = [b for b in bosses if b.active]

        survived_meteors = []
        for m in meteors:
            m.update()
            if m.active:
                if m.rect.top < HEIGHT:
                    survived_meteors.append(m)
                else:
                    score += 1
            else:
                if m.frame < 8:
                    survived_meteors.append(m)
        meteors = survived_meteors

        # --- 반사된 투사체 충돌 판정 ---
        for atk in enemy_attacks:
            if atk.active and atk.reflected:
                for ship in enemy_ships[:]:
                    if ship.invincible == 0 and atk.rect.colliderect(ship.rect):
                        explosions.append(Explosion(ship.rect.center, ORANGE_EXP))
                        enemy_ships.remove(ship)
                        score += 50
                        EXPLOSION_SOUND.play()
                for ms in missile_ships[:]:
                    if ms.invincible == 0 and atk.rect.colliderect(ms.rect):
                        ms.hp -= 1
                        ms.invincible = 30
                        ms.hp_bar_timer = 3 * FPS
                        explosions.append(Explosion(atk.rect.center, BLUE_EXP))
                        EXPLOSION_SOUND.play()
                        if ms.hp <= 0:
                            explosions.append(Explosion(ms.rect.center, BOSS_BOOM_IMAGES))
                            missile_ships.remove(ms)
                            score += 100
                for m in meteors:
                    if m.active and atk.rect.colliderect(m.rect):
                        m.destroy()
                        score += 10
                        METEOR_SOUND.play()
                for boss in bosses[:]:
                    if boss.invincible == 0 and atk.rect.colliderect(boss.rect):
                        killed = boss.take_damage(1)
                        explosions.append(Explosion(atk.rect.center, BLUE_EXP))
                        EXPLOSION_SOUND.play()
                        if killed:
                            explosions.append(Explosion(boss.rect.center, BOSS_BOOM_IMAGES))
                            score += 500

        for mis in missiles:
            if mis.active and mis.reflected:
                for ship in enemy_ships[:]:
                    if ship.invincible == 0 and mis.rect.colliderect(ship.rect):
                        explosions.append(Explosion(ship.rect.center, ORANGE_EXP))
                        enemy_ships.remove(ship)
                        score += 50
                        EXPLOSION_SOUND.play()
                for ms in missile_ships[:]:
                    if ms.invincible == 0 and mis.rect.colliderect(ms.rect):
                        ms.hp -= 1
                        ms.invincible = 30
                        ms.hp_bar_timer = 3 * FPS
                        explosions.append(Explosion(mis.rect.center, BLUE_EXP))
                        EXPLOSION_SOUND.play()
                        if ms.hp <= 0:
                            explosions.append(Explosion(ms.rect.center, BOSS_BOOM_IMAGES))
                            missile_ships.remove(ms)
                            score += 100
                for boss in bosses[:]:
                    if boss.invincible == 0 and mis.rect.colliderect(boss.rect):
                        killed = boss.take_damage(1)
                        explosions.append(Explosion(mis.rect.center, BLUE_EXP))
                        EXPLOSION_SOUND.play()
                        if killed:
                            explosions.append(Explosion(boss.rect.center, BOSS_BOOM_IMAGES))
                            score += 500

        # --- 플레이어 피격 판정 ---
        can_take_damage = not god_mode and invincible == 0
        if invincible > 0:
            invincible -= 1

        hit = False
        for atk in enemy_attacks:
            if atk.active and not atk.reflected and player_rect.colliderect(atk.rect):
                if parry_active_timer > 0:
                    atk.reflected = True
                    if atk.charge_timer > 0:
                        atk.dx = 0
                        atk.dy = -atk.speed
                        atk.charge_timer = 0
                    else:
                        atk.dx *= -1
                        atk.dy *= -1
                    parry_cooldown = 0
                    parry_active_timer = 0
                    parry_anim_idx = -1
                elif can_take_damage:
                    hit =	 True
                    atk.active = False
                    break

        if not hit:
            for m in meteors:
                if m.active and player_rect.colliderect(m.rect):
                    if parry_active_timer > 0:
                        pass
                    elif can_take_damage:
                        hit = True
                        m.destroy()
                        METEOR_SOUND.play()
                        break

        if not hit:
            for ship in enemy_ships:
                if player_rect.colliderect(ship.rect):
                    if parry_active_timer > 0:
                        pass
                    elif can_take_damage:
                        hit = True
                        break

        if not hit:
            for ms in missile_ships:
                if player_rect.colliderect(ms.rect):
                    if parry_active_timer > 0:
                        pass
                    elif can_take_damage:
                        hit = True
                        break

        if not hit:
            for boss in bosses:
                if not boss.dying and player_rect.colliderect(boss.rect):
                    if parry_active_timer > 0:
                        pass
                    elif can_take_damage:
                        hit = True
                        break

        if not hit:
            for boss in bosses:
                if not boss.dying and boss.attack_phase in ('firing', 'recovering'):
                    _sprite_cx = int(boss.x) + BOSS_W // 2
                    _sprite_cy = int(boss.y) + BOSS_H // 2
                    _reach = boss.hb_oy + boss.hb_h - BOSS_H // 2
                    _theta = math.radians(boss.boss_draw_angle)
                    _lcx = int(_sprite_cx + _reach * math.sin(_theta))
                    _lcy = int(_sprite_cy + _reach * math.cos(_theta))
                    _lex, _ley = boss._laser_exit(_lcx, _lcy, boss.fire_angle)
                    if player_rect.clipline(_lcx, _lcy, int(_lex), int(_ley)):
                        if can_take_damage:
                            hit = True
                            break

        if not hit:
            for mis in missiles:
                if mis.active and not mis.reflected and player_rect.colliderect(mis.rect):
                    if parry_active_timer > 0:
                        mis.reflected = True
                        mis.dx *= -1
                        mis.dy *= -1
                        parry_cooldown = 0
                        parry_active_timer = 0
                        parry_anim_idx = -1
                    elif can_take_damage:
                        hit = True
                        mis.active = False
                        break

        if hit:
            lives -= 1
            invincible = 90
            trigger_shake(15)
            if lives <= 0:
                if game_over_screen(score): main()
                return

        # --- 그리기 작업 ---
        blink = (invincible // 10) % 2 != 0

        if not blink:
            screen.blit(current_image, player_rect)
            flame_frame_idx = (pygame.time.get_ticks() // 100) % 4
            flame_x = player_rect.x + flame_offset_x
            flame_y = player_rect.bottom - PIXEL_SCALE
            screen.blit(FLAME_IMAGES[flame_frame_idx], (flame_x, flame_y))

            if parry_anim_idx >= 0:
                frame_number = PARRY_SEQ[parry_anim_idx]
                parry_img = PARRY_IMAGES[frame_number]
                parry_rect = parry_img.get_rect(center=player_rect.center)
                screen.blit(parry_img, parry_rect)

        for boss in bosses:
            boss.draw(screen)

        for ms in missile_ships:
            ms.draw(screen)

        for ship in enemy_ships:
            ship.draw(screen)

        for atk in enemy_attacks:
            atk.draw(screen)

        for mis in missiles:
            mis.draw(screen)

        for m in meteors:
            m.draw(screen)

        for exp in explosions:
            exp.draw(screen)

        if show_hitbox:
            pygame.draw.rect(screen, GREEN, player_rect, 2)
            pygame.draw.circle(screen, CYAN, player_rect.center, int(PARRY_RADIUS), 2)
            for m in meteors:
                if m.active: pygame.draw.rect(screen, RED, m.rect, 2)
            for ms in missile_ships:
                pygame.draw.rect(screen, WHITE, ms.rect, 2)
            for ship in enemy_ships:
                pygame.draw.rect(screen, YELLOW, ship.rect, 2)
            for atk in enemy_attacks:
                color = CYAN if atk.reflected else MAGENTA
                pygame.draw.rect(screen, color, atk.rect, 2)
            for boss in bosses:
                pygame.draw.rect(screen, CYAN, boss.rect, 2)

        draw_hud(score, level_cfg, lives, parry_cooldown)

        # 가상 화면(800x600)에 흔들림 적용
        ox, oy = get_shake_offset()
        if ox != 0 or oy != 0:
            shaken_screen = screen.copy()
            screen.fill((0, 0, 0))
            screen.blit(shaken_screen, (ox, oy))

        # 완성된 가상 화면을 유저 모니터에 맞춰 레터박스 스케일링 후 출력
        real_screen.fill((0, 0, 0)) # 좌우/상하 남는 여백(레터박스)
        scaled_surface = pygame.transform.scale(screen, (SCALED_W, SCALED_H))
        real_screen.blit(scaled_surface, (OFFSET_X, OFFSET_Y))

        pygame.display.flip()

if __name__ == "__main__":
    while True:
        title_screen()
        diff = difficulty_screen()
        DIFF_SETTINGS.update(diff)
        start_stage = stage_select_screen()
        main(start_stage)
