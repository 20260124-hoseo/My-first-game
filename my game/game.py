import pygame
import sys
import random # 1. 무작위 색상을 위해 추가

pygame.init()
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Circle vs Square - Color Change Mode")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
font = pygame.font.SysFont(None, 30)

# 초기 위치 및 색상 설정
circle_x, circle_y = 250, 250
circle_radius = 40
circle_color = WHITE # 원의 현재 색상

rect_width, rect_height = 80, 80
rect_x = 750 - (rect_width // 2)
rect_y = 250 - (rect_height // 2)
rect_color = WHITE # 사각형의 현재 색상

BASE_SPEED = 5
clock = pygame.time.Clock()
running = True

while running:
    # --- 1. 이벤트 처리 (키를 '누르는 순간' 감지) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 키보드를 누르는 순간(KEYDOWN) 색상 변경
        if event.type == pygame.KEYDOWN:
            # 원 조작키(W,A,S,D) 중 하나라도 누르면 원 색상 변경
            if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                circle_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            
            # 사각형 조작키(방향키) 중 하나라도 누르면 사각형 색상 변경
            if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                rect_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    # --- 2. 실시간 이동 감지 (기존 방식 유지) ---
    keys = pygame.key.get_pressed()
    current_speed = BASE_SPEED * 2 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else BASE_SPEED

    if keys[pygame.K_w]: circle_y -= current_speed
    if keys[pygame.K_s]: circle_y += current_speed
    if keys[pygame.K_a]: circle_x -= current_speed
    if keys[pygame.K_d]: circle_x += current_speed

    if keys[pygame.K_UP]:    rect_y -= current_speed
    if keys[pygame.K_DOWN]:  rect_y += current_speed
    if keys[pygame.K_LEFT]:  rect_x -= current_speed
    if keys[pygame.K_RIGHT]: rect_x += current_speed

    # --- 3. 경계 처리 ---
    circle_x = max(circle_radius, min(circle_x, SCREEN_WIDTH - circle_radius))
    circle_y = max(circle_radius, min(circle_y, SCREEN_HEIGHT - circle_radius))
    rect_x = max(0, min(rect_x, SCREEN_WIDTH - rect_width))
    rect_y = max(0, min(rect_y, SCREEN_HEIGHT - rect_height))

    # --- 4. 그리기 ---
    screen.fill(BLACK)
    
    # 설정된 circle_color와 rect_color로 그리기
    pygame.draw.circle(screen, circle_color, (int(circle_x), int(circle_y)), circle_radius)
    pygame.draw.rect(screen, rect_color, [rect_x, rect_y, rect_width, rect_height])

    # 상태 표시
    status = "BOOST!" if current_speed > BASE_SPEED else "Normal"
    status_text = font.render(f"Speed: {status}", True, WHITE)
    screen.blit(status_text, (10, 40))

    # FPS 및 좌표 제목 표시
    current_fps = int(clock.get_fps())
    fps_text = font.render(f"FPS: {current_fps}", True, WHITE)
    screen.blit(fps_text, (10, 10))
    
    title_str = f"Circle: ({int(circle_x)}, {int(circle_y)}) | Rect: ({int(rect_x)}, {int(rect_y)})"
    pygame.display.set_caption(title_str)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()