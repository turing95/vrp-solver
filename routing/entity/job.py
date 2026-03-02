from routing.entity.utils import validate_int


class Job(object):

    def __init__(self,
                 id: int,
                 vehicle_id,
                 task_ids,
                 plan):
        self._id = self.id = id
        self._vehicle_id = self.vehicle_id = vehicle_id
        self._task_ids = self.task_ids = list(task_ids)
        self._plan = plan

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = validate_int(value, attr="id", non_negative=True)

    @property
    def vehicle_id(self):
        return self._vehicle_id

    @vehicle_id.setter
    def vehicle_id(self, value):
        self._vehicle_id = validate_int(value, attr="vehicle_id", non_negative=True)

    @property
    def task_ids(self):
        return list(self._task_ids)

    @task_ids.setter
    def task_ids(self, value):
        for i in value:
            validate_int(i, attr="task_id", non_negative=True)
        self._task_ids = list(value)

    @property
    def executing_task(self):
        return self._plan.executing_task[self.id]

    def __repr__(self):
        tasks = "[" + ', '.join([f"->{t}" if t == self.executing_task else f"{t}" for t in self.task_ids]) + ']'
        return f"Job <id: {self.id}, vehicle_id: {self.vehicle_id}, task_ids: {tasks}>"
