from __future__ import division, print_function

import random as rng
import networkx as nx
import timeit
import gc
from pyevolve.GenomeBase import GenomeBase

from ga import topology

def find_attacker_path(g):
    nodes = set()
    safety_period = g.graph["safety-period"]
    safety_period = len(g.nodes()) if safety_period == 0 else safety_period
    current_node = g.graph["sink"]
    while safety_period > 0:
        safety_period -= 1
        neighbourhood = __get_neighbourhood(g, current_node)
        neighbourhood_slots = __get_neighbourhood_slots(g, current_node)
        min_slot = min(neighbourhood_slots)
        for n in neighbourhood:
            if g.node[n]["slot"] == min_slot:
                current_node = n
                nodes.add(n)
                break
    return nodes

def find_attacker_path_end(g):
    nodes = set()
    safety_period = g.graph["safety-period"]
    safety_period = len(g.nodes()) if safety_period == 0 else safety_period
    current_node = g.graph["sink"]
    while safety_period > 0:
        safety_period -= 1
        neighbourhood = __get_neighbourhood(g, current_node)
        neighbourhood_slots = __get_neighbourhood_slots(g, current_node)
        min_slot = min(neighbourhood_slots)
        for n in neighbourhood:
            if g.node[n]["slot"] == min_slot:
                if n in nodes:
                    return current_node
                current_node = n
                nodes.add(n)
                break
    return current_node

from fitness import get_fitness_function

def time_get_neighbourhood(g):
    def wrapper(func, *args, **kwargs):
        def wrapped():
            for n in g.nodes_iter():
                func(g, n)
        return wrapped

    # n_wrapped = wrapper(__get_neighbourhood)
    twohop_wrapped = wrapper(__get_two_hop_neighbourhood)
    # slots_wrapped = wrapper(__get_two_hop_neighbourhood_slots)

    # print(timeit.timeit(n_wrapped, number=1))
    print(timeit.timeit(twohop_wrapped, number=1))
    # print(timeit.timeit(slots_wrapped, number=1))


def __get_neighbourhood(g, current_node):
    return g[current_node].keys()

def __get_neighbourhood_slots(g, current_node):
    neighbourhood = __get_neighbourhood(g, current_node)
    return [ g.node[n]["slot"] for n in neighbourhood ]

def __get_two_hop_neighbourhood(g, current_node):
    onehop = g[current_node].keys()
    twohop = list(onehop)
    for n in onehop:
        twohop += g[n].keys()
    return list(set([ i for i in twohop if i != current_node]))

def __get_two_hop_neighbourhood_slots(g, current_node):
    twohop = __get_two_hop_neighbourhood(g, current_node)
    return [ g.node[n]["slot"] for n in twohop ]

def __get_descendents(g, current_node):
    children = __get_children(g, current_node)
    descendents = list(children) #Making a copy
    for n in children:
        descendents += __get_descendents(g, n)
    return descendents

def __get_children(g, current_node):
    children = list(g.node[current_node]["children"])
    for c in children:
        if g.node[c]["parent"] != current_node:
            raise RuntimeException("Broken parent-child relationship")
    return children

def __get_potential_children(g, current_node):
    potential_children = []
    neighbours = g[current_node].keys()
    for n in neighbours:
        if g.node[n]["hop"] > g.node[current_node]["hop"]:
            potential_children.append(n)
    return potential_children

def __get_probable_children(g, current_node):
    probable_children = []
    potential_children = __get_potential_children(g, current_node)
    for pc in potential_children:
        if g.node[pc]["slot"] < g.node[current_node]["slot"]:
            probable_children.append(pc)
    return probable_children

def __get_potential_parents(g, current_node):
    potential_parents = []
    neighbours = g[current_node].keys()
    for n in neighbours:
        if g.node[n]["hop"] < g.node[current_node]["hop"]:
            potential_parents.append(n)
    return potential_parents

