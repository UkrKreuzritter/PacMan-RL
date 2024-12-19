import pygame
from entities.pacai import pacai_class
from cell_map import CellMap
from stages.GameStage import GameStage
from utils.file_utils import FileUtils
from enums.direction import Direction
from enums.game_states import GameState
from Vectors import calculate_relative_position
import sys
from enums.cell import Cell
import numpy as np
import pickle
import neat
import heapq
generation = 0
import json
import time
timer = 80
time_to_kill_pac = 10
REGIME = 4
best_model = None
fitness = -10000000
# 0 = Просто палети збирати
# 1 = Один привид
# 4 = БЄГІТЄ, Я КОНЧЕНИЙ
class Game:
    BACKGROUND_CORDS = (0, 0)
    BACKGROUND_NAME = "board"
    MAX_FPS = 60
    GAME_ICON_NAME = "icon"
    GAME_TITLE = "PACMAN"
    DIMENSIONS = (1300, 720)
    def __init__(self, n):
        global time_to_kill_pac, REGIME
        pygame.init()
        self.pop, self.alive = n, n
        self._clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.DIMENSIONS)
        self.background = FileUtils.get_image(self.BACKGROUND_NAME)
        self.time_to_kill_pac = time_to_kill_pac
        self.REGIME = REGIME
        self.frame = 1
        self.pacman_start = (13.5, 26)
        CellMap.get_instance()
        self.DICT = {}
        # self.scores = [[0]for i in range(n)]
        # self.metrics = [[0]for i in range(n)]
        # self.deltas = [[0]for i in range(n)]
        self.calculate_dict()
        self.game_stages = [GameStage(self) for i in range(n)]
        self._update_window()
        
    
    def _update(self, arr):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_ESCAPE]:
            sys.exit(0)
        self.alive = self.pop
        for num, i in enumerate(self.game_stages):
            if i and not i.is_end():
                i.update(arr[num])
            if i.is_end():
                self.alive-=1

    def _render(self):
        self.screen.blit(self.background, self.BACKGROUND_CORDS)
        for i in self.game_stages:
            if i and not i.is_end():
                i.render(self.screen)

    def _update_window(self):
        icon = FileUtils.get_image(self.GAME_ICON_NAME)
        pygame.display.set_caption(self.GAME_TITLE)
        pygame.display.set_icon(icon)
        pygame.display.flip()

    def get_x_y(self, x, y):
        x_size, y_size = CellMap.CELLS_PER_PLANE
        return (x+x_size)%x_size, (y+y_size)%y_size
    def check_if_accessible(self, cell):
        return CellMap.get_instance().get_cell_type(cell)!=Cell.WALL and CellMap.get_instance().get_cell_type(cell)!=Cell.SPACE_GATE

    def BFS(self, start_cell):
        x_size, y_size = CellMap.CELLS_PER_PLANE
        max = x_size*y_size+1
        map_BFS = np.zeros(x_size*y_size)+max
        queue = []
        heapq.heappush(queue, (0, start_cell))
        while queue:
            gotten = heapq.heappop(queue)
            val = gotten[0]
            x, y = int(gotten[1][0]), int(gotten[1][1])
            index = x + y * x_size
            if map_BFS[index]!=max:
                map_BFS[index] = min(map_BFS[index], val+1)
                continue
            map_BFS[index] = val
            possible_coors =[self.get_x_y(x+1, y),self.get_x_y(x-1, y),self.get_x_y(x, y+1),self.get_x_y(x, y-1)]
            for coor in possible_coors:
                new_x, new_y = coor[0], coor[1]
                new_index = new_x + new_y * x_size
                if self.check_if_accessible(coor) and map_BFS[new_index]==max:
                    heapq.heappush(queue,(val+1, coor))
        return map_BFS

    def add_to_dict(self, BFS_res, cell):
        x_size, y_size = CellMap.CELLS_PER_PLANE
        maxim = x_size*y_size+1
        x, y = int(cell[0]), int(cell[1])
        index = x + y * x_size
        self.DICT[index] = []
        for y_bfs in range(y_size):
            for x_bfs in range(x_size):
                index_bfs = x_bfs + y_bfs * x_size
                if BFS_res[index_bfs]!=maxim:
                    self.DICT[index].append((BFS_res[index_bfs], index_bfs))
        self.DICT[index].sort()
    
    def calculate_dict(self):
        x_size, y_size = CellMap.CELLS_PER_PLANE
        maxim = x_size*y_size+1
        BFS_res = self.BFS(self.pacman_start)
        self.add_to_dict(BFS_res, self.pacman_start)
        for y in range(y_size):
            for x in range(x_size):
                index_bfs = x + y * x_size
                if BFS_res[index_bfs]!=maxim:
                    new_BFS = self.BFS((x, y))
                    self.add_to_dict(new_BFS, (x, y))



