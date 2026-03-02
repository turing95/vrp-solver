cdef class Job:
    cdef public int id
    cdef public object task_ids  # list of task ids
    cdef public int vehicle_id
    cdef public int vehicle_type_id
    cdef public float stop_cost
    cdef public int stop_time
    cdef public int[:] work_shift
    cdef public int max_weight
    cdef public int max_volume
    cdef public float cost
    cdef public int executing_task
    cdef public float unit_distance_cost
    cdef public dict delivery_group_size # number of task per each delivery group
    cdef public int remaining_size  # Number of tasks after the executing tasks

    #cpdef int copy_from(self, Job other)