def __get_probable_parents(g, current_node):
    probable_parents = []
    potential_parents = __get_potential_parents(g, current_node)
    for pp in potential_parents:
        if g.node[pp]["slot"] > g.node[current_node]["slot"]:
            probable_parents.append(pp)
    return probable_parents


# def __fix(g, current_node=None):
    # assignment_interval = 10
    # if not current_node:
        # current_node = g.graph["sink"]
        # g.node[current_node]["parent"] = None

    # if not g.node[current_node]["children"]:
        # probable_children = __get_probable_children(g, current_node)
        # potential_children = __get_potential_children(g, current_node)
    # else:
        # pass

#TODO Does nothing about node collisions that already exist, it just doesn't make more?
def __connect_parents(g):
    # assignment_interval = 10
    repeat = True
    while repeat:
        repeat = False
        for n in g.nodes_iter():
            if n == g.graph["sink"]:
                continue

            if g.node[n]["parent"] is None:
                new_parents = __get_probable_parents(g, n)
                if new_parents:
                    new_parent = rng.choice(new_parents)
                    g.node[n]["parent"] = new_parent
                    g.node[new_parent]["children"].add(n)
                    # #TODO Solve for collisions (didn't seem to work)
                    # slot_collides = True
                    # while slot_collides:
                        # slot_collides = False
                        # if g.node[n]["slot"] in __get_two_hop_neighbourhood_slots(g, n):
                            # slot_collides = True
                            # g.node[n]["slot"] -= 1
                            # for c in g.node[n]["children"]:
                                # g.node[c]["parent"] = None
                                # repeat = True
                            # g.node[n]["children"].clear()


                else:
                    new_parent = rng.choice(__get_potential_parents(g, n))
                    g.node[n]["parent"] = new_parent
                    g.node[new_parent]["children"].add(n)
                    # g.node[n]["slot"] = g.node[new_parent]["slot"] - 1
                    neighbour_slots = __get_two_hop_neighbourhood_slots(g, n)
                    for i in range(1, 100): #TODO Possibly doesn't find a slot (usually does)
                        if g.node[new_parent]["slot"] - i not in neighbour_slots:
                            g.node[n]["slot"] = g.node[new_parent]["slot"] - i
                            break
                    for c in g.node[n]["children"]:
                        g.node[c]["parent"] = None
                        repeat = True
                    g.node[n]["children"].clear()

                # neighbour_slots = __get_two_hop_neighbourhood_slots(g, n)
                # slot_collides = g.node[n]["slot"] in neighbour_slots
                # while slot_collides:
                    # slot_collides = False
                    # if g.node[n]["slot"] in neighbour_slots:
                        # slot_collides = True
                        # g.node[n]["slot"] -= 1
                        # for c in g.node[n]["children"]:
                            # g.node[c]["parent"] = None
                            # repeat = True
                        # g.node[n]["children"].clear()

def __resolve(g):
    repeat = True
    while repeat:
        repeat = False
        for n in g.nodes_iter():
            if g.node[n]["parent"] is None:
                if n == g.graph["sink"]:
                    continue
                slot_changed = False
                parent_choice = __get_probable_parents(g, n)
                parent_choice = __get_potential_parents(g, n) if len(parent_choice) == 0 else parent_choice
                new_parent = rng.choice(parent_choice)
                __set_parent(g, n, new_parent)
                # g.node[n]["parent"] = new_parent
                # g.node[new_parent]["children"].add(n)
                if g.node[n]["slot"] >= g.node[new_parent]["slot"]:
                    g.node[n]["slot"] = g.node[new_parent]["slot"] - 1
                    slot_changed = True
                neighbour_slots = __get_two_hop_neighbourhood_slots(g, n)
                while g.node[n]["slot"] in neighbour_slots:
                    g.node[n]["slot"] -= 1
                    slot_changed = True
                if slot_changed:
                    for c in list(g.node[n]["children"]):
                        # g.node[c]["parent"] = None
                        __set_parent(g, c, None)
                        repeat = True
                    # g.node[n]["children"].clear()

