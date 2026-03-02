from unittest import TestCase

from routing.algorithm.solution import Solution
from test.fixtures.instance_with_state import create_test_instance


class TestInitWithState(TestCase):

    def setUp(self):
        self.instance = create_test_instance(delivery_window_right_margin=5)
        self.instance.delivery_window_right_margin = 5
        self.job = self.instance.plan.jobs[0]

        self.job.task_ids += [6, 3, 7, 5]

    def test_shrink_delivery_window(self):
        sol = Solution(self.instance)
        for t in sol.tasks:
            self.assertEqual((0, 65), tuple(t.delivery_window))
