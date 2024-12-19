import time

from cell_map import CellMap
from entities.entity import Entity
from enums.direction import Direction
from enums.ghost_mode import GhostMode
from utils.file_utils import FileUtils
from utils.time_utils import TimeUtils
import heapq
from enums.ghost_state import GhostState


class Pacman(Entity):
    _icons_loaded = False
    icons = {}

    ICON_SUFFIX = {0: "whole", 1: "open"}
    ICONS_LIST = {
        "pacman-dead",
        "pacman-half-down",
        "pacman-half-left",
        "pacman-half-up",
        "pacman-half-right",
        "pacman-open-down",
        "pacman-open-left",
        "pacman-open-up",
        "pacman-open-right",
        "pacman-third-down",
        "pacman-third-left",
        "pacman-third-up",
        "pacman-third-right",
        "pacman-whole-down",
        "pacman-whole-left",
        "pacman-whole-up",
        "pacman-whole-right",
    }
    DEFAULT_IMAGE = "pacman-open-left"
    DEFAULT_DIRECTION = Direction.LEFT
    START_CELL = (13.5, 26)
    ICON_UPDATE_TIME = 100  # milliseconds after icon is updated
    DEFAULT_LIVES = 1

    def __init__(self, game):
        super().__init__()
        self._load_icons()

        self._next_direction = None
        self._icon_counter = 0
        self.lives = self.DEFAULT_LIVES
        self.is_eating = False
        self.game = game
        self.collectibles_manager = self.game.collectibles

        self.reset()

    def reset(self):
        super().reset()
        self.image = FileUtils.get_image(self.DEFAULT_IMAGE)
        self.direction = self.DEFAULT_DIRECTION

        self.cell = self.START_CELL
        self._update_position(CellMap.get_cell_position(self.cell))
        self._last_icon_update = time.time()

    def _update_direction(self, new_direction, key_pressed=0):

        self._next_direction = new_direction
        # for key in self.KEY_TO_DIRECTION_MAPPING.keys():
        #     if key_pressed[key]:
        #         new_direction = self.KEY_TO_DIRECTION_MAPPING[key]
        # self._next_direction = new_direction
        # break

        if (
            self._next_direction
            and self._can_move_at_direction(self._next_direction)
            and not self._moving
        ):
            self.direction = self._next_direction
            self._next_direction = None

    def _update_icon(self):
        if TimeUtils.elapsed(self._last_icon_update) >= self.ICON_UPDATE_TIME:
            self.image = FileUtils.get_image(self._get_icon_name())
            self._update_counter()
            self._last_icon_update = time.time()

    def _can_move_at_direction(self, direction):
        current_cell = self._target_cell if self._target_cell else self.cell
        next_cell = CellMap.get_instance().get_next_cell(current_cell, direction)
        return self.is_cell_walkable(next_cell)

    def _get_icon_name(self):
        icon_type = Pacman.ICON_SUFFIX[self._icon_counter]
        direction_in_lowercase = self.direction.name.lower()

        return f"pacman-{icon_type}-{direction_in_lowercase}"

    def _update_counter(self):
        self._icon_counter = (self._icon_counter + 1) % 2

    def _get_speed(self):
        if self.game.ghosts.current_mode == GhostMode.FRIGHTENED:
            if self.is_eating:
                speed_percent = self.game.levels.current.pacman_dots_fright
            else:
                speed_percent = self.game.levels.current.pacman_speed_fright
        else:
            if self.is_eating:
                speed_percent = self.game.levels.current.pacman_dots_normal
            else:
                speed_percent = self.game.levels.current.pacman_speed_normal

        return self._get_speed_by_percent(speed_percent)

    def _prepare_move(self, speed):

        self.game.collectibles.handle_collision(self.cell)
        self.game.fruits.handle_collision()

        next_cell = CellMap.get_instance().get_next_cell(self.cell, self.direction)
        if self.is_cell_walkable(next_cell):
            self._moving = True
            self._target_cell = next_cell
            self._move_start_time = time.time()
            self._animated_movement(speed)

    def update(self, key_pressed):
        direction = self._auto_update_direction()
        self._update_direction(direction)
        self._update_icon()
        self._move()

    def _BFS_collectibles(self, start_cell, is_collectable):
        queue = [(0, start_cell)]

        if is_collectable(start_cell):
            return 0

        distances = {}

        while queue:
            distance, cell = heapq.heappop(queue)

            if cell in distances:
                distances[cell] = min(distances[cell], distance + 1)
            else:
                distances[cell] = distance

            if is_collectable(cell):
                return distances[cell]

            for direction in Direction:
                next_cell = CellMap.get_instance().get_next_cell(cell, direction)
                if self.is_cell_walkable(next_cell) and next_cell not in distances:
                    heapq.heappush(queue, (distance + 1, next_cell))

        return None

    def _BFS_ghost(self, ghosts_list, max_distance=10):
        queue = [(0, cell) for cell in ghosts_list]
        distances = {}

        while queue:
            # ic(queue)
            distance, cell = heapq.heappop(queue)

            if cell in distances:
                distances[cell] = min(distances[cell], distance + 1)
                continue

            distances[cell] = distance

            for direction in Direction:
                next_cell = CellMap.get_instance().get_next_cell(cell, direction)
                if self.is_cell_walkable(next_cell) and next_cell not in distances:
                    heapq.heappush(queue, (distance + 1, next_cell))

        return distances

    def calculate_value(self, pos, dct):
        if not dct:
            return 0
        result = 0
        count = 0
        for direction in Direction:
            next_cell = CellMap.get_instance().get_next_cell(pos, direction)
            if self.is_cell_walkable(next_cell):
                count += 1
                result += dct[next_cell]

        return result / count

    def _auto_update_direction(self):

        ghost_cells = [
            ghost.cell
            for ghost in self.game.ghosts.ghosts
            if ghost.state == GhostState.ACTIVE
        ]
        current_cell = self.cell
        possible_coors = []
        for direction in Direction:
            possible_coors.append(
                CellMap.get_instance().get_next_cell(current_cell, direction)
            )

        out_ghost = self._BFS_ghost(ghost_cells)
        # ic(out_ghost, self._BFS_ghost(ghost_cells), ghost_cells)

        DIST = 5
        outs_run = [DIST, DIST, DIST, DIST]
        outs_get = [10000, 10000, 10000, 10000]
        directs = list(Direction)

        dct = {}
        for i, pos in enumerate(possible_coors):
            if self.is_cell_walkable(pos):
                outs_get[i] = self._BFS_collectibles(
                    pos,
                    is_collectable=lambda cell: CellMap.get_instance().is_collectible(
                        cell
                    )
                    and cell not in self.collectibles_manager.collected_cells,
                )
                # outs_run[i] = out_ghost.get(pos, 10000)
                outs_run[i] = self.calculate_value(pos, out_ghost)
                dct[(directs[i], pos)] = outs_get[i]

        direction_final = None
        for i in range(4):
            if min(outs_get) == outs_get[i]:
                # self.direction = directs[i]
                # self._next_direction = directs[i]
                direction_final = directs[i]

        if min(outs_run) < DIST:
            for i in range(4):
                outs_run[i] *= self.is_cell_walkable(possible_coors[i])
            for i in range(4):
                if max(outs_run) == outs_run[i]:
                    # self.direction = directs[i]
                    # self._next_direction = directs[i]
                    direction_final = directs[i]
        return direction_final

        # current_cell = self.cell
        # collectible_distances = self._bfs_collectibles(current_cell)
        # ghost_distances = self._bfs_ghosts()
        # possible_moves = [
        #     CellMap.get_instance().get_next_cell(current_cell, direction)
        #     for direction in Direction
        # ]

        # # Evaluate moves based on distances to collectibles and ghosts
        # best_move = None
        # dct = {}
        # iteration = 0
        # max_score = -float("inf")
        # for i, move in enumerate(possible_moves):
        #     if not self.is_cell_walkable(move):
        #         continue
        #     collectible_score = collectible_distances.get(move, -1000)
        #     ghost_score = ghost_distances.get(move, 1000)
        #     score = ghost_score + collectible_score

        #     if score > max_score:
        #         max_score = score
        #         best_move = list(Direction)[i]

        #     dct[move] = {
        #         "move": list(Direction)[i],
        #         "score": score,
        #         "collectible_score": collectible_score,
        #         "ghost_score": ghost_score,
        #         "collectible_distances": collectible_distances,
        #     }

        # if best_move:
        #     self.direction = best_move

        # ic(best_move, score, ghost_score, collectible_score, dct, self.direction)

    # def _bfs_collectibles(self, start_cell):
    #     distances = self._BFS_collectibles(
    #         start_cell,
    #         is_collectable=lambda cell: CellMap.get_instance().is_collectible(cell)
    #         and cell in self.collectibles_manager.collected_cells,
    #     )
    #     return distances if distances else {}

    # def _bfs_ghosts(self):
    #     ghost_cells = [
    #         ghost.cell
    #         for ghost in self.game.ghosts.ghosts
    #         if ghost.state == GhostState.ACTIVE
    #     ]
    #     return self._BFS_ghost(
    #         ghost_cells,
    #         max_distance=10,
    #     )

    # def _bfs(self, start_cells, is_goal=None, search_collect=False, max_distance=None):
    #     queue = [
    #         (0, start_cell)
    #         for start_cell in (
    #             start_cells if isinstance(start_cells, list) else [start_cells]
    #         )
    #     ]

    #     distances = {}

    #     while queue:
    #         distance, cell = heapq.heappop(queue)

    #         if cell in distances:
    #             continue

    #         distances[cell] = distance

    #         if (
    #             is_goal
    #             and is_goal(cell)
    #             and distances[cell] != 0
    #             and cell not in self.collectibles_manager.collected_cells
    #         ):
    #             ic(cell, is_goal(cell), self.collectibles_manager.collected_cells)
    #             return {cell: distances[cell]}

    #         if max_distance and distance >= max_distance:
    #             continue

    #         for direction in Direction:
    #             next_cell = CellMap.get_instance().get_next_cell(cell, direction)
    #             if self.is_cell_walkable(next_cell) and next_cell not in distances:
    #                 heapq.heappush(queue, (distance + 1, next_cell))

    #     return distances

    # new code

    def _get_direction_to_cell(self, cell):
        print(cell)
        x, y = cell
        current_x, current_y = self.cell

        if x < current_x:
            direction = Direction.LEFT
        elif x > current_x:
            direction = Direction.RIGHT
        elif y < current_y:
            direction = Direction.DOWN
        elif y > current_x:
            direction = Direction.UP
        else:
            raise ValueError("Cell must differ from current cell")

        return direction

    @classmethod
    def _load_icons(cls):
        if not cls._icons_loaded:
            for icon in cls.ICONS_LIST:
                FileUtils.get_image(icon)
