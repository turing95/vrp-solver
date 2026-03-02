from typing import Tuple

from routing.entity.error import ValidationError
from routing.entity.utils import validate_int
from routing.entity.constant import NONE_TASK, NONE_DELIVERY

DeliveryWindowType = Tuple[int, int]
PositionType = Tuple[float, float]
ServiceTimeType = int


class Task(object):
    def __init__(self,
                 id: int,
                 delivery_window: DeliveryWindowType,
                 geo_hash: int,
                 service_time: ServiceTimeType = 0,
                 coordinates: PositionType = (),
                 delivery_window_right_margin: int = 0
                 ):
        self._id = self.id = id
        self._delivery_window = self.delivery_window = delivery_window
        self._delivery_window_right_margin = self.delivery_window_right_margin = delivery_window_right_margin
        self._coordinates = self.coordinates = coordinates
        self._service_time = self.service_time = service_time
        self._geo_hash = self.geo_hash = geo_hash
        self._weight = self.weight = 0
        self._volume = self.volume = 0
        self._dropoff_id = self.dropoff_id = NONE_TASK  # Associated dropoff id
        self._pickup_id = self.pickup_id = NONE_TASK  # Associated pickup id, will always be NONE_TASK
        self._delivery_id = self.delivery_id = NONE_DELIVERY

        self._validate_delivery_window()

    def _validate_delivery_window(self):
        if self.delivery_window[0] > self.delivery_window[1] or self.delivery_window[0] < 0:
            raise ValidationError(f"Unexpected delivery window endpoints {self.delivery_window}")
        if self.delivery_window[0] > self.delivery_window[1] - self.delivery_window_right_margin:
            raise ValidationError(f"Delivery window right margin is too big {self.delivery_window_right_margin} "
                                  f"w.r.t the delivery window {self.delivery_window}")

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = validate_int(value, attr="id", non_negative=True)

    @property
    def delivery_window(self):
        return self._delivery_window

    @delivery_window.setter
    def delivery_window(self, value):
        self._delivery_window = (validate_int(value[0], attr="delivery_window[0]", non_negative=True),
                                 validate_int(value[1], attr="delivery_window[1]", non_negative=True))

    @property
    def delivery_window_right_margin(self):
        return self._delivery_window_right_margin

    @delivery_window_right_margin.setter
    def delivery_window_right_margin(self, value):
        self._delivery_window_right_margin = validate_int(value, attr="delivery_window_right_margin", non_negative=True)

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, value):
        if len(value) == 2:
            self._coordinates = (validate_int(value[0], attr="coordinates[0]"),
                                 validate_int(value[1], attr="coordinates[1]"))
        else:
            self._coordinates = ()

    @property
    def service_time(self):
        return self._service_time

    @service_time.setter
    def service_time(self, value):
        self._service_time = validate_int(value, attr="service_time", non_negative=True)

    @property
    def geo_hash(self):
        return self._geo_hash

    @geo_hash.setter
    def geo_hash(self, value):
        self._geo_hash = validate_int(value, attr="geo_hash", non_negative=True)

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = validate_int(value, attr="weight")

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = validate_int(value, attr="volume")

    @property
    def pickup_id(self):
        return self._pickup_id

    @pickup_id.setter
    def pickup_id(self, value):
        self._pickup_id = validate_int(value, attr="pickup_id", allow_none=True, non_negative=True)

    @property
    def dropoff_id(self):
        return self._dropoff_id

    @dropoff_id.setter
    def dropoff_id(self, value):
        self._dropoff_id = validate_int(value, attr="dropoff_id", allow_none=True, non_negative=True)

    @property
    def delivery_id(self):
        return self._delivery_id

    @delivery_id.setter
    def delivery_id(self, value):
        self._delivery_id = validate_int(value, attr="delivery_id", allow_none=True, non_negative=True)


class Pickup(Task):

    def __repr__(self):
        return (
            f"Pickup <id: {self.id}, delivery_window: {self.delivery_window}, coordinates: {self.coordinates}, "
            f"service_time: {self.service_time}, geo_hash: {self.geo_hash}, weight: {self.weight}, "
            f"volume: {self.volume}>"
        )


class Dropoff(Task):

    def __repr__(self):
        return (
            f"Dropoff <id: {self.id}, delivery_window: {self.delivery_window}, coordinates: {self.coordinates}, "
            f"service_time: {self.service_time}, geo_hash: {self.geo_hash}, weight: {self.weight}, "
            f"volume: {self.volume}>"
        )
