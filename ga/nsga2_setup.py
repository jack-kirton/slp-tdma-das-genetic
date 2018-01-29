from __future__ import print_function, division

from ga import nsga2
from ga import genome
from ga import topology


class NetworkIndividual(nsga2.Individual):
    def __init__(self):
        super(NetworkIndividual, self).__init__()
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

    def __eq__(self, other):
        return self.n == other.n

    def copy(self, other):
        super(NetworkIndividual, self).copy(other)
        other._n = self._n.copy()

    def clone(self):
        i = NetworkIndividual()
        self.copy(i)
        return i


class NetworkGeneticInfo(nsga2.GeneticInfo):
    def __init__(self, topology, seed=None, population_size=80, mutation_rate=0.01, num_generations=201,
            tournament_participants=2, maximise=True):
        super(NetworkGeneticInfo, self).__init__(seed=seed, population_size=population_size,
                mutation_rate=mutation_rate, num_generations=num_generations,
                tournament_participants=tournament_participants, maximise=maximise)
        self.topology = topology

    def create(self):
        i = NetworkIndividual()
        i.set_topology(self.topology)
        i.n.graph["safety-period"] = 0
        return i

    def initialise(self, individual):
        genome.initialise(individual)

    def mutate(self, individual, mutation_rate):
        return genome.mutate(individual, pmut=mutation_rate)

    def crossover(self, father, mother):
        return genome.crossover(None, dad=father, mom=mother)


