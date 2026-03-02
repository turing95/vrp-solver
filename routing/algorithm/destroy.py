from routing.algorithm.solution import Solution
from routing.entity.constant import NONE_JOB, NONE_TASK

import random

l_max = 7  # max number of task removed for each job
l_avg = 7  # average number task to remove


def destroy(sol: Solution):
    if sol.jobs.size == 0:
        return
    job_list = set()
    seed_id = random.choice(sol.tasks_to_plan)
    # this is used in case the seed is not assigned to any job.
    vehicle_type_id = random.choice(sol.instance.vehicle_types).id
    neighbourhood = sol.instance.get_neighbour_tasks(seed_id, vehicle_type_id)

    avg_size = int(sol.compute_avg_job_remaining_task())
    d, l_ub = compute_job_to_destroy(avg_size, sol.jobs.size)

    neighbour_i = 0
    task_id = seed_id
    while len(job_list) < d and neighbour_i < len(neighbourhood):
        task = sol.tasks[task_id]

        if task.job_id != NONE_JOB and task.job_id not in job_list:
            job = sol.jobs[task.job_id]

            # task should be after the executing task to be removed
            if job.executing_task == NONE_TASK or sol.tasks[job.executing_task].position < task.position:
                job_list.add(task.job_id)

                # Compute number of delivery to remove
                # Assumption: there is at least one remaining tasks in the job (task by construction is not completed)
                l = random.randint(1, min(job.remaining_size, l_ub + 1))  # +1 because l_ub can be 0

                # Determine a sequence of task to remove, start_pos included end_pos excluded
                e_pos = sol.tasks[job.executing_task].position if job.executing_task != NONE_TASK else - 1
                start_pos = random.randint(max(e_pos + 1, task.position - l),
                                           min(len(job.task_ids) - 1, task.position + l))
                end_pos = min(start_pos + l, len(job.task_ids) - 1)

                # Remove the associated delivery.
                # TODO removing a partial delivery with the pickup completed (before the executing task) and the dropoff
                #  not completed might break the capacity constraints leading to infeasible solution.
                #  This should be avoided since it breaks the assumption of the overall routing library.
                delivery_list = set()
                for i in range(start_pos, end_pos):
                    delivery_list.add(sol.tasks[job.task_ids[i]].delivery_id)

                sol.remove_deliveries(job.id, delivery_list)

        # Next one
        task_id = neighbourhood[neighbour_i]
        neighbour_i += 1


def compute_job_to_destroy(avg_job_size, job_number):
    """
    Compute the number of job to destroy and the max number
    of task to destroy for each job.
    """
    l_ub = min(l_max, avg_job_size)
    d_ub = min(int(4.0 * l_avg / (1 + l_ub)), job_number)
    return random.randint(1, d_ub), l_ub
