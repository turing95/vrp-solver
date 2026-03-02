from unittest import TestCase

from routing.algorithm.solution import Solution
from test.fixtures.instance_two_jobs import create_test_instance


class TestInitWithSpanPenalty(TestCase):

    def setUp(self):
        self.instance = create_test_instance()
        self.instance.span_penalty = 7
        self.plan = self.instance.plan

    def test_case_0(self):
        """Init balanced_job_size when there is no executing task, no state"""
        sol = Solution(self.instance)
        self.assertEqual(4, sol.balanced_job_size)

    def test_case_1(self):
        """Init balanced_job_size when there is an executing task, no state"""
        self.plan.set_executing_task(job_id=0, task_id=3)
        sol = Solution(self.instance)

        self.assertEqual(2, sol.balanced_job_size)

    def test_case_2(self):
        """Round up balanced_job_size in case of a fractional average number of task per jobs"""
        self.plan.set_executing_task(job_id=0, task_id=1)
        sol = Solution(self.instance)

        self.assertEqual(3, sol.balanced_job_size)

    def test_job_cost(self):
        """Include the span penalty when initializing a job, no state"""
        self.plan.set_tasks(job_id=0, route=[(0, 0, 4), (2, 9, 13), (1, 18, 22), (3, 39, 43), (6, 48, 54)])

        sol = Solution(self.instance)
        self.assertEqual(4, sol.balanced_job_size)

        self.assertEqual(
            (7 * 1  # span penalty
             + 2 +  # first stop
             2 + 3 * 5  # cost from 0 to 2
             + 2 + 3 * 5  # cost from 2 to 1
             + 2 + 3 * 15  # cost from 1 to 3
             + 2 + 3 * 5  # cost from 3 to 6
             ),
            sol.jobs[0].cost)

    def test_job_cost(self):
        """Include the span penalty when initializing a job, with state"""
        self.plan.set_tasks(job_id=0, route=[(0, 0, 4), (2, 9, 13), (1, 18, 22), (3, 39, 43), (6, 48, 52), (7, 64, 70)])
        self.plan.set_tasks(job_id=1, route=[(4, 0, 4), (5, 24, 28)])
        self.plan.set_executing_task(job_id=0, task_id=2)
        self.plan.set_executing_task(job_id=1, task_id=5)

        sol = Solution(self.instance)
        self.assertEqual(2, sol.balanced_job_size)

        self.assertEqual(
            (7 * 2  # span penalty
             + 2 + 3 * 5  # cost from 2 to 1
             + 2 + 3 * 15  # cost from 1 to 3
             + 2 + 3 * 5  # cost from 3 to 6
             + 2 + 3 * 10  # cost from 6 to 7
             ),
            sol.jobs[0].cost)
