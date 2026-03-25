import pygame

# 1. 초기화
pygame.init()

# 화면 설정
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Collision Detection: AABB vs Circle")

# 색상 정의
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)      # AABB 색상
BLUE = (0, 0, 255)     # 바운딩 서클 색상
YELLOW = (255, 255, 0) # 원형 충돌 배경색
GREEN = (0, 255, 0)    # AABB 충돌 배경색

# 사각형 초기 설정
rect_size = (100, 100)
circle_radius = rect_size[0] // 2  # 반지름 50

# 1) 중앙 사각형 (고정)
center_rect = pygame.Rect(0, 0, rect_size[0], rect_size[1])
center_rect.center = (400, 300)

# 2) 왼쪽 사각형 (이동 가능)
moving_rect = pygame.Rect(0, 0, rect_size[0], rect_size[1])
moving_rect.center = (200, 300)

# 속도 및 프레임 설정
move_speed = 2
clock = pygame.time.Clock()

# 메인 루프
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # WASD 이동 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: moving_rect.x -= move_speed
    if keys[pygame.K_d]: moving_rect.x += move_speed
    if keys[pygame.K_w]: moving_rect.y -= move_speed
    if keys[pygame.K_s]: moving_rect.y += move_speed

    # --- 충돌 감지 로직 ---
    # 1. 원형 충돌 계산 (루트 없이 거리의 제곱으로 비교)
    dx = moving_rect.centerx - center_rect.centerx
    dy = moving_rect.centery - center_rect.centery
    distance_squared = dx**2 + dy**2
    radius_sum_squared = (circle_radius * 2)**2 # (50 + 50)의 제곱

    # 조건문 판단
    if distance_squared < radius_sum_squared:
        # 두 원이 닿았을 때 (가장 안쪽 충돌)
        bg_color = YELLOW
    elif center_rect.colliderect(moving_rect):
        # 원은 안 닿았지만 사각형(AABB)끼리 닿았을 때 (모서리 부분)
        bg_color = GREEN
    else:
        # 아무 충돌도 없을 때
        bg_color = BLACK

    # 화면 그리기 (위에서 결정된 배경색 적용)
    screen.fill(bg_color)
    
    # 본체(회색) 그리기
    pygame.draw.rect(screen, GRAY, center_rect)
    pygame.draw.rect(screen, GRAY, moving_rect)

    # AABB(빨간 테두리 사각형) 표시
    pygame.draw.rect(screen, RED, center_rect, 2)
    pygame.draw.rect(screen, RED, moving_rect, 2)

    # 원형 바운딩 박스(파란 테두리 원) 표시
    pygame.draw.circle(screen, BLUE, center_rect.center, circle_radius, 2)
    pygame.draw.circle(screen, BLUE, moving_rect.center, circle_radius, 2)

    # 업데이트
    pygame.display.flip()

pygame.quit()