from routing.entity.constant import NONE_JOB, NONE_DELIVERY, NONE_POSITION


cdef class Insertion(object):

    def __init__(self, cost):
        self.delivery = NONE_DELIVERY
        self.pickup_pos = NONE_POSITION
        self.dropoff_pos = NONE_POSITION
        self.job_id = NONE_JOB
        self.cost = cost

    def setup(self, delivery_id, cost):
        self.delivery = delivery_id
        self.pickup_pos = NONE_POSITION
        self.dropoff_pos = NONE_POSITION
        self.job_id = NONE_JOB
        self.cost = cost
