from routing.algorithm.job cimport Job
from routing.algorithm.task cimport Task
from routing.algorithm.insertion cimport Insertion

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

    # object
    cdef public object instance

    # arrays
    cdef public object not_completed_deliveries, tasks_to_plan

    # dictionaries
    cdef public dict delivery_group_job, compatible_vehicle_skills, compatible_vehicle_work_shift

    # Memory views
    cdef public Task[:] tasks
    cdef public Job[:] jobs
    cdef public int[:] delivery_pickup_id  # get the pickup id from the delivery id
    cdef public int[:] delivery_dropoff_id  # get the dropoff id from the delivery id
    cdef public int[:] delivery_drop_penalty  # get the drop penalty associated with a delivery id
    cdef public int[:,:,:] distance
    cdef public int[:,:,:] travel_time

    # Attributes
    cdef public int current_time
    cdef public int balanced_job_size
    cdef public float delivery_window_penalty, max_lag_penalty, span_penalty
    cdef public Insertion best_insertion

    # Methods
    cdef float c_init_job_cost(self, int job_tasks_number) except -1

    cdef int c_init_task_time(self, int task_id, int job_id) except -1

    cdef int c_compute_arc_cum_capacity(self, int prev_task_id, int next_task_id) except -1

    cdef int c_compute_arc_time(self, int prev_task_id, int next_task_id, int job_id) except -1

    cdef float c_arc_cost(self, int prev_task_id, int next_task_id, int job_id) except -1

    cdef float c_insertion_cost(self, int job_id, int delivery_id, int pickup_pos, int dropoff_pos) except -1000000

cdef int max_int(int a, int b) except -1