import cython
import random
import math
import numpy as np
from array import array

from routing.algorithm.job import Job
from routing.algorithm.task import Task
from routing.algorithm.insertion import Insertion

from routing.algorithm.job cimport Job
from routing.algorithm.task cimport Task
from routing.algorithm.insertion cimport Insertion
from routing.entity.constant cimport C_NONE_JOB, C_NONE_TASK, C_NONE_POSITION, C_NONE_DELIVERY_GROUP, C_NONE_TIME
from routing.entity.error import RoutingError

cdef class Solution(object):
    """
    Represents either a solution or partial solution of the problem with some delivery to be performed.

    It allows to compute the insertion cost of a delivery (pair of pickup and dropoff) and to insert
    a delivery into a given point of a given job.

    It assumes that there are as many jobs as the vehicles. In other words, it assumes
    there is a 1:1 mappings between a vehicle and a job. With this assumption all the information
    about a vehicle can be moved into the job structure.

    To evaluate the insertion cost of a delivery, additional information like the arrival time and
    the cumulative capacities are updated sequentially starting from the current executing task.

    The task that are in execution or are already completed are initialized with their associated arrival_time,
    position, cumulative weight and volume and these value never change.

    TODO change insertion cost to use dedicated attribute to compute the arrival and the cost, and change the arrival
         only when the insertion is performed. this is not a bug but it could be useful to have those attribute
         consistent with the current solution.
    """

    def __init__(self, instance):
        self.instance = instance
        self.current_time = self.instance.plan.current_time

        # Penalty coefficients
        self.delivery_window_penalty = self.instance.delivery_window_penalty
        self.max_lag_penalty = self.instance.max_lag_penalty
        self.span_penalty = self.instance.span_penalty

        self.not_completed_deliveries = array('i')  # deliveries which pickup or dropoff are not assigned to a job.
        self.tasks_to_plan = array('i')  # all the tasks but the completed ones or in execution. They might be in a job or not.

        # Init jobs
        self.jobs = np.array([
            Job(job_id=j.id,
                vehicle_id=j.vehicle_id,
                vehicle_type_id=self.instance.get_vehicle_type(j.vehicle_id),
                stop_cost=self.instance.get_stop_cost(j.vehicle_id),
                stop_time=self.instance.get_stop_time(self.instance.get_vehicle_type(j.vehicle_id)),
                work_shift=self.instance.get_work_shift(j.vehicle_id),
                max_weight=self.instance.get_vehicle_max_weight(j.vehicle_id),
                max_volume=self.instance.get_vehicle_max_volume(j.vehicle_id),
                executing_task=self.instance.plan.executing_task[j.id],
                unit_distance_cost=self.instance.get_unit_distance_cost(j.vehicle_id),
                delivery_group_ids=self.instance.delivery_groups.keys()
                )
            for j in instance.plan.jobs.values()], dtype='object')

        # Init tasks
        self.tasks = np.array([
            Task(task_id=t.id,
                 weight=t.weight,
                 volume=t.volume,
                 delivery_window=(t.delivery_window[0], t.delivery_window[1] - t.delivery_window_right_margin),
                 service_time=t.service_time,
                 geo_hash=t.geo_hash,
                 arrival_time=self.instance.plan.arrival_time[t.id],
                 departure_time=self.instance.plan.departure_time[t.id],
                 delivery_id=t.delivery_id,
                 pickup_id=t.pickup_id,
                 dropoff_id=t.dropoff_id,
                 max_lag=self.instance.get_max_lag(t.delivery_id),
                 delivery_group_id=self.instance.get_delivery_group(t.delivery_id), )
            for t in self.instance.tasks.values()
        ], dtype='object')

        # Init distances and travel time matrices
        expected_shape = (self.tasks.size, self.tasks.size, len(self.instance.vehicle_types))
        if self.instance.distance_matrix.shape != expected_shape:
            raise RoutingError(
                f"Expected distance_matrix to have shape {expected_shape}, got {self.instance.distance_matrix.shape}")
        if self.instance.travel_time_matrix.shape != expected_shape:
            raise RoutingError(
                f"Expected travel_time_matrix to have shape {expected_shape}, got {self.instance.travel_time_matrix.shape}")
        self.distance = self.instance.distance_matrix
        self.travel_time = self.instance.travel_time_matrix

        # TODO The following 3 dict can be substituted with an array of object deliveries
        self.delivery_pickup_id = array("i", [delivery.pickup_id for delivery in self.instance.deliveries.values()])
        self.delivery_dropoff_id = array("i", [delivery.dropoff_id for delivery in self.instance.deliveries.values()])
        self.delivery_drop_penalty = array("i", [self.instance.compute_penalty(delivery.id) for delivery in self.instance.deliveries.values()])

        self.delivery_group_job = {k: C_NONE_JOB for k in self.instance.delivery_groups.keys()}

        # Compatibility between vehicle and deliveries skills   # Should I move these into the instance?
        self.compatible_vehicle_skills = {
            (vehicle, delivery): self.instance.has_required_skills(vehicle, delivery)
            for delivery in self.instance.deliveries
            for vehicle in self.instance.vehicles
        }

        # Compatibility between vehicle work shift and deliveries time windows   # Should I move these into the instance?
        self.compatible_vehicle_work_shift = {
            (vehicle, delivery): self.instance.has_compatible_work_shift(vehicle, delivery)
            for delivery in self.instance.deliveries
            for vehicle in self.instance.vehicles
        }

        for j in instance.plan.jobs.values():
            self.init_job_tasks(j.id, j.task_ids)

        self.init_incomplete_deliveries()
        self.init_tasks_to_plan()

        # desired number of tasks per job to have balanced jobs
        self.balanced_job_size = math.ceil(float(len(self.tasks_to_plan)) / len(self.jobs)) if len(self.jobs) > 0 else 0

        # compute the job data once the balanced job size is defined
        for j in instance.plan.jobs.values():
            self.compute_job_data(j.id)

        # Best insertion found for a single delivery during the search
        self.best_insertion = Insertion(self.instance.drop_penalty + self.instance.drop_penalty_delta + 1)

    def init_job_tasks(self, job_id, task_ids):
        """
        Lazily initialize the job with the given sequence of tasks.

        It computes the delivery group of the job but not the cost.

        For each task it sets the position, the cumulative capacities,
        and the arrival time.
        """

        self.jobs[job_id].task_ids = array('i', task_ids)

        for t_i, t_id in enumerate(task_ids):
            task = self.tasks[t_id]
            task.job_id = job_id
            task.position = t_i

            if t_i == 0:
                task.cum_weight = 0
                task.cum_volume = 0
            else:
                self.compute_arc_cum_capacity(prev_task_id, t_id)

            g = task.delivery_group_id
            if g != C_NONE_DELIVERY_GROUP:
                self.delivery_group_job[g] = job_id
                self.jobs[job_id].delivery_group_size[g] += 1
            prev_task_id = t_id

    def init_incomplete_deliveries(self):
        """
        Initialize the list of not completed deliveries.
        A delivery is not completed if either the pickup or the dropoff are
        not in any job.
        """
        for d in self.instance.deliveries.values():
            pickup = self.tasks[d.pickup_id]
            dropoff = self.tasks[d.dropoff_id]

            if pickup.job_id == C_NONE_JOB or dropoff.job_id == C_NONE_JOB:
                self.not_completed_deliveries.append(d.id)

    def init_tasks_to_plan(self):
        """
        Initialize the list of task to plan.
        A task can be planned if it's not assigned to any jobs or its position in the job is strictly greater than
        the position of the executing task when present.
        """
        for t in self.tasks:
            if t.job_id == C_NONE_JOB:
                self.tasks_to_plan.append(t.id)
            else:
                job = self.jobs[t.job_id]
                if job.executing_task == C_NONE_TASK:
                    self.tasks_to_plan.append(t.id)
                else:
                    executing_task = self.tasks[job.executing_task]
                    if t.position > executing_task.position:
                        self.tasks_to_plan.append(t.id)

    def sort_incomplete_deliveries(self):
        random.shuffle(self.not_completed_deliveries)

    def compute_job_data(self, job_id):
        """
        Compute the cumulative weight, the cumulative volume, arrival time, the remaining tasks size,
        and the cost of the given job starting from the executing task.

        Assumption: the job start as soon as possible, which means that the first task is
        completed in the first feasible time instance w.r.t to the delivery window and
        the vehicle work shift.

        Assumption: the arrival time of the executing task is already initialized amd correspond
        to the expected time of arrival.
        """

        job = self.jobs[job_id]
        initial_pos = self.tasks[job.executing_task].position if job.executing_task != C_NONE_TASK else 0
        job.remaining_size = len(job.task_ids) - (self.tasks[job.executing_task].position + 1 if job.executing_task != C_NONE_TASK else 0)
        job.cost = self.c_init_job_cost(job.remaining_size)

        if len(job.task_ids) - initial_pos > 1:
            # There is at least one arc to evaluate (one exiting arc from the executing node)

            for i in range(initial_pos, len(job.task_ids) - 1):
                prev_task = self.tasks[job.task_ids[i]]
                next_task = self.tasks[job.task_ids[i + 1]]

                # Initialize data
                if i == initial_pos and i == 0:
                    # in case i == initial_pos != 0, the position and the arrival time are already present
                    # (prev task is the executing task) and there is no need to initialize.
                    prev_task.position = 0
                    self.init_task_time(prev_task.id, job.id)
                    prev_task.cum_weight = 0
                    prev_task.cum_volume = 0
                    job.cost += job.stop_cost

                self.compute_arc_cum_capacity(prev_task.id, next_task.id)
                self.compute_arc_time(prev_task.id, next_task.id, job.id)
                job.cost += self.arc_cost(prev_task.id, next_task.id, job.id)
                next_task.position = i + 1

    def apply_insertion(self, insertion: Insertion):
        """
        Insert a delivery into a job and update the job_id and position of
        the associated pickup and dropoff tasks.

        Recompute all the data associated with the job.

        After the insertion the delivery is always removed from
        the not_completed_deliveries list. The delivery group of the delivery
        is assigned to the job.
        """
        pickup_id = self.delivery_pickup_id[insertion.delivery]
        dropoff_id = self.delivery_dropoff_id[insertion.delivery]
        job = self.jobs[insertion.job_id]

        delivery_group = self.instance.get_delivery_group(insertion.delivery)

        # Update data structure
        if insertion.pickup_pos != C_NONE_POSITION:
            job.task_ids.insert(insertion.pickup_pos, pickup_id)
            if delivery_group != C_NONE_DELIVERY_GROUP:
                job.delivery_group_size[delivery_group] += 1
            self.tasks[pickup_id].job_id = insertion.job_id

        if insertion.dropoff_pos != C_NONE_POSITION:
            offset = 0 if insertion.pickup_pos == C_NONE_POSITION else 1
            job.task_ids.insert(insertion.dropoff_pos + offset, dropoff_id)
            if delivery_group != C_NONE_DELIVERY_GROUP:
                job.delivery_group_size[delivery_group] += 1
            self.tasks[dropoff_id].job_id = insertion.job_id

        if delivery_group != C_NONE_DELIVERY_GROUP:
            self.delivery_group_job[delivery_group] = insertion.job_id

        # Remove the delivery from the incomplete deliveries
        self.not_completed_deliveries.remove(insertion.delivery)

        self.compute_job_data(insertion.job_id)

    def remove_deliveries(self, job_id, delivery_ids):
        """
        Remove all the tasks associated with the given deliveries from the given job.
        The tasks that are before the executing task, if present, are not removed.
        After this operation the delivery will be in the not_completed_delivery.

        Recompute all the data associated with the job.

        Assumption: the job and position of the delivery tasks are a meaningful value.
        """
        job = self.jobs[job_id]
        executing_task_position = -1 if job.executing_task == C_NONE_TASK else self.tasks[job.executing_task].position

        for d in delivery_ids:
            pickup = self.tasks[self.instance.get_pickup(d)]
            dropoff = self.tasks[self.instance.get_dropoff(d)]
            delivery_group = self.instance.get_delivery_group(d)

            removed = False
            if pickup.position > executing_task_position:
                job.task_ids.remove(pickup.id)
                pickup.job_id = C_NONE_JOB
                pickup.position = C_NONE_POSITION
                if delivery_group != C_NONE_DELIVERY_GROUP:
                    job.delivery_group_size[delivery_group] -= 1
                removed = True

            if dropoff.position > executing_task_position:
                job.task_ids.remove(dropoff.id)
                dropoff.job_id = C_NONE_JOB
                dropoff.position = C_NONE_POSITION
                if delivery_group != C_NONE_DELIVERY_GROUP:
                    job.delivery_group_size[delivery_group] -= 1
                removed = True

            if removed:
                self.not_completed_deliveries.append(d)

                if delivery_group != C_NONE_DELIVERY_GROUP and job.delivery_group_size[delivery_group] <= 0:
                    self.delivery_group_job[delivery_group] = C_NONE_JOB

                self.compute_job_data(job_id)

    def compute_cost(self):
        """
        Compute and return the cost by summing up all the job cost (without
        computing them) and the cost for the incomplete deliveries.
        """

        return (
                sum(j.cost for j in self.jobs)
                + sum(self.delivery_drop_penalty[delivery_id] for delivery_id in self.not_completed_deliveries)
        )

    cdef float c_init_job_cost(self, int job_tasks_number) except -1:
        """
        Compute and return the initial cost of the job according to its size.
        If the number of tasks is smaller than or equal to a balance job return zero
        otherwise an appropriate penalty.

        Returns: the initial cost value for a job according to its size
        """

        return self.span_penalty * max_int(0, job_tasks_number - self.balanced_job_size)

    cdef int c_init_task_time(self, int task_id, int job_id) except -1:
        """
        Compute the arrival time and the departure time for the given task as it was
        the first task to be performed.
        
        The arrival time is set as the max between the current time and the first possible time
        to perform the task according to the delivery window and the work shift.
        """
        cdef Task task = self.tasks[task_id]
        cdef Job job = self.jobs[job_id]

        task.arrival_time = max_int(self.current_time, max_int(task.delivery_window[0], job.work_shift[0]))
        task.departure_time = task.arrival_time + task.service_time + job.stop_time

        return 0

    def init_task_time(self, task_id, job_id):
        """Wrapper to test the function within the Python interpreter"""
        self.c_init_task_time(task_id, job_id)

    def compute_arc_cum_capacity(self, prev_task_id, next_task_id):
        """Wrapper to test the function within the Python interpreter"""
        self.c_compute_arc_cum_capacity(prev_task_id, next_task_id)

    cdef int c_compute_arc_cum_capacity(self, int prev_task_id, int next_task_id) except -1:
        """
        Compute and update the cumulative weight and volume before visiting the right
        endpoint of the given arc.
        """
        cdef Task prev_task = self.tasks[prev_task_id]
        cdef Task next_task = self.tasks[next_task_id]

        # Update the cumulative weight
        next_task.cum_weight = prev_task.cum_weight + prev_task.weight

        # Update the cumulative volume
        next_task.cum_volume = prev_task.cum_volume + prev_task.volume
        return 0

    def compute_arc_time(self, prev_task_id, next_task_id, job_id):
        """Wrapper to test the function within the Python interpreter"""
        self.c_compute_arc_time(prev_task_id, next_task_id, job_id)

    @cython.profile(False)
    cdef inline int c_compute_arc_time(self, int prev_task_id, int next_task_id, int job_id) except -1:
        """
        Compute and update the arrival time associated with the right endpoint of the
        given arc.
        
        Assumption: the departure time of all the executed task and the executing task has to be defined.
        """
        cdef Task prev_task = self.tasks[prev_task_id]
        cdef Task next_task = self.tasks[next_task_id]
        cdef Job job = self.jobs[job_id]

        # Compute the arrival time at the next task. Use the current time as departure time from the previous task
        # if the prev task is the executing task and its departure time is in the past. (The executing task was the
        # last task, and now it is completed. The job stopped there waiting future tasks.)
        if (job.executing_task != C_NONE_TASK
                and prev_task_id == job.executing_task
                and self.current_time > prev_task.departure_time):
            next_task.arrival_time = self.current_time
        else:
            next_task.arrival_time = prev_task.departure_time
        next_task.arrival_time += self.travel_time[prev_task.id, next_task.id, job.vehicle_type_id]

        # Compute the departure time at the next task
        next_task.departure_time = max_int(next_task.arrival_time, next_task.delivery_window[0]) + next_task.service_time
        next_task.departure_time += (job.stop_time if prev_task.geo_hash != next_task.geo_hash else 0)
        return 0

    def arc_cost(self, prev_task_id, next_task_id, job_id):
        """Wrapper to test the function within the Python interpreter"""
        return self.c_arc_cost(prev_task_id, next_task_id, job_id)

    @cython.profile(False)
    cdef inline float c_arc_cost(self, int prev_task_id, int next_task_id, int job_id) except -1:
        """
        Compute and return the cost of an arc.

        This value change according to the path to reach prev_task and therefore
        on the arrival time at the next_task. Thus, to get the correct cost
        the arrival time should be updated to the correct value before computing
        the arc cost.
        """
        cdef Task prev_task = self.tasks[prev_task_id]
        cdef Task next_task = self.tasks[next_task_id]
        cdef Job job = self.jobs[job_id]

        cdef Task pickup
        cdef int dropoff_lag = 0
        if next_task.pickup_id != C_NONE_TASK:
            pickup = self.tasks[next_task.pickup_id]
            dropoff_lag = max_int(0, next_task.arrival_time - pickup.arrival_time - next_task.max_lag)

        # Distance component
        cdef float cost = job.unit_distance_cost * self.distance[prev_task_id, next_task_id, job.vehicle_type_id]
        # Stop component
        cost += (job.stop_cost if (prev_task.geo_hash != next_task.geo_hash) else 0)
        # Delivery window penalty
        cost += self.delivery_window_penalty * max_int(0, next_task.arrival_time - next_task.delivery_window[1])
        # Max lag penalty
        cost += self.max_lag_penalty * dropoff_lag

        return cost

    def insertion_cost(self, job_id, delivery_id, pickup_pos, dropoff_pos):
        """Wrapper to test the function within the Python interpreter"""
        return self.c_insertion_cost(job_id, delivery_id, pickup_pos, dropoff_pos)

    cdef float c_insertion_cost(self, int job_id, int delivery_id, int pickup_pos, int dropoff_pos) except -1000000:
        """
        Compute the cost of the job to add the given delivery in the given pickup
        and dropoff positions without changing the current job structure.

        If we have n tasks then position 0 means before the first task while position n means after
        the last task.

        Assumption: when a delivery, pickup_pos, dropoff_pos are valid, then
        executing_task_position < pickup_pos <= dropoff_pos <= (number of tasks in the job)

        If pickup_pos/dropoff_pos is not a valid index (e.g. is C_NONE_POSITION, < 0) the cost for adding
        the associated pickup/dropoff is not taken into account.

        After evaluating the cost, all the values of arrival time after the executing task are
        no longer valid.
        
        Note the value used to propagate an exception is -1000000, this could be a problem if the cost
        can be negative. Anyway It should never happen as long as the distances respect the 
        triangle inequality. However if is not the case, it is extremely unlikely to have such a return value. 
        """

        cdef Job job = self.jobs[job_id]
        cdef int[:] task_ids = job.task_ids  # sequence of tasks to scan
        cdef int n_tasks = task_ids.size
        cdef int pickup = self.delivery_pickup_id[delivery_id]
        cdef int dropoff = self.delivery_dropoff_id[delivery_id]
        cdef float cost = 0

        # Initialize the cost by considering the span penalty
        cdef int expected_size = job.remaining_size
        if pickup_pos != C_NONE_TASK:
            expected_size += 1
        if dropoff_pos != C_NONE_TASK:
            expected_size += 1
        cost = self.c_init_job_cost(expected_size)

        # First available position for both pickup and dropoff
        cdef int initial_pos = self.tasks[job.executing_task].position + 1 if job.executing_task != C_NONE_TASK else 0

        # Index pointing to the task in the sequence to consider as next task
        cdef int i = 0

        # Determine the first arc used to start the scan
        cdef int prev_task
        cdef int next_task
        if initial_pos == 0:
            prev_task = C_NONE_TASK
            if pickup_pos == 0:
                next_task = pickup
                i = 0
            else:
                next_task = task_ids[0] if n_tasks > 0 else C_NONE_TASK
                i = 1
        else:
            prev_task = job.executing_task
            if pickup_pos == initial_pos:
                next_task = pickup
                i = initial_pos
            elif dropoff_pos == initial_pos:
                next_task = dropoff
                i = initial_pos
            else:
                next_task = task_ids[initial_pos] if n_tasks > initial_pos else C_NONE_TASK
                i = initial_pos + 1

        # Scan all the arcs which endpoints are prev_task and next_task
        while next_task != C_NONE_TASK:
            if prev_task == C_NONE_TASK:
                # initialize next task
                # if prev_task is not C_NONE_TASK, the arrival time are already present because either is the executing
                # task or because of the previous iteration
                cost += job.stop_cost
                self.c_init_task_time(next_task, job_id)
            else:
                self.c_compute_arc_time(prev_task, next_task, job.id)
                # increment the cost
                cost += self.c_arc_cost(prev_task, next_task, job.id)

            prev_task = next_task

            # Determine the next_task
            if pickup_pos == i and next_task != pickup and prev_task != dropoff:
                next_task = pickup
            elif dropoff_pos == i and next_task != dropoff:
                next_task = dropoff
            else:
                next_task = task_ids[i] if i < n_tasks else C_NONE_TASK
                i += 1

        # Check the work shift
        cdef Task last_task = self.tasks[dropoff] if dropoff_pos == n_tasks else self.tasks[task_ids[-1]]
        if last_task.departure_time > job.work_shift[1]:
            return self.delivery_drop_penalty[delivery_id] + 1

        return cost - job.cost

    def get_fixed_job(self, delivery_id):
        """
        Check whether there exist a fixed job for the given delivery.
        A job j might be fixed for a delivery when:
        - the pickup is already done by the job
        - or the delivery group associated with the delivery is assigned to the job.
        Return C_NONE_JOB if no fixed job is present.
        """

        delivery_group = self.instance.get_delivery_group(delivery_id)
        pickup_id = self.instance.get_pickup(delivery_id)
        pickup_job_id = self.tasks[pickup_id].job_id

        if delivery_group != C_NONE_DELIVERY_GROUP:
            fixed_job_id = self.delivery_group_job[delivery_group]
        elif pickup_job_id != C_NONE_JOB:
            fixed_job_id = pickup_job_id
        else:
            fixed_job_id = C_NONE_JOB

        return fixed_job_id

    def compute_avg_job_remaining_task(self):
        """
        Compute the average number of remaining tasks among all the jobs
        """
        return (sum(j.remaining_size for j in self.jobs) / self.jobs.size) if self.jobs.size > 0 else 0

    def copy_from(self, other):
        """
        Copy everything from a solution into the current one
        """
        self.instance = other.instance
        self.not_completed_deliveries = array('i', other.not_completed_deliveries)
        self.tasks_to_plan = array('i', other.tasks_to_plan)
        self.delivery_group_job = dict(other.delivery_group_job)
        self.compatible_vehicle_skills = dict(other.compatible_vehicle_skills)
        self.compatible_vehicle_work_shift = dict(other.compatible_vehicle_work_shift)

        assert self.tasks.size == other.tasks.size
        assert self.jobs.size == other.jobs.size
        for i in range(0, other.tasks.size):
             self.tasks[i].copy_from(other.tasks[i])
        for i in range(0, other.jobs.size):
            self.jobs[i].copy_from(other.jobs[i])

    def __repr__(self):
        jobs = []
        for j in self.jobs:
            jobs.append(f"{j.id}: [" + ', '.join(
                [f'->{t}' if t == j.executing_task else f'{t}' for t in j.task_ids]) + ']')
        return f"{{{', '.join(jobs)}}}"

    def __str__(self):
        s = ""
        for j in self.jobs:
            s += f"job {j.id}, shift ({j.work_shift[0]}, {j.work_shift[1]}), max_weight {j.max_weight}, max_volume {j.max_volume}, vehicle {j.vehicle_id}\n"
            for t_id in j.task_ids:
                t = self.tasks[t_id]
                s += f"\t{'->' if t.id == j.executing_task else ''}task {t.id}, at {t.arrival_time} ({t.delivery_window[0]}, {t.delivery_window[1]}), cum_weight {t.cum_weight}, cum_volume {t.cum_volume}, group {t.delivery_group_id}\n"
            s += "\n"
        return s


@cython.profile(False)
cdef inline int max_int(int a, int b) except -1:
    if a >= b:
        return a
    else:
        return b

