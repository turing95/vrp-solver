from unittest import TestCase

from routing.algorithm.solution import Solution
from test.fixtures.instance_with_state import create_test_instance


class TestComputeArcTime(TestCase):

    def setUp(self):
        self.instance = create_test_instance()
        # [0, 2, 1, ->4] arrival time at 4 is 29, departure at 33, arrival at 6 should be 38
        self.job = self.instance.plan.jobs[0]

    def test_case_0(self):
        """arrival is before the delivery window opening"""
        self.instance.tasks[6].delivery_window = (39, 70)
        sol = Solution(self.instance)
        sol.compute_arc_time(4, 6, 0)

        self.assertEqual(33 + 5,  # departure time + travel time
                         sol.tasks[6].arrival_time)

        self.assertEqual(38 + 1 + 1 + 3,  # arrival time + waiting time + stop time + service time
                         sol.tasks[6].departure_time)

    def test_case_1(self):
        """arrival is in the delivery window"""
        self.instance.tasks[6].delivery_window = (38, 70)
        sol = Solution(self.instance)
        sol.compute_arc_time(4, 6, 0)

        self.assertEqual(33 + 5,  # departure time + travel time
                         sol.tasks[6].arrival_time)

        self.assertEqual(38 + 0 + 1 + 3,  # arrival time + waiting time + stop time + service time
                         sol.tasks[6].departure_time)

    def test_case_2(self):
        """arrival is after the delivery window arrival"""
        self.instance.tasks[6].delivery_window = (0, 35)
        self.instance.plan.set_task_arrival_time(0, 4, 45)
        sol = Solution(self.instance)
        sol.compute_arc_time(4, 6, 0)

        self.assertEqual(33 + 5,  # departure time + travel time
                         sol.tasks[6].arrival_time)

        self.assertEqual(38 + 0 + 1 + 3,  # arrival + waiting + stop time + service time
                         sol.tasks[6].departure_time)

    def test_case_4(self):
        """Executing task departure time is smaller than current time. (In such a case the current time should be
        considered as the actual departure time from the executing task. This because the job stopped in the last
        task for a while waiting for future tasks.)"""
        self.instance.plan.current_time = 40  # departure from 4 (executing task) is 33
        sol = Solution(self.instance)

        sol.compute_arc_time(4, 6, 0)

        self.assertEqual(40 + 5,  # current time + travel time
                         sol.tasks[6].arrival_time)

        self.assertEqual(45 + 0 + 1 + 3,  # arrival + waiting + stop time + service time
                         sol.tasks[6].departure_time)

        pass
