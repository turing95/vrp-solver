from typing import Tuple

from routing.entity.utils import validate_int
from routing.entity.utils import validate_float


class Vehicle(object):

    def __init__(self,
                 id: int,
                 vehicle_type_id: int,
                 work_shift: Tuple[int, int],
                 max_weight: int = 0,
                 max_volume: int = 0,
                 stop_cost: float = 0,
                 unit_distance_cost: float = 1,
                 skills: Tuple[int] = (),
                 ):
        self._id = self.id = id
        self._vehicle_type_id = self.vehicle_type_id = vehicle_type_id
        self._max_weight = self.max_weight = max_weight
        self._max_volume = self.max_volume = max_volume
        self._unit_distance_cost = self.unit_distance_cost = unit_distance_cost
        self._skills = self.skills = set(skills)
        self._work_shift = self.work_shift = work_shift
        self._stop_cost = self.stop_cost = stop_cost

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = validate_int(value, attr="id", non_negative=True)

    @property
    def vehicle_type_id(self):
        return self._vehicle_type_id

    @vehicle_type_id.setter
    def vehicle_type_id(self, value):
        self._vehicle_type_id = validate_int(value, attr="vehicle_type_id", non_negative=True)

    @property
    def max_volume(self):
        return self._max_volume

    @max_volume.setter
    def max_volume(self, value):
        self._max_volume = validate_int(value, attr="max_volume", non_negative=True)

    @property
    def max_weight(self):
        return self._max_weight

    @max_weight.setter
    def max_weight(self, value):
        self._max_weight = validate_int(value, attr="max_weight", non_negative=True)

    @property
    def unit_distance_cost(self):
        return self._unit_distance_cost

    @unit_distance_cost.setter
    def unit_distance_cost(self, value):
        self._unit_distance_cost = validate_float(value, attr="unit_distance_cost", non_negative=True)

    @property
    def skills(self):
        return set(self._skills)

    @skills.setter
    def skills(self, value):
        for s in value:
            validate_int(s, attr="skill", non_negative=True)
        self._skills = set(value)

    @property
    def work_shift(self):
        return self._work_shift

    @work_shift.setter
    def work_shift(self, value):
        self._work_shift = (validate_int(value[0], attr="work_shift[0]", non_negative=True),
                            validate_int(value[1], attr="work_shift[1]", non_negative=True))

    @property
    def stop_cost(self):
        return self._stop_cost

    @stop_cost.setter
    def stop_cost(self, value):
        self._stop_cost = validate_float(value, attr="stop_cost", non_negative=True)

    def __repr__(self):
        return f"Vehicle {self.id}"

    def __str__(self):
        return (
            f"Vehicle <id: {self.id}, vehicle_type_id: {self.vehicle_type_id}, max_weight: {self.max_weight}, "
            f"max_volume: {self.max_volume}, unit_distance_cost: {self.unit_distance_cost}, skills: {self.skills}, "
            f"work_shift: {self.work_shift}, stop_cost: {self.stop_cost}>"
        )
