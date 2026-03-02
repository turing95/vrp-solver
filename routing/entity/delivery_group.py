from routing.entity.utils import validate_int


class DeliveryGroup(object):

    def __init__(self, id: int):
        self.id = id
        self.delivery_ids = set()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = validate_int(value, attr="id")

    @property
    def delivery_ids(self):
        return set(self._delivery_ids)

    @delivery_ids.setter
    def delivery_ids(self, value):
        for i in value:
            validate_int(i, attr="delivery_id")
        self._delivery_ids = set(value)

    def add_delivery(self, delivery_id: int):
        self.delivery_ids.add(delivery_id)

    def add_deliveries(self, *delivery_ids: int):
        self.delivery_ids.update(delivery_ids)

    def __repr__(self):
        return f"DeliveryGroup <id: {self.id}, delivery_ids: {self.delivery_ids}>"
