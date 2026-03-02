from unittest import TestCase

from routing.algorithm.solution import Solution
from routing.algorithm.insertion import Insertion
from test.fixtures.instance_with_state import create_test_instance
from routing.entity.constant import NONE_POSITION, NONE_JOB


class TestApplyInsertion(TestCase):

    def setUp(self):
        self.instance = create_test_instance()

        # Create a delivery group for the delivery 0
        self.instance.create_delivery_group(0)

        # set up a job
        self.job = self.instance.plan.jobs[0]
        self.job.task_ids = [0, 2, 4, 3, 5]

        # set up the solution
        self.sol = Solution(self.instance)

        # set up a partial insertion of the only dropoff (like if the pickup was already processed)
        self.partial_insertion = Insertion(self.sol.delivery_drop_penalty[0])
        self.partial_insertion.setup(0, self.sol.delivery_drop_penalty[0])
        self.partial_insertion.job_id = 0
        self.partial_insertion.pickup_pos = NONE_POSITION
        self.partial_insertion.dropoff_pos = 5

    def test_case_1(self):
        """
        Dropoff at the end.
        """
        self.sol.apply_insertion(self.partial_insertion)
        self.assertEqual([0, 2, 4, 3, 5, 1], list(self.sol.jobs[0].task_ids))

    def test_case_2(self):
        """
        Dropoff right after the pickup
        """
        self.partial_insertion.dropoff_pos = 1
        self.sol.apply_insertion(self.partial_insertion)
        self.assertEqual([0, 1, 2, 4, 3, 5], list(self.sol.jobs[0].task_ids))

    def test_case_3(self):
        """
        Dropoff in the middle
        """
        self.partial_insertion.dropoff_pos = 3
        self.sol.apply_insertion(self.partial_insertion)
        self.assertEqual([0, 2, 4, 1, 3, 5], list(self.sol.jobs[0].task_ids))

    def test_correctly_set_job(self):
        # preconditions
        self.assertEqual(NONE_JOB, self.sol.tasks[1].job_id)

        self.sol.apply_insertion(self.partial_insertion)

        # job is correctly set
        self.assertEqual(0, self.sol.tasks[1].job_id)

    def test_correctly_update_delivery_group(self):
        # preconditions
        self.assertEqual(0, self.sol.delivery_group_job[0])
        self.assertEqual(1, self.sol.jobs[0].delivery_group_size[0])

        self.sol.apply_insertion(self.partial_insertion)

        # delivery group are correctly updated
        self.assertEqual(0, self.sol.delivery_group_job[0])
        self.assertEqual(2, self.sol.jobs[0].delivery_group_size[0])

