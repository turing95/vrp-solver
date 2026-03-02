from unittest import TestCase

from routing.algorithm.solution import Solution
from test.fixtures.instance_with_state import create_test_instance
from routing.entity.constant import NONE_POSITION


class TestInsertionCostWithFixedExecutingPickup(TestCase):

    def setUp(self):
        self.instance = create_test_instance()
        self.job = self.instance.plan.jobs[0]

        # Set up a plan: dropoff 5 is not in the job, delivery 2 is partially completed, pickup 4 is the executing task
        self.job.task_ids += [6, 3, 7]

        self.sol = Solution(self.instance)

    def test_case_1(self):
        sol = self.sol
        job = self.sol.jobs[0]

        # Dropoff right after the executing task
        # tasks:        [0, 2,  1, ->4,  5,  6,  3,  7]
        # arrival time: [0, 9, 18,  29, 53, 72, 81, 90]

        expected_cost = (2 + 3 * 20  # stop cost + distance from 4 to 5
                         + 2 + 3 * 15 + 5 * 2  # stop cost + distance from 5 to 6 + tw penalty
                         + 2 + 3 * 5 + 5 * 11  # stop cost + distance from 6 to 3 + tw penalty
                         + 2 + 3 * 5 + 5 * 20  # stop cost + distance from 3 to 7 + tw penalty
                         - job.cost)

        cost = sol.insertion_cost(job_id=job.id, delivery_id=2, pickup_pos=NONE_POSITION, dropoff_pos=4)
        self.assertEqual(expected_cost, cost)

    def test_case_2(self):
        sol = self.sol
        job = self.sol.jobs[0]

        # two positions after the executing task
        # tasks:        [0, 2,  1, ->4,   6,  5,  3,  7]
        # arrival time: [0, 9, 18,  29,  38, 57, 71, 80]

        expected_cost = (2 + 3 * 5  # stop cost + distance from 4 to 6
                         + 2 + 3 * 15  # stop cost + distance from 6 to 5
                         + 2 + 3 * 10 + 5 * 1  # stop cost + distance from 5 to 3 + tw penalty
                         + 2 + 3 * 5 + 5 * 10  # stop cost + distance from 3 to 7 + tw penalty
                         - job.cost)

        cost = sol.insertion_cost(job_id=job.id, delivery_id=2, pickup_pos=NONE_POSITION, dropoff_pos=5)
        self.assertEqual(expected_cost, cost)

    def test_case_3(self):
        sol = self.sol
        job = self.sol.jobs[0]

        # Dropoff in the middle
        # tasks:        [0, 2,  1, ->4,  6,  3,  5,  7]
        # arrival time: [0, 9, 18,  29, 38, 47, 61, 70]

        expected_cost = (2 + 3 * 5  # stop cost + distance from 4 to 6
                         + 2 + 3 * 5  # stop cost + distance from 6 to 3
                         + 2 + 3 * 10  # stop cost + distance from 3 to 5
                         + 2 + 3 * 5   # stop cost + distance from 5 to 7
                         - job.cost)

        cost = sol.insertion_cost(job_id=job.id, delivery_id=2, pickup_pos=NONE_POSITION, dropoff_pos=6)
        self.assertEqual(expected_cost, cost)

    def test_case_4(self):
        sol = self.sol
        job = self.sol.jobs[0]

        # Dropoff in the last position
        # tasks:        [0, 2,  1, ->4,  6,  3,  7,  5]
        # arrival time: [0, 9, 18,  29, 38, 47, 56, 65]

        expected_cost = (2 + 3 * 5  # stop cost + distance from 4 to 6
                         + 2 + 3 * 5  # stop cost + distance from 6 to 3
                         + 2 + 3 * 5  # stop cost + distance from 3 to 7
                         + 2 + 3 * 5  # stop cost + distance from 7 to 5
                         - job.cost)

        cost = sol.insertion_cost(job_id=job.id, delivery_id=2, pickup_pos=NONE_POSITION, dropoff_pos=7)
        self.assertEqual(expected_cost, cost)
