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

# 이미지 초기화 (크기 원상 복구)
try:
    PLAYER_IMAGES = load_sprites(_asset("sprites", "player.png"), 3, 8, 8, PLAYER_W, PLAYER_H)
    FLAME_IMAGES  = load_sprites(_asset("sprites", "flame.png"), 4, 8, 8, PLAYER_W, PLAYER_H)
    PARRY_IMAGES  = load_sprites(_asset("sprites", "parry.png"), 4, 16, 16, PARRY_SIZE, PARRY_SIZE)
    METEOR_IMAGES = load_sprites(_asset("sprites", "meteor.png"), 8, 96, 96, METEOR_RENDER_W, METEOR_RENDER_H, cols=8)
    ENEMY_SHIP_IMAGES = load_sprites(_asset("sprites", "enemy_ship1.png"), 3, 8, 8, E_SHIP_W, E_SHIP_H, cols=3)

    EXPLOSION_IMAGES = load_sprites(_asset("sprites", "enemy_boom.png"), 6, 8, 8, 40, 40, cols=3) 
    ORANGE_EXP = EXPLOSION_IMAGES[0:3]
    BLUE_EXP = EXPLOSION_IMAGES[3:6]

    ATTACK_W, ATTACK_H = 20, 20 
    attack_img_raw = pygame.image.load(_asset("sprites", "enemy_attack1.png")).convert_alpha()
    ATTACK_IMG = pygame.transform.scale(attack_img_raw, (ATTACK_W, ATTACK_H))

    ENEMY_ATTACK_SOUND = pygame.mixer.Sound(_asset("sounds", "laserSmall_002.ogg"))

    METEOR_SOUND = pygame.mixer.Sound(_asset("sounds", "meteor_boom.ogg"))
    METEOR_SOUND.set_volume(0.3)

    PARRY_SOUND = pygame.mixer.Sound(_asset("sounds", "farry.mp3"))

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
_neb_flip    = pygame.transform.flip(_neb_img, True, True)
_planet_imgs = [_load_bg(f"planets{i}.png") for i in range(1, 6)]
_dust_img    = _load_bg("dust.png")
_dust_flip   = pygame.transform.flip(_dust_img, True, True)

# 레이어 순서: Background → nebulae → planets → dust
# type "single" : 동일 이미지 반복
# type "flip"   : 교대로 상하좌우 반전하여 이음새 없이 반복
# type "random" : 5종 이미지 중 무작위 선택하여 반복
BG_LAYERS = [
    {"y": 0.0, "speed": 0.3, "type": "single", "img": _bg_img},
    {"y": 0.0, "speed": 0.6, "type": "flip",   "img": _neb_img,  "top": _neb_flip},
    {"y": 0.0, "speed": 1.6, "type": "random", "imgs": _planet_imgs,
     "cur": random.choice(_planet_imgs), "prev": random.choice(_planet_imgs)},
    {"y": 0.0, "speed": 1.0, "type": "flip",   "img": _dust_img, "top": _dust_flip},
]

def update_bg_layers():
    for L in BG_LAYERS:
        L["y"] += L["speed"]
        if L["y"] >= HEIGHT:
            L["y"] -= HEIGHT
            if L["type"] == "flip":
                L["img"], L["top"] = L["top"], L["img"]
            elif L["type"] == "random":
                L["prev"] = L["cur"]
                L["cur"] = random.choice(L["imgs"])

def draw_bg_layers():
    for L in BG_LAYERS:
        y = int(L["y"])
        if L["type"] == "single":
            screen.blit(L["img"], (0, y - HEIGHT))
            screen.blit(L["img"], (0, y))
        elif L["type"] == "flip":
            screen.blit(L["top"], (0, y - HEIGHT))
            screen.blit(L["img"], (0, y))
        elif L["type"] == "random":
            screen.blit(L["prev"], (0, y - HEIGHT))
            screen.blit(L["cur"], (0, y))

