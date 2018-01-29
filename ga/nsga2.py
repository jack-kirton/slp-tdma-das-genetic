# from __future__ import division
# import functools

# class Individual(object):
    # def __init__(self):
        # self.rank = None
        # self.crowding_distance = None
        # self.domination_count = None
        # self.dominated_solutions = set()
        # self.features = None
        # self.objectives = None
        # self.dominates = None


# class Population(object):
    # def __init__(self):
        # self.population = []
        # self.fronts = []

    # def __len__(self):
        # return len(self.population)

    # def __iter__(self):
        # return iter(self.population)

    # def extend(self, new_individuals):
        # self.population.extend(new_individuals)


# class NSGA2Utils(object):
    # @staticmethod
    # def fast_nondominated_sort(population):
        # population.fronts = []
        # population.fronts.append([])
        # for individual in population:
            # individual.domination_count = 0
            # individual.dominated_solutions = set()

            # for other_individual in population:
                # if individual.dominates(other_individual):
                    # individual.dominated_solutions.add(other_individual)
                # elif other_individual.dominates(individual):
                    # individual.domination_count += 1

            # if individual.domination_count == 0:
                # population.fronts[0].append(individual)
                # individual.rank = 0

        # i = 0
        # while len(population.fronts[i]) > 0:
            # next_front = []
            # for individual in population.fronts[i]:
                # for other_individual in individual.dominated_solutions:
                    # other_individual.domination_count -= 1
                    # if other_individual.domination_count == 0:
                        # other_individual.rank = i + 1
                        # next_front.append(other_individual)
            # i += 1
            # population.fronts.append(next_front)

    # @staticmethod
    # def __sort_objective(ind1, ind2, m):
        # return cmp(ind1.objectives[m], ind2.objectives[m])

    # @staticmethod
    # def calculate_crowding_distance(front):
        # if len(front) > 0:
            # solutions_num = len(front)
            # for individual in front:
                # individual.crowding_distance = 0

            # for m in xrange(len(front[0].objectives)):
                # front = sorted(front, cmp=functools.partial(NSGA2Utils.__sort_objective, m=m))
                # front[0].crowding_distance = 1.0 #Maximum output of objective functions
                # front[-1].crowding_distance = 1.0
                # for i, val in enumerate(front[1:-2]):
                    # front[i].crowding_distance = (front[i+1].crowding_distance - front[i-1].crowding_distance) / (1.0 - 0.0) # Max - Min

    # @staticmethod
    # def crowding_operator(individual, other_individual):
        # if (ind1.rank < ind2.rank) or ((ind1.rank == ind2.rank) and (ind1.crowding_distance > ind2.crowding_distance)):
            # return 1
        # else:
            # return -1


# class NSGA2Engine(object):
    # def __init__(self):
        # self.population = None
        # self.num_generations = 200
        # self.on_generation_finished = []
        # self.num_individuals = 80

    # def evolve(self):
        # return


# class NSGA2GenomeBase(pyevolve.GenomeBase):
    # def __init__(self):
        # super(NSGA2GenomeBase, self).__init__()
        # self.rank = None
        # self.crowding_distance = None
        # self.domination_count = None
        # self.dominated_solutions = set()
        # self.dominates = None

    # def resetStats(self):
        # self.score = []
        # self.fitness = []

    # def evaluate(self, **kwargs):
        # self.resetStats()
        # for it in self.evaluator.applyFunctions(self, **kwargs):
            # self.score.append(it)

    # def copy(self, g):
        # super(NSGA2GenomeBase, self).copy(g)
        # g.rank = self.rank
        # g.crowding_distance = self.crowding_distance
        # g.domination_count = self.domination_count
        # g.dominated_solutions = self.dominated_solutions
        # g.dominates = self.dominates

    # def clone(self):
        # new_copy = NSGA2GenomeBase()
        # self.copy(new_copy)
        # return new_copy


