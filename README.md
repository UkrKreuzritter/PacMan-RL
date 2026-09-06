# NEAT Pac-Man

A Pac-Man clone (built with `pygame`) whose player is controlled by a neural network
evolved with **NEAT** (NeuroEvolution of Augmenting Topologies, via `neat-python`)
instead of scripted/manual controls.

This is the `neat_pacman` branch. The project also has a `bfs_pacman` branch
(pathfinding-driven Pac-Man) and a plain/ordinal Pac-Man branch.

## How it works

Each generation, an entire population of Pac-Man genomes plays simultaneously on
screen. Every genome is a feed-forward neural network that receives 12 sensor
inputs per frame and outputs one of 4 relative moves (forward/right/backward/left).
Fitness is based on score gained (pellets/fruit eaten), with a penalty for dying.
NEAT evolves network topology and weights across generations, and the best
genome's network is drawn live on screen during training.

- **Inputs (12)**: line-of-sight in each direction, nearest-distance sensors in
  each direction, and pellet/safety checks in each direction — computed in
  [entities/pacai.py](entities/pacai.py) from [stages/GameStage.py](stages/GameStage.py).
- **Outputs (4)**: go forward / right / backward / left, relative to Pac-Man's
  current heading (translated to an absolute direction in [Vectors.py](Vectors.py)).
- **Fitness**: per-frame score delta, with a `-2000` penalty on death
  (see `run_pacman` in [Train.py](Train.py)).
- **Distance data**: [Train.py](Train.py) precomputes all-pairs shortest paths
  across the maze with BFS (`Game.BFS` / `Game.calculate_dict`) so genomes can
  sense distances through walls/corridors, not just straight lines.
- NEAT hyperparameters (population size, mutation rates, activation functions,
  etc.) live in [config-feedforward.txt](config-feedforward.txt).

## Project layout

- [Train.py](Train.py) — entry point: sets up the NEAT population, runs the
  game loop for every genome in parallel, computes fitness, and evolves.
- [Vectors.py](Vectors.py) — converts a network's relative-direction output
  into an absolute direction based on Pac-Man's current heading.
- [cell_map.py](cell_map.py) / [level.py](level.py) — maze/cell grid and level
  parameters (ghost speeds, fright duration, fruit schedule, etc.).
- [settings.py](settings.py) — general NEAT/population/training settings
  (population size, phases, save folders, etc.).
- [entities/](entities/) — Pac-Man, ghosts (Blinky, Pinky, Inky, Clyde), and
  the `pacai_class` sensor-vector builder fed to the network.
- [managers/](managers/) — collectibles, fruit, ghost, and level managers.
- [stages/](stages/) — a single game instance (`GameStage`/`stage`), one per
  genome, run in parallel each generation.
- [enums/](enums/) — direction, cell type, ghost mode/state/speed enums.
- [collectibles/](collectibles/), [fruits/](fruits/) — pellet and fruit entities.
- [resources/](resources/) — images, sounds, and level layout data.
- [utils/](utils/) — shared helpers (e.g. file/image loading).
- `*.pkl` (e.g. `best_model.pkl`, `winnerN.pkl`) — pickled NEAT genomes saved
  from training, used as checkpoints to resume/seed future runs.

## Requirements

- Python 3
- `pygame`
- `neat-python`
- `numpy`

```bash
pip install pygame neat-python numpy
```

## Running

```bash
python Train.py
```

This loads `config-feedforward.txt` for NEAT hyperparameters, seeds a new
population from a previously saved genome (`winner15.pkl` by default — update
the filename in [Train.py](Train.py) if you don't have this checkpoint), runs
training for a fixed number of generations, and pickles the resulting winner
(e.g. `winner16.pkl`).

To start from scratch instead of a saved checkpoint, use `neat.Population(config)`
directly instead of `create_population_with_base_genome`.