PARRY_SEQ = [3, 3, 3, 3, 2, 2, 2, 1, 1, 0]

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
    def __init__(self, target_x, target_y):
        self.w = E_SHIP_W
        self.h = E_SHIP_H
        self.x = (WIDTH / 2) - (self.w / 2)
        self.y = -self.h
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 4 # 속도 원상 복구
        self.rect = pygame.Rect(int(self.x), int(self.y), self.w, self.h)
        self.frame = 1
        
        self.is_in_position = False
        self.attack_timer = random.randint(1 * FPS, 8 * FPS)

    def update(self):
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
                self.attack_timer = random.randint(1 * FPS, 8 * FPS)
                return True
        return False

    def draw(self, surface):
        surface.blit(ENEMY_SHIP_IMAGES[self.frame], self.rect)

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
        self.speed = 6 # 투사체 속도 원상 복구
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

def main():
    global enemy_ships
    
    # 시작 Y 좌표 원상 복구
    player_rect = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 100, PLAYER_W, PLAYER_H)
    meteors = []
    enemy_ships = []
    enemy_attacks = []
    explosions = [] 
    
    score = 0
    lives = 5
    invincible = 0
    
    stage_timer = 0
    ships_spawned = 0
    meteor_spawn_timer = 0
    
    parry_cooldown = 0
    parry_anim_idx = -1 
    parry_anim_timer = 0
    parry_active_timer = 0 
    
    show_hitbox = False

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

        level_cfg = LEVELS[0]

        # --- 적 우주선 생성 로직 ---
        if stage_timer >= 5 * FPS and ships_spawned < 8:
            if (stage_timer - 5 * FPS) % int(0.5 * FPS) == 0:
                pair_idx = ships_spawned // 2 
                left_target_x = (WIDTH / 9) * (pair_idx + 1) - (E_SHIP_W / 2)
                right_target_x = (WIDTH / 9) * (8 - pair_idx) - (E_SHIP_W / 2)
                target_y = 80 # 도착 높이 원상 복구
                
                enemy_ships.append(EnemyShip(left_target_x, target_y))
                enemy_ships.append(EnemyShip(right_target_x, target_y))
                ships_spawned += 2

        # --- 운석 생성 로직 ---
        meteor_spawn_timer += 1
        if meteor_spawn_timer >= level_cfg["spawn"]:
            meteor_spawn_timer = 0
            x = random.randint(0, WIDTH - ENEMY_W)
            speed = random.randint(level_cfg["min_speed"], level_cfg["max_speed"])
            meteors.append(Meteor(x, -ENEMY_H, ENEMY_W, ENEMY_H, speed))

        # --- 위치 및 애니메이션 업데이트 ---
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
                    if atk.rect.colliderect(ship.rect):
                        explosions.append(Explosion(ship.rect.center, ORANGE_EXP))
                        enemy_ships.remove(ship)
                        score += 50
                        EXPLOSION_SOUND.play()
                for m in meteors:
                    if m.active and atk.rect.colliderect(m.rect):
                        m.destroy()
                        score += 10
                        METEOR_SOUND.play()

        # --- 플레이어 피격 판정 ---
        if invincible > 0:
            invincible -= 1
        else:
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
                    else:
                        hit = True
                        atk.active = False
                        break

            if not hit:
                for m in meteors:
                    if m.active and player_rect.colliderect(m.rect):
                        if parry_active_timer > 0:
                            pass 
                        else:
                            hit = True
                            m.destroy()
                            METEOR_SOUND.play()
                            break
            
            if not hit:
                for ship in enemy_ships:
                    if player_rect.colliderect(ship.rect):
                        if parry_active_timer > 0:
                            pass 
                        else:
                            hit = True
                            break

            if hit:
                lives -= 1
                invincible = 90
                trigger_shake(15) # 화면 흔들림 강도 원상 복구
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

        for ship in enemy_ships:
            ship.draw(screen)

        for atk in enemy_attacks:
            atk.draw(screen)

        for m in meteors:
            m.draw(screen)
            
        for exp in explosions:
            exp.draw(screen)

        if show_hitbox:
            pygame.draw.rect(screen, GREEN, player_rect, 2)
            pygame.draw.circle(screen, CYAN, player_rect.center, int(PARRY_RADIUS), 2)
            for m in meteors:
                if m.active: pygame.draw.rect(screen, RED, m.rect, 2)
            for ship in enemy_ships:
                pygame.draw.rect(screen, YELLOW, ship.rect, 2)
            for atk in enemy_attacks:
                color = CYAN if atk.reflected else MAGENTA
                pygame.draw.rect(screen, color, atk.rect, 2)

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
    main()