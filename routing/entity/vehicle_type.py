from routing.entity.utils import validate_int


class VehicleType(object):

    def __init__(self,
                 id: int,
                 stop_time: int):
        self._id = self.id = id
        self._stop_time = self.stop_time = stop_time

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = validate_int(value, attr="id", non_negative=True)

    @property
    def stop_time(self):
        return self._stop_time

    @stop_time.setter
    def stop_time(self, value):
        self._stop_time = validate_int(value, attr="stop_time", non_negative=True)

    def __repr__(self):
        return f"VehicleType {self.id}"

    def __str__(self):
        return f"VehicleType <id: {self.id}, stop_time: {self.stop_time}>"
