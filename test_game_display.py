import pygame
import sys
import random
from hand_control import HandController
from good_guys.orange import Orange
from good_guys.chungus import Chungus
from good_guys.ugandan import Ugandan
from bad_guys.banana import Banana
from bad_guys.coffee import Coffee
from bad_guys.feet import Feet
from bad_guys.sahur import Sahur

pygame.init()
pygame.mixer.init()

# Screen
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battle of the Brain Rot")

# Background
background = pygame.image.load("images/background.png").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Fist
fist_img = pygame.image.load("images/fist.png").convert_alpha()
fist_img = pygame.transform.scale(fist_img, (160, 160))
fist_rect = fist_img.get_rect()

# Fonts
title_font = pygame.font.Font(None, 100)
sub_font = pygame.font.Font(None, 45)
ui_font = pygame.font.Font(None, 60)

# Game varbs
clock = pygame.time.Clock()
running = True
game_active = False
score = 0
game_time = 120  
start_ticks = None

# Sounds
try:
    smack_sound = pygame.mixer.Sound("smack.mp3")
    smack_sound.set_volume(0.5)
except Exception as e:
    print("Could not load smack.mp3:", e)
    smack_sound = None

try:
    pygame.mixer.music.load("sigma.mp3")
    pygame.mixer.music.set_volume(0.4)
except Exception as e:
    print("Could not load sigma.mp3:", e)

# Hand controller
hand = HandController()
try:
    hand.start()
except Exception as e:
    print("Hand control failed:", e)
    hand = None

# Spawn
def spawn_entities():
    good_guys = [Orange(), Chungus(), Ugandan()]
    bad_guys = [Banana(), Coffee(), Feet(), Sahur()]
    for g in good_guys + bad_guys:
        g.image = pygame.transform.scale(g.image, (int(g.rect.width * 1.6), int(g.rect.height * 1.6)))
        g.rect.width = int(g.rect.width * 1.6)
        g.rect.height = int(g.rect.height * 1.6)
    return good_guys, bad_guys

good_guys, bad_guys = spawn_entities()

# Start 
def draw_start_screen():
    SCREEN.blit(background, (0, 0))
    title_text = title_font.render("Battle of the Brain Rot", True, (255, 200, 0))
    sub_text = sub_font.render("Destroy all the Gen Alpha brainrot characters!", True, (255, 255, 255))
    sub_text2 = sub_font.render("Make sure to keep the original brain rot alive!", True, (255, 255, 255))
    prompt = ui_font.render("Make a fist or click to start", True, (255, 255, 255))

    SCREEN.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//2 - 150))
    SCREEN.blit(sub_text, (SCREEN_WIDTH//2 - sub_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
    SCREEN.blit(sub_text2, (SCREEN_WIDTH//2 - sub_text2.get_width()//2, SCREEN_HEIGHT//2))
    SCREEN.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2 + 100))
    pygame.display.flip()

# Game loop
try:
    while running:
        if not game_active:
            pygame.mixer.music.stop()
            draw_start_screen()
            start_click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    start_click = True

            if hand:
                _, _, _, click = hand.update()
                if click:
                    start_click = True

            if start_click:
                game_active = True
                start_ticks = pygame.time.get_ticks()
                score = 0
                good_guys, bad_guys = spawn_entities()
                
                try:
                    pygame.mixer.music.play(-1)
                except:
                    pass

        else:
            mouse_clicked = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_clicked = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_active = False

            # Hands
            frame_surface, hx, hy, click = hand.update() if hand else (None, 0.5, 0.5, False)
            if click:
                mouse_clicked = True

            # Timer
            elapsed = (pygame.time.get_ticks() - start_ticks) / 1000
            time_left = max(0, int(game_time - elapsed))
            if time_left <= 0:
                game_active = False

                pygame.mixer.music.stop()
                continue

            # Fist
            mx = int(hx * SCREEN_WIDTH)
            my = int(hy * SCREEN_HEIGHT)
            fist_rect.center = (mx, my)

            SCREEN.blit(background, (0, 0))

            # Move & draw 
            for g in good_guys + bad_guys:
                if g.moving_direction == "left":
                    g.rect.x -= g.velocity
                    if g.rect.right < 0: g.rect.left = SCREEN_WIDTH
                elif g.moving_direction == "right":
                    g.rect.x += g.velocity
                    if g.rect.left > SCREEN_WIDTH: g.rect.right = 0
                elif g.moving_direction == "up":
                    g.rect.y -= g.velocity
                    if g.rect.bottom < 0: g.rect.top = SCREEN_HEIGHT
                else:
                    g.rect.y += g.velocity
                    if g.rect.top > SCREEN_HEIGHT: g.rect.bottom = 0
                SCREEN.blit(g.image, g.rect)

            # Collisions 
            if mouse_clicked:
                hit_anything = False
                for bad in list(bad_guys):
                    if fist_rect.colliderect(bad.rect):
                        score += 3
                        bad_guys.remove(bad)
                        bad_guys.append(random.choice([Banana(), Coffee(), Feet(), Sahur()]))
                        hit_anything = True

                for good in list(good_guys):
                    if fist_rect.colliderect(good.rect):
                        score -= 1
                        good_guys.remove(good)
                        good_guys.append(random.choice([Orange(), Chungus(), Ugandan()]))
                        hit_anything = True
                        
                if hit_anything and smack_sound:
                    smack_sound.play()


            # Draw fist 
            SCREEN.blit(fist_img, fist_rect)

            # Embed camera feed
            if frame_surface:
                cam_scaled = pygame.transform.scale(frame_surface, (320, 240))
                SCREEN.blit(cam_scaled, (SCREEN_WIDTH - 340, SCREEN_HEIGHT - 260))

            # UI
            score_text = ui_font.render(f"Score: {score}", True, (255, 255, 255))
            time_text = ui_font.render(f"Time: {time_left}s", True, (255, 255, 255))
            SCREEN.blit(score_text, (20, 20))
            SCREEN.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 20, 20))

            pygame.display.flip()
            clock.tick(60)
finally:
    try:
        hand.stop()
    except:
        pass
    pygame.quit()
    sys.exit()
