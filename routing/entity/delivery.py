from typing import Tuple
from routing.entity.utils import validate_int
from routing.entity.constant import NONE_DELIVERY_GROUP


class Delivery(object):

    def __init__(self,
                 id: int,
                 pickup_id: int,
                 dropoff_id: int,
                 max_lag: int,
                 weight: int = 0,
                 volume: int = 0,
                 skills: Tuple[int] = (),
                 delivery_group_id: int = NONE_DELIVERY_GROUP
                 ):
        self._id = self.id = id
        self._pickup_id = self.pickup_id = pickup_id
        self._dropoff_id = self.dropoff_id = dropoff_id
        self._weight = self.weight = weight
        self._volume = self.volume = volume
        self._max_lag = self.max_lag = max_lag
        self._skills = self.skills = skills
        self._delivery_group_id = self.delivery_group_id = delivery_group_id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = validate_int(value, attr="id", non_negative=True)

    @property
    def pickup_id(self):
        return self._pickup_id

    @pickup_id.setter
    def pickup_id(self, value):
        self._pickup_id = validate_int(value, attr="pickup_id", non_negative=True)

    @property
    def dropoff_id(self):
        return self._dropoff_id

    @dropoff_id.setter
    def dropoff_id(self, value):
        self._dropoff_id = validate_int(value, attr="dropoff_id", non_negative=True)

    @property
    def delivery_group_id(self):
        return self._delivery_group_id

    @delivery_group_id.setter
    def delivery_group_id(self, value):
        self._delivery_group_id = validate_int(value, attr="delivery_group_id", allow_none=True, non_negative=True)

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = validate_int(value, attr="weight", non_negative=True)

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = validate_int(value, attr="volume", non_negative=True)

    @property
    def max_lag(self):
        return self._max_lag

    @max_lag.setter
    def max_lag(self, value):
        self._max_lag = validate_int(value, attr="max_lag", non_negative=True)

    @property
    def skills(self):
        return set(self._skills)

    @skills.setter
    def skills(self, value):
        for s in value:
            validate_int(s, attr="skill", non_negative=True)
        self._skills = set(value)

    def __repr__(self):
        return f"Delivery {self.id}"

    def __str__(self):
        return ("Delivery <"
                f"id: {self.id}, pickup_id: {self.pickup_id}, dropoff_id: {self.dropoff_id}, weight: {self.weight}, "
                f"volume: {self.volume}, max_lag: {self.max_lag}, skills: {self.skills}, "
                f" delivery_group_id: {self.delivery_group_id}"
                ">")
