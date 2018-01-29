#!/usr/bin/env python2

from __future__ import print_function

from ga import nsga2
from ga import nsga2_setup
from ga import genome
from ga import fitness
from ga import topology
from ga import plot

from nsga2_plotter import Plotter

def print_generation(i, population):
    print("Generation: {}".format(i))
    print("Population Size: {}".format(len(population)))
    print("Num Fronts: {}".format(len(population.fronts)-1)) #XXX It always appends an empty front

plotter = Plotter(None)
def plot_front(i, population):
    global plotter
    plotter.plot_population_best_front(population, i)


def main():
    g_info = nsga2_setup.NetworkGeneticInfo(topology.GridTopology(11,11), population_size=80, num_generations=101, mutation_rate=0.02)
    g_info.objective_functions = (fitness.slot_fitness, fitness.path_dist_fitness)
    engine = nsga2.Engine(g_info)
    engine.on_generation_complete.append(print_generation)
    engine.on_generation_complete.append(plot_front)
    engine.evolve()
    for j, front in enumerate(engine.population.fronts):
        print("Front {}".format(j))
        print("========")
        for i, individual in enumerate(front):
            print("{}: {}, Slots: {}, Path: {}".format(i, [float("{:.3f}".format(score)) for score in individual.objective_scores], genome.get_slots_used(individual), len(genome.find_attacker_path(individual.network))))
    genome.normalise_slots(engine.population.fronts[0][0])
    plot.plot_network(engine.population.fronts[0][0])
    raw_input("Enter to continue...")

if __name__ == "__main__":
    main()
