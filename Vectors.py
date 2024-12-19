from enums.direction import Direction
def get_vector_from_direction(direction):
    dict = {Direction.UP: [-1, 0], Direction.DOWN: [1, 0], Direction.LEFT: [0, -1], Direction.RIGHT: [0, 1]}
    return dict[direction]

def backward(dir):
    dict = {Direction.UP:Direction.DOWN, Direction.DOWN:Direction.UP,Direction.LEFT:Direction.RIGHT, Direction.RIGHT:Direction.LEFT}
    return dict[dir]

def left(dir):
    dict = {Direction.UP:Direction.LEFT, Direction.DOWN:Direction.RIGHT,Direction.LEFT:Direction.DOWN, Direction.RIGHT:Direction.UP}
    return dict[dir]

def right(dir):
    dict = {Direction.UP:Direction.RIGHT, Direction.DOWN:Direction.LEFT,Direction.LEFT:Direction.UP, Direction.RIGHT:Direction.DOWN}
    return dict[dir]

def forward(dir):
    return dir

def calculate_relative_position(pac_dir, out_dir):
    dict = {Direction.UP:forward, Direction.DOWN:backward,Direction.LEFT:left, Direction.RIGHT:right}
    return dict[out_dir](pac_dir)