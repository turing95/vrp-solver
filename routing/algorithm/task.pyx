from array import array
from routing.entity.constant import NONE_JOB, NONE_POSITION


cdef class Task(object):

    def __init__(self, task_id, weight, volume, delivery_window, service_time, geo_hash, arrival_time, departure_time,
                 max_lag, delivery_id, pickup_id, dropoff_id, delivery_group_id):
        self.id = task_id
        self.delivery_id = delivery_id
        self.pickup_id = pickup_id
        self.dropoff_id = dropoff_id
        self.delivery_group_id = delivery_group_id
        self.weight = weight
        self.volume = volume
        self.delivery_window = array('i', delivery_window)
        self.service_time = service_time
        self.geo_hash = geo_hash
        self.job_id = NONE_JOB  # job serving the task
        self.cum_weight = 0  # weight before task t
        self.cum_volume = 0  # volume before task t
        self.arrival_time = arrival_time  # arrival time at task t, it doesn't include waiting time and service time
        self.departure_time = departure_time
        self.max_lag = max_lag
        self.position = NONE_POSITION  # position within the job

    def copy_from(self, other):
        self.id = other.id
        self.delivery_id = other.delivery_id
        self.pickup_id = other.pickup_id
        self.dropoff_id = other.dropoff_id
        self.delivery_group_id = other.delivery_group_id
        self.weight = other.weight
        self.volume = other.volume
        self.delivery_window = array('i', other.delivery_window)
        self.service_time = other.service_time
        self.geo_hash = other.geo_hash
        self.job_id = other.job_id
        self.cum_weight = other.cum_weight
        self.cum_volume = other.cum_volume
        self.arrival_time = other.arrival_time
        self.departure_time = other.departure_time
        self.max_lag = other.max_lag
        self.position = other.position
