from array import array


cdef class Job(object):
    # Assumption: for any vehicle there is a job, eventually empty.
    def __init__(self,
                 job_id, vehicle_id, vehicle_type_id, stop_cost, stop_time,
                 work_shift, max_weight, max_volume, executing_task, unit_distance_cost, delivery_group_ids):
        self.id = job_id
        self.task_ids = array('i', [])
        self.vehicle_id = vehicle_id
        self.vehicle_type_id = vehicle_type_id
        self.stop_cost = stop_cost
        self.stop_time = stop_time
        self.work_shift = array('i', work_shift)
        self.max_weight = max_weight
        self.max_volume = max_volume
        self.cost = 0
        self.executing_task = executing_task
        self.unit_distance_cost = unit_distance_cost
        self.delivery_group_size = {g: 0 for g in delivery_group_ids}  # number of task per each delivery group
        self.remaining_size = 0  # Number of tasks after the executing tasks

    def copy_from(self, other):
        self.id = other.id
        self.task_ids = array('i', other.task_ids)
        self.vehicle_id = other.vehicle_id
        self.vehicle_type_id = other.vehicle_type_id
        self.stop_cost = other.stop_cost
        self.stop_time = other.stop_time
        self.work_shift = array('i', other.work_shift)
        self.max_weight = other.max_weight
        self.max_volume = other.max_volume
        self.cost = other.cost
        self.executing_task = other.executing_task
        self.unit_distance_cost = other.unit_distance_cost
        self.delivery_group_size = dict(other.delivery_group_size)
        self.remaining_size = other.remaining_size
