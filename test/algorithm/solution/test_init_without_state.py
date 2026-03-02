from unittest import TestCase

from routing.algorithm.solution import Solution
from test.fixtures.instance_without_state import create_test_instance
from routing.entity.constant import NONE_POSITION, NONE_JOB


class TestInitWithoutState(TestCase):

    def setUp(self):
        self.instance = create_test_instance()
        self.job = self.instance.plan.jobs[0]

        # Set up a plan
        self.job.task_ids = [2, 4, 3, 5]

    def test_init_incomplete_deliveries(self):
        sol = Solution(self.instance)

        # Incomplete Deliveries
        self.assertEqual(1, len(sol.not_completed_deliveries))
        self.assertTrue(0 in sol.not_completed_deliveries)

    def test_init_best_insertion(self):
        sol = Solution(self.instance)

        # Best insertion
        self.assertEqual(101, sol.best_insertion.cost)
        self.assertEqual(NONE_POSITION, sol.best_insertion.pickup_pos)
        self.assertEqual(NONE_POSITION, sol.best_insertion.dropoff_pos)
        self.assertEqual(NONE_POSITION, sol.best_insertion.job_id)

    def test_init_job(self):
        sol = Solution(self.instance)
        job_id = self.job.id

        self.assertEqual([job_id], [j.id for j in sol.jobs])

        # Job are cloned but the reference is different
        self.assertEqual(self.job.task_ids, list(sol.jobs[job_id].task_ids))
        self.assertFalse(self.job.task_ids is sol.jobs[job_id].task_ids)

        # Initialize the job with the correct vehicle
        self.assertTrue(self.job.vehicle_id == sol.jobs[job_id].vehicle_id)

        # Initialize the job with the correct cost
        self.assertEqual(
            (
                15 * 3   # distance
                + 4 * 2  # stop
                + 0 * 5  # tw penalty
            ),
            sol.jobs[job_id].cost)

        # Initialize the job with the correct remaining task size value
        self.assertEqual(4, sol.jobs[0].remaining_size)

    def test_init_task(self):
        sol = Solution(self.instance)

        self.assertEqual([0, 1, 2, 3, 4, 5], list([t.id for t in sol.tasks]))

        self.assertEqual(NONE_JOB, sol.tasks[0].job_id)
        self.assertEqual(NONE_JOB, sol.tasks[1].job_id)
        self.assertEqual(self.job.id, sol.tasks[2].job_id)
        self.assertEqual(self.job.id, sol.tasks[3].job_id)
        self.assertEqual(self.job.id, sol.tasks[4].job_id)
        self.assertEqual(self.job.id, sol.tasks[5].job_id)

    def test_init_time(self):
        sol = Solution(self.instance)
        self.assertEqual(list(self.instance.tasks.keys()), [t.id for t in sol.tasks])

        cum_time = 0
        stop_and_service_time = 1 + 3
        self.assertEqual(cum_time, sol.tasks[2].arrival_time)
        self.assertEqual(cum_time + stop_and_service_time, sol.tasks[2].departure_time)

        cum_time += stop_and_service_time + 5  # stop time + service time + travel time
        self.assertEqual(cum_time, sol.tasks[4].arrival_time)
        self.assertEqual(cum_time + stop_and_service_time, sol.tasks[4].departure_time)

        cum_time += 1 + 3 + 5  # stop time + service time + travel time
        self.assertEqual(cum_time, sol.tasks[3].arrival_time)
        self.assertEqual(cum_time + stop_and_service_time, sol.tasks[3].departure_time)

        cum_time += 1 + 3 + 5  # stop time + service time + travel time
        self.assertEqual(cum_time, sol.tasks[5].arrival_time)
        self.assertEqual(cum_time + stop_and_service_time, sol.tasks[5].departure_time)

    def test_init_time_with_current_time(self):
        self.instance.plan.current_time = 10
        sol = Solution(self.instance)
        self.assertEqual(list(self.instance.tasks.keys()), [t.id for t in sol.tasks])

        cum_time = 10
        stop_and_service_time = 1 + 3
        self.assertEqual(cum_time, sol.tasks[2].arrival_time)
        self.assertEqual(cum_time + stop_and_service_time, sol.tasks[2].departure_time)

        cum_time += stop_and_service_time + 5  # stop time + service time + travel time
        self.assertEqual(cum_time, sol.tasks[4].arrival_time)
        self.assertEqual(cum_time + stop_and_service_time, sol.tasks[4].departure_time)

        cum_time += 1 + 3 + 5  # stop time + service time + travel time
        self.assertEqual(cum_time, sol.tasks[3].arrival_time)
        self.assertEqual(cum_time + stop_and_service_time, sol.tasks[3].departure_time)

        cum_time += 1 + 3 + 5  # stop time + service time + travel time
        self.assertEqual(cum_time, sol.tasks[5].arrival_time)
        self.assertEqual(cum_time + stop_and_service_time, sol.tasks[5].departure_time)

    def test_init_cum_weight(self):
        sol = Solution(self.instance)

        self.assertEqual(0, sol.tasks[2].cum_weight)
        self.assertEqual(5, sol.tasks[4].cum_weight)
        self.assertEqual(10, sol.tasks[3].cum_weight)
        self.assertEqual(5, sol.tasks[5].cum_weight)

    def test_init_cum_volume(self):
        sol = Solution(self.instance)

        self.assertEqual(0, sol.tasks[2].cum_volume)
        self.assertEqual(3, sol.tasks[4].cum_volume)
        self.assertEqual(6, sol.tasks[3].cum_volume)
        self.assertEqual(3, sol.tasks[5].cum_volume)

    def test_init_task_position(self):
        sol = Solution(self.instance)

        self.assertEqual(NONE_POSITION, sol.tasks[0].position)
        self.assertEqual(NONE_POSITION, sol.tasks[1].position)
        self.assertEqual(0, sol.tasks[2].position)
        self.assertEqual(1, sol.tasks[4].position)
        self.assertEqual(2, sol.tasks[3].position)
        self.assertEqual(3, sol.tasks[5].position)

    def test_init_delivery_group(self):
        self.instance.create_delivery_group(0, 1)
        self.instance.create_delivery_group(2)

        self.instance.plan.jobs[0].task_ids = [0, 2, 4, 3, 5, 1]

        sol = Solution(self.instance)

        self.assertEqual(0, sol.delivery_group_job[0])
        self.assertEqual(0, sol.delivery_group_job[1])
        self.assertEqual(4, sol.jobs[0].delivery_group_size[0])
        self.assertEqual(2, sol.jobs[0].delivery_group_size[1])
