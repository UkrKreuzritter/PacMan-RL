import pygame

from cell_map import CellMap
from enums.game_states import GameState

class CollectibleManager:
    def __init__(self, game=None):
        self.group = pygame.sprite.Group()
        self.game = game
        self.collected = 0
        x_size, y_size = CellMap.CELLS_PER_PLANE
        self.map = [-1]*y_size
        for i in range(y_size):
            self.map[i]=[0 for i in range(x_size)]
        self._load()

    def render(self, screen):
        self.group.draw(screen)

    def add(self, collectible):
        self.group.add(collectible)

    def update(self):
        for collectible in self.group:
            collectible.update()
    def get_value_at(self, cell):
        x, y = cell
        x, y = int(x), int(y)
        return self.map[y][x]
    def handle_collision(self, cell):
        collision = False
        for collectible in self.group:
            if collectible.collides(cell):
                x, y = cell
                self.map[y][x] = 0
                collision = True
                self.game.add_score(collectible.score)
                self.add_collected()
                collectible.on_collect(self.game)
                collectible.kill()

        self.game.pacman.is_eating = collision

    def add_collected(self):
        self.collected += 1
        if self.collected >= CellMap.get_instance().count:
            self.game.update_state(GameState.LEVEL_END)
        else:
            self.game.ghosts.update_counter()

    def _load(self):
        all_collectibles = CellMap.get_instance().collectibles
        for i, collectible_type in enumerate(all_collectibles):
            for cell in all_collectibles[collectible_type]:
                position = CellMap.get_cell_position(cell)
                self.add(collectible_type(position, cell))
                x, y = cell
                if i==0:
                    self.map[y][x] = 10
                else:
                    self.map[y][x] = 50