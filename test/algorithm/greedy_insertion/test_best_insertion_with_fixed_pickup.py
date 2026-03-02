from unittest import TestCase

from routing.utils.compute_distance import compute_distance
from test.fixtures.instance_with_state import create_test_instance
from routing.algorithm.solution import Solution
from routing.algorithm.greedy_insertion import compute_best_positions
from routing.entity.constant import NONE_POSITION


class TestBestInsertionWithFixedPickup(TestCase):

    def setUp(self):
        self.instance = create_test_instance()
        self.instance.plan.jobs[0].task_ids = [0, 2, 1, 4, 6, 7, 5]

    def test_case_1(self):
        """
        Best position in an empty job.
        Job initial tasks sequence is [0, 2, 1, ->4]  the resulting one should be [0, 2, 1, ->4, 3].
        """
        self.instance.plan.jobs[0].task_ids = [0, 2, 1, 4]

        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 1)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(NONE_POSITION, sol.best_insertion.pickup_pos)
        self.assertEqual(4, sol.best_insertion.dropoff_pos)
        self.assertEqual(32, sol.best_insertion.cost)

    def test_case_2(self):
        """
        Dropoff right after the executing task.
        Job initial tasks sequence is [0, 2, 1, ->4, 6, 7, 5] the resulting one should be [0, 2, 1, ->4, 3, 6, 7, 5].
        """
        self.instance.tasks[3].coordinates = (0, 18)
        compute_distance(self.instance)

        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 1)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(NONE_POSITION, sol.best_insertion.pickup_pos)
        self.assertEqual(4, sol.best_insertion.dropoff_pos)
        self.assertEqual(2, sol.best_insertion.cost)

    def test_case_3(self):
        """
        Dropoff two positions after the executing task.
        Job initial tasks sequence is [0, 2, 1, ->4, 6, 7, 5] the resulting one should be [0, 2, 1, ->4, 6, 3, 7, 5].
        """
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 1)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(NONE_POSITION, sol.best_insertion.pickup_pos)
        self.assertEqual(5, sol.best_insertion.dropoff_pos)
        self.assertEqual(2, sol.best_insertion.cost)

    def test_case_4(self):
        """
        Dropoff in the middle.
        Job initial tasks sequence is [0, 2, 1, ->4, 6, 7, 5] the resulting one should be [0, 2, 1, ->4, 6, 7, 3, 5].
        """
        self.instance.tasks[3].coordinates = (0, 32)
        compute_distance(self.instance)

        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 1)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(NONE_POSITION, sol.best_insertion.pickup_pos)
        self.assertEqual(6, sol.best_insertion.dropoff_pos)
        self.assertEqual(2, sol.best_insertion.cost)

    def test_case_5(self):
        """
        Dropoff in the end.
        Job initial tasks sequence is [0, 2, 1, ->4, 6, 7, 5] the resulting one should be [0, 2, 1, ->4, 6, 7, 5, 3].
        """
        self.instance.tasks[3].coordinates = (0, 40)
        compute_distance(self.instance)

        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 1)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(NONE_POSITION, sol.best_insertion.pickup_pos)
        self.assertEqual(7, sol.best_insertion.dropoff_pos)
        self.assertEqual(17, sol.best_insertion.cost)