# def __resolve_collision(g, n):
    # repeat = False
    # twohop = __get_two_hop_neighbourhood(g, n)
    # for ne in twohop:
        # if g.node[n]["slot"] == g.node[ne]["slot"]:
            # repeat = True
            # if g.node[n]["hop"] > g.node[ne]["hop"]:
                # g.node[n]["slot"] -= 1
                # break

    # if repeat:
        # __resolve_collision(g, n)


# def __resolve_collision(g, n):
    # repeat = False
    # twohop = __get_two_hop_neighbourhood(g, n)
    # for ne in twohop:
        # if g.node[n]["slot"] == g.node[ne]["slot"]:
            # repeat = True
            # if g.node[n]["hop"] > g.node[ne]["hop"]:
                # g.node[n]["slot"] -= 1
                # continue
            # else:
                # g.node[ne]["slot"] -= 1

    # if repeat:
        # __resolve_collision(g, n)

# def __resolve_collisions(g):
    # repeat = False
    # for n in g.nodes_iter():
        # twohop = __get_two_hop_neighbourhood(g, n)
        # for ne in twohop:
            # if g.node[n]["slot"] == g.node[ne]["slot"]:
                # repeat = True
                # if g.node[n]["hop"] > g.node[ne]["hop"]:
                    # g.node[n]["slot"] -= 1
                    # continue
                # else:
                    # g.node[ne]["slot"] -= 1

    # if repeat:
        # __resolve_collisions(g)

def get_template_genome(topo, fitness_name):
    g = NetworkGenome()
    # g.add_nodes_from(topo.nodes.keys()) #TODO Superfluous statement (edges add the nodes)
    # for k,v in topo.nodes:
        # g.node[k]["coord"] = v
    # g.add_edges_from(topo.edges)
    g.set_topology(topo)
    g.initializator.set(initialise)
    g.mutator.set(mutate)
    g.crossover.set(crossover)
    g.evaluator.set(get_fitness_function(fitness_name))
    g.setParams(
            bestrawscore=1.0,
            rounddecimal=5
            )
    return g

def initialise(genome, *args, **kwargs):
    max_psuedo_slots = 1000 #TODO Don't choose this arbitrarily
    for n in genome.n.nodes_iter():
        if n == genome.n.graph["sink"]:
            genome.n.node[n]["slot"] = max_psuedo_slots
        else:
            genome.n.node[n]["slot"] = rng.randint(1, max_psuedo_slots-1)
        genome.n.node[n]["hop"] = nx.shortest_path_length(genome.n, source=n, target=genome.n.graph["sink"])
        genome.n.node[n]["parent"] = None
        genome.n.node[n]["children"] = set()

    # #TODO An attempt to initialise with no collisions (didn't help)
    # repeat = True
    # while repeat:
        # repeat = False
        # for n in genome.n.nodes_iter():
            # if genome.n.node[n]["slot"] in __get_two_hop_neighbourhood_slots(genome.n, n):
                # genome.n.node[n]["slot"] -= 1
                # repeat = True

    __resolve(genome.n)

# def __one_crossover(g1, g2):
    # crossover_node = g1.n.graph["sink"]
    # while crossover_node == g1.n.graph["sink"]:
        # crossover_node = rng.choice(g2.n.nodes())
    # subnetwork = set(__get_descendents(g2.n, crossover_node)) #TODO Add depth of search parameter
    # for n in subnetwork:
        # g1.n.node[n]["slot"] = g2.n.node[n]["slot"]
        # g1.n.node[n]["parent"] = g2.n.node[n]["parent"] if g2.n.node[n]["parent"] in subnetwork else None
        # for c in g1.n.node[n]["children"]:
            # g1.n.node[c]["parent"] = None
        # g1.n.node[n]["children"] = set()
        # for c in g2.n.node[n]["children"]:
            # if c in subnetwork:
                # g1.n.node[n]["children"].add(c)
                # g1.n.node[c]["parent"] = n
    # __resolve(g1.n)

