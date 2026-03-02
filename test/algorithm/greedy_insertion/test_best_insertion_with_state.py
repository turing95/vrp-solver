from unittest import TestCase

from routing.utils.compute_distance import compute_distance
from test.fixtures.instance_with_state import create_test_instance
from routing.algorithm.solution import Solution
from routing.algorithm.greedy_insertion import compute_best_positions


class TestBestInsertionWithState(TestCase):

    def setUp(self):
        self.instance = create_test_instance()
        self.instance.plan.jobs[0].task_ids = [0, 2, 1, 4, 3, 5]

    def test_case_1(self):
        """
        Best position with no other task to do in the job.
        Job initial tasks sequence is [0, 2, 1, ->4] the resulting one should be [0, 2, 1, ->4, 6, 7].
        """
        self.instance.plan.jobs[0].task_ids = [0, 2, 1, 4]

        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 3)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(4, sol.best_insertion.pickup_pos)
        self.assertEqual(4, sol.best_insertion.dropoff_pos)
        self.assertEqual(49, sol.best_insertion.cost)

    def test_case_2(self):
        """
        Pickup at the start, dropoff at the end.
        Job initial tasks sequence is [0, 2, 1, ->4, 3, 5] the resulting one should be [0, 2, 1, ->4, 6, 3, 5, 7].
        """
        self.instance.tasks[7].coordinates = (0, 40)
        compute_distance(self.instance)

        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 3)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(4, sol.best_insertion.pickup_pos)
        self.assertEqual(6, sol.best_insertion.dropoff_pos)
        self.assertEqual(19, sol.best_insertion.cost)

    def test_case_3(self):
        """
        Both pickup and dropoff right after the executing task
        Job initial tasks sequence is [0, 2, 1, ->4, 3, 5] the resulting one should be [0, 1, 2, ->4, 6, 7, 3, 5].
        """
        self.instance.tasks[7].coordinates = (0, 22)
        compute_distance(self.instance)

        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 3)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(4, sol.best_insertion.pickup_pos)
        self.assertEqual(4, sol.best_insertion.dropoff_pos)
        self.assertEqual(4, sol.best_insertion.cost)

    def test_case_4(self):
        """
        Both pickup and dropoff at the end
        Job initial tasks sequence is [0, 2, 1, ->4, 3, 5] the resulting one should be [0, 2, 1, ->4, 3, 5, 6, 7].
        """
        self.instance.tasks[6].coordinates = (0, 40)
        self.instance.tasks[7].coordinates = (0, 45)
        compute_distance(self.instance)

        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 3)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(6, sol.best_insertion.pickup_pos)
        self.assertEqual(6, sol.best_insertion.dropoff_pos)
        self.assertEqual(34 + 25, sol.best_insertion.cost)  # 25 tw penalty

    def test_case_5(self):
        """
        Pickup at the start, dropoff in the middle.
        Job initial tasks sequence is [0, 2, 1, ->4, 3, 5] the resulting one should be [0, 2, 1, ->4, 6, 3, 7, 5].
        """

        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 3)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(4, sol.best_insertion.pickup_pos)
        self.assertEqual(5, sol.best_insertion.dropoff_pos)
        self.assertEqual(4, sol.best_insertion.cost)

    def test_case_6(self):
        """
        Pickup in the middle, dropoff in the middle but separated by other tasks.
        Job initial tasks sequence is [0, 2, 1, ->4, 3, 5] the resulting one should be [0, 2, 1, ->4, 3, 6, 5, 7].
        """
        self.instance.tasks[6].coordinates = (0, 27)
        self.instance.tasks[7].coordinates = (0, 40)
        compute_distance(self.instance)
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 3)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(5, sol.best_insertion.pickup_pos)
        self.assertEqual(6, sol.best_insertion.dropoff_pos)
        self.assertEqual(19, sol.best_insertion.cost)

    def test_case_7(self):
        """
        Pickup in the middle, dropoff in the middle separated by no other tasks.
        Job initial tasks sequence is [0, 2, 1, ->4, 3, 5] the resulting one should be [0, 2, 1, ->4, 3, 6, 7, 5].
        """
        self.instance.tasks[6].coordinates = (0, 27)
        compute_distance(self.instance)
        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 3)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(5, sol.best_insertion.pickup_pos)
        self.assertEqual(5, sol.best_insertion.dropoff_pos)
        self.assertEqual(4, sol.best_insertion.cost)

    def test_case_8(self):
        """
        Pickup in the middle, dropoff in the middle but separated by other tasks.
        Job initial tasks sequence is [0, 2, ->1, 4, 3, 5] the resulting one should be [0, 2, ->1, 4, 6, 3, 7, 5].
        """
        self.instance.plan.executing_task[0] = 1
        compute_distance(self.instance)

        sol = Solution(self.instance)
        compute_best_positions(sol, 0, 3)

        self.assertEqual(0, sol.best_insertion.job_id)
        self.assertEqual(4, sol.best_insertion.pickup_pos)
        self.assertEqual(5, sol.best_insertion.dropoff_pos)
        self.assertEqual(4, sol.best_insertion.cost)
