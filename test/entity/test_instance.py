from unittest import TestCase
import math

from routing import Instance
from routing.entity.error import ValidationError
from routing.entity.task import Pickup
from routing.entity.task import Dropoff
from routing.entity.delivery import Delivery
from routing.entity.vehicle_type import VehicleType
from routing.entity.vehicle import Vehicle
from routing.entity.constant import NONE_TASK
from test.fixtures.instance_with_state import create_test_instance


class TestInstance(TestCase):

    def setUp(self):
        # Empty instance
        self.instance = Instance()

        self.pickup_data = {
            "delivery_window": (0, 60),
            "coordinates": (3, 4),
            "service_time": 5,
            "geo_hash": 0
        }

        self.dropoff_data = {
            "delivery_window": (0, 60),
            "coordinates": (3, 4),
            "service_time": 5,
            "geo_hash": 0
        }

        self.delivery_data = {
            "weight": 1,
            "volume": 2,
            "max_lag": 3,
            "skills": [4, 5],
        }

        self.vehicle_type_data = {
            "stop_time": 1
        }

        self.vehicle_data = {
            "max_weight": 1,
            "max_volume": 2,
            "unit_distance_cost": 3,
            "skills": [4, 5],
            "work_shift": (0, 70),
            "stop_cost": 8
        }

    #
    # Test independency of the task, delivery,
    # vehicle, vehicle and job id
    #
    def test_id_independency(self):
        for i in range(10):
            pickup = self.instance.create_pickup(**self.pickup_data)
            dropoff = self.instance.create_dropoff(**self.dropoff_data)
            delivery = self.instance.create_delivery(
                pickup_id=pickup.id,
                dropoff_id=dropoff.id,
                **self.delivery_data
            )
            vehicle_type = self.instance.create_vehicle_type(**self.vehicle_type_data)
            vehicle, job = self.instance.create_vehicle(
                vehicle_type_id=vehicle_type.id,
                **self.vehicle_data
            )

            self.assertEqual(i*2, pickup.id)
            self.assertEqual(i*2 + 1, dropoff.id)
            self.assertEqual(i, delivery.id)
            self.assertEqual(i, vehicle_type.id)
            self.assertEqual(i, vehicle.id)
            self.assertEqual(i, job.id)

    #
    # Test pickup creation, getter and id
    #
    def test_pickup_creation(self):
        pickup = self.instance.create_pickup(**self.pickup_data)

        self.assertIs(type(pickup), Pickup)
        self.assertEqual(self.instance.tasks[pickup.id], pickup)
        self.assertEqual(5, self.instance.get_service_time(pickup.id))
        self.assertEqual(0, self.instance.get_geo_hash(pickup.id))
        self.assertEqual((0, 60), self.instance.get_delivery_window(pickup.id))
        self.assertEqual(0, self.instance.get_task_weight(pickup.id))
        self.assertEqual(0, self.instance.get_task_volume(pickup.id))

    def test_pickup_sequential_id(self):
        for i in range(10):
            pickup = self.instance.create_pickup(**self.pickup_data)
            self.assertEqual(i, pickup.id)

    def test_pickup_creation_with_id(self):
        for i in range(10):
            pickup = self.instance.create_pickup(id=i, **self.pickup_data)
            self.assertEqual(i, pickup.id)

    def test_pickup_creation_with_non_sequential_id(self):
        self.assertRaises(ValidationError, lambda: self.instance.create_pickup(id=1, **self.pickup_data))

    def test_pickup_creation_initialize_plan(self):
        pickup = self.instance.create_pickup(**self.pickup_data)
        self.assertEqual(0, self.instance.plan.arrival_time[pickup.id])
    #
    # Test dropoff creation, getter and id
    #
    def test_dropoff_creation(self):
        dropoff = self.instance.create_dropoff(**self.dropoff_data)

        self.assertIs(type(dropoff), Dropoff)
        self.assertEqual(5, self.instance.get_service_time(dropoff.id))
        self.assertEqual(0, self.instance.get_geo_hash(dropoff.id))
        self.assertEqual((0, 60), self.instance.get_delivery_window(dropoff.id))
        self.assertEqual(0, self.instance.get_task_weight(dropoff.id))
        self.assertEqual(0, self.instance.get_task_volume(dropoff.id))

    def test_dropoff_sequential_id(self):
        for i in range(10):
            dropoff = self.instance.create_dropoff(**self.dropoff_data)
            self.assertEqual(i, dropoff.id)

    def test_dropoff_creation_with_id(self):
        for i in range(10):
            dropoff = self.instance.create_dropoff(id=i, **self.pickup_data)
            self.assertEqual(i, dropoff.id)

    def test_dropoff_creation_with_non_sequential_id(self):
        self.assertRaises(ValidationError, lambda: self.instance.create_dropoff(id=1, **self.pickup_data))

    def test_dropoff_creation_initialize_plan(self):
        dropoff = self.instance.create_dropoff(**self.dropoff_data)
        self.assertEqual(0, self.instance.plan.arrival_time[dropoff.id])

    #
    # Test delivery creation, getter and id
    #
    def test_delivery_creation(self):
        pickup = self.instance.create_pickup(**self.pickup_data)
        dropoff = self.instance.create_dropoff(**self.dropoff_data)
        delivery = self.instance.create_delivery(
            pickup_id=pickup.id,
            dropoff_id=dropoff.id,
            **self.delivery_data
        )

        self.assertIs(type(delivery), Delivery)
        self.assertEqual(pickup.id, self.instance.get_pickup(delivery.id))
        self.assertEqual(dropoff.id, self.instance.get_dropoff(delivery.id))
        self.assertEqual(3, self.instance.get_max_lag(delivery.id))
        self.assertEqual(1, self.instance.get_task_weight(pickup.id))
        self.assertEqual(-1, self.instance.get_task_weight(dropoff.id))
        self.assertEqual(2, self.instance.get_task_volume(pickup.id))
        self.assertEqual(-2, self.instance.get_task_volume(dropoff.id))
        self.assertEqual(NONE_TASK, pickup.pickup_id)
        self.assertEqual(dropoff.id, pickup.dropoff_id)
        self.assertEqual(pickup.id, dropoff.pickup_id)
        self.assertEqual(NONE_TASK, dropoff.dropoff_id)

    def test_delivery_creation_with_delivery_group(self):
        group = self.instance.create_delivery_group()
        pickup = self.instance.create_pickup(**self.pickup_data)
        dropoff = self.instance.create_dropoff(**self.dropoff_data)
        delivery = self.instance.create_delivery(
            pickup_id=pickup.id,
            dropoff_id=dropoff.id,
            delivery_group_id=group.id,
            **self.delivery_data
        )

        self.assertEqual(group.id, self.instance.get_delivery_group(delivery.id))

    def test_delivery_creation_with_pickup_dropoff_data(self):
        delivery = self.instance.create_delivery(pickup=self.pickup_data,
                                                 dropoff=self.dropoff_data,
                                                 **self.delivery_data)
        self.assertEqual(0, delivery.id)

    def test_delivery_sequential_id(self):
        for i in range(10):
            pickup = self.instance.create_pickup(**self.pickup_data)
            dropoff = self.instance.create_dropoff(**self.dropoff_data)

            delivery = self.instance.create_delivery(
                pickup_id=pickup.id,
                dropoff_id=dropoff.id,
                **self.delivery_data
            )

            self.assertEqual(i, delivery.id)

    def test_delivery_creation_with_id(self):
        pickup = self.instance.create_pickup(**self.pickup_data)
        dropoff = self.instance.create_dropoff(**self.dropoff_data)
        delivery = self.instance.create_delivery(id=0, pickup_id=pickup.id, dropoff_id=dropoff.id, **self.delivery_data)
        self.assertEqual(0, delivery.id)

    def test_delivery_creation_with_non_sequential_id(self):
        self.assertRaises(ValidationError, lambda: self.instance.create_dropoff(id=1, **self.pickup_data))

    #
    # Test vehicle_type creation, getter and id
    #
    def test_vehicle_type_creation(self):
        vehicle_type = self.instance.create_vehicle_type(**self.vehicle_type_data)

        self.assertIs(type(vehicle_type), VehicleType)
        self.assertEqual(1, self.instance.get_stop_time(vehicle_type.id))

    def test_vehicle_type_sequential_id(self):
        for i in range(10):
            vehicle_type = self.instance.create_vehicle_type(**self.vehicle_type_data)
            self.assertEqual(i, vehicle_type.id)

    def test_v_type_creation_with_id(self):
        for i in range(10):
            vehicle_type = self.instance.create_vehicle_type(id=i, **self.vehicle_type_data)
            self.assertEqual(i, vehicle_type.id)

    def test_v_type_creation_with_non_sequential_id(self):
        self.assertRaises(ValidationError, lambda: self.instance.create_vehicle_type(id=1, **self.vehicle_type_data))

    #
    # Test vehicle_type creation, getter and id
    #
    def test_vehicle_creation(self):
        vehicle_type = self.instance.create_vehicle_type(**self.vehicle_type_data)
        vehicle, job = self.instance.create_vehicle(
            vehicle_type_id=vehicle_type.id,
            **self.vehicle_data
        )

        self.assertIs(type(vehicle), Vehicle)
        self.assertEqual(vehicle_type.id, self.instance.get_vehicle_type(vehicle.id))
        self.assertEqual(1, self.instance.get_vehicle_max_weight(vehicle.id))
        self.assertEqual(2, self.instance.get_vehicle_max_volume(vehicle.id))
        self.assertEqual((0, 70), self.instance.get_work_shift(vehicle.id))
        self.assertEqual(8, self.instance.get_stop_cost(vehicle.id))

        self.assertTrue(1, self.instance.plan.get_job_count())
        self.assertTrue(job.id in self.instance.plan.jobs.keys())

    def test_vehicle_sequential_id(self):
        for i in range(10):
            vehicle_type = self.instance.create_vehicle_type(**self.vehicle_type_data)
            vehicle, job = self.instance.create_vehicle(
                vehicle_type_id=vehicle_type.id,
                **self.vehicle_data
            )

            self.assertEqual(i, vehicle_type.id)
            self.assertEqual(i, vehicle.id)
            self.assertEqual(i, job.id)

    def test_vehicle_creation_with_id(self):
        vehicle_type = self.instance.create_vehicle_type(**self.vehicle_type_data)
        for i in range(10):
            vehicle, _ = self.instance.create_vehicle(id=i, vehicle_type_id=vehicle_type.id, **self.vehicle_data)
            self.assertEqual(i, vehicle.id)

    def test_vehicle_with_non_sequential_id(self):
        vehicle_type = self.instance.create_vehicle_type(**self.vehicle_type_data)
        self.assertRaises(ValidationError, lambda: self.instance.create_vehicle(id=1,
                                                                                vehicle_type_id=vehicle_type.id,
                                                                                **self.vehicle_data))

    def test_vehicle_creation_initialize_plan(self):
        vehicle_type = self.instance.create_vehicle_type(**self.vehicle_type_data)
        _, job = self.instance.create_vehicle(
            vehicle_type_id=vehicle_type.id,
            **self.vehicle_data
        )
        self.assertIn(job, self.instance.plan.jobs.values())
        self.assertEqual(NONE_TASK, self.instance.plan.executing_task[job.id])

    #
    # Test distances
    #

    def test_add_distance(self):
        pickup = self.instance.create_pickup(**self.pickup_data)
        dropoff = self.instance.create_dropoff(**self.dropoff_data)
        self.instance.create_delivery(id=0, pickup_id=pickup.id, dropoff_id=dropoff.id, **self.delivery_data)
        self.instance.create_vehicle_type(**self.vehicle_type_data)
        self.instance.create_vehicle_type(**self.vehicle_type_data)
        self.instance.add_distances([(0, 1, 0, 2),
                                     (0, 1, 1, 3),
                                     (1, 0, 0, 4),
                                     (1, 0, 1, 5)
                                     ])

        self.assertEqual(2, self.instance.get_distance(0, 1, 0))
        self.assertEqual(3, self.instance.get_distance(0, 1, 1))
        self.assertEqual(4, self.instance.get_distance(1, 0, 0))
        self.assertEqual(5, self.instance.get_distance(1, 0, 1))

    def test_add_travel_time(self):
        pickup = self.instance.create_pickup(**self.pickup_data)
        dropoff = self.instance.create_dropoff(**self.dropoff_data)
        self.instance.create_delivery(id=0, pickup_id=pickup.id, dropoff_id=dropoff.id, **self.delivery_data)
        self.instance.create_vehicle_type(**self.vehicle_type_data)
        self.instance.create_vehicle_type(**self.vehicle_type_data)
        self.instance.add_travel_times([(0, 1, 0, 2),
                                        (0, 1, 1, 3),
                                        (1, 0, 0, 4),
                                        (1, 0, 1, 5)
                                        ])

        self.assertEqual(2, self.instance.get_travel_time(0, 1, 0))
        self.assertEqual(3, self.instance.get_travel_time(0, 1, 1))
        self.assertEqual(4, self.instance.get_travel_time(1, 0, 0))
        self.assertEqual(5, self.instance.get_travel_time(1, 0, 1))

    def test_has_required_skill_method(self):
        # Create delivery
        pickup = self.instance.create_pickup(**self.pickup_data)
        dropoff = self.instance.create_dropoff(**self.dropoff_data)
        delivery = self.instance.create_delivery(
            pickup_id=pickup.id,
            dropoff_id=dropoff.id,
            **{**self.delivery_data, **{"skills": [0, 1]}}
        )

        vehicle_type = self.instance.create_vehicle_type(**self.vehicle_type_data)
        # Create vehicles
        vehicle1, _ = self.instance.create_vehicle(
            vehicle_type_id=vehicle_type.id,
            **{**self.vehicle_data, **{"skills": [0, 1]}}
        )

        vehicle2, _ = self.instance.create_vehicle(
            vehicle_type_id=vehicle_type.id,
            **{**self.vehicle_data, **{"skills": []}}
        )

        vehicle3, _ = self.instance.create_vehicle(
            vehicle_type_id=vehicle_type.id,
            **{**self.vehicle_data, **{"skills": [0]}}
        )

        vehicle4, _ = self.instance.create_vehicle(
            vehicle_type_id=vehicle_type.id,
            **{**self.vehicle_data, **{"skills": [2, 3]}}
        )

        self.assertTrue(self.instance.has_required_skills(vehicle1.id, delivery.id))
        self.assertFalse(self.instance.has_required_skills(vehicle2.id, delivery.id))
        self.assertFalse(self.instance.has_required_skills(vehicle3.id, delivery.id))
        self.assertFalse(self.instance.has_required_skills(vehicle4.id, delivery.id))

    def test_has_compatible_work_shift_method(self):
        # Create vehicles
        vehicle_type = self.instance.create_vehicle_type(**self.vehicle_type_data)
        vehicle, _ = self.instance.create_vehicle(
            vehicle_type_id=vehicle_type.id,
            **{**self.vehicle_data, **{"work_shift": (20, 30)}}
        )

        # Create delivery
        p = self.instance.create_pickup(**{**self.pickup_data, **{"delivery_window": (20, 22)}})
        d = self.instance.create_dropoff(**{**self.dropoff_data, **{"delivery_window": (28, 30)}})
        delivery1 = self.instance.create_delivery(pickup_id=p.id, dropoff_id=d.id, **self.delivery_data)

        p = self.instance.create_pickup(**{**self.pickup_data, **{"delivery_window": (18, 20)}})
        d = self.instance.create_dropoff(**{**self.dropoff_data, **{"delivery_window": (30, 32)}})
        delivery2 = self.instance.create_delivery(pickup_id=p.id, dropoff_id=d.id, **self.delivery_data)

        p = self.instance.create_pickup(**{**self.pickup_data, **{"delivery_window": (15, 19)}})
        d = self.instance.create_dropoff(**{**self.dropoff_data, **{"delivery_window": (28, 29)}})
        delivery3 = self.instance.create_delivery(pickup_id=p.id, dropoff_id=d.id, **self.delivery_data)

        p = self.instance.create_pickup(**{**self.pickup_data, **{"delivery_window": (21, 22)}})
        d = self.instance.create_dropoff(**{**self.dropoff_data, **{"delivery_window": (31, 35)}})
        delivery4 = self.instance.create_delivery(pickup_id=p.id, dropoff_id=d.id, **self.delivery_data)

        p = self.instance.create_pickup(**{**self.pickup_data, **{"delivery_window": (15, 19)}})
        d = self.instance.create_dropoff(**{**self.dropoff_data, **{"delivery_window": (31, 35)}})
        delivery5 = self.instance.create_delivery(pickup_id=p.id, dropoff_id=d.id, **self.delivery_data)

        self.assertTrue(self.instance.has_compatible_work_shift(vehicle.id, delivery1.id))
        self.assertTrue(self.instance.has_compatible_work_shift(vehicle.id, delivery2.id))
        self.assertFalse(self.instance.has_compatible_work_shift(vehicle.id, delivery3.id))
        self.assertFalse(self.instance.has_compatible_work_shift(vehicle.id, delivery4.id))
        self.assertFalse(self.instance.has_compatible_work_shift(vehicle.id, delivery5.id))

    def test_compute_penalty(self):
        instance = create_test_instance()  # an instance with a partial plan
        instance.drop_penalty = 1000
        instance.drop_penalty_delta = 500
        instance.drop_penalty_slope = 0.1

        # Delivery 0 completed -> drop penalty should be the min possible
        # Delivery 1 partially completed -> drop penalty computed according the dropoff task
        # Delivery 2 not completed -> drop penalty computed according the pickup
        instance.plan.set_tasks(0, [(0, 0, 4), (2, 20, 24), (1, 30, 34), (4, 40, 44)])
        instance.plan.set_executing_task(0, 1)
        instance.tasks[3].delivery_window = (0, 20)
        instance.tasks[4].delivery_window = (0, 40)

        self.assertEqual(1500, instance.compute_penalty(0))
        self.assertEqual(int(1000 + 500 * math.e ** (-0.1 * 20)), instance.compute_penalty(1))
        self.assertEqual(int(1000 + 500 * math.e ** (-0.1 * 40)), instance.compute_penalty(2))