# class NSGA2Population(pyevolve.GPopulation):
    # def __init__(self, genome):
        # super(NSGA2Population, self).__init__(genome)











from __future__ import division

import random
import functools


class Individual(object):
    def __init__(self):
        self.rank = None
        self.crowding_distance = None
        self.domination_count = None
        self.dominated_solutions = set()
        self.objective_scores = []

    def copy(self, other):
        other.rank = self.rank
        other.crowding_distance = self.crowding_distance
        other.domination_count = self.domination_count
        other.dominated_solutions = set(self.dominated_solutions)
        other.objective_scores = self.objective_scores[:]

    def clone(self):
        i = Individual()
        self.copy(i)
        return i


class GeneticInfo(object):
    def __init__(self, seed=None, population_size=80, mutation_rate=0.02, num_generations=201,
            tournament_participants=2, maximise=True):
        self.seed = seed
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.num_generations = num_generations
        self.tournament_participants = tournament_participants
        self._maximise = maximise

        self._objective_functions = tuple()

    @property
    def maximise(self):
        return self._maximise

    @maximise.setter
    def maximise(self, val):
        self._maximise = bool(val)

    @property
    def minimise(self):
        return not self._maximise

    @minimise.setter
    def minimise(self, val):
        self._maximise = not bool(val)

    @property
    def objective_functions(self):
        return self._objective_functions

    @objective_functions.setter
    def objective_functions(self, val):
        self._objective_functions = tuple(val)

    def create(self):
        raise NotImplementedError()

    def initialise(self, individual):
        raise NotImplementedError()

    def mutate(self, individual, mutation_rate):
        raise NotImplementedError()

    def crossover(self, father, mother):
        raise NotImplementedError()

    # def dominates(self, individual, other):
        # if self._maximise: #TODO No idea if maximise is correct
            # worse_than_other = all([ i >= j for i,j in zip(individual.objective_scores, other.objective_scores) ])
            # better_than_other = any([ i > j for i,j in zip(individual.objective_scores, other.objective_scores) ])
        # else:
            # worse_than_other = all([ i <= j for i,j in zip(individual.objective_scores, other.objective_scores) ])
            # better_than_other = any([ i < j for i,j in zip(individual.objective_scores, other.objective_scores) ])
        # return worse_than_other and better_than_other

    def dominates(self, individual, other):
        # if self._maximise:
            # return all([ i > j for i,j in zip(individual.objective_scores, other.objective_scores) ])
        # else:
            # return all([ i < j for i,j in zip(individual.objective_scores, other.objective_scores) ])
        if self.minimise:
            worse_than_other = all([ i <= j for i,j in zip(individual.objective_scores, other.objective_scores) ])
            better_than_other = any([ i < j for i,j in zip(individual.objective_scores, other.objective_scores) ])
        else:
            worse_than_other = all([ (1-i) <= (1-j) for i,j in zip(individual.objective_scores, other.objective_scores) ])
            better_than_other = any([ (1-i) < (1-j) for i,j in zip(individual.objective_scores, other.objective_scores) ])

        return worse_than_other and better_than_other

    def evaluate(self, individual):
        individual.objective_scores = []
        for f in self.objective_functions:
            individual.objective_scores.append(f(individual))


class Population(object):
    def __init__(self):
        self.population = []
        self.fronts = []

    def __len__(self):
        return len(self.population)

    def __iter__(self):
        return iter(self.population)

    def extend(self, new_individuals):
        self.population.extend(new_individuals)


