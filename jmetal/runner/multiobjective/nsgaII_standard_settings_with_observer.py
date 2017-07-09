import logging
from typing import List

from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.component.consumer import WriteFrontToFileConsumer
from jmetal.core.solution import FloatSolution
from jmetal.operator.crossover import SBX
from jmetal.operator.mutation import Polynomial
from jmetal.operator.selection import BinaryTournament
from jmetal.problem.multiobjective.unconstrained import Kursawe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    problem = Kursawe()
    algorithm = NSGAII[FloatSolution, List[FloatSolution]](
        problem,
        population_size = 100,
        max_evaluations = 25000,
        mutation = Polynomial(1.0/problem.number_of_variables, distribution_index=20),
        crossover = SBX(1.0, distribution_index=20),
        selection = BinaryTournament())

    observer = WriteFrontToFileConsumer("output_directory")

    algorithm.observable.register(observer=observer)

    algorithm.start()
    algorithm.join()

    logger.info("Algorithm (continuous problem): " + algorithm.get_name())
    logger.info("Problem: " + problem.get_name())
    logger.info("Computing time: " + str(algorithm.total_computing_time))

if __name__ == '__main__':
    main()
