
from pyevolve import GSimpleGA
from pyevolve import Selectors

def get_engine(genome):
    ga = GSimpleGA.GSimpleGA(genome)
    ga.selector.set(Selectors.GTournamentSelectorAlternative)
    ga.setGenerations(100) #Default: 100, Usually 500, 10000
    ga.setPopulationSize(80) #Default: 80
    ga.setElitism(True)
    ga.setElitismReplacement(1) #Default: 1
    ga.setMutationRate(0.02) #Default: 0.02
    ga.setCrossoverRate(0.9) #Default: 0.9
    # ga.terminationCriteria.set(GSimpleGA.RawScoreCriteria)
    # ga.terminationCriteria.set(ConvergeTerminationCriteria)
    # termination_criteria = FitnessDiffTerminationCriteria(0.0075)
    # ga.terminationCriteria.set(termination_criteria)
    return ga

def get_engine_with_params(genome, generations, elitism, mutation_rate, crossover_rate):
    ga = GSimpleGA.GSimpleGA(genome)
    ga.selector.set(Selectors.GTournamentSelectorAlternative)
    ga.setGenerations(generations)
    ga.setPopulationSize(80)
    if elitism == 0:
        ga.setElitism(False)
    else:
        ga.setElitism(True)
        ga.setElitismReplacement(elitism)
    ga.setMutationRate(mutation_rate)
    ga.setCrossoverRate(crossover_rate)
    return ga


def ConvergeTerminationCriteria(ga_engine):
    pop = ga_engine.getPopulation()
    return pop[0] == pop[-1]


class FitnessDiffTerminationCriteria(object):
    def __init__(self, delta):
        self.delta = delta

    def __call__(self, ga_engine):
        pop = ga_engine.getPopulation()
        return pop[0].getRawScore() - pop[-1].getRawScore() < self.delta
