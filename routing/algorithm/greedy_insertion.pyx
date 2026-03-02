from routing.entity.constant import NONE_JOB

from routing.algorithm.solution cimport Solution
from routing.algorithm.job cimport Job
from routing.algorithm.task cimport Task
from routing.entity.constant cimport C_NONE_TASK, C_NONE_POSITION

from routing.algorithm.solution import Solution
from routing.algorithm.job import Job
from routing.algorithm.task import Task

def greedy_insertion(solution):
    cdef Solution sol = solution
    sol.sort_incomplete_deliveries()

    # Main loop
    deliveries = list(sol.not_completed_deliveries)  # incomplete deliveries changes during the insertion
    for delivery_id in deliveries:
        sol.best_insertion.setup(delivery_id, sol.delivery_drop_penalty[delivery_id] + 1)
        fixed_job_id = sol.get_fixed_job(delivery_id)

        if fixed_job_id != NONE_JOB:
            compute_best_positions(sol, fixed_job_id, delivery_id)
        else:
            for j in sol.jobs[:]:
                vehicle_id = j.vehicle_id

                if not sol.compatible_vehicle_skills[vehicle_id, delivery_id]:
                    continue

                if not sol.compatible_vehicle_work_shift[vehicle_id, delivery_id]:
                    continue

                c_compute_best_positions(sol, j.id, delivery_id)

        if sol.best_insertion.cost <= sol.delivery_drop_penalty[delivery_id]:
            sol.apply_insertion(sol.best_insertion)


def compute_best_positions(solution: Solution, j_id: int, delivery_id: int):
    """Wrapper to test the function within the Python interpreter"""
    return c_compute_best_positions(solution, j_id, delivery_id)

cdef int c_compute_best_positions(Solution solution, int j_id, int delivery_id) except -1:
    cdef Solution sol = solution
    cdef Job job = sol.jobs[j_id]

    cdef Task pickup = sol.tasks[sol.delivery_pickup_id[delivery_id]]
    cdef Task dropoff = sol.tasks[sol.delivery_dropoff_id[delivery_id]]
    cdef int vehicle_id = job.vehicle_id
    cdef int job_size = len(job.task_ids)

    cdef int first_position = sol.tasks[job.executing_task].position + 1 if job.executing_task != C_NONE_TASK else 0
    cdef int last_position = job_size + 1  # last position is one past the last task (+1 because range is not inclusive)
    cdef float cost = 0
    cdef int p_pos = 0
    cdef int d_pos = 0

    # Cumulative weight at the current pos and at the end of the job (might be different that 0 in case of partial job)
    cdef int current_weight = 0
    cdef int current_volume = 0
    cdef int end_weight = 0
    cdef int end_volume = 0

    if job_size > 0:
        end_weight = sol.tasks[job.task_ids[job_size - 1]].cum_weight + sol.tasks[job.task_ids[job_size - 1]].weight
        end_volume = sol.tasks[job.task_ids[job_size - 1]].cum_volume + sol.tasks[job.task_ids[job_size - 1]].volume

    if pickup.position == C_NONE_POSITION:  # Evaluate the possible combinations of pickup and dropoff position

        for p_pos in range(first_position, last_position):
            # Get the cumulative weight and volume before the task at p_pos (p_pos might be greater than job_size)
            if p_pos < job_size:
                current_weight = sol.tasks[job.task_ids[p_pos]].cum_weight
                current_volume = sol.tasks[job.task_ids[p_pos]].cum_volume
            elif job_size > 0:
                current_weight = end_weight
                current_volume = end_volume
            else:
                current_weight = 0
                current_volume = 0

            # Skip current p_pos if there is not enough capacity
            if current_weight + pickup.weight > job.max_weight:
                continue
            if current_volume + pickup.volume > job.max_volume:
                continue

            for d_pos in range(p_pos, last_position):
                # Get the cumulative weight and volume before the task at d_pos (d_pos might be greater than job_size)
                if d_pos < job_size:
                    current_weight = sol.tasks[job.task_ids[d_pos]].cum_weight
                    current_volume = sol.tasks[job.task_ids[d_pos]].cum_volume
                elif job_size > 0:
                    current_weight = end_weight
                    current_volume = end_volume
                else:
                    current_weight = 0
                    current_volume = 0

                # Skip all the next d-pod if the current capacity at this point is already exceeded
                if current_weight + pickup.weight > job.max_weight:
                    break
                if current_volume + pickup.volume > job.max_volume:
                    break

                cost = sol.c_insertion_cost(j_id, delivery_id, p_pos, d_pos)
                if cost < sol.best_insertion.cost:
                    sol.best_insertion.cost = cost
                    sol.best_insertion.job_id = j_id
                    sol.best_insertion.pickup_pos = p_pos
                    sol.best_insertion.dropoff_pos = d_pos

    elif dropoff.position == C_NONE_POSITION:  # Only evaluate the position of the dropoff
        # dropoff position has to be after the pickup, i.e. from max(pickup.position + 1, first_position)
        if pickup.position >= first_position:
            first_position = pickup.position + 1

        for d_pos in range(first_position, last_position):
            cost = sol.c_insertion_cost(j_id, delivery_id, C_NONE_POSITION, d_pos)
            if cost < sol.best_insertion.cost:
                sol.best_insertion.cost = cost
                sol.best_insertion.job_id = j_id
                sol.best_insertion.pickup_pos = C_NONE_POSITION
                sol.best_insertion.dropoff_pos = d_pos

            # Stop search further if the cumulative capacity after the current position is bigger than the max capacity.
            if d_pos + 1 < job_size and sol.tasks[job.task_ids[d_pos + 1 ]].cum_weight > job.max_weight:
                break
            if d_pos + 1 < job_size and sol.tasks[job.task_ids[d_pos + 1]].cum_volume > job.max_volume:
                break
    return 0
