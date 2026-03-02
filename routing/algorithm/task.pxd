cdef class Task:
    cdef public int id
    cdef public int delivery_id
    cdef public int pickup_id
    cdef public int dropoff_id
    cdef public int delivery_group_id
    cdef public int weight
    cdef public int volume
    cdef public int[:] delivery_window
    cdef public int service_time
    cdef public int geo_hash
    cdef public int job_id
    cdef public int cum_weight  # weight before task t
    cdef public int cum_volume  # volume before task t
    cdef public int arrival_time  # arrival time at task t, it doesn't include waiting time and service time
    cdef public int departure_time  # departure time from task t. It includes waiting time before leaving t (in case t is the last task of the route).
    cdef public int max_lag  # job serving the task
    cdef public int position  # position within the job

    #cpdef int copy_from(self, other)