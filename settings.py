"""
NEAT Settings

Options with a default value indicated can be left as None or completely removed and the default 
value for that setting will be used. If an entire dictionary has default values that you wish to 
use you may completely remove the dictionary.
"""


# The arguments needed to initiate an instance of the Player class
player_args = {}


genome_settings = {

    # The number of inputs for the Neural Network
    'input_count': 12,
    # The number of options the Player has
    'output_count': 4,
    # The activation to use for all Nodes in hidden layers i.e. all layers except input and output
    'hidden_activation': None,  # Options are ['sigmoid', 'relu', 'linear'], Default = 'sigmoid'

}


population_settings = {

    # The number of Players per generation
    'size': 128,
    # The percentage of Players to remove from each Species before creating offspring each generation
    'cull_percentage': 0.7,    # Default = 0.5
    # The number of generations to go without improvement before removing all but the 2 best performing Species
    'max_staleness': None,  # Default = 20
    # Folder to save each generation to (overwritten each time) so the program can be paused and resumed
    'save_folder': 'latest_pop',

}


species_settings = {

    # Values used for determining whether two Genomes are part of the same Species
    'excess_coefficient': None, # Default = 1
    'disjoint_coefficient': None, # Default = 1
    'weight_difference_coefficient': None,  # Default = 0.4
    'compatibility_threshold': 1.5,    # Default = 3

    # The number of generations a Species can go without improvement before being removed
    'max_staleness': None,  # Default = 15
}


reproduction_settings = {

    # The rate at which offspring are created by crossover then mutation over just mutation
    'crossover_rate': None, # Default = 0.75
    # The rate at which an inherited Connection is disabled if it was present in both parents and disabled 
    # in at least one of them
    'disabled_rate': None,  # Default = 0.75
    # The rate at which a Genome will have its Connection weights mutated
    'weights_rate': None,   # Default = 0.8
    # The rate at which a Genome that is having its weights mutated will replace a weight over perturbing it
    'weight_replacement_rate': None,    # Default = 0.1
    # The rate at which a new Connection will be added to a Genome
    'connection_rate': None,    # Default = 0.1
    # The rate at which a new Node will be added to a Genome
    'node_rate': None,  # Default = 0.03

}


progress_settings = {

    'print_progress': None, # Default = True
    # Choose whether to build a record of the progress at the end of each generation in a csv file
    'record_progress': None, # Default = False
    # Filename of csv file to output each generation's progress (if applicable)
    'filename': None, # Default = 'progress'
    # For bests and averages these must be attributes of the Player class you use
    # The Player class will always have the fitness attribute
    # Attributes to keep track of the Population's best
    'bests': ['score', 'fitness'],  # Default = ['fitness']
    # Attributes to keep track of the Population' average
    'averages': ['score', 'fitness'],    # Default = ['fitness']
    # Choose whether to include the number of Species in the progress report
    'include_species': None, # Default = True

}


playback_settings = {

    # Folder to save the top performing Genomes of each generation to
    'save_folder': 'playback',  # Default = 'playback'
    # The number of Genomes from each Species to save (set to -1 for all)
    'number': 1,   # Default = 1

}


settings = {

    # Choose whether to start a Population of Players with randomized Genomes or load a previous save
    # When choosing to load they will be attempted to be loaded from population_settings['save_folder']
    'creation_type': 'load', # Options are ['new', 'load']
    # Choose whether to load the settings from the save or use the ones present in this file (if applicable)
    # Only the player_args, progress_settings and playback_settings will be replaced
    'load_all_settings': False,
    # The number of generations to run the Population until
    # A loaded Population will remember the generation it was saved at and still only run till this number
    'total_generations': 200,

    # Choose which phase to train
    'phase': 'full_game',   # Options are ['only_dots', 'dots_and_blinky', 'dots_and_two_ghosts', 'dots_and_ghosts', 'full_game']
    # Define whether starting a new phase so that loading is handled correctly
    'is_new_phase': True,   # Should be False if first phase

    'player_args': player_args,
    'genome_settings': genome_settings,
    'population_settings': population_settings,
    'species_settings': species_settings,
    'reproduction_settings': reproduction_settings,
    'progress_settings': progress_settings,
    'playback_settings': playback_settings,

}


simulation_settings = {

    'max_stationary_count': 20,
    'max_famine_count': 2000,

}