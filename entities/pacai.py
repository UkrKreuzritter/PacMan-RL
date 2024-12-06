from enums.ghost_mode import GhostMode
from enums.direction import Direction
import pygame
import os
import numpy as np
class pacai_class():
    def __init__(self, direction, map, collected):
        self.direction = self.encode_dir(direction)
        self.map = map
        self.collected = collected
    def __str__(self):
        return str(self.map)
    def encode_dir(self, dir):
        if dir == Direction.LEFT:
            return 1
        if dir == Direction.RIGHT:
            return 2
        if dir == Direction.DOWN:
            return 3
        return 4
    def dir_to_num(self, dir):
        if dir == Direction.LEFT:
            return (-1, 0)
        if dir == Direction.RIGHT:
            return (1, 0)
        if dir == Direction.DOWN:
            return (0, 1)
        return (0, -1)
    def calc_dif_of_dirs(self, dir1, dir2):
        return abs(dir1[0]-dir2[0])+abs(dir1[1]-dir2[1])
    def save_results(self):
        num = len(os.listdir("train\pics"))
        pygame.image.save(self.map, f"train\pics\pic_{num}.jpg")
        with open('train\dir.txt', 'a') as f:
            f.write(str(self.direction) + " " + str(self.collected)+"\n")