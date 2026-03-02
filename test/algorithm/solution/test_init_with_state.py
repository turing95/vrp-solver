from unittest import TestCase

from routing.algorithm.solution import Solution
from test.fixtures.instance_with_state import create_test_instance
from routing.entity.constant import NONE_JOB


class TestInitWithState(TestCase):

    def setUp(self):
        self.instance = create_test_instance()
        self.job = self.instance.plan.jobs[0]

        self.job.task_ids += [6, 3, 7, 5]

    def test_init_current_time(self):
        sol = Solution(self.instance)
        self.assertEqual(0, sol.current_time)

        self.instance.plan.set_current_time(10)
        sol = Solution(self.instance)
        self.assertEqual(10, sol.current_time)

    def test_init_incomplete_deliveries(self):
        self.job.task_ids = [0, 2, 1, 4]

        sol = Solution(self.instance)

        # Incomplete Deliveries
        self.assertEqual(3, len(sol.not_completed_deliveries))
        self.assertTrue(1 in sol.not_completed_deliveries)
        self.assertTrue(2 in sol.not_completed_deliveries)
        self.assertTrue(3 in sol.not_completed_deliveries)

    def test_tasks_to_plan(self):
        self.job.task_ids = [0, 2, 1, 4]
        sol = Solution(self.instance)

        self.assertEqual(4, len(sol.tasks_to_plan))
        for t in [3, 5, 6, 7]:
            self.assertTrue(t in sol.tasks_to_plan)

    def test_init_job_cost(self):
        """
        Cost should not include the cost for the completed and executing tasks,
        just the remaining ones.
        """

        sol = Solution(self.instance)
        job_id = self.job.id

        # Initialize the job with the correct cost
        self.assertEqual(
            (
                2 + 3 * 5  # cost from 4 to 6
                + 2 + 3 * 5  # cost from 6 to 3
                + 2 + 3 * 5  # cost from 3 to 7
                + 2 + 3 * 5  # cost from 7 to 5
            ),
            sol.jobs[job_id].cost)

    def test_job_remaining_tasks_size(self):
        sol = Solution(self.instance)

        # Initialize the job with the correct remaining task size value
        self.assertEqual(4, sol.jobs[0].remaining_size)

    def test_init_task(self):
        sol = Solution(self.instance)

        self.assertEqual([0, 1, 2, 3, 4, 5, 6, 7], [t.id for t in sol.tasks])

        for i in [0, 1, 2, 3, 4, 5, 6, 7]:
            self.assertEqual(self.job.id, sol.tasks[i].job_id)

    def test_init_time(self):
        service_and_stop_time = 1 + 3  # stop time + service time
        for current_time, arrival_time in [(0, 38), (40, 45)]:  # cum_time = arrival time at the first not executed task
            self.instance.plan.current_time = current_time
            sol = Solution(self.instance)
            self.assertEqual(list(self.instance.tasks.keys()), [t.id for t in sol.tasks])

            # Already completed task
            self.assertEqual(0, sol.tasks[0].arrival_time)
            self.assertEqual(4, sol.tasks[0].departure_time)
            self.assertEqual(9, sol.tasks[2].arrival_time)
            self.assertEqual(13, sol.tasks[2].departure_time)
            self.assertEqual(18, sol.tasks[1].arrival_time)
            self.assertEqual(22, sol.tasks[1].departure_time)
            self.assertEqual(29, sol.tasks[4].arrival_time)
            self.assertEqual(33, sol.tasks[4].departure_time)

            # Future tasks
            self.assertEqual(arrival_time, sol.tasks[6].arrival_time)
            self.assertEqual(arrival_time + service_and_stop_time, sol.tasks[6].departure_time)

            arrival_time += service_and_stop_time + 5  # stop time + service time + travel time
            self.assertEqual(arrival_time, sol.tasks[3].arrival_time)
            self.assertEqual(arrival_time + service_and_stop_time, sol.tasks[3].departure_time)

            arrival_time += service_and_stop_time + 5  # stop time + service time + travel time
            self.assertEqual(arrival_time, sol.tasks[7].arrival_time)
            self.assertEqual(arrival_time + service_and_stop_time, sol.tasks[7].departure_time)

            arrival_time += service_and_stop_time + 5  # stop time + service time + travel time
            self.assertEqual(arrival_time, sol.tasks[5].arrival_time)
            self.assertEqual(arrival_time + service_and_stop_time, sol.tasks[5].departure_time)

    def test_init_cum_weight(self):
        sol = Solution(self.instance)

        self.assertEqual(0, sol.tasks[0].cum_weight)
        self.assertEqual(10, sol.tasks[1].cum_weight)
        self.assertEqual(5, sol.tasks[2].cum_weight)
        self.assertEqual(15, sol.tasks[3].cum_weight)
        self.assertEqual(5, sol.tasks[4].cum_weight)
        self.assertEqual(5, sol.tasks[5].cum_weight)
        self.assertEqual(10, sol.tasks[6].cum_weight)
        self.assertEqual(10, sol.tasks[7].cum_weight)

    def test_init_cum_volume(self):
        sol = Solution(self.instance)

        self.assertEqual(0, sol.tasks[0].cum_volume)
        self.assertEqual(6, sol.tasks[1].cum_volume)
        self.assertEqual(3, sol.tasks[2].cum_volume)
        self.assertEqual(9, sol.tasks[3].cum_volume)
        self.assertEqual(3, sol.tasks[4].cum_volume)
        self.assertEqual(3, sol.tasks[5].cum_volume)
        self.assertEqual(6, sol.tasks[6].cum_volume)
        self.assertEqual(6, sol.tasks[7].cum_volume)

    def test_init_task_position(self):
        sol = Solution(self.instance)

        self.assertEqual(0, sol.tasks[0].position)
        self.assertEqual(2, sol.tasks[1].position)
        self.assertEqual(1, sol.tasks[2].position)
        self.assertEqual(5, sol.tasks[3].position)
        self.assertEqual(3, sol.tasks[4].position)
        self.assertEqual(7, sol.tasks[5].position)
        self.assertEqual(4, sol.tasks[6].position)
        self.assertEqual(6, sol.tasks[7].position)

    def test_init_delivery_group(self):
        self.instance.create_delivery_group(0)
        self.instance.create_delivery_group(1, 2, 3)
        self.instance.create_delivery_group()

        sol = Solution(self.instance)

        self.assertEqual(0, sol.delivery_group_job[0])
        self.assertEqual(0, sol.delivery_group_job[1])
        self.assertEqual(NONE_JOB, sol.delivery_group_job[2])
        self.assertEqual(2, sol.jobs[0].delivery_group_size[0])
        self.assertEqual(6, sol.jobs[0].delivery_group_size[1])
        self.assertEqual(0, sol.jobs[0].delivery_group_size[2])
