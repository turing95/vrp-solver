cdef class Insertion:
    cdef public int delivery
    cdef public int pickup_pos
    cdef public int dropoff_pos
    cdef public int job_id
    cdef public float cost