# def __one_crossover(g1, g2, crossover_node):
    # subnetwork = set(__get_descendents(g2, crossover_node))
    # for n in subnetwork:
        # g1.node[n]["slot"] = g2.node[n]["slot"]
        # g1.node[g1.node[n]["parent"]]["children"].discard(n)
        # g1.node[n]["parent"] = g2.node[n]["parent"] if g2.node[n]["parent"] in subnetwork else None
        # for c in g1.node[n]["children"]:
            # g1.node[c]["parent"] = None
        # g1.node[n]["children"].clear()
        # for c in g2.node[n]["children"]:
            # if c in subnetwork:
                # g1.node[n]["children"].add(c)
                # # g1.node[c]["parent"] = n
        # __resolve(g1)

    # for n in subnetwork:
        # __resolve_collisions(g1, n)
        # __resolve(g1)

def __set_parent(g, current_node, new_parent):
    if g.node[current_node]["parent"] is not None:
        g.node[g.node[current_node]["parent"]]["children"].discard(current_node)
    g.node[current_node]["parent"] = new_parent
    if new_parent is not None:
        g.node[new_parent]["children"].add(current_node)

# def __one_crossover(g1, g2, crossover_node):
    # subnetwork = set(__get_descendents(g2, crossover_node))
    # for n in subnetwork:
        # #Set new slot
        # g1.node[n]["slot"] = g2.node[n]["slot"]
        # #Remove child from old parent
        # if g2.node[n]["parent"] in subnetwork:
            # g1.node[n]["parent"] = g2.node[n]["parent"]
            # g1.node[g1.node[n]["parent"]]["children"].add(n)
            # # g1.node[n]["children"] = set(g2.node[n]["children"])
        # else:
            # g1.node[g1.node[n]["parent"]]["children"].discard(n)
            # g1.node[n]["parent"] = None
        # __resolve_collisions(g1, n)

    # __resolve(g1)

def __one_crossover(g1, g2, crossover_node):
    subnetwork = __get_descendents(g2, crossover_node) + [crossover_node] #set() call unnecessary
    for n in subnetwork:
        g1.node[n]["slot"] = g2.node[n]["slot"]
        if g2.node[n]["parent"] in subnetwork:
            __set_parent(g1, n, g2.node[n]["parent"])
            # __set_parent(g1, n, None)
        else: #This occurs once with the crossover node
            __set_parent(g1, n, None)
    __check_crossover(g1, crossover_node)

def __check_crossover(g, n):
    parent = g.node[n]["parent"]
    children = list(g.node[n]["children"])
    neighbourhood_slots = __get_two_hop_neighbourhood_slots(g, n)
    if parent is None:
        parent_choice = __get_probable_parents(g, n)
        parent_choice = __get_potential_parents(g, n) if len(parent_choice) == 0 else parent_choice
        new_parent = rng.choice(parent_choice)
        __set_parent(g, n, new_parent)
    if g.node[n]["slot"] > g.node[g.node[n]["parent"]]["slot"]:
        g.node[n]["slot"] = g.node[g.node[n]["parent"]]["slot"] - 1
    while g.node[n]["slot"] in neighbourhood_slots:
        g.node[n]["slot"] -= 1
    for c in children:
        __check_crossover(g, c)




#TODO Causes collisions and DAS breakages
def crossover(genome, *args, **kwargs):
    father = kwargs["dad"]
    mother = kwargs["mom"]
    son = father.clone()
    daughter = mother.clone()
    crossover_node = father.n.graph["sink"]
    while crossover_node == father.n.graph["sink"]:
        crossover_node = rng.choice(father.n.nodes())
    __one_crossover(son.n, mother.n, crossover_node)
    __one_crossover(daughter.n, father.n, crossover_node)
    return son, daughter

def mutate_nothing(genome, *args, **kwargs):
    return 0

