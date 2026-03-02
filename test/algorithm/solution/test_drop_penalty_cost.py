from unittest import TestCase

from routing.algorithm.solution import Solution
from test.fixtures.instance_with_state import create_test_instance


class TestDropPenaltyCost(TestCase):

    def setUp(self):
        self.instance = create_test_instance()
        self.instance.drop_penalty = 1000
        self.instance.drop_penalty_delta = 1000
        self.instance.drop_penalty_slope = 0.01
        self.job = self.instance.plan.jobs[0]

        # Set up a plan
        self.job.task_ids += [3, 5]  # tasks 6 and 7 of delivery 3 are not yet planned

    def test_init_drop_penalty(self):
        """Test that correctly initialize the drop penalty"""

        self.instance.tasks[0].delivery_window = (0, 30)
        self.instance.tasks[1].delivery_window = (0, 35)
        self.instance.tasks[2].delivery_window = (0, 40)
        self.instance.tasks[3].delivery_window = (0, 45)
        self.instance.tasks[4].delivery_window = (0, 50)
        self.instance.tasks[5].delivery_window = (0, 55)
        self.instance.tasks[6].delivery_window = (0, 60)
        self.instance.tasks[7].delivery_window = (0, 65)

        sol = Solution(self.instance)

        self.assertEqual(self.instance.compute_penalty(0), sol.delivery_drop_penalty[0])
        self.assertEqual(self.instance.compute_penalty(1), sol.delivery_drop_penalty[1])
        self.assertEqual(self.instance.compute_penalty(2), sol.delivery_drop_penalty[2])
        self.assertEqual(self.instance.compute_penalty(3), sol.delivery_drop_penalty[3])

    def test_solution_cost_case_0(self):
        """Test the solution cost method with a delivery not completed"""
        sol = Solution(self.instance)
        # Precondition: delivery 3 is the only delivery not completed
        self.assertEqual(1, len(sol.not_completed_deliveries))
        self.assertIn(3, sol.not_completed_deliveries)

        # The cost of the solution is the cost of the only job present plus the drop penalty of delivery 3
        self.assertEqual(sol.jobs[0].cost + self.instance.compute_penalty(3), sol.compute_cost())

    def test_solution_cost_case_1(self):
        """Test the solution cost method with a delivery partially completed"""
        self.job.task_ids += [3, 5, 6]
        sol = Solution(self.instance)

        # Precondition: delivery 3 is the only delivery not completed
        self.assertEqual(1, len(sol.not_completed_deliveries))
        self.assertIn(3, sol.not_completed_deliveries)

        # The cost of the solution is the cost of the only job present plus the drop penalty of delivery 3
        self.assertEqual(sol.jobs[0].cost + self.instance.compute_penalty(3), sol.compute_cost())
