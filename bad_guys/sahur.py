import pygame
import random
from settings import *

class Sahur:
    def __init__(self): 
        random_size_val = random.uniform(size_randomize[0], size_randomize[1])
        size = (int(orange_size[0] * random_size_val), int(orange_size[1] * random_size_val))

        self.moving_direction, start_pos = self.define_spawn_pos(size)

        self.rect = pygame.Rect(start_pos[0], start_pos[1], int(size[0] // 1.4), int(size[1] // 1.4))
        self.image = pygame.image.load("images/sahur.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(size[0] // 1.4), int(size[1] // 1.4)))

        self.current_frame = 0
        self.animation_timer = 0

    def define_spawn_pos(self, size):
        vel = random.uniform(orange_speed["min"], orange_speed["max"])
        moving_direction = random.choice(["left", "right", "up", "down"])

        if moving_direction == "left":
            start_pos = (width, random.randint(0, height - size[1]))
        elif moving_direction == "right":
            start_pos = (-size[0], random.randint(0, height - size[1]))
        elif moving_direction == "up":
            start_pos = (random.randint(0, width - size[0]), height)
        else:
            start_pos = (random.randint(0, width - size[0]), -size[1])

        self.velocity = vel
        return moving_direction, start_pos
