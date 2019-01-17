import copy
from typing import TypeVar, List

from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.config import store
from jmetal.core.operator import Mutation, Crossover, Selection
from jmetal.core.problem import Problem
from jmetal.operator.selection import EnvironmentalSelection
from jmetal.util.comparator import DominanceComparator, Comparator
from jmetal.util.point import ReferencePoint
from jmetal.util.ranking import FastNonDominatedRanking
from jmetal.util.solution_list import Evaluator, Generator
from jmetal.util.termination_criterion import TerminationCriterion

S = TypeVar('S')
R = TypeVar('R')

"""
.. module:: NSGA-III
   :platform: Unix, Windows
   :synopsis: NSGA-III (Non-dominance Sorting Genetic Algorithm III) implementation.

.. moduleauthor:: Antonio Benítez-Hidalgo <antonio.b@uma.es>
"""


class NSGAIII(NSGAII):

    def __init__(self,
                 problem: Problem,
                 mutation: Mutation,
                 crossover: Crossover,
                 selection: Selection,
                 termination_criterion: TerminationCriterion,
                 population_generator: Generator = store.default_generator,
                 population_evaluator: Evaluator = store.default_evaluator,
                 dominance_comparator: Comparator = DominanceComparator()):
        """  NSGA-III implementation.

        :param problem: The problem to solve.
        :param population_size: Size of the population.
        :param mutation: Mutation operator (see :py:mod:`jmetal.operator.mutation`).
        :param crossover: Crossover operator (see :py:mod:`jmetal.operator.crossover`).
        :param selection: Selection operator (see :py:mod:`jmetal.operator.selection`).
        """
        super(NSGAIII, self).__init__(
            problem=problem,
            population_size=0,
            offspring_population_size=0,
            mutation=mutation,
            crossover=crossover,
            selection=selection,
            termination_criterion=termination_criterion,
            population_evaluator=population_evaluator,
            population_generator=population_generator
        )
        self.dominance_comparator = dominance_comparator
        self.reference_points = self.generate_reference_points(problem.number_of_objectives)

        self.population_size = len(self.reference_points)
        while self.population_size % 4 > 0:
            self.population_size += 1

        self.offspring_population_size = self.population_size

    def generate_reference_points(self, num_objs: int, num_divisions_per_obj: int = 4):
        def gen_refs_recursive(position, num_objs, left, total, element):
            if element == num_objs - 1:
                position[element] = left / total
                return [ReferencePoint(copy.deepcopy(position))]
            else:
                res = []
                for i in range(left):
                    position[element] = i / total
                    res += gen_refs_recursive(position, num_objs, left - i, total, element + 1)
                return res

        return gen_refs_recursive([0] * num_objs, num_objs, num_objs * num_divisions_per_obj,
                                  num_objs * num_divisions_per_obj, 0)

    def replacement(self, population: List[S], offspring_population: List[S]) -> List[S]:
        """ Implements NSGA-III selection as described in

        * Deb, K., & Jain, H. (2014). An Evolutionary Many-Objective Optimization
          Algorithm Using Reference-Point-Based Nondominated Sorting Approach,
          Part I: Solving Problems With Box Constraints. IEEE Transactions on
          Evolutionary Computation, 18(4), 577–601. doi:10.1109/TEVC.2013.2281535.
        """

        # Algorithm 1 steps 4--8
        ranking = FastNonDominatedRanking(self.dominance_comparator)
        ranking.compute_ranking(population + offspring_population)

        ranking_index = 0
        pop = []

        while len(pop) < self.population_size:
            if len(ranking.get_subfront(ranking_index)) < self.population_size - len(pop):
                pop = pop + ranking.get_subfront(ranking_index)
                ranking_index += 1
            else:
                break

        # complete selected individuals using the reference point based approach
        selection = EnvironmentalSelection(number_of_objectives=self.problem.number_of_objectives,
                                           reference_points=self.reference_points,
                                           k=self.population_size - len(pop))
        pop += selection.execute(ranking.get_subfront(ranking_index))

        return pop

    def get_result(self):
        ranking = FastNonDominatedRanking(self.dominance_comparator)
        ranking.compute_ranking(self.solutions)

        return ranking.get_subfront(0)

    def get_name(self) -> str:
        return 'NSGAIII'
