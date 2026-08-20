import pygame
import random
from gpiozero import Button

pygame.init()
WIDTH = 480 
HEIGHT = 320
flags = pygame.NOFRAME
screen = pygame.display.set_mode([WIDTH, HEIGHT], flags)
pygame.mouse.set_visible(False)
try:
    button = Button(5, pull_up=True)
except:
    button = None

green = (0, 255, 0)
dark_green = (0, 150, 0)
black = (0, 0, 0)
score = 0
high_score = 0
player_x = 70
player_y = 200
y_change = 0
gravity = 1
obstacles = [300, 450, 600]
obstacles_speed = 2.5
active = False
walking_frames = []
frame_index = 0
animation_speed = 0.2
for i in range(18):
    filename = f"images/walking/{i:02d}.png"

    image = pygame.image.load(filename).convert_alpha()
    image = pygame.transform.scale(image, (60, 70))
    image = pygame.transform.flip(image, True, False)

    walking_frames.append(image)

 
pygame.display.set_caption("Pipboy Runner")
background = black
fps = 50
font = pygame.font.Font("monofonto rg.otf", 16)
timer = pygame.time.Clock()

running = True
button_counter = 0
last_score = 0
while running:
    timer.tick(fps)
    screen.fill(background)
    if not active:
        instruction_text = font.render('Press the button to start.', True, green, black)
        screen.blit(instruction_text, (130, 150))
    score_text = font.render(f"Score: {score}", True, green)
    screen.blit(score_text, (50, 50))
    high_score_text = font.render(f'High Score: {high_score}', True, green, black)
    screen.blit(high_score_text, (150, 50))
    floor = pygame.draw.rect(screen, green, [0, 270, WIDTH, 8])

    #player
    if active:
        frame_index += animation_speed
        if frame_index >= len(walking_frames):
            frame_index = 0
    screen.blit(walking_frames[int(frame_index)], (player_x, player_y))

    player_hitbox = pygame.Rect(player_x+20,player_y + 35,24,30)

    obstacle0 = pygame.draw.rect(screen, dark_green, [obstacles[0], 248, 8, 20])
    obstacle1 = pygame.draw.rect(screen, dark_green, [obstacles[1], 248, 8, 20])
    obstacle2 = pygame.draw.rect(screen, dark_green, [obstacles[2], 248, 8, 20])
    jump_pressed = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not active:
                obstacles = [300, 450, 600]
                score = 0
                active = True
            elif event.key == pygame.K_SPACE:
                jump_pressed = True
    button_counter += 1
    if button is not None and button_counter >= 5:
        try:

            if button.is_pressed:
                if not active:
                    obstacles = [300, 450, 600]
                    score = 0
                    active = True
                else:
                    jump_pressed = True

        except Exception as e:
            print(e)
    if jump_pressed and y_change == 0:
        y_change = 15
    for i in range(len(obstacles)):
        if active:
            obstacles[i] -= obstacles_speed
            if obstacles[i] < -8:
                obstacles[i] = random.randint(550, 650)
                score += 1
            if player_hitbox.colliderect(obstacle0) or player_hitbox.colliderect(obstacle1) or player_hitbox.colliderect(obstacle2):
                active = False
                if score > high_score:
                    high_score = score

    if y_change > 0 or player_y < 200:
        player_y -= y_change
        y_change -= gravity
    if player_y > 200:
        player_y = 200
    if player_y == 200 and y_change < 0:
        y_change = 0

    pygame.display.flip()
pygame.quit()