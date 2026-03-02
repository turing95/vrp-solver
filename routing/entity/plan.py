from routing.entity.job import Job
from routing.entity.utils import IdGenerator, validate_int
from routing.entity.error import UnexpectedTaskId, UnexpectedJobId, ValidationError
from routing.entity.constant import NONE_TASK, NONE_TIME

from typing import Tuple, List


class Plan(object):
    """
    The main class to represent the delivery plan and its progress.

    A plan is composed by a collection of jobs, one for each vehicle in the instance.
    Each job has an ordered sequence (potentially empty) of tasks already completed,
    to be executed or in execution. Each task is identified by its id.

    To keep trak of the progress of each job, the plan keeps track of:
    - the executing task associated with each job. It is NONE_TASK if the job is not started,
    - the arrival time of each task in the jobs,
    - the current time

    The arrival time can represent either the real arrival time, for the completed task
    (i.e. those before the executing task) or the expected arrival time for the executing
    task and for the tasks not executed.

    The arrival time is always defined (not None) for the tasks assigned to a job.
    """

    def __init__(self, instance, current_time):
        """
        Initialize an empty plan with no job.
        The current time is initialized to zero by default.

        Args:
            instance: a routing.entity.instance.Instance
        """
        self.instance = instance

        # Plan state
        self.current_time = validate_int(current_time, attr="current time", non_negative=True)
        self.jobs = {}
        self._job_id_generator = IdGenerator(0)

        # Jobs state
        self.executing_task = {}

        # Tasks state
        self.arrival_time = {}
        self.departure_time = {}

    def create_job(self, **kwargs):
        """
        Create and return a new job

        Args:
            **kwargs: See `routing.entity.job.Job` for the list of accepted attributes.

        Returns: the created job
        """
        job_id = self._job_id_generator.look_ahead()
        if 'id' in kwargs:
            given_id = kwargs.pop('id')
            if not given_id == job_id:
                raise ValidationError(f"Job id {given_id} is not valid. Expected sequential job ids.")

        j = Job(id=job_id, plan=self, **kwargs)
        self._job_id_generator.next_id()
        self.jobs[j.id] = j
        return j

    def get_job_count(self):
        """
        Get the number of job in the plan

        Returns: the number of job in the plan
        """
        return len(self.jobs.items())

    def init_job_state(self, job_id):
        """
        Initialize the job state (set the executing task to NONE_TASK)

        Args:
            job_id: the id of the job to initialize
        """
        self.executing_task[job_id] = NONE_TASK

    def init_task_state(self, task_id):
        """
        Initialize the task state (set the arrival time to 0)

        Args:
            task_id: the id of the task to initialize
        """
        self.arrival_time[task_id] = 0
        self.departure_time[task_id] = NONE_TIME

    def set_tasks(self, job_id: int, route: List[Tuple[int, int, int]]):
        """
        Given a route i.e. a list of pair (task_id, arrival_time, departure_time), set the sequence
        of tasks associated with the given job and set the (expected or actual) arrival time
        and the (expected or actual) departure time associated with each task.

        Raises an exception if a given task doesn't exist or if the executing
        task associated with the job is not in the given sequence of task.

        If a task is already in another job move it from the old job to the given job.

        Args:
            job_id: the id of the job
            route: an ordered collection of tuple (task_id, arrival_time, departure_time)
        """
        # Validate input
        self._validate_job_id(job_id)
        for task_id, arrival_time, departure_time in route:
            self._validate_task_id(task_id)
            if arrival_time is not None and arrival_time != NONE_TIME:
                self._validate_arrival_time(arrival_time)
            if departure_time is not None and departure_time != NONE_TIME:
                self._validate_departure_time(departure_time)

        task_ids = [r[0] for r in route]
        task_ids_set = set(task_ids)

        # Remove the task from the other jobs
        for j in self.jobs.values():
            j.task_ids = [t_id for t_id in j.task_ids if t_id not in task_ids_set]

        # Assign the task to the job and update the arrival time
        self.jobs[job_id].task_ids = task_ids
        for task_id, arrival_time, departure_time in route:
            if arrival_time is not None and arrival_time != NONE_TIME:
                self.arrival_time[task_id] = arrival_time
            if departure_time is not None and departure_time != NONE_TIME:
                self.departure_time[task_id] = departure_time

        self._validate_job(job_id)

    def set_task_arrival_time(self, job_id, task_id, arrival_time):
        """
        Set the arrival time of the given task.

        Args:
            job_id: the job id serving the given task
            task_id: the task id for which we want to update the arrival time
            arrival_time: the (expected) arrival time

        """
        self._validate_job_id(job_id)
        self._validate_job_task_id(job_id, task_id)
        self._validate_arrival_time(arrival_time)

        self.arrival_time[task_id] = arrival_time

    def set_task_departure_time(self, job_id, task_id, departure_time):
        """
        Set the departure time from a task.

        Args:
            job_id: the job id serving the given task
            task_id: the task id for which we want to update the arrival time
            departure_time: the (actual) departure time

        """
        self._validate_job_id(job_id)
        self._validate_job_task_id(job_id, task_id)
        self._validate_departure_time(departure_time)

        self.departure_time[task_id] = departure_time

    def set_executing_task(self, job_id, task_id):
        """
        Set the new executing task for a job.
        Check that the executing task has a defined arrival time and departure time

        Args:
            job_id: the job id
            task_id: the new executing task
        """
        self._validate_job_id(job_id)
        self._validate_job_task_id(job_id, task_id)
        self._validate_arrival_time(self.arrival_time[task_id])
        self._validate_departure_time(self.departure_time[task_id])

        self.executing_task[job_id] = task_id

    def set_current_time(self, current_time, set_executing_task=False, update_departure_time=True):
        """
        Set the current time and optionally find the executing task.

        A task t is marked as executing if:
        - task t-1 arrival_time < current_time <= task t arrival_time, or
        - t is the last task and task t < current_time

        It follows that the first task can never be set as the executing task by this function.

        Args:
            current_time: the new current time
            set_executing_task: if True then automatically find and set the executing task of all the jobs.
            update_departure_time: if True (default) then update the departure time of all the executing tasks
                that are also the last task in the route to max(departure_time, current_time). This way we handle
                executing tasks that have been completed but which vehicle is waiting for future tasks.
        """
        validate_int(current_time, attr="current time", non_negative=True)
        self.current_time = current_time

        if set_executing_task:
            for j in self.jobs.values():
                # Find new executing task
                self.executing_task[j.id] = NONE_TASK
                for prev_t_id, t_id in zip(j.task_ids[:-1], j.task_ids[1:]):
                    if self.arrival_time[prev_t_id] < current_time <= self.arrival_time[t_id]:
                        self.set_executing_task(j.id, t_id)
                        break
                    if t_id == j.task_ids[-1] and current_time > self.arrival_time[t_id]:
                        self.set_executing_task(j.id, t_id)

                        # Check if the executing task was also completed and set the departure time
                        task = self.instance.tasks[t_id]
                        vehicle_type = self.instance.vehicle_types[self.instance.vehicles[j.vehicle_id].vehicle_type_id]
                        if current_time > self.arrival_time[t_id] + task.service_time + vehicle_type.stop_time:
                            self.departure_time[self.executing_task[j.id]] = current_time

        if update_departure_time:
            for j in self.jobs.values():
                executing_task = self.executing_task[j.id]
                # Update departure time
                if executing_task != NONE_TASK and executing_task == j.task_ids[-1]:
                    # update if departure was already present (otherwise the task might not be completed)
                    if self.departure_time[executing_task] != NONE_TIME:
                        self.departure_time[executing_task] = max(current_time, self.departure_time[executing_task])

    def not_completed_tasks(self):
        """
        Get all the task that does not belong to any job.

        Returns: a set of task ids that do not appear in any job
        """
        tasks_set = set(self.instance.tasks.keys())
        for job in self.jobs.values():
            tasks_set -= set(job.task_ids)
        return tasks_set

    def is_task_executed(self, task_id):
        """
        Check if a task is already executed and cannot be planned i.e. it is assigned to a job
        and its position is before the executing task.

        Returns: true when the task is already executed, false otherwise
        """
        for job in self.jobs.values():
            executing_task_id = self.executing_task[job.id]
            if (
                    # The job has an executing task
                    executing_task_id != NONE_TASK
                    # The task belong to the job
                    and task_id in set(job.task_ids)
                    # the task is before or is the executing task
                    and job.task_ids.index(task_id) <= job.task_ids.index(executing_task_id)
            ):
                return True
        return False

    def compute_task_time(self, job_id, task_id):
        """
        Compute the expected arrival time and the expected departure time of a given task.

        The expected arrival time is computed as expected departure time of the previous task + travel time.
        The expected departure time is computed based as the expected arrival time + the stop time + the service time.

        Returns: a pair (expected arrival time, expected departure time)
        """
        self._validate_job_id(job_id)
        self._validate_job_task_id(job_id, task_id)

        job = self.jobs[job_id]
        task = self.instance.tasks[task_id]
        vehicle = self.instance.vehicles[job.vehicle_id]
        vehicle_type = self.instance.vehicle_types[self.instance.vehicles[job.vehicle_id].vehicle_type_id]

        task_index = job.task_ids.index(task_id)

        if task_index == 0:
            arrival_time = max(self.current_time, vehicle.work_shift[0], task.delivery_window[0])
        else:
            # check presence of the departure time
            validate_int(self.departure_time[job.task_ids[task_index - 1]], "departure_time", non_negative=True)
            arrival_time = (self.departure_time[job.task_ids[task_index - 1]]
                            + self.instance.travel_time[job.task_ids[task_index - 1], task.id, vehicle_type.id])

        departure_time = max(arrival_time, task.delivery_window[0], vehicle.work_shift[0]) + vehicle_type.stop_time + task.service_time
        return arrival_time, departure_time

    def _validate_job_id(self, job_id):
        if job_id not in self.jobs.keys():
            raise UnexpectedJobId(f"Job {job_id} does not exist")

    def _validate_job(self, job_id):
        job = self.jobs[job_id]

        # All task are valid
        for t_id in job.task_ids:
            self._validate_task_id(t_id)

        # No duplicated tasks
        if len(job.task_ids) != len(set(job.task_ids)):
            raise UnexpectedTaskId("Duplicated task id")

        # Check that the executing task is still in the job
        if self.executing_task[job_id] != NONE_TASK and self.executing_task[job_id] not in job.task_ids:
            raise UnexpectedTaskId(f"Executing task {self.executing_task[job_id]} is not in the job {job.id}")

    def _validate_task_id(self, task_id):
        if task_id not in self.instance.tasks.keys():
            raise UnexpectedTaskId(f"Task {task_id} does not exist")

    def _validate_job_task_id(self, job_id, task_id):
        if task_id not in self.jobs[job_id].task_ids:
            raise UnexpectedTaskId(f"Task {task_id} is not in the job {job_id}")

    def _validate_arrival_time(self, arrival_time):
        if not isinstance(arrival_time, int) or arrival_time < 0:
            raise ValidationError("Arrival time should be a positive integer")

    def _validate_departure_time(self, departure_time):
        if not isinstance(departure_time, int) or departure_time < 0:
            raise ValidationError("Departure time should be a positive integer")

    def _validate_not_planned_task(self, task_id):
        for j in self.jobs.values():
            if task_id in j.task_ids:
                raise UnexpectedTaskId(f"Task {task_id} is already in another job")

    def __repr__(self):
        return f"JobPlan [{ ', '.join([str(j) for j in self.jobs.values()])}]"

    def __str__(self):
        return f"JobsPlan <current_time: {self.current_time}, jobs: [{ ', '.join([str(j) for j in self.jobs.values()])}]>"
