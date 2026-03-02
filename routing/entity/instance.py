from typing import List
import numpy as np
import math

from routing.entity.task import Pickup, Dropoff
from routing.entity.delivery import Delivery
from routing.entity.delivery_group import DeliveryGroup
from routing.entity.vehicle_type import VehicleType
from routing.entity.vehicle import Vehicle
from routing.entity.plan import Plan
from routing.entity.error import ValidationError, UnexpectedTaskId, UnexpectedVehicleTypeId
from routing.entity.utils import IdGenerator, validate_float, validate_int
from routing.entity.constant import NONE_DELIVERY_GROUP


class Instance(object):
    """
    The main class to create and update a problem instance.

    A **problem instance** is composed by:
    - a collection of tasks (pickup and dropoff),
    - a collection of deliveries,
    - a collection of delivery group,
    - a collection of vehicle types,
    - a collection of vehicles,
    - a collection of distances (dictionary that stores for each vehicle type the distance between any pair of tasks)
    - a collection of travel times  (dictionary that stores for each vehicle type the travel time between any pair of tasks)
    - the dense distance matrix, a np.ndarray of int with shape (n task, n task, n vehicle types)
    - the dense travel time matrix, a np.ndarray of int with shape (n task, n task, n vehicle types)
    - a delivery plan.

    The delivery plan (`routing.entity.plan.Plan`) is used to keep track of
    the jobs (`routing.entity.job.Job`) associated with the vehicles and their delivery
    progress.

    **Assumptions**:
    - every entity (task, vehicle, delivery, job) is associated with an id. The id must be a sequential integer.
      The instance class automatically generates an id for any entity that is created without an id.
    - with every vehicle is associated exactly one job, eventually empty i.e. with no tasks.
    """

    def __init__(self,
                 current_time: int = 0,
                 delivery_window_penalty: float = 1,
                 drop_penalty: float = float("inf"),
                 max_lag_penalty: float = 1,
                 delivery_window_right_margin: int = 0,
                 span_penalty: float = 0,
                 inf_distance: int = 50000,
                 inf_travel_time: int = 50000,
                 drop_penalty_delta: float = 0,
                 drop_penalty_slope: float = 0,
                 ):
        """
        Initialize an empty instance with the given coefficients.

        Args:
            delivery_window_penalty: objective function penalty to pay for each unit of extra time w.r.t the
                                     task delivery window used to complete a task
            drop_penalty: constant term of the drop penalty function, see Instance.compute_drop_penalty
             for the definition of the drop penalty function,
            drop_penalty_delta: max variation of the drop penalty function, see Instance.compute_drop_penalty
             for the definition of the drop penalty function,
            drop_penalty_slope: coefficient of the drop penalty function that determine the slope of the drop penalty
              function, see Instance.compute_drop_penalty for the definition of the drop penalty function,
            max_lag_penalty: objective function penalty to pay for each unit of extra time w.r.t the delivery max
                             lag used to complete a delivery
            delivery_window_right_margin: unit of time subtracted from the right endpoint of all task delivery-windows
            span_penalty: objective function penalty to pay for each task in a job that exceed the required number of
                tasks to have a completely balanced set of jobs.
            inf_distance: the default distance between two tasks when no distance if given. It should be a large enough
                value (infinite distance) like if the two tasks are not connected.
            inf_travel_time: the default travel time between two tasks when no travel time is given. It should be a
                large enough value (infinite travel time) like if the two tasks are not connected.

        **Examples**:
        ```python
        from routing import Instance

        # Create an empty instance from a config object
        i = Instance(delivery_window_penalty=20, drop_penalty=1000)

        # Create an empty instance from a config object
        config = {"delivery_window_penalty": 20, "drop_penalty": 1000}
        i = Instance(**config)
        ```
        """
        # Instance data
        self.distance = {}
        self.distance_matrix = np.ndarray(shape=(0, 0, 0))
        self.travel_time = {}
        self.travel_time_matrix = np.ndarray(shape=(0, 0, 0))
        self.neighbour_tasks = {}
        self.tasks = {}
        self.deliveries = {}
        self.delivery_groups = {}
        self.vehicle_types = {}
        self.vehicles = {}

        # Job planning
        self.plan = Plan(instance=self, current_time=current_time)

        # Id generators
        self._task_id_generator = IdGenerator(0)
        self._delivery_id_generator = IdGenerator(0)
        self._vehicle_type_id_generator = IdGenerator(0)
        self._vehicle_id_generator = IdGenerator(0)
        self._delivery_group_id_generator = IdGenerator(0)

        # Objective function coefficients
        self.delivery_window_penalty = validate_float(delivery_window_penalty,
                                                      attr="delivery_window_penalty",
                                                      non_negative=True)
        self.drop_penalty = validate_float(drop_penalty, attr="drop_penalty", non_negative=True)
        self.drop_penalty_delta = validate_float(drop_penalty_delta, attr="drop_penalty_delta", non_negative=True)
        self.drop_penalty_slope = validate_float(drop_penalty_slope, attr="drop_penalty_slope", non_negative=True)
        self.max_lag_penalty = validate_float(max_lag_penalty, attr="max_lag_penalty", non_negative=True)
        self.delivery_window_right_margin = validate_int(delivery_window_right_margin,
                                                         attr="delivery_window_right_margin")
        self.span_penalty = validate_float(span_penalty, attr="span_penalty", non_negative=True)
        self.inf_distance = validate_int(inf_distance, attr="inf_distance", non_negative=True)
        self.inf_travel_time = validate_int(inf_travel_time, attr="inf_travel_time", non_negative=True)

    def update(self, vehicle_types=None, vehicles=None, deliveries=None, distance=None, travel_time=None):
        """
        Update an instance by adding the given vehicle_types, vehicles deliveries, distance and travel times.

        Args:
            vehicle_types: optional list of dict object with the vehicle types attributes. See
                Instance.create_vehicle_type for the list of accepted attributes.
            vehicles: optional list of dict object with the vehicle attributes. See
                Instance.create_vehicle for the list of accepted attributes.
            deliveries: optional list of dict object with the delivery attributes. See
                Instance.create_delivery for the list of accepted attributes.
            distance: optional list of dict object with the distance See
                Instance.add_distances for the list of accepted attributes.
            travel_time: optional list of dict object with the travel times. See
                Instance.add_travel_times for the list of accepted attributes.

        Example:
        ```python

        i = Instance()

        data = {
            "vehicle_types": [
                {"id": 0, "stop_time": 5},
                {"id": 1, "stop_time": 7},
            ],
            "vehicles": [
                {"id": 0, "vehicle_types_id": 0, "work_shift": (0, 60), "max_weight":100, "max_volume":100},
                {"id": 1, "vehicle_types_id": 0, "work_shift": (60, 120), "max_weight":100, "max_volume":100}
            ]
        }

        # Add new vehicle types and vehicles to the instance
        i.update(**data)
        ```
        """

        if vehicle_types is not None:
            for t in vehicle_types:
                self.create_vehicle_type(**t)

        if vehicles is not None:
            for v in vehicles:
                self.create_vehicle(**v)

        if deliveries is not None:
            for d in deliveries:
                self.create_delivery(**d)

        if distance:
            self.add_distances(distance)

        if travel_time:
            self.add_travel_times(travel_time)

    def create_pickup(self, **kwargs):
        """
        Create a pickup task.

        Args:
            **kwargs: named attributes of a task. See `routing.entity.task.Task` for the list of accepted attributes..

        Returns: a pickup task
        """
        task_id = self._task_id_generator.look_ahead()
        if 'id' in kwargs:
            given_id = kwargs.pop('id')
            if not given_id == task_id:
                raise ValidationError(f"Task id {given_id} is not valid. Expected sequential task ids.")

        p = Pickup(id=task_id, delivery_window_right_margin=self.delivery_window_right_margin, **kwargs)
        self._task_id_generator.next_id()
        self.tasks[p.id] = p
        self.plan.init_task_state(p.id)
        return p

    def create_dropoff(self, **kwargs):
        """
        Create a dropoff task.

        Args:
            **kwargs: named attributes of a task. See `routing.entity.task.Task` for the list of accepted attributes..

        Returns: a dropoff task
        """
        task_id = self._task_id_generator.look_ahead()
        if 'id' in kwargs:
            given_id = kwargs.pop('id')
            if not given_id == task_id:
                raise ValidationError(f"Task id {given_id} is not valid. Expected sequential task ids.")

        d = Dropoff(id=task_id, delivery_window_right_margin=self.delivery_window_right_margin, **kwargs)
        self._task_id_generator.next_id()
        self.tasks[d.id] = d
        self.plan.init_task_state(d.id)
        return d

    def create_delivery(self, pickup=None, dropoff=None, **kwargs):
        """
        Create a delivery, optionally if a pickup/dropoff is given it also create the picup/dropoff task.

        Args:
            pickup: an optional dict object with the pickup attributes. See `routing.entity.task.Task` for the list of
                attributes.
            dropoff: an optional a dict object with the dropoff attributes. See `routing.entity.task.Task` for the list of
                attributes.
            **kwargs: named attributes of a delivery. See `routing.entity.delivery.Delivery` for the list of accepted attributes..

        Returns: a delivery
        """
        delivery_id = self._delivery_id_generator.look_ahead()
        if 'id' in kwargs:
            given_id = kwargs.pop('id')
            if not given_id == delivery_id:
                raise ValidationError(f"Delivery id {given_id} is not valid. Expected sequential delivery ids.")

        if pickup is not None:
            pickup_object = self.create_pickup(**pickup)
            if 'pickup_id' in kwargs:
                raise ValidationError("Unexpected attribute pickup_id when pickup data is given")
            kwargs['pickup_id'] = pickup_object.id

        if dropoff is not None:
            dropoff_object = self.create_dropoff(**dropoff)
            if 'dropoff_id' in kwargs:
                raise ValidationError("Unexpected attribute dropoff_id when dropoff data is given")
            kwargs['dropoff_id'] = dropoff_object.id

        d = Delivery(id=delivery_id, **kwargs)
        self._delivery_id_generator.next_id()
        self.deliveries[d.id] = d

        # Set up delivery id
        self.tasks[d.pickup_id].delivery_id = d.id
        self.tasks[d.dropoff_id].delivery_id = d.id

        # Set up weight and volume associated with the task
        self.tasks[d.pickup_id].weight = d.weight
        self.tasks[d.pickup_id].volume = d.volume

        # dropoff has always negative weight and volume
        self.tasks[d.dropoff_id].weight = -d.weight
        self.tasks[d.dropoff_id].volume = -d.volume

        # Set the associated pickup/dropoff
        self.tasks[d.pickup_id].dropoff_id = d.dropoff_id
        self.tasks[d.dropoff_id].pickup_id = d.pickup_id

        if d.delivery_group_id != NONE_DELIVERY_GROUP:
            self.delivery_groups[d.delivery_group_id].add_delivery(d.id)
        return d

    def create_vehicle_type(self, **kwargs):
        """
        Create a vehicle type.

        Args:
            **kwargs: named attributes of a vehicle type. See `routing.entity.vehicle_type.VehicleType`
                for the list of accepted attributes..

        Returns: a delivery
        """

        vehicle_type_id = self._vehicle_type_id_generator.look_ahead()
        if 'id' in kwargs:
            given_id = kwargs.pop('id')
            if not given_id == vehicle_type_id:
                raise ValidationError(f"VehicleType id {given_id} is not valid. Expected sequential vehicle type ids.")

        t = VehicleType(id=vehicle_type_id, **kwargs)
        self._vehicle_type_id_generator.next_id()
        self.vehicle_types[t.id] = t
        return t

    def create_vehicle(self, job_id=None, **kwargs):
        """
        Create a vehicle and its associated job.

        Args:
            job_id: an optional id for the job to be created along with the vehicle. If None the job_id will be equal
                to the vehicle id.
            **kwargs: named attributes of a vehicle. See `routing.entity.vehicle.Vehicle`
                for the list of accepted attributes.

        Returns: a tuple with the vehicle as the first item and the job as the secon item.
        """
        vehicle_id = self._vehicle_id_generator.look_ahead()
        if 'id' in kwargs:
            given_id = kwargs.pop('id')
            if not given_id == vehicle_id:
                raise ValidationError(f"Vehicle id {given_id} is not valid. Expected sequential vehicle ids.")

        v = Vehicle(id=vehicle_id, **kwargs)
        self.vehicles[v.id] = v

        # Create an empty job for the new vehicle
        j = self.plan.create_job(id=(job_id if job_id is not None else v.id), vehicle_id=v.id, task_ids=[])
        self.plan.init_job_state(job_id=j.id)
        self._vehicle_id_generator.next_id()
        return v, j

    def create_delivery_group(self, *delivery_ids):
        """
        Create a delivery group for the given list of deliveries.

        Args:
            **delivery_ids: collection of delivery id to put in the same group

        Returns: the created delivery group
        """
        g = DeliveryGroup(id=self._delivery_group_id_generator.next_id())
        g.add_deliveries(*delivery_ids)
        for d in delivery_ids:
            self.deliveries[d].delivery_group_id = g.id
        self.delivery_groups[g.id] = g
        return g

    def add_deliveries(self, *deliveries):
        """
        Add a collection of deliveries to the instance.

        Args:
            **deliveries: collection of dict object with the delivery attributes.
                See `routing.entity.delivery.Delivery` for the list of accepted attributes..

        Returns: the created delivery group
        """
        for delivery_data in deliveries:
            self.create_delivery(**delivery_data)

    def add_distances(self, distances: List):
        """
        Add a collection of distances and compute the distance matrix.
        Args:
            **distances: collection of tuples object.
                Each tuple is like (int task_i_id, int task_j_id, int vehicle_type_id, int value)
        """
        for from_id, to_id, vehicle_type_id, value in distances:
            self._validate_task(from_id)
            self._validate_task(to_id)
            self._validate_vehicle_id(vehicle_type_id)
            self.distance[from_id, to_id, vehicle_type_id] = validate_int(value, attr="distance")
        self.compute_distance_matrix()

    def add_travel_times(self, travel_times):
        """
        Add a collection of travel times.
        This method also compute the travel time matrix and the neighbor tasks for each task.

        Args:
            **travel_times: collection of tuples object.
                Each tuple is like (int task_i_id, int task_j_id, int vehicle_type_id, int value)
        """
        for from_id, to_id, vehicle_type_id, value in travel_times:
            self._validate_task(from_id)
            self._validate_task(to_id)
            self._validate_vehicle_id(vehicle_type_id)
            self.travel_time[from_id, to_id, vehicle_type_id] = validate_int(value, attr="travel_time")
        self.compute_travel_time_matrix()
        self.compute_neighbour_tasks()

    def compute_neighbour_tasks(self):
        """
        Compute the neighbourhood of all the tasks by looking the travel time matrix.
        The neighborhood of a task is a sequence of task sorted by non-decreasing travel time.
        """
        for task_id in self.tasks.keys():
            for vehicle_type_id in self.vehicle_types.keys():
                neighborhood = np.argsort(self.travel_time_matrix[task_id, :, vehicle_type_id]).tolist()
                neighborhood.remove(task_id)
                self.neighbour_tasks[task_id, vehicle_type_id] = neighborhood

    def compute_distance_matrix(self):
        """
        Create the full distance matrix as a np.ndarray of integer with shape (n task, n task, n vehicle types)
        """

        self.distance_matrix = np.full((len(self.tasks), len(self.tasks), len(self.vehicle_types)),
                                       self.inf_distance,
                                       dtype=np.dtype("i"))
        for k, v in self.distance.items():
            (from_id, to_id, vehicle_type) = k
            self.distance_matrix[from_id, to_id, vehicle_type] = v

    def compute_travel_time_matrix(self):
        """
        Create the full travel time matrix as a np.ndarray of integer with shape (n task, n task, n vehicle types)
        """

        self.travel_time_matrix = np.full((len(self.tasks), len(self.tasks), len(self.vehicle_types)),
                                          self.inf_travel_time,
                                          dtype=np.dtype("i"))
        for k, v in self.travel_time.items():
            (from_id, to_id, vehicle_type) = k
            self.travel_time_matrix[from_id, to_id, vehicle_type] = v

    def get_neighbour_tasks(self, task_id, vehicle_type_id):
        return self.neighbour_tasks[task_id, vehicle_type_id]

    def get_distance(self, from_task_id, to_task_id, vehicle_type_id):
        return self.distance[from_task_id, to_task_id, vehicle_type_id]

    def get_travel_time(self, from_task_id, to_task_id, vehicle_type_id):
        return self.travel_time[from_task_id, to_task_id, vehicle_type_id]

    def get_delivery_group(self, delivery_id):
        return self.deliveries[delivery_id].delivery_group_id

    def get_vehicle_type(self, vehicle_id):
        return self.vehicles[vehicle_id].vehicle_type_id

    def get_pickup(self, delivery_id):
        return self.deliveries[delivery_id].pickup_id

    def get_dropoff(self, delivery_id):
        return self.deliveries[delivery_id].dropoff_id

    def get_max_lag(self, delivery_id):
        return self.deliveries[delivery_id].max_lag

    def get_task_weight(self, task_id):
        return self.tasks[task_id].weight

    def get_task_volume(self, task_id):
        return self.tasks[task_id].volume

    def get_service_time(self, task_id):
        return self.tasks[task_id].service_time

    def get_delivery_window(self, task_id):
        return self.tasks[task_id].delivery_window

    def get_vehicle_max_weight(self, vehicle_id):
        return self.vehicles[vehicle_id].max_weight

    def get_vehicle_max_volume(self, vehicle_id):
        return self.vehicles[vehicle_id].max_volume

    def get_unit_distance_cost(self, vehicle_id):
        return self.vehicles[vehicle_id].unit_distance_cost

    def get_geo_hash(self, task_id):
        return self.tasks[task_id].geo_hash

    def get_coordinates(self, task_id):
        return self.tasks[task_id].coordinates

    def get_stop_cost(self, vehicle_id):
        return self.vehicles[vehicle_id].stop_cost

    def get_work_shift(self, vehicle_id):
        return self.vehicles[vehicle_id].work_shift

    def get_stop_time(self, vehicle_type_id):
        return self.vehicle_types[vehicle_type_id].stop_time

    def has_required_skills(self, vehicle_id, delivery_id):
        """
        Check whether a vehicle has all the required skills for a delivery.
        """
        vehicle = self.vehicles[vehicle_id]
        delivery = self.deliveries[delivery_id]
        return all(s in vehicle.skills for s in delivery.skills)

    def has_compatible_work_shift(self, vehicle_id, delivery_id):
        """
        Check whether a vehicle work shift is compatible with the pickup and
        dropoff delivery windows of a delivery.
        """
        vehicle = self.vehicles[vehicle_id]
        pickup = self.tasks[self.deliveries[delivery_id].pickup_id]
        dropoff = self.tasks[self.deliveries[delivery_id].dropoff_id]
        return pickup.delivery_window[1] >= vehicle.work_shift[0] and dropoff.delivery_window[0] <= vehicle.work_shift[
            1]

    def get_latest_time(self):
        """
        Get the latest time instance among all the work shift.

        Returns: the max right endpoint among all the work shift.
        """
        return max(v.work_shift[1] for v in self.vehicles.values())

    def get_earliest_time(self):
        """
        Get the earliest time instance among all the work shift.

        Returns: the min left endpoint among all the work shift.
        """
        return min(v.work_shift[0] for v in self.vehicles.values())

    def compute_penalty(self, delivery_id):
        """
        Compute the penalty for dropping a delivery.

        The drop penalty change according to the priority of the delivery and is defined as:
            penalty = drop_penalty + drop_penalty_delta * exp(-drop_penalty_slope * x)
        where x is the remaining time to complete the first not completed task of the delivery.

        Args:
            delivery_id: the id of the delivery

        Returns: an integer that correspond to the penalty to drop the delivery
        """
        delivery = self.deliveries[delivery_id]

        if not self.plan.is_task_executed(delivery.pickup_id):
            next_task_id = delivery.pickup_id
        elif not self.plan.is_task_executed(delivery.dropoff_id):
            next_task_id = delivery.dropoff_id
        else:
            next_task_id = None  # delivery is already executed

        if next_task_id is not None:
            x = self.tasks[next_task_id].delivery_window[1] - self.plan.current_time
        else:
            x = 0

        return int(self.drop_penalty + self.drop_penalty_delta * math.e ** (- self.drop_penalty_slope * x))

    def update_delivery(self, *args, **kwargs):
        raise NotImplemented

    def cancel_delivery(self, *args, **kwargs):
        # TODO implement it: add an attribute to the delivery to mark it as cancelled. The algorithm then
        #  should not add it to any job.
        raise NotImplemented

    def _validate_task(self, task_id):
        if task_id not in self.tasks:
            raise UnexpectedTaskId(f"Task {task_id} not in the instance")

    def _validate_vehicle_id(self, vehicle_type_id):
        if vehicle_type_id not in self.vehicle_types:
            raise UnexpectedVehicleTypeId(f"Vehicle type {vehicle_type_id} not in the instance")
