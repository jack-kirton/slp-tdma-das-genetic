from __future__ import division, print_function

import networkx as nx

from ga.genome import find_attacker_path, find_attacker_path_end


def get_fitness_choices():
    return _fitness_functions.keys()

def get_fitness_function(name):
    return _fitness_functions[name]


def _basic_fitness(genome):
    return not genome.n.graph["source"] in find_attacker_path(genome.n)

def _slot_fitness(genome):
    unique_slots = set()
    for n in genome.n.nodes_iter():
        unique_slots.add(genome.n.node[n]["slot"])
    return (len(genome.n.nodes()) - len(unique_slots))/len(genome.n.nodes())

def _path_dist_from_src_fitness(genome):
    end_node = find_attacker_path_end(genome.n)
    dist = nx.shortest_path_length(genome.n, source=genome.n.graph["source"], target=end_node)
    network_diameter = nx.diameter(genome.n)
    return dist/network_diameter


def slot_fitness(genome):
    if not _basic_fitness(genome):
        return 0.0
    return _slot_fitness(genome)

def slot_and_path_dist_fitness(genome):
    if not _basic_fitness(genome):
        return 0.0
    return 0.75*_slot_fitness(genome) + 0.25*_path_dist_from_src_fitness(genome)


_fitness_functions = {
        'slot':                 slot_fitness,
        'slot-with-path-dist':  slot_and_path_dist_fitness
        }
