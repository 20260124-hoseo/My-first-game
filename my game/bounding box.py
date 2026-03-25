import pygame
import math

# --- SAT(분리축 정리) 헬퍼 함수 ---
def get_axes(corners):
    axes = []
    for i in range(2):
        p1 = corners[i]
        p2 = corners[i + 1]
        edge = (p2[0] - p1[0], p2[1] - p1[1])
        normal = (-edge[1], edge[0]) 
        length = math.hypot(normal[0], normal[1])
        if length != 0:
            axes.append((normal[0] / length, normal[1] / length))
    return axes

def project(corners, axis):
    dots = [x * axis[0] + y * axis[1] for x, y in corners]
    return min(dots), max(dots)

def sat_collide(corners1, corners2):
    axes = get_axes(corners1) + get_axes(corners2)
    for axis in axes:
        min1, max1 = project(corners1, axis)
        min2, max2 = project(corners2, axis)
        if max1 < min2 or max2 < min1:
            return False
    return True

# 1. 초기화
pygame.init()

# 화면 설정
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Collision Debug UI")

# 폰트 초기화 (UI 텍스트용)
font = pygame.font.SysFont(None, 36)

# 색상 정의
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
RED = (255, 0, 0)      
BLUE = (0, 100, 255)   # 텍스트 가독성을 위해 살짝 밝은 파란색
YELLOW = (255, 255, 0) 
GREEN = (0, 255, 0)    
DARK_RED = (150, 0, 0) 

# 사각형 초기 설정
rect_size = (100, 100)
circle_radius = rect_size[0] // 2

# --- 1) 중앙 사각형 설정 ---
center_pos = (400, 300)
center_aabb_rect = pygame.Rect(0, 0, rect_size[0], rect_size[1])
center_aabb_rect.center = center_pos

center_surface = pygame.Surface(rect_size, pygame.SRCALPHA)
center_surface.fill(GRAY)
center_angle = 0  

# --- 2) 왼쪽 사각형 ---
moving_rect = pygame.Rect(0, 0, rect_size[0], rect_size[1])
moving_rect.center = (200, 300)

# 속도 및 프레임 설정
move_speed = 2
clock = pygame.time.Clock()

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_a]: moving_rect.x -= move_speed
    if keys[pygame.K_d]: moving_rect.x += move_speed
    if keys[pygame.K_w]: moving_rect.y -= move_speed
    if keys[pygame.K_s]: moving_rect.y += move_speed

    if keys[pygame.K_z]:
        center_angle += 2
    else:
        center_angle += 1
    
    center_angle %= 360

    # --- 충돌 계산용 변수 준비 ---
    dx = moving_rect.centerx - center_pos[0]
    dy = moving_rect.centery - center_pos[1]
    distance_squared = dx**2 + dy**2
    radius_sum_squared = (circle_radius * 2)**2

    hw, hh = rect_size[0] / 2, rect_size[1] / 2
    angle_rad = math.radians(-center_angle)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    local_corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    world_corners = []
    for lx, ly in local_corners:
        rx = lx * cos_a - ly * sin_a
        ry = lx * sin_a + ly * cos_a
        world_corners.append((rx + center_pos[0], ry + center_pos[1]))

    moving_corners = [
        moving_rect.topleft,
        moving_rect.topright,
        moving_rect.bottomright,
        moving_rect.bottomleft
    ]

    # --- 💡 1. 개별 충돌 여부 판단 ---
    # 이제 if-elif로 묶지 않고 각각 따로 검사하여 True/False를 저장합니다.
    hit_circle = distance_squared < radius_sum_squared
    hit_obb = sat_collide(moving_corners, world_corners)
    hit_aabb = center_aabb_rect.colliderect(moving_rect)

    # --- 💡 2. 배경색 결정 (기존 우선순위 유지) ---
    if hit_circle:
        bg_color = YELLOW
    elif hit_obb:
        bg_color = DARK_RED 
    elif hit_aabb:
        bg_color = GREEN
    else:
        bg_color = BLACK

    # 화면 배경 채우기
    screen.fill(bg_color)
    
    # --- 도형 그리기 ---
    pygame.draw.rect(screen, GRAY, moving_rect)
    rotated_surface = pygame.transform.rotate(center_surface, center_angle)
    temp_rotated_rect = rotated_surface.get_rect(center=center_pos)
    screen.blit(rotated_surface, temp_rotated_rect.topleft)

    pygame.draw.rect(screen, RED, center_aabb_rect, 2)
    pygame.draw.rect(screen, RED, moving_rect, 2)
    pygame.draw.circle(screen, BLUE, center_pos, circle_radius, 2)
    pygame.draw.circle(screen, BLUE, moving_rect.center, circle_radius, 2)
    pygame.draw.polygon(screen, GREEN, world_corners, 2)

    # --- 💡 3. 좌측 상단 UI 텍스트 렌더링 ---
    # 충돌 시 요청하신 색상의 'HIT', 충돌 안 했을 땐 회색 'MISS' 표시
    text_aabb = font.render(f"AABB: {'HIT' if hit_aabb else 'MISS'}", True, RED if hit_aabb else GRAY)
    text_obb = font.render(f"OBB: {'HIT' if hit_obb else 'MISS'}", True, GREEN if hit_obb else GRAY)
    text_circle = font.render(f"Circle: {'HIT' if hit_circle else 'MISS'}", True, BLUE if hit_circle else GRAY)

    # 화면에 텍스트 찍기 (blit)
    screen.blit(text_aabb, (10, 10))    # (x, y) 좌표
    screen.blit(text_obb, (10, 50))
    screen.blit(text_circle, (10, 90))

    pygame.display.flip()

pygame.quit()