#TODO Do something different when node has no children
def mutate(genome, *args, **kwargs):
    ga = kwargs["ga_engine"]
    mutation_rate = kwargs["pmut"]
    mutation_count = 0
    for n in genome.n.nodes():
        if n == genome.n.graph["sink"] or rng.random() > mutation_rate:
            continue
        highest = genome.n.node[genome.n.node[n]["parent"]]["slot"]
        lowest = highest - 100 #TODO This could cause a slot to be wrong if largest slot is less than highest-1000
        neighbourhood_slots = __get_two_hop_neighbourhood_slots(genome.n, n)
        if len(genome.n.node[n]["children"]) == 0: #TODO Find a better solution to nodes with no children
            genome.n.node[n]["slot"] = highest - 1
            while genome.n.node[n]["slot"] in neighbourhood_slots:
                genome.n.node[n]["slot"] -= 1
            mutation_count += 1
            continue
        for c in genome.n.node[n]["children"]:
            lowest = genome.n.node[c]["slot"] if genome.n.node[c]["slot"] > lowest else lowest
        #TODO This assumes DAS is NOT BROKEN in order to work
        if highest - 1 < lowest + 1:
            continue
        #Attempt to resolve slot collisions
        attempt = 5
        while attempt != 0:
            new_slot = rng.randint(lowest + 1, highest - 1)
            if new_slot in neighbourhood_slots:
                attempt -= 1
            else:
                genome.n.node[n]["slot"] = new_slot
                break
        if attempt == 0: #Failed to solve slot collisions so don't mutate
            continue
        mutation_count += 1
    return mutation_count

def mutate_aggressive(genome, *args, **kwargs):
    ga = kwargs["ga_engine"]
    mutation_rate = kwargs["pmut"]
    mutation_count = 0
    for n in genome.n.nodes():
        if n == genome.n.graph["sink"] or rng.random() > pmut:
            continue
    return mutation_count


def __resolve_collisions(g, current_node):
    if g.node[current_node]["parent"] is None:
        return False
    original_slot = g.node[current_node]["slot"]
    neighbourhood_slots = __get_two_hop_neighbourhood_slots(g, current_node)
    parent = g.node[current_node]["parent"]
    highest = g.node[parent]["slot"] - 1
    lowest = None
    new_slot = highest
    for c in g.node[current_node]["children"]:
        lowest = g.node[c]["slot"] if g.node[c]["slot"] > lowest else lowest
    while new_slot in neighbourhood_slots and new_slot > lowest:
        new_slot -= 1
    if new_slot == lowest:
        g.node[parent]["children"].discard(current_node)
        g.node[current_node]["parent"] = None
        return False
    else:
        g.node[current_node]["slot"] = new_slot
        return True



def get_slots_used(genome):
    unique_slots = set()
    for n in genome.n.nodes_iter():
        unique_slots.add(genome.n.node[n]["slot"])
    return len(unique_slots)

def normalise_slots(genome):
    n = genome.n
    slots = set()
    for node in n.nodes_iter():
        slots.add(n.node[node]["slot"])
    slots = sorted(list(slots))
    for node in n.nodes_iter():
        index = slots.index(n.node[node]["slot"]) + 1
        n.node[node]["slot"] = index


#Fixed with git version of Pyevolve
#XXX Can't use super as GenomeBase is an old-style class
#XXX Can't use property decorator as GenomeBase is an old-style class
class NetworkGenome(GenomeBase):
    def __init__(self):
        super(NetworkGenome, self).__init__()
        self._n = None

    def set_topology(self, t):
        if isinstance(t, topology.Topology):
            self._n = t.network.copy()
        else:
            raise AttributeError("NetworkGenome.topology must be an instance of Topology")

    @property
    def network(self):
        return self._n

    @property
    def n(self):
        return self._n

    #override
    def copy(self, g):
        super(NetworkGenome, self).copy(g)
        g._n = self.network.copy()

    #override
    def clone(self):
        g = NetworkGenome()
        self.copy(g)
        return g

    def __eq__(self, other):
        return self.n == other.n