def draw_net(screen, config, genome):
    BLACK = (0, 255, 255)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)

    labels_input = ["Line forward", "Line to right", "Line backward", "Line to left", "Min dist forward", "Min dist right", "Min dist backward", "Min dist left",
                    "Check forward", "Check right", "Check down", "Check left"]
    labels_output = ["Go forward", "Go right", "Go backward", "Go left"]

    inputs = config.genome_config.input_keys
    outputs = config.genome_config.output_keys
    nodes = list(genome.nodes.keys())
    connections = genome.connections

    node_positions = {}
    layer_gap = 50

    # Initialize font
    pygame.font.init()
    font = pygame.font.Font(None, 24)

    # Input nodes
    for i, node in enumerate(inputs):
        node_positions[node] = (750, 100 + layer_gap * i)
        # Render input labels
        label = font.render(labels_input[i], True, GREEN)
        screen.blit(label, (node_positions[node][0] - 150, node_positions[node][1] - 10))

    # Output nodes
    for i, node in enumerate(outputs):
        node_positions[node] = (1050, 150 + 3*layer_gap * (i))
        # Render output labels
        label = font.render(labels_output[i], True, BLACK)
        screen.blit(label, (node_positions[node][0] + 20, node_positions[node][1] - 10))

    # Hidden nodes
    hidden_nodes = [n for n in nodes if n not in inputs and n not in outputs]
    for i, node in enumerate(hidden_nodes):
        node_positions[node] = (900, 125 + layer_gap * (i - 1))

    # Draw connections
    for conn_key, conn in connections.items():
        if conn.enabled:
            start = node_positions[conn_key[0]]
            end = node_positions[conn_key[1]]
            color = RED if conn.weight > 0 else BLUE
            pygame.draw.line(screen, color, start, end, 2)

    # Draw nodes
    for node, pos in node_positions.items():
        color = RED
        if node in inputs:
            color = GREEN
        elif node in outputs:
            color = BLACK
        pygame.draw.circle(screen, color, pos, 10)



def run_pacman(genomes, config):
    global generation, timer, best_model, fitness
    
    best_model = genomes[0][1]
    nets = []
    for _, g in genomes:
        nets.append(neat.nn.FeedForwardNetwork.create(g, config))
        g.fitness = 0


    # Init my game
    game = Game(len(genomes))
    generation_font = pygame.font.SysFont("Arial", 30)

    
    generation += 1
    directs = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
    max_score = 0
    outs = [None for i in genomes]
    while game.frame<timer*game.MAX_FPS and game.alive>0:
        fitness = -1
        for index, stage in enumerate(game.game_stages):
            if stage.is_end():
                outs[index] = None
            else:
                pai = pacai_class(stage).arr
                output = nets[index].activate(pai)
                i = directs[output.index(max(output))]
                outs[index] = calculate_relative_position(stage.pacman.direction,i)

        for i, stage in enumerate(game.game_stages):
            max_score = max(max_score, stage.collectibles.collected)
            if not stage.is_end():
                # game.scores[i][0] = stage.score
                # game.metrics[i][0] +=(stage.score - stage.prev_score)
                # game.deltas[i][0] +=(stage.score - stage.prev_score)/game.frame*game.MAX_FPS
                genomes[i][1].fitness += (stage.score - stage.prev_score) # metrics
                if(genomes[i][1].fitness and fitness<genomes[i][1].fitness):
                    fitness = genomes[i][1].fitness
                    best_model = genomes[i][1]

        if game.alive==0:
            break
        game.frame+=1
        game._update(outs)
        game._render()
        game._clock.tick(Game.MAX_FPS)
        text = generation_font.render("Generation: " + str(generation-1) + "     Remain time: " + str(int(timer-game.frame//game.MAX_FPS))+ "      " + str(max_score)+"/244", True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (275, 40)
        game.screen.blit(text, text_rect)
        draw_net(game.screen, config, best_model)
        pygame.display.update()
        pygame.event.pump()
    # with open(f"result{time.time()}.json", "w") as f:
    #     json.dump({"scores": game.scores, "metrics": game.metrics, "deltas": game.deltas}, f)
    for i, stage in enumerate(game.game_stages):
        if stage.state == GameState.DEAD_END:
            genomes[i][1].fitness -= 2000
    
    print(f"Max score is: {max_score} out of 244. {round(max_score/2.44,3)}%")
    
    
def create_population_with_base_genome(config, base_genome):
    """
    Initialize a NEAT population using a base genome.
    """
    # Create a new population with the NEAT config
    population = neat.Population(config)

    # Replace the initial population with clones of the base genome
    for genome_id, genome in population.population.items():
        genome.connections = base_genome.connections.copy()
        genome.nodes = base_genome.nodes.copy()
        genome.fitness = None  # Reset fitness for new training

    return population
if __name__ == "__main__":
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Create core evolution algorithm class
    
    with open("winner15.pkl", "rb") as f:
        winner = pickle.load(f)
    p = create_population_with_base_genome(config, winner)
    # Add reporter for fancy statistical result
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    winner = p.run(run_pacman, 5)
    with open("winner16.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()
    
