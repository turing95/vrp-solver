from unittest import TestCase

from routing.algorithm.solution import Solution
from test.fixtures.instance_with_state import create_test_instance
from routing.entity.constant import NONE_POSITION


class TestInsertionCostWithFixedPickup(TestCase):

    def setUp(self):
        self.instance = create_test_instance()
        self.job = self.instance.plan.jobs[0]

        # Set up a plan
        self.job.task_ids += [6, 7, 5]  # dropoff 3 is not in the job, delivery 1 is partially completed

        self.sol = Solution(self.instance)

    def test_cost_insertion_with_fixed_pickup_case_1(self):
        sol = self.sol
        job = self.sol.jobs[0]

        # Dropoff right after the executing task
        # tasks:        [0, 2,  1, ->4,  3,  6,  7, 5]
        # arrival time: [0, 9, 18,  29, 43, 52, 66, 75]

        expected_cost = (2 + 3 * 10  # stop cost + distance from 4 to 3
                         + 2 + 3 * 5  # stop cost + distance from 3 to 6
                         + 2 + 3 * 10  # stop cost + distance from 6 to 7
                         + 2 + 3 * 5 + 5 * 5  # stop cost + distance from 7 to 5 + tw penalty
                         - job.cost)

        cost = sol.insertion_cost(job_id=job.id, delivery_id=1, pickup_pos=NONE_POSITION, dropoff_pos=4)
        self.assertEqual(expected_cost, cost)

    def test_cost_insertion_with_fixed_pickup_case_2(self):
        sol = self.sol
        job = self.sol.jobs[0]

        # two positions after the executing task
        # tasks:        [0, 2,  1, ->4,   6,  3,  7, 5]
        # arrival time: [0, 9, 18,  29,  38, 47, 56, 64]

        expected_cost = (2 + 3 * 5  # stop cost + distance from 4 to 6
                         + 2 + 3 * 5  # stop cost + distance from 6 to 3
                         + 2 + 3 * 5  # stop cost + distance from 3 to 7
                         + 2 + 3 * 5  # stop cost + distance from 7 to 5 + tw penalty
                         - job.cost)

        cost = sol.insertion_cost(job_id=job.id, delivery_id=1, pickup_pos=NONE_POSITION, dropoff_pos=5)
        self.assertEqual(expected_cost, cost)

    def test_cost_insertion_with_fixed_pickup_case_3(self):
        sol = self.sol
        job = self.sol.jobs[0]

        # Dropoff in the middle
        # tasks:        [0, 2,  1, ->4,  6,  7,  3,  5]
        # arrival time: [0, 9, 18,  29, 38, 52, 61, 75]

        expected_cost = (2 + 3 * 5  # stop cost + distance from 4 to 6
                         + 2 + 3 * 10  # stop cost + distance from 6 to 7
                         + 2 + 3 * 5  # stop cost + distance from 7 to 3
                         + 2 + 3 * 10 + 5 * 5  # stop cost + distance from 3 to 5 + tw penalty
                         - job.cost)

        cost = sol.insertion_cost(job_id=job.id, delivery_id=1, pickup_pos=NONE_POSITION, dropoff_pos=6)
        self.assertEqual(expected_cost, cost)

    def test_cost_insertion_with_fixed_pickup_case_4(self):
        sol = self.sol
        job = self.sol.jobs[0]

        # Dropoff in the last position
        # tasks:        [0, 2,  1, ->4,  6,  7,  5,  3]
        # arrival time: [0, 9, 18,  29, 38, 52, 61, 75]

        expected_cost = (2 + 3 * 5  # stop cost + distance from 4 to 6
                         + 2 + 3 * 10  # stop cost + distance from 6 to 7
                         + 2 + 3 * 5  # stop cost + distance from 7 to 5
                         + 2 + 3 * 10 + 5 * 5  # stop cost + distance from 5 to 3 + tw penalty
                         - job.cost)

        cost = sol.insertion_cost(job_id=job.id, delivery_id=1, pickup_pos=NONE_POSITION, dropoff_pos=7)
        self.assertEqual(expected_cost, cost)
