from unittest import TestCase

from array import array
from routing.algorithm.solution import Solution
from test.fixtures.instance_without_state import create_test_instance


class TestInsertionCostWithoutState(TestCase):

    def setUp(self):
        self.instance = create_test_instance()
        self.job = self.instance.plan.jobs[0]

        # Set up a plan
        self.job.task_ids = [2, 4, 3, 5]

        self.sol = Solution(self.instance)

    def test_case_0(self):
        sol = self.sol
        job = sol.jobs[0]

        # Both pickup and dropoff before the first tasks
        # tasks:        [0, 1, 2, 4, 3, 5]
        # arrival time: [ 0, 29, 53, 62, 71, 80]
        # arc_cost:     [ 2, 77, 17, 27, 72, 117]
        cost = sol.insertion_cost(job_id=job.id, delivery_id=0, pickup_pos=0, dropoff_pos=0)
        self.assertEqual(2  # First task only stop cost
                         + 2 + 3 * 25  # stop cost + distance from 0 to 1
                         + 2 + 3 * 20  # stop cost + distance from 1 to p2
                         + 2 + 3 * 5 + 5 * 2  # stop cost + distance from p2 to 4
                         + 2 + 3 * 5 + 5 * 11  # stop cost + distance + tw penalty from 4 to 3
                         + 2 + 3 * 5 + 5 * 20  # stop cost + distance + tw penalty from 3 to 5
                         - job.cost,
                         cost)

    def test_case_1(self):
        sol = self.sol
        job = sol.jobs[0]

        # Both pickup and dropoff after the last tasks
        # tasks:        [2, 4, 3, 5, 0, 1]
        # arrival time: [ 0, 9, 18, 27, 51, 80]
        cost = sol.insertion_cost(job_id=job.id, delivery_id=0, pickup_pos=4, dropoff_pos=4)
        self.assertEqual(2  # First task only stop cost
                         + 2 + 3 * 5  # stop cost + distance from 2 to 4
                         + 2 + 3 * 5  # stop cost + distance from 4 to 3
                         + 2 + 3 * 5  # stop cost + distance from 3 to 5
                         + 2 + 3 * 20  # stop cost + distance from 5 to 0
                         + 2 + 3 * 25 + 5 * 20  # stop cost + distance + tw penalty from 0 to 1
                         - job.cost,
                         cost)

    def test_case_2(self):
        sol = self.sol
        job = sol.jobs[0]

        # Pickup before first task dropoff after the first
        # tasks:        [0, 2, 1, 4, 3, 5]
        # arrival time: [ 0, 9, 33, 52, 61, 70]
        cost = sol.insertion_cost(job_id=job.id, delivery_id=0, pickup_pos=0, dropoff_pos=1)
        self.assertEqual(2  # First task only stop cost
                         + 2 + 3 * 5  # stop cost + distance from 0 to 2
                         + 2 + 3 * 20  # stop cost + distance from 2 to 1
                         + 2 + 3 * 15  # stop cost + distance from 1 to 4
                         + 2 + 3 * 5 + 5 * 1  # stop cost + distance from 4 to 3
                         + 2 + 3 * 5 + 5 * 10  # stop cost + distance + tw penalty from 3 to 5
                         - job.cost,
                         cost)

    def test_case_3(self):
        sol = self.sol
        job = sol.jobs[0]

        # Pickup in the second position and dropoff in the middle of the job separated by 1 task
        # tasks:        [2, 0, 4, 1, 3, 5]
        # arrival time: [ 0, 9, 23, 42, 56, 65]
        cost = sol.insertion_cost(job_id=job.id, delivery_id=0, pickup_pos=1, dropoff_pos=2)
        self.assertEqual(2  # First task only stop cost
                         + 2 + 3 * 5  # stop cost + distance from 2 to 0
                         + 2 + 3 * 10  # stop cost + distance from 0 to 4
                         + 2 + 3 * 15  # stop cost + distance from 4 to 1
                         + 2 + 3 * 10  # stop cost + distance from 1 to 3
                         + 2 + 3 * 5 + 5 * 5  # stop cost + distance + tw penalty from 3 to 5
                         - job.cost,
                         cost)

    def test_case_4(self):
        sol = self.sol
        job = sol.jobs[0]

        # Pickup dropoff in the middle of the job separated by no task
        # tasks:        [2, 4, 0, 1, 3, 5]
        # arrival time: [ 0, 9, 23, 52, 66, 75]
        # arc_cost:     []
        cost = sol.insertion_cost(job_id=job.id, delivery_id=0, pickup_pos=2, dropoff_pos=2)
        self.assertEqual(2  # First task only stop cost
                         + 2 + 3 * 5  # stop cost + distance from 2 to 4
                         + 2 + 3 * 10  # stop cost + distance from 4 to 0
                         + 2 + 3 * 25  # stop cost + distance from 0 to 1
                         + 2 + 3 * 10 + 5 * 6  # stop cost + distance + tw penalty from 1 to 3
                         + 2 + 3 * 5 + 5 * 15  # stop cost + distance + tw penalty from 3 to 5
                         - job.cost,
                         cost)

    def test_case_5(self):
        sol = self.sol
        job = sol.jobs[0]

        # Pickup in the middle dropoff in the last
        # tasks:        [2, 4, 0, 3, 5, 1]
        # arrival time: [ 0,  9, 23, 42, 51, 60]
        cost = sol.insertion_cost(job_id=job.id, delivery_id=0, pickup_pos=2, dropoff_pos=4)
        self.assertEqual(2  # First task only stop cost
                         + 2 + 3 * 5  # stop cost + distance from 2 to 4
                         + 2 + 3 * 10  # stop cost + distance from 4 to 0
                         + 2 + 3 * 15  # stop cost + distance from 0 to 1
                         + 2 + 3 * 5  # stop cost + distance from 1 to 3
                         + 2 + 3 * 5   # stop cost + distance from 3 to 5
                         - job.cost,
                         cost)

    def test_case_6(self):
        sol = self.sol
        job = sol.jobs[0]

        # Pickup in the first dropoff in the last
        # tasks:        [0, 2, 4, 3, 5, 1]
        # arrival time: [ 0,  9, 18, 27, 36, 45]
        cost = sol.insertion_cost(job_id=job.id, delivery_id=0, pickup_pos=0, dropoff_pos=4)
        self.assertEqual(2  # First task only stop cost
                         + 2 + 3 * 5  # stop cost + distance from 0 to 2
                         + 2 + 3 * 5  # stop cost + distance from 2 to 4
                         + 2 + 3 * 5  # stop cost + distance from 4 to 3
                         + 2 + 3 * 5  # stop cost + distance from 3 to 5
                         + 2 + 3 * 5   # stop cost + distance from 5 to 1
                         - job.cost,
                         cost)

    def test_work_shift_constraint(self):
        sol = self.sol
        job = sol.jobs[0]
        job.work_shift = array('i', (0, 79))

        # Both pickup and dropoff before the first tasks
        # tasks:        [0, 1, 2, 4, 3, 5]
        # arrival time: [ 0, 29, 53, 62, 71, 80]
        cost = sol.insertion_cost(job_id=job.id, delivery_id=0, pickup_pos=0, dropoff_pos=0)
        self.assertEqual(self.instance.drop_penalty + 1, cost)

