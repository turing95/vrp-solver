from unittest import TestCase

from routing.entity.error import UnexpectedTaskId, UnexpectedJobId
from routing.entity.job import Job
from test.fixtures.instance_with_state import create_test_instance
from routing.entity.constant import NONE_TASK


class TestPlan(TestCase):

    def setUp(self):
        self.instance = create_test_instance()
        self.plan = self.instance.plan

        self.job_data = {"vehicle_id": 0, "task_ids": []}

    def test_create_job(self):
        job = self.plan.create_job(**self.job_data)

        self.assertIs(type(job), Job)
        self.assertEqual(self.plan.get_job_count() - 1, job.id)
        self.assertEqual(0, job.vehicle_id)
        self.assertEqual([], job.task_ids)

    def test_sequential_job_id(self):
        next_index = self.plan.get_job_count()
        for i in range(next_index, next_index+10):
            job = self.plan.create_job(**self.job_data)
            self.assertEqual(i, job.id)

    def test_set_tasks(self):
        self.plan.set_tasks(0, [(0, 0, 4), (2, 10, 14), (1, 20, 24), (4, 30, 34), (5, 40, 44), (6, 50, 54)])
        self.assertEqual([0, 2, 1, 4, 5, 6], self.plan.jobs[0].task_ids)
        # Arrival time
        self.assertEqual(self.plan.arrival_time[0], 0)
        self.assertEqual(self.plan.arrival_time[2], 10)
        self.assertEqual(self.plan.arrival_time[1], 20)
        self.assertEqual(self.plan.arrival_time[4], 30)
        self.assertEqual(self.plan.arrival_time[5], 40)
        self.assertEqual(self.plan.arrival_time[6], 50)
        # Departure time
        self.assertEqual(self.plan.departure_time[0], 4)
        self.assertEqual(self.plan.departure_time[2], 14)
        self.assertEqual(self.plan.departure_time[1], 24)
        self.assertEqual(self.plan.departure_time[4], 34)
        self.assertEqual(self.plan.departure_time[5], 44)
        self.assertEqual(self.plan.departure_time[6], 54)

    def test_set_tasks_with_not_valid_task(self):
        self.assertRaises(UnexpectedTaskId, lambda: self.plan.set_tasks(0, [(0, 0, 4), (1, 10, 14), (2, 20, 24), (3, 30, 34), (100, 40, 44)]))

    def test_set_tasks_with_duplicated_task(self):
        self.assertRaises(UnexpectedTaskId, lambda: self.plan.set_tasks(0, [(0, 0, 4), (2, 10, 14), (1, 20, 24)]))

    def test_set_tasks_that_remove_executing_task(self):
        self.assertRaises(UnexpectedTaskId, lambda: self.plan.set_tasks(0, [(0, 0, 4), (2, 10, 14), (1, 20, 24)]))

    def test_set_tasks_remove_task_if_in_other_jobs(self):
        self.plan.set_tasks(0, [(0, 0, 4), (2, 10, 14), (1, 20, 24), (4, 30, 34), (5, 40, 44), (6, 50, 54)])
        self.assertEqual([0, 2, 1, 4, 5, 6], self.plan.jobs[0].task_ids)

        self.plan.set_tasks(0, [(0, 0, 4), (2, 10, 14), (1, 20, 24), (4, 30, 34), (6, 50, 54)])
        self.assertEqual([0, 2, 1, 4, 6], self.plan.jobs[0].task_ids)

    def test_set_task_arrival_time(self):
        self.plan.set_task_arrival_time(0, 1, 30)
        self.assertEqual(30, self.plan.arrival_time[1])

    def test_set_task_arrival_time_without_valid_task(self):
        self.assertRaises(UnexpectedTaskId, lambda: self.plan.set_task_arrival_time(0, 100, 30))

    def test_set_task_arrival_time_without_valid_job(self):
        self.assertRaises(UnexpectedJobId, lambda: self.plan.set_task_arrival_time(1, 1, 30))

    def test_set_task_arrival_time_without_valid_job_task_pair(self):
        self.assertRaises(UnexpectedTaskId, lambda: self.plan.set_task_arrival_time(0, 5, 30))

    def test_set_task_departure_time(self):
        self.plan.set_task_departure_time(0, 1, 30)
        self.assertEqual(30, self.plan.departure_time[1])

    def test_set_task_departure_time_without_valid_task(self):
        self.assertRaises(UnexpectedTaskId, lambda: self.plan.set_task_departure_time(0, 100, 30))

    def test_set_task_departure_time_without_valid_job(self):
        self.assertRaises(UnexpectedJobId, lambda: self.plan.set_task_departure_time(1, 1, 30))

    def test_set_task_departure_time_without_valid_job_task_pair(self):
        self.assertRaises(UnexpectedTaskId, lambda: self.plan.set_task_departure_time(0, 5, 30))

    def test_set_executing_task(self):
        self.plan.set_tasks(0, [(0, 0, 4), (2, 10, 14), (1, 20, 24), (4, 30, 34), (5, 40, 44), (6, 50, 54)])
        self.plan.set_executing_task(0, 5)
        self.assertEqual(5, self.plan.executing_task[0])
        self.assertEqual(40, self.plan.arrival_time[5])

    def test_set_executing_task_without_valid_task(self):
        self.assertRaises(UnexpectedTaskId, lambda: self.plan.set_executing_task(0, 100))

    def test_set_executing_task_without_valid_job(self):
        self.assertRaises(UnexpectedJobId, lambda: self.plan.set_executing_task(1, 4))

    def test_set_executing_task_without_valid_job_task_pair(self):
        self.plan.set_tasks(0, [(0, 10, 13), (2, 20, 24), (1, 30, 34), (4, 40, 44), (5, 50, 54)])
        self.assertRaises(UnexpectedTaskId, lambda: self.plan.set_task_arrival_time(0, 6, 30))

    def test_set_current_time(self):
        self.plan.set_current_time(40)
        self.assertEqual(40, self.plan.current_time)

    def test_set_current_time_with_invalid_data(self):
        self.assertRaises(ValueError, lambda: self.plan.set_current_time(-1))

    def test_set_current_time_and_executing_task_case_0(self):
        """job is not yet started"""
        self.plan.set_task_arrival_time(0, 0, 2)
        self.plan.set_current_time(1, set_executing_task=True)
        self.assertEqual(NONE_TASK, self.plan.executing_task[0])

    def test_set_current_time_and_executing_task_case_1(self):
        """Executing task in the middle of the job"""
        self.plan.set_current_time(10, set_executing_task=True)
        self.assertEqual(1, self.plan.executing_task[0])

    def test_set_current_time_and_executing_task_case_2(self):
        """Executing task is the last task"""
        self.plan.set_tasks(0, [(0, 0, 4), (2, 20, 24), (1, 30, 34), (4, 40, 44), (5, 50, 54)])
        self.plan.set_current_time(51, set_executing_task=True)
        self.assertEqual(5, self.plan.executing_task[0])

    def test_set_current_time_and_executing_task_case_3(self):
        """Executing task is the last task and expected departure is smaller than current time"""
        self.plan.set_tasks(0, [(0, 0, 4), (2, 20, 24), (1, 30, 34), (4, 40, 44), (5, 50, 54)])
        self.plan.set_current_time(100, set_executing_task=True)
        self.assertEqual(5, self.plan.executing_task[0])
        self.assertEqual(100, self.plan.departure_time[5])

    def test_is_task_executed_case_0(self):
        """There is an executing task and so some tasks are executed and some not"""
        self.plan.set_tasks(0, [(0, 0, 4), (2, 20, 24), (1, 30, 34), (4, 40, 44), (5, 50, 54)])
        self.plan.set_executing_task(0, 1)

        self.assertTrue(self.plan.is_task_executed(0))
        self.assertTrue(self.plan.is_task_executed(2))
        self.assertTrue(self.plan.is_task_executed(1))
        self.assertFalse(self.plan.is_task_executed(4))
        self.assertFalse(self.plan.is_task_executed(5))
        self.assertFalse(self.plan.is_task_executed(3))

    def test_is_task_executed_case_1(self):
        """There is no executing task so all the task are not executed"""
        self.plan.set_tasks(0, [(0, 0, 4), (2, 20, 24), (1, 30, 34), (4, 40, 44), (5, 50, 54)])
        self.plan.executing_task[0] = NONE_TASK

        self.assertFalse(self.plan.is_task_executed(0))
        self.assertFalse(self.plan.is_task_executed(2))
        self.assertFalse(self.plan.is_task_executed(1))
        self.assertFalse(self.plan.is_task_executed(4))
        self.assertFalse(self.plan.is_task_executed(5))
        self.assertFalse(self.plan.is_task_executed(3))
