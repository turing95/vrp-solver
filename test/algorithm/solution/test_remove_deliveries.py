from unittest import TestCase
from array import array

from routing.algorithm.solution import Solution
from test.fixtures.instance_with_state import create_test_instance
from routing.entity.constant import NONE_POSITION, NONE_JOB, NONE_DELIVERY_GROUP


class TestRemoveDeliveries(TestCase):

    def setUp(self):
        self.instance = create_test_instance()

        # set up a job
        self.job = self.instance.plan.jobs[0]
        self.job.task_ids = [0, 2, 1, 4, 6, 3, 7, 5]  # 4 is the executing task

        # set up the solution
        self.sol = Solution(self.instance)

    def test_update_job(self):
        """
        Remove a single delivery with both pickup and dropoff to be completed
        """
        self.sol.remove_deliveries(self.job.id, [3])
        self.assertEqual([0, 2, 1, 4, 3, 5], list(self.sol.jobs[0].task_ids))

        self.assertEqual(array('i', [3]), self.sol.not_completed_deliveries)

        # Removed task
        self.assertEqual(NONE_JOB, self.sol.tasks[6].job_id)
        self.assertEqual(NONE_JOB, self.sol.tasks[7].job_id)

        # Remaining task 0
        self.assertEqual(0, self.sol.tasks[0].job_id)
        self.assertEqual(0, self.sol.tasks[1].job_id)
        self.assertEqual(0, self.sol.tasks[2].job_id)
        self.assertEqual(0, self.sol.tasks[3].job_id)
        self.assertEqual(0, self.sol.tasks[4].job_id)
        self.assertEqual(0, self.sol.tasks[5].job_id)

    def test_update_position(self):
        """
        Remove a single delivery with both pickup and dropoff to be completed
        """
        self.sol.remove_deliveries(self.job.id, [3])
        self.assertEqual([0, 2, 1, 4, 3, 5], list(self.sol.jobs[0].task_ids))

        self.assertEqual(array('i', [3]), self.sol.not_completed_deliveries)

        # Removed task
        self.assertEqual(NONE_POSITION, self.sol.tasks[6].position)
        self.assertEqual(NONE_POSITION, self.sol.tasks[7].position)

        # Remaining task 0
        self.assertEqual(0, self.sol.tasks[0].position)
        self.assertEqual(2, self.sol.tasks[1].position)
        self.assertEqual(1, self.sol.tasks[2].position)
        self.assertEqual(4, self.sol.tasks[3].position)
        self.assertEqual(3, self.sol.tasks[4].position)
        self.assertEqual(5, self.sol.tasks[5].position)

    def test_update_arrival_time(self):
        """
        Remove a single delivery with both pickup and dropoff to be completed
        """
        self.sol.remove_deliveries(self.job.id, [3])
        self.assertEqual([0, 2, 1, 4, 3, 5], list(self.sol.jobs[0].task_ids))

        self.assertEqual(array('i', [3]), self.sol.not_completed_deliveries)

        # Remaining task 0
        self.assertEqual(0, self.sol.tasks[0].arrival_time)
        self.assertEqual(18, self.sol.tasks[1].arrival_time)
        self.assertEqual(9, self.sol.tasks[2].arrival_time)
        self.assertEqual(43, self.sol.tasks[3].arrival_time)
        self.assertEqual(29, self.sol.tasks[4].arrival_time)
        self.assertEqual(57, self.sol.tasks[5].arrival_time)

    def test_update_cum_weight(self):
        """
        Remove a single delivery with both pickup and dropoff to be completed
        """
        self.sol.remove_deliveries(self.job.id, [3])
        self.assertEqual([0, 2, 1, 4, 3, 5], list(self.sol.jobs[0].task_ids))

        self.assertEqual(array('i', [3]), self.sol.not_completed_deliveries)

        # Remaining task 0
        self.assertEqual(0, self.sol.tasks[0].cum_weight)
        self.assertEqual(10, self.sol.tasks[1].cum_weight)
        self.assertEqual(5, self.sol.tasks[2].cum_weight)
        self.assertEqual(10, self.sol.tasks[3].cum_weight)
        self.assertEqual(5, self.sol.tasks[4].cum_weight)
        self.assertEqual(5, self.sol.tasks[5].cum_weight)

    def test_update_cum_volume(self):
        """
        Remove a single delivery with both pickup and dropoff to be completed
        """
        self.sol.remove_deliveries(self.job.id, [3])
        self.assertEqual([0, 2, 1, 4, 3, 5], list(self.sol.jobs[0].task_ids))

        self.assertEqual(array('i', [3]), self.sol.not_completed_deliveries)

        # Remaining task 0
        self.assertEqual(0, self.sol.tasks[0].cum_volume)
        self.assertEqual(6, self.sol.tasks[1].cum_volume)
        self.assertEqual(3, self.sol.tasks[2].cum_volume)
        self.assertEqual(6, self.sol.tasks[3].cum_volume)
        self.assertEqual(3, self.sol.tasks[4].cum_volume)
        self.assertEqual(3, self.sol.tasks[5].cum_volume)

    def test_update_group_data(self):
        """
        Remove a delivery that belongs to a group of delivery
        """
        # Create a delivery group for the delivery 1 and 3
        self.instance.create_delivery_group(3)
        sol = Solution(self.instance)

        sol.remove_deliveries(0, [3])

        self.assertEqual(NONE_DELIVERY_GROUP, sol.delivery_group_job[0])
        self.assertEqual(0, sol.jobs[0].delivery_group_size[0])

    def test_works_with_partial_deliveries(self):
        """
        Remove a delivery with both pickup and dropoff to be executed and a partially executed delivery
        """
        self.sol.remove_deliveries(self.job.id, [1, 3])
        self.assertEqual([0, 2, 1, 4, 5], list(self.sol.jobs[0].task_ids))

        self.assertEqual(array('i', [1, 3]), self.sol.not_completed_deliveries)

        self.assertEqual(NONE_JOB, self.sol.tasks[6].job_id)
        self.assertEqual(NONE_POSITION, self.sol.tasks[6].position)
        self.assertEqual(NONE_JOB, self.sol.tasks[7].job_id)
        self.assertEqual(NONE_POSITION, self.sol.tasks[7].position)
        self.assertEqual(0, self.sol.tasks[2].job_id)
        self.assertEqual(1, self.sol.tasks[2].position)
        self.assertEqual(NONE_JOB, self.sol.tasks[3].job_id)
        self.assertEqual(NONE_POSITION, self.sol.tasks[3].position)
