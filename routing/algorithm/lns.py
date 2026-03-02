from routing.entity.instance import Instance
from routing.algorithm.solution import Solution
from routing.algorithm.greedy_insertion import greedy_insertion
from routing.algorithm.destroy import destroy
from routing.entity.error import TimeOutException
import random

iter_for_tasks = 30  # number of iteration for each tasks to plan


def lns(instance: Instance, iter_for_task: int = iter_for_tasks):
    """
    Large neighbourhood search.
    """

    # Set the random seed
    random.seed(4711)

    sol = Solution(instance)
    iterations = len(sol.tasks_to_plan) * iter_for_task

    # Initialize the best solution
    best_sol = Solution(instance)
    best_sol.copy_from(sol)
    best_cost = best_sol.compute_cost()

    try:
        for _ in range(iterations):
            sol.copy_from(best_sol)  # Start from the best sol
            destroy(sol)
            greedy_insertion(sol)
            cost = sol.compute_cost()

            if cost <= best_cost:
                try:  # avoid the timeout happen while I'm coping the solution into the best sol
                    best_sol.copy_from(sol)
                    best_cost = cost
                except TimeOutException:
                    return sol
    except TimeOutException:
        return best_sol

    return best_sol
