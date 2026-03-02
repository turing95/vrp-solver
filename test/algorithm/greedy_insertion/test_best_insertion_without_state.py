from unittest import TestCase

from routing.utils.compute_distance import compute_distance
from test.fixtures.instance_without_state import create_test_instance
from routing.algorithm.solution import Solution
from routing.algorithm.greedy_insertion import compute_best_positions


class TestBestInsertion(TestCase):

    def setUp(self):
        self.instance = create_test_instance()

    def test_case_1(self):
        """
        Best position in an empty job.
        Job initial tasks sequence is [] the resulting one should be [0, 1].
        """

        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 0)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(0, sol.best_insertion.pickup_pos)
        self.assertEqual(0, sol.best_insertion.dropoff_pos)
        self.assertEqual(79, sol.best_insertion.cost)

    def test_case_2(self):
        """
        Pickup at the start, dropoff at the end.
        Job initial tasks sequence is [2, 4, 3, 5] the resulting one should be [0, 2, 4, 3, 5, 1].
        """

        self.instance.plan.jobs[0].task_ids = [2, 4, 3, 5]
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 0)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(0, sol.best_insertion.pickup_pos)
        self.assertEqual(4, sol.best_insertion.dropoff_pos)
        self.assertEqual(34, sol.best_insertion.cost)

    def test_case_3(self):
        """
        Both pickup and dropoff at the start
        Job initial tasks sequence is [2, 4, 3, 5] the resulting one should be [0, 1, 2, 4, 3, 5].
        """

        # Move the task 1 close to the start so the best position is at the beginning
        self.instance.tasks[1].coordinates = (0, 3)
        compute_distance(self.instance)

        self.instance.plan.jobs[0].task_ids = [2, 4, 3, 5]
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 0)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(0, sol.best_insertion.pickup_pos)
        self.assertEqual(0, sol.best_insertion.dropoff_pos)
        self.assertEqual(19, sol.best_insertion.cost)

    def test_case_4(self):
        """
        Both pickup and dropoff at the end
        Job initial tasks sequence is [2, 4, 3, 5] the resulting one should be [2, 4, 3, 5, 0, 1].
        """
        # Move the task 1 close to the start so the best position is at the beginning
        self.instance.tasks[0].coordinates = (0, 22)
        compute_distance(self.instance)

        self.instance.plan.jobs[0].task_ids = [2, 4, 3, 5]
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 0)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(4, sol.best_insertion.pickup_pos)
        self.assertEqual(4, sol.best_insertion.dropoff_pos)
        self.assertEqual(19, sol.best_insertion.cost)

    def test_case_5(self):
        """
        Pickup at the start, dropoff in the middle.
        Job initial tasks sequence is [2, 4, 3, 5] the resulting one should be [0, 2, 4, 3, 1, 5].
        """

        # Move the task 1 close to the start so the best position is at the beginning
        self.instance.tasks[1].coordinates = (0, 18)
        compute_distance(self.instance)

        self.instance.plan.jobs[0].task_ids = [2, 4, 3, 5]
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 0)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(0, sol.best_insertion.pickup_pos)
        self.assertEqual(3, sol.best_insertion.dropoff_pos)
        self.assertEqual(19, sol.best_insertion.cost)

    def test_case_6(self):
        """
        Pickup in the middle, dropoff in the middle but separated by other tasks.
        Job initial tasks sequence is [2, 4, 3, 5] the resulting one should be [2, 0, 4, 1, 3, 5].
        """
        # Move the task 1 close to the start so the best position is at the beginning
        self.instance.tasks[0].coordinates = (0, 7)
        self.instance.tasks[1].coordinates = (0, 12)
        compute_distance(self.instance)

        self.instance.plan.jobs[0].task_ids = [2, 4, 3, 5]
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 0)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(1, sol.best_insertion.pickup_pos)
        self.assertEqual(2, sol.best_insertion.dropoff_pos)
        self.assertEqual(4, sol.best_insertion.cost)

    def test_case_7(self):
        """
        Pickup in the middle, dropoff in the middle separated by no other tasks.
        Job initial tasks sequence is [2, 4, 3, 5] the resulting one should be [2, 0, 1, 4, 3, 5].
        """
        # Move the task 1 close to the start so the best position is at the beginning
        self.instance.tasks[0].coordinates = (0, 7)
        self.instance.tasks[1].coordinates = (0, 8)
        compute_distance(self.instance)

        self.instance.plan.jobs[0].task_ids = [2, 4, 3, 5]
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 0)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(1, sol.best_insertion.pickup_pos)
        self.assertEqual(1, sol.best_insertion.dropoff_pos)
        self.assertEqual(4, sol.best_insertion.cost)

    def test_case_8(self):
        """
        Pickup in the middle, dropoff at the end.
        Job initial tasks sequence is [2, 4, 3, 5] the resulting one should be [2, 0, 4, 3, 5, 1].
        """

        # Move the task 1 close to the start so the best position is at the beginning
        self.instance.tasks[0].coordinates = (0, 7)
        compute_distance(self.instance)

        self.instance.plan.jobs[0].task_ids = [2, 4, 3, 5]
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 0)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(1, sol.best_insertion.pickup_pos)
        self.assertEqual(4, sol.best_insertion.dropoff_pos)
        self.assertEqual(19, sol.best_insertion.cost)