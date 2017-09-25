#!/usr/bin/env python2

from __future__ import division, print_function

import sys
import os
import os.path
import itertools
import argparse

import networkx as nx

from ga import genome
from ga import test
from ga import engine
from ga import topology
from ga import plot
from ga.output_adapters import SQLite3Adapter
from ga.header import generate_c_header
from ga.fitness import get_fitness_choices


# def generate_initial_grid(size=11):
    # g = nx.grid_2d_graph(size, size)
    # g.graph["size"] = 11
    # g.graph["sink"] = (5,5)
    # g.graph["source"] = (0,0)
    # for n in g.nodes_iter():
        # g.node[n]["slot"] = 0
    # return g

def main():
    topology = GridTopology(11, 11)
    g_template = genome.get_template_genome(topology)
    g = g_template.clone()
    genome.initialise(g)
    # test.das(g)
    # test.collisions(g)
    # plot_network(g)
    # raw_input("Enter to continue...")
    # return
    g2 = g_template.clone()
    genome.initialise(g2)
    # plot_network(g2)
    # raw_input("Enter to continue...")
    son, daughter = genome.crossover(g_template, dad=g, mom=g2)
    genome.mutate(son, ga_engine=None, pmut=0.1)
    genome.mutate(daughter, ga_engine=None, pmut=0.1)
    print("Testing DAS...")
    print("Son:-")
    if not test.das(son):
        plot_network(son)
        raw_input("Enter to continue...")
    print("Daughter:-")
    if not test.das(daughter):
        plot_network(daughter)
        raw_input("Enter to continue...")
    print("Testing collisions...")
    print("Son:-")
    if not test.collisions(son):
        plot_network(son)
        raw_input("Enter to continue...")
    print("Daughter:-")
    if not test.collisions(daughter):
        plot_network(daughter)
        raw_input("Enter to continue...")
    genome.fitness(g)

def main2():
    topology = GridTopology(11, 11)
    g_template = genome.get_template_genome(topology)
    # for i in xrange(1000):
        # print(i)
        # g = g_template.clone()
        # genome.initialise(g)
        # test.collisions(g)
        # test.das(g)
    # return
    # for i in xrange(1000):
        # print(i)
        # g = g_template.clone()
        # genome.initialise(g)
        # genome.mutate(g, ga_engine=None, pmut=0.1)
        # test.collisions(g)
        # test.das(g)
    # return
    # for i in xrange(1000):
        # print(i)
        # g1 = g_template.clone()
        # g2 = g_template.clone()
        # genome.initialise(g1)
        # genome.initialise(g2)
        # g3, g4 = genome.crossover(g_template, dad=g1, mom=g2)
        # test.collisions(g3)
        # test.das(g3)
    # return
    ga = engine.get_engine(g_template)
    ga.evolve(freq_stats=1)
    g = ga.bestIndividual()
    print("Raw Score: {}".format(g.getRawScore()))
    print("Slots Used: {}".format(genome.get_slots_used(g)))
    # test.das(g)
    # test.collisions(g)
    test.collisions(g)
    test.das(g)
    genome.normalise_slots(g)
    plot.plot_network(g)
    raw_input("Enter to continue...")

def main3():
    topology = GridTopology(11, 11)
    genomes = [ genome.get_template_genome(topology) ]
    generations = [100]
    elitism = [0, 1, 4, 8, 12, 16, 20]
    mutation = [0.0, 0.01, 0.02, 0.05, 0.1]
    crossover = [1.0, 0.95, 0.9]
    repeats = 100
    ga_engine_params = itertools.product(genomes, generations, elitism, mutation, crossover)
    print("Elitism | Mutation | Crossover | Slots")
    for params in ga_engine_params:
        slots = []
        for i in xrange(repeats):
            ga = engine.get_engine_with_params(*params)
            ga.evolve(freq_stats=0)
            g = ga.bestIndividual()
            slots.append(genome.get_slots_used(g))
        print("{0[2]:7} | {0[3]:8.8} | {0[4]:9.9} | {1:5.5}".format(params, sum(slots)/len(slots)))

def main_run(args):
    g_template = genome.get_template_genome(args.topology, args.fitness)
    g_template.n.graph['safety-period'] = args.safety_period
    ga = engine.get_engine_with_params(g_template, args.generations, 1, 0.02, 0.9)
    sqlite_adapter = SQLite3Adapter(dbname=args.database, id=args.identity, frequency=1, commit_freq=100)
    ga.setDBAdapter(sqlite_adapter)
    freq_stats = 1 if args.verbose else 0
    ga.evolve(freq_stats=freq_stats)
    g = ga.bestIndividual()
    print("Raw Score: {}".format(g.getRawScore()))
    print("Slots Used: {}".format(genome.get_slots_used(g)))

def main_run_multiple(args):
    base_id = args.identity
    for i in xrange(args.number):
        args.identity = base_id + str(i)
        print("ID: {}".format(args.identity))
        main_run(args)
        print("")

