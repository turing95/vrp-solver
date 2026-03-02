from unittest import TestCase

from routing.algorithm.solution import Solution
from routing.algorithm.insertion import Insertion
from test.fixtures.instance_with_state import create_test_instance
from routing.entity.constant import NONE_JOB, NONE_DELIVERY_GROUP


class TestApplyInsertion(TestCase):

    def setUp(self):
        self.instance = create_test_instance()

        # Create a delivery group for the delivery 0
        self.instance.create_delivery_group(0)

        # set up a job
        self.job = self.instance.plan.jobs[0]
        self.job.task_ids = [2, 4, 3, 5]

        # set up the solution
        self.sol = Solution(self.instance)

        # set up an insertion of both pickup and dropoff
        self.complete_insertion = Insertion(self.sol.delivery_drop_penalty[0])
        self.complete_insertion.setup(0, self.sol.delivery_drop_penalty[0])
        self.complete_insertion.job_id = 0
        self.complete_insertion.pickup_pos = 0
        self.complete_insertion.dropoff_pos = 4

    def test_case_1(self):
        """
        Insert the pickup at the beginning of the job and the dropoff at the end.
        """
        self.sol.apply_insertion(self.complete_insertion)
        self.assertEqual([0, 2, 4, 3, 5, 1], list(self.sol.jobs[0].task_ids))

    def test_case_2(self):
        """
        Insert the pickup in the same position .
        """
        self.complete_insertion.pickup_pos = 2
        self.complete_insertion.dropoff_pos = 2
        self.sol.apply_insertion(self.complete_insertion)
        self.assertEqual([2, 4, 0, 1, 3, 5], list(self.sol.jobs[0].task_ids))

    def test_case_3(self):
        """
        Insert the pickup and dropoff separated by one task.
        """
        self.complete_insertion.pickup_pos = 2
        self.complete_insertion.dropoff_pos = 3
        self.sol.apply_insertion(self.complete_insertion)
        self.assertEqual([2, 4, 0, 3, 1, 5], list(self.sol.jobs[0].task_ids))

    def test_correctly_set_job(self):
        # preconditions
        self.assertEqual(NONE_JOB, self.sol.tasks[0].job_id)
        self.assertEqual(NONE_JOB, self.sol.tasks[1].job_id)

        self.sol.apply_insertion(self.complete_insertion)

        # job is correctly set
        self.assertEqual(0, self.sol.tasks[0].job_id)
        self.assertEqual(0, self.sol.tasks[1].job_id)

    def test_correctly_update_delivery_group(self):
        # preconditions
        self.assertEqual(NONE_DELIVERY_GROUP, self.sol.delivery_group_job[0])
        self.assertEqual(0, self.sol.jobs[0].delivery_group_size[0])

        self.sol.apply_insertion(self.complete_insertion)

        # delivery group are correctly updated
        self.assertEqual(0, self.sol.delivery_group_job[0])
        self.assertEqual(2, self.sol.jobs[0].delivery_group_size[0])