class Engine(object):
    def __init__(self, info):
        self.info = info
        random.seed(info.seed)

        self.population = None
        self.on_generation_complete = []

    def create_initial_population(self):
        p = Population()
        for _ in xrange(self.info.population_size):
            i = self.info.create()
            self.info.initialise(i)
            self.info.evaluate(i)
            p.population.append(i)
        return p

    def create_children(self, population):
        children = []
        while len(children) < len(population):
            father = self.individual_select(population)
            mother = father
            while father is mother:
                mother = self.individual_select(population)
            son, daughter = self.info.crossover(father, mother)
            self.info.mutate(son, self.info.mutation_rate)
            self.info.mutate(daughter, self.info.mutation_rate)
            self.info.evaluate(son)
            self.info.evaluate(daughter)
            children.append(son)
            children.append(daughter)
        return children

    def evolve(self):
        self.population = self.create_initial_population()
        self._fast_nondominated_sort(self.population)
        for front in self.population.fronts:
            self._calculate_crowding_distance(front)
        children = self.create_children(self.population)
        for i in xrange(self.info.num_generations):
            self.population.extend(children)
            self._fast_nondominated_sort(self.population)
            new_population = Population()
            front_num = 0
            # print("Front[0] size: {}".format(len(self.population.fronts[front_num])))
            # print("Front[1] size: {}".format(len(self.population.fronts[front_num+1])))
            while len(new_population) + len(self.population.fronts[front_num]) <= self.info.population_size:
                self._calculate_crowding_distance(self.population.fronts[front_num])
                new_population.extend(self.population.fronts[front_num])
                front_num += 1

            sorted(self.population.fronts[front_num], cmp=Engine._crowding_operator)
            new_population.extend(self.population.fronts[front_num][0:self.info.population_size-len(new_population)])
            # returned_population = self.population
            self.population = new_population
            self._fast_nondominated_sort(self.population) #XXX Required for on_generation_complete functions but causes slowdown
            children = self.create_children(self.population)
            for f in self.on_generation_complete:
                # f(i, returned_population)
                f(i, self.population)
        return self.population

    def individual_select(self, population):
        participants = random.sample(population, self.info.tournament_participants)
        best = None
        for p in participants:
            if best is None or Engine._crowding_operator(p, best) == 1:
                best = p
        return best

    def _fast_nondominated_sort(self, population):
        population.fronts = []
        population.fronts.append([])
        for individual in population:
            individual.domination_count = 0
            individual.dominated_solutions = set()

            for other_individual in population:
                if self.info.dominates(individual, other_individual):
                    individual.dominated_solutions.add(other_individual)
                elif self.info.dominates(other_individual, individual):
                    individual.domination_count += 1

            if individual.domination_count == 0:
                population.fronts[0].append(individual)
                individual.rank = 0

        i = 0
        while len(population.fronts[i]) > 0:
            next_front = []
            for individual in population.fronts[i]:
                for other_individual in individual.dominated_solutions:
                    other_individual.domination_count -= 1
                    if other_individual.domination_count == 0:
                        other_individual.rank = i + 1
                        next_front.append(other_individual)
            i += 1
            population.fronts.append(next_front)

    @staticmethod
    def __crowding_sort_objective(ind1, ind2, m):
        return cmp(ind1.objective_scores[m], ind2.objective_scores[m])

    def _calculate_crowding_distance(self, front):
        if len(front) > 0:
            for individual in front:
                individual.crowding_distance = 0

            for m in xrange(len(front[0].objective_scores)):
                front = sorted(front, cmp=functools.partial(Engine.__crowding_sort_objective, m=m))
                front[0].crowding_distance = 1.0 #Maximum output of objective functions
                front[-1].crowding_distance = 1.0
                for i, val in enumerate(front[1:-2]):
                    front[i].crowding_distance = (front[i+1].crowding_distance - front[i-1].crowding_distance) / (1.0 - 0.0) # Max - Min
                # print("Objective {} crowding: {}".format(m, [ i.crowding_distance for i in front ]))

    @staticmethod
    def _crowding_operator(ind1, ind2):
        if (ind1.rank < ind2.rank) or ((ind1.rank == ind2.rank) and (ind1.crowding_distance > ind2.crowding_distance)):
            return 1
        else:
            return -1




