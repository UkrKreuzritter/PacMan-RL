import time
from cell_map import CellMap
from enums.game_states import GameState
from managers.fruit_manager import FruitManager
from managers.ghost_manager import GhostManager
from entities.pacman import Pacman
from managers.collectibles_manager import CollectibleManager
from managers.level_manager import LevelManager
from stages.stage import Stage
from utils.time_utils import TimeUtils
from enums.direction import Direction
from enums.cell import Cell
from Vectors import get_vector_from_direction, calculate_relative_position
class GameStage(Stage):
    PACMAN_DEAD_TIME = 2500
    EAT_FREEZE_TIME = 500
    LEVEL_END_MUSIC_TIME = 2000
    LEVEL_END_FULL_TIME = 4000
    BACKGROUND_UPDATE_TIME = 150
    START_DELAY = 4000
    def __init__(self, game):
        super().__init__()
        self.collected = 0
        self.game = game
        self.state = GameState.PLAYING
        self._state_start = time.time()
        self.levels = LevelManager(self)
        self.collectibles = CollectibleManager(self)
        self.pacman = Pacman(self)
        self.ghosts = GhostManager(self)
        self.fruits = FruitManager(self)
        self.score = 0
        self.prev_score = 0
        self._started = True
        self._freeze = False
        self.last_collected_time = time.time()
        self.map_BFS = None
        self.queue = None
        self.dead = 0
        self.time_to_kill_pac = game.time_to_kill_pac
        self.REGIME = game.REGIME
        CellMap.get_instance()

    def add_score(self, score):
        self.score += score
    
    def calc_index(self, cell):
        x_size = CellMap.CELLS_PER_PLANE[0]
        x, y = int(cell[0]), int(cell[1])
        return x + y * x_size
    
    def get_distance(self, cell1, cell2):
        ind_1 = self.calc_index(cell1)
        ind_2 = self.calc_index(cell2)
        if not (ind_1 in self.game.DICT):
            return 10000
        for i in self.game.DICT[ind_1]:
            steps, ind_i = i
            if ind_2 == ind_i:
                return steps
        return 10000
    
    def is_ghost_in_square(self, cell, sq, gh_cell):
        x_size, y_size = CellMap.CELLS_PER_PLANE
        w, h = sq
        new_x = min(cell[0]+w-1, x_size-1)
        new_y = max(cell[1]-h+1, 0)
        return cell[0] <= gh_cell[0] <= new_x and new_y <= gh_cell[1] <= cell[1]
    
    def return_square(self, dir, cell):
        x_size, y_size = CellMap.CELLS_PER_PLANE
        x, y = int(self.pacman.cell[0]), int(self.pacman.cell[1])
        w, h = 9, 5
        
        if (dir == Direction.UP):
            return self.is_ghost_in_square((max(x-w//2, 0), max(y-1, 0)), (w,h), cell)
        if (dir == Direction.DOWN):
            return self.is_ghost_in_square((max(x-w//2, 0), min(y+h-2, y_size-1)), (w,h), cell)
        if (dir == Direction.LEFT):
            return self.is_ghost_in_square((max(x-h, 0), min(y+w//2, y_size-1)), (h,w), cell)
        return self.is_ghost_in_square((min(x+1, x_size-1), min(y+w//2, y_size-1)), (h,w), cell)
            
    
    def calculate_danger(self):
        pac_dir = self.pacman.direction
        danger_arr =[0, 0, 0, 0]
        directs = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        directs = [calculate_relative_position(pac_dir, i) for i in directs]
        for i, ghost in enumerate(self.ghosts.ghosts):
            if i>self.REGIME:
                return danger_arr
            for k, dir in enumerate(directs):
                if ghost._can_kill():
                    danger_arr[k] = self.return_square(dir, ghost.cell)
        return danger_arr
        
    
    def calculate_nearest(self, cell):
        x_size = CellMap.CELLS_PER_PLANE[0]
        index = self.calc_index(cell)
        if not (index in self.game.DICT):
            return self.pacman.cell
        for i in self.game.DICT[index]:
            _, ind = i
            x_ind, y_ind = ind % x_size, ind // x_size
            if self.collectibles.get_value_at((x_ind, y_ind)):
                return x_ind, y_ind
        return self.pacman.cell
    
    def is_on_the_side(self, dir, pac_cel, cell):
        if cell == pac_cel:
            return 0
        if dir == Direction.UP:
            return cell[1]<pac_cel[1]
        if dir == Direction.DOWN:
            return pac_cel[1]<cell[1]
        if dir == Direction.LEFT:
            return cell[0]<pac_cel[0]
        return pac_cel[0]<cell[0]
    def get_number_of_pals_in_each_direction(self):
        x_size, y_size = CellMap.CELLS_PER_PLANE
        pac_dir = self.pacman.direction
        directs = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        directs = [calculate_relative_position(pac_dir, i) for i in directs]
        x, y = int(self.pacman.cell[0]), int(self.pacman.cell[1])
        x_s, y_s = self.calculate_nearest((x,y))
        scores = [self.is_on_the_side(i, (x,y), (x_s, y_s)) for i in directs]
        return scores
    def is_a_ghost_frightened(self, cell):
        for i, ghost in enumerate(self.ghosts.ghosts):
            if i>self.REGIME:
                return False
            if int(ghost.cell[0]) == cell[0] and int(ghost.cell[1]) == cell[1] and not ghost._can_kill():
                return True
        return False
    def is_a_ghost_in_cell(self, cell):
        for i, ghost in enumerate(self.ghosts.ghosts):
            if i>self.REGIME:
                return False
            if int(ghost.cell[0]) == cell[0] and int(ghost.cell[1]) == cell[1]:
                return True
        return False
    def view_field(self):
        pac_dir = self.pacman.direction
        directs = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        x_size, y_size = CellMap.CELLS_PER_PLANE
        directs = [get_vector_from_direction(calculate_relative_position(pac_dir, i)) for i in directs]
        found = []
        for y_d, x_d in directs:
            x, y = int(self.pacman.cell[0]), int(self.pacman.cell[1])
            iter = 0
            while self.collectibles.get_value_at((x, y))==0 and CellMap.get_instance().get_cell_type((x, y))!=Cell.WALL and CellMap.get_instance().get_cell_type((x, y))!=Cell.SPACE_GATE and iter < 10 and not self.is_a_ghost_in_cell((x, y)):
                y=(y + y_d+y_size)%y_size
                x=(x + x_d+x_size)%x_size
                iter+=1
            if (CellMap.get_instance().get_cell_type((x, y))==Cell.WALL or CellMap.get_instance().get_cell_type((x, y))==Cell.SPACE_GATE) and iter == 1: # wall
               found.append(-1)
            elif self.is_a_ghost_frightened((x, y)) and iter < 4: # ghost
                found.append(2)
            elif self.is_a_ghost_in_cell((x, y)) and iter < 4: # ghost
                found.append(-3)
            else:
                if(self.collectibles.get_value_at((x, y))==50): # big palette
                    found.append(2)
                elif (self.collectibles.get_value_at((x, y))==10): # pelette
                    found.append(0.5)
                else: # air
                    found.append(0)
            
        return found
    def update_state(self, state_type):
        self.state = state_type
        self._state_start = time.time()
        if state_type == GameState.EAT_GHOST_FREEZE:
            self.ghosts.pause()
        elif state_type == GameState.EAT_FRUIT_FREEZE:
            self.ghosts.pause()

    def is_end(self):
        return self.state == GameState.DEAD_END or self.state == GameState.LEVEL_END
    
    def pause(self):
        if self._started:
            self.ghosts.pause()

    def update(self, dir = Direction.LEFT):    
        self.prev_score = self.score
        time_elapsed = TimeUtils.elapsed(self._state_start)
    
        if self.state == GameState.PLAYING:
            self.collectibles.update()
            self.fruits.update()
            self.pacman.update(dir)
            self.ghosts.update(self.REGIME)

        elif (self.state == GameState.EAT_GHOST_FREEZE or self.state == GameState.EAT_FRUIT_FREEZE) and time_elapsed >= self.EAT_FREEZE_TIME:
            self.update_state(GameState.PLAYING)
            self.ghosts.unpause()

        if (self.prev_score != self.score):
            self.last_collected_time=time.time()

        if time.time() - self.last_collected_time>self.time_to_kill_pac:
            self.pacman.alive = 0 
            self.state = GameState.DEAD_END

    def render(self, screen):
        self.collectibles.render(screen)
        self.fruits.render(screen)

        if self.state != GameState.EAT_GHOST_FREEZE and self.state != GameState.EAT_FRUIT_FREEZE:
            self.pacman.render(screen)

        if self.state != GameState.LEVEL_END:
            self.ghosts.render(screen, self.REGIME)