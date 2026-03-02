from unittest import TestCase

from routing.algorithm.solution import Solution
from routing.entity.constant import NONE_TASK
from test.fixtures.instance_two_jobs import create_test_instance


class TestInsertionCostWithSpanPenalty(TestCase):

    def setUp(self):
        self.instance = create_test_instance()
        self.instance.span_penalty = 7
        self.plan = self.instance.plan

    def test_case_0(self):
        """span penalty is zero when the job is perfectly balanced, no state"""

        self.plan.set_tasks(job_id=1, route=[(6, 0, 4), (7, 14, 18)])
        sol = Solution(self.instance)
        job = sol.jobs[1]

        cost = sol.insertion_cost(job_id=1, delivery_id=2, pickup_pos=0, dropoff_pos=2)
        self.assertEqual(0  # span penalty
                         + 2  # first task
                         + 2 + 3 * 5  # stop cost + distance from 4 to 6
                         + 2 + 3 * 10  # stop cost + distance from 6 to 7
                         + 2 + 3 * 5  # stop cost + distance from 7 to 5
                         - job.cost,
                         cost)

    def test_case_1(self):
        """span penalty zero when the job has less task than the desired, no state"""
        sol = Solution(self.instance)
        job = sol.jobs[1]

        cost = sol.insertion_cost(job_id=1, delivery_id=2, pickup_pos=0, dropoff_pos=0)
        self.assertEqual(0  # span penalty
                         + 2  # first task
                         + 2 + 3 * 20  # stop cost + distance from 4 to 5
                         - job.cost,
                         cost)

    def test_case_2(self):
        """span penalty strictly positive when the job has more task than the desired, no state"""
        sol = Solution(self.instance)
        job = sol.jobs[0]

        cost = sol.insertion_cost(job_id=0, delivery_id=2, pickup_pos=3, dropoff_pos=4)
        self.assertEqual(7 * 2  # span penalty
                         + 2  # first task
                         + 2 + 3 * 5  # stop cost + distance from 0 to 2
                         + 2 + 3 * 5  # stop cost + distance from 2 to 1
                         + 2 + 3 * 5  # stop cost + distance from 1 to 4
                         + 2 + 3 * 10  # stop cost + distance from 4 to 3
                         + 2 + 3 * 10  # stop cost + distance from 3 to 5
                         - job.cost,
                         cost)

    def test_case_3(self):
        """span penalty is zero when the job is perfectly balanced, with state"""

        self.plan.set_tasks(job_id=1, route=[(4, 0, 4), (5, 24, 28)])
        self.plan.set_executing_task(job_id=1, task_id=5)
        self.plan.set_executing_task(job_id=0, task_id=2)

        sol = Solution(self.instance)
        job = sol.jobs[1]

        self.assertEqual(2, sol.balanced_job_size)

        cost = sol.insertion_cost(job_id=1, delivery_id=3, pickup_pos=2, dropoff_pos=2)
        self.assertEqual(0  # span penalty
                         + 2 + 3 * 15  # stop cost + distance from 5 to 6
                         + 2 + 3 * 10  # stop cost + distance from 6 to 7
                         - job.cost,
                         cost)

    def test_case_4(self):
        """span penalty strictly positive when the job is not balanced, with state"""

        self.plan.set_tasks(job_id=0, route=[(0, 0, 4), (2, 9, 13), (1, 18, 22), (6, 48, 54)])  # task 3 and 7 are missing
        self.plan.set_tasks(job_id=1, route=[(4, 0, 4), (5, 24, 28)])
        self.plan.set_executing_task(job_id=0, task_id=2)
        self.plan.set_executing_task(job_id=1, task_id=5)

        sol = Solution(self.instance)
        job = sol.jobs[0]

        self.assertEqual(2, sol.balanced_job_size)

        cost = sol.insertion_cost(job_id=0, delivery_id=1, pickup_pos=NONE_TASK, dropoff_pos=4)
        self.assertEqual(7 * 1  # span penalty
                         + 2 + 3 * 5  # stop cost + distance from 2 to 1
                         + 2 + 3 * 10  # stop cost + distance from 1 to 6
                         + 2 + 3 * 5  # stop cost + distance from 6 to 3
                         - job.cost,
                         cost)