def main_optimise_parameters(args):
    return

def main_plot_network(args):
    plot.plot_network_sqlite(args.database, args.identity)
    raw_input("Enter to continue...")

def main_plot_animate(args):
    plot.plot_network_animate_sqlite(args.database, args.identity)
    raw_input("Enter to continue...")

def main_plot_fitness(args):
    plot.plot_generations_sqlite(args.database, args.identity)
    raw_input("Enter to continue...")

def main_plot_slots(args):
    plot.plot_slot_v_generation_sqlite(args.database, args.identity)
    raw_input("Enter to continue...")

def main_c_header(args):
    header_content = generate_c_header(args.database, args.identity)
    args.output_file.write(header_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate an SLP-aware DAS schedule')
    # parser.add_argument('-db', '--database', action='store', type=unicode, required=False, default='evolution.db',
            # help='The SQLite3 database where results will be stored (default="evolution.db")')
    # parser.add_argument('-id', '--identity', action='store', type=str, required=False, default='',
            # help='The ID that database records will be given (default="")')
    # parser.add_argument('-v', '--verbose', action='store_true', required=False,
            # help='Increase verbosity')
    subparsers = parser.add_subparsers(title='Subcommands')

    def identity_args(parser):
        parser.add_argument('-db', '--database', action='store', type=unicode, required=False, default='evolution.db',
                help='The SQLite3 database where results will be stored (default="evolution.db")')
        parser.add_argument('-id', '--identity', action='store', type=str, required=False, default='',
                help='The ID that database records will be given (default="")')

    def verbose_args(parser):
        parser.add_argument('-v', '--verbose', action='store_true', required=False,
                help='Increase verbosity')

    def run_args(parser):
        parser.add_argument('-t', '--topology', action='store', type=topology.eval_input, required=True,
                help='The topology of the network (e.g. \'GridTopology(11,11)\')')
        parser.add_argument('-f', '--fitness', action='store', type=unicode, required=True,
                choices=get_fitness_choices(),
                help='The fitness function to use in evaluating genomes')
        parser.add_argument('-sp', '--safety-period', action='store', type=int, required=False, default=0,
                help='The safety period (in TDMA periods)')
        parser.add_argument('-g', '--generations', action='store', type=int, required=False, default=100,
                help='The number of generations to iterate for')

    run_parser = subparsers.add_parser('run', help='Execute a run of the genetic algorithm')
    identity_args(run_parser)
    verbose_args(run_parser)
    run_args(run_parser)
    run_parser.set_defaults(func=main_run)

    run_multiple_parser = subparsers.add_parser('run-multiple', help='Execute many runs at once')
    identity_args(run_multiple_parser)
    verbose_args(run_multiple_parser)
    run_args(run_multiple_parser)
    run_multiple_parser.add_argument('-n', '--number', action='store', type=int, required=True,
            help='The number of runs to execute')
    run_multiple_parser.set_defaults(func=main_run_multiple)

    run_optimise_parser = subparsers.add_parser('optimise-parameters', help='Find optimal internal parameters for the genetic algorithm')
    run_optimise_parser.set_defaults(func=main_optimise_parameters)
    #TODO: Optimise parameters arguments

    plot_parser = subparsers.add_parser('plot', help='Create plots of specified run')
    plot_subparsers = plot_parser.add_subparsers(title='Plots')

    plot_network_parser = plot_subparsers.add_parser('network', help="Graphical representation of a solution")
    identity_args(plot_network_parser)
    plot_network_parser.set_defaults(func=main_plot_network)

    plot_animate_parser = plot_subparsers.add_parser('animate', help="Animate through generations of a solution")
    identity_args(plot_animate_parser)
    plot_animate_parser.set_defaults(func=main_plot_animate)

    plot_fitness_parser = plot_subparsers.add_parser('fitness', help="Generations vs fitness")
    identity_args(plot_fitness_parser)
    plot_fitness_parser.set_defaults(func=main_plot_fitness)

    plot_slots_parser = plot_subparsers.add_parser('slots', help="Generations vs total slots")
    identity_args(plot_slots_parser)
    plot_slots_parser.set_defaults(func=main_plot_slots)

    c_header_parser = subparsers.add_parser('c-header', help='Output a C header file containing the necessary details to be implemented')
    identity_args(c_header_parser)
    c_header_parser.add_argument('-f', '--output-file', action='store', type=argparse.FileType(mode='w'), required=False, default=sys.stdout,
            help='The file that the C header will be output to (default: stdout)')
    c_header_parser.set_defaults(func=main_c_header)

    args = parser.parse_args()

    #Extra processing for all options
    if os.path.isfile(args.database) and not os.access(args.database, os.R_OK | os.W_OK):
        raise IOError('Database "{}" does not have read and write permissions'.format(args.database))

    args.func(args)
