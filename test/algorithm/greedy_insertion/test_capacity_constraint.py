from unittest import TestCase

from routing.algorithm.solution import Solution
from routing.entity.constant import NONE_POSITION
from test.fixtures.instance_without_state import create_test_instance
from routing.algorithm.greedy_insertion import compute_best_positions


class TestCapacityConstraint(TestCase):

    def setUp(self):
        self.instance = create_test_instance()  # best solution [0, 2, 4, 3, 5, 1]

    def test_weight_case_1(self):
        """
        Best position change when the cumulative weight at the best position is exceeded.
        """
        self.instance.plan.jobs[0].task_ids = [0, 2, 3, 1]

        # Precondition delivery 2 can be delivered
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 2)
        self.assertEqual(sol.best_insertion.pickup_pos, 2)
        self.assertEqual(sol.best_insertion.dropoff_pos, 3)

        # Test delivery 2 cannot be delivered in the best position after increasing the weight, but should be delivered
        # either at the beginning or at the end
        self.instance.tasks[4].weight = 15
        self.instance.tasks[5].weight = -15
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 2)
        self.assertNotEqual(sol.best_insertion.pickup_pos, 2)
        self.assertNotEqual(sol.best_insertion.dropoff_pos, 3)

    def test_weight_case_2(self):
        """
        Only available position for dropoff is right after the pickup position otherwise the next pickup would exceed
        the capacity.
        """
        self.instance.plan.jobs[0].task_ids = [0, 2, 4, 5, 1]  # missing dropoff 3

        # Precondition delivery 1 can be delivered
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 1)
        self.assertEqual(NONE_POSITION, sol.best_insertion.pickup_pos)
        self.assertEqual(3, sol.best_insertion.dropoff_pos)

        # Test delivery 2 dropoff is right after the pickup
        self.instance.tasks[2].weight = 10
        self.instance.tasks[3].weight = -10
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 1)
        self.assertEqual(NONE_POSITION, sol.best_insertion.pickup_pos)
        self.assertEqual(2, sol.best_insertion.dropoff_pos)

    def test_volume_case_1(self):
        """
        Best position change when the cumulative volume at the best position is exceeded.
        """
        self.instance.plan.jobs[0].task_ids = [0, 2, 3, 1]

        # Precondition delivery 2 can be delivered
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 2)
        self.assertEqual(sol.best_insertion.pickup_pos, 2)
        self.assertEqual(sol.best_insertion.dropoff_pos, 3)

        # Test delivery 2 cannot be delivered in the best position after increasing the weight, but should be delivered
        # either at the beginning or at the end
        self.instance.tasks[4].volume = 9
        self.instance.tasks[5].volume = -9
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 2)
        self.assertNotEqual(sol.best_insertion.pickup_pos, 2)
        self.assertNotEqual(sol.best_insertion.dropoff_pos, 3)

    def test_volume_case_2(self):
        """
        Only available position for dropoff is right after the pickup position otherwise the next pickup would exceed
        the capacity.
        """
        self.instance.plan.jobs[0].task_ids = [0, 2, 4, 5, 1]  # missing dropoff 3

        # Precondition delivery 1 can be delivered
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 1)
        self.assertEqual(NONE_POSITION, sol.best_insertion.pickup_pos)
        self.assertEqual(3, sol.best_insertion.dropoff_pos)

        # Test delivery 2 dropoff is right after the pickup
        self.instance.tasks[2].volume = 6
        self.instance.tasks[3].volume = -6
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 1)
        self.assertEqual(NONE_POSITION, sol.best_insertion.pickup_pos)
        self.assertEqual(2, sol.best_insertion.dropoff_pos)
