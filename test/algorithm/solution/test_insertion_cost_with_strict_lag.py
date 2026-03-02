from unittest import TestCase

from routing.algorithm.solution import Solution
from test.fixtures.instance_with_state import create_test_instance


class TestInsertionCostWithState(TestCase):

    def setUp(self):
        self.instance = create_test_instance(max_lag=30)
        self.job = self.instance.plan.jobs[0]

        # Set up a plan
        self.job.task_ids += [3, 5]  # tasks 6 and 7 of delivery 3 are not yet planned

        self.sol = Solution(self.instance)

    def test_case_0(self):
        sol = self.sol
        job = sol.jobs[0]

        # Both pickup and dropoff right after the executing task
        # tasks:        [0, 2,  1, ->4,  6,  7,  3,  5]
        # arrival time: [0, 9, 18,  29, 38, 52, 61, 75]
        cost = sol.insertion_cost(job_id=job.id, delivery_id=3, pickup_pos=4, dropoff_pos=4)
        self.assertEqual(2 + 3 * 5  # stop cost + distance from 4 to 6
                         + 2 + 3 * 10  # stop cost + distance from 6 to 7
                         + 2 + 3 * 5 + 2 * 22  # stop cost + distance from 7 to 3 + lag penalty
                         + 2 + 3 * 10 + 5 * 5 + 2 * 16  # stop cost + distance from 3 to 5 + tw penalty + lag penalty
                         - job.cost,
                         cost)

    def test_case_1(self):
        sol = self.sol
        job = sol.jobs[0]

        # Both pickup and dropoff after the last tasks
        # tasks:        [0, 2,  1, ->4,  3,  5,  6,  7]
        # arrival time: [0, 9, 18,  29, 43, 57, 76, 90]
        cost = sol.insertion_cost(job_id=job.id, delivery_id=3, pickup_pos=6, dropoff_pos=6)
        self.assertEqual(2 + 3 * 10 + 2 * 4  # stop cost + distance from 4 to 3 + lag penalty
                         + 2 + 3 * 10  # stop cost + distance from 3 to 5
                         + 2 + 3 * 15 + 5 * 6  # stop cost + distance from 5 to 6
                         + 2 + 3 * 10 + 5 * 20  # stop cost + distance from 6 to 7 + tw penalty
                         - job.cost,
                         cost)

    def test_case_2(self):
        sol = self.sol
        job = sol.jobs[0]

        # Pickup right after the executing task, dropoff in the middle
        # tasks:        [0, 2,  1, ->4,  6,  3,  7,  5]
        # arrival time: [0, 9, 18,  29, 38, 47, 56, 65]
        cost = sol.insertion_cost(job_id=job.id, delivery_id=3, pickup_pos=4, dropoff_pos=5)
        self.assertEqual(2 + 3 * 5  # stop cost + distance from 4 to 6
                         + 2 + 3 * 5 + 2 * 8  # stop cost + distance from 6 to 3 + lag penalty
                         + 2 + 3 * 5  # stop cost + distance from 3 to 7
                         + 2 + 3 * 5 + 2 * 6  # stop cost + distance from 7 to 5 + lag penalty
                         - job.cost,
                         cost)

    def test_case_3(self):
        sol = self.sol
        job = sol.jobs[0]

        # Pickup two positions after the executing task, dropoff separated by 1 task
        # tasks:        [0, 2,  1, ->4,  3,  6,  5,  7]
        # arrival time: [0, 9, 18,  29, 43, 52, 71, 80]
        cost = sol.insertion_cost(job_id=job.id, delivery_id=3, pickup_pos=5, dropoff_pos=6)
        self.assertEqual(2 + 3 * 10 + 2 * 4 # stop cost + distance from 4 to 3
                         + 2 + 3 * 5  # stop cost + distance from 3 to 6
                         + 2 + 3 * 15 + 5 * 1 + 2 * 12  # stop cost + distance from 6 to 5 + tw penalty + lag penalty
                         + 2 + 3 * 5 + 5 * 10  # stop cost + distance from 5 to 7 + tw penalty
                         - job.cost,
                         cost)

    def test_case_4(self):
        sol = self.sol
        job = sol.jobs[0]

        # Pickup and dropoff in the middle of the job separated by no task
        # tasks:        [0, 2,  1, ->4,  3,  6,  7,  5]
        # arrival time: [0, 9, 18,  29, 43, 52, 66, 75]
        cost = sol.insertion_cost(job_id=job.id, delivery_id=3, pickup_pos=5, dropoff_pos=5)
        self.assertEqual(2 + 3 * 10 + 2 * 4  # stop cost + distance from 4 to 3 + lag penalty
                         + 2 + 3 * 5  # stop cost + distance from 3 to 6
                         + 2 + 3 * 10  # stop cost + distance from 6 to 7
                         + 2 + 3 * 5 + 5 * 5 + 2 * 16  # stop cost + distance from 7 to 5 + tw penalty + lag penalty
                         - job.cost,
                         cost)

    def test_case_5(self):
        sol = self.sol
        job = sol.jobs[0]

        # Pickup right after the executing task, dropoff in the last
        # tasks:        [0, 2,  1, ->4,  6,  3, 5, 7]
        # arrival time: [0, 9, 18,  29, 38, 47, 61, 70]
        cost = sol.insertion_cost(job_id=job.id, delivery_id=3, pickup_pos=4, dropoff_pos=6)
        self.assertEqual(2 + 3 * 5  # stop cost + distance from 4 to 6
                         + 2 + 3 * 5 + 2 * 8  # stop cost + distance from 6 to 3
                         + 2 + 3 * 10 + 2 * 2  # stop cost + distance from 3 to 5 + lag penalty
                         + 2 + 3 * 5 + 2 * 2 # stop cost + distance from 5 to 7 + lag penalty
                         - job.cost,
                         cost)
