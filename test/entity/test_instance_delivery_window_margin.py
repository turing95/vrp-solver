from unittest import TestCase

from routing import Instance
from routing.entity.error import ValidationError


class TestInstanceDeliveryWindowMargin(TestCase):

    def setUp(self):
        # Empty instance
        self.instance = Instance(delivery_window_right_margin=10)

        self.task_data = {
            "delivery_window": (0, 60),
            "coordinates": (3, 4),
            "service_time": 5,
            "geo_hash": 0
        }

    def test_case_0(self):
        """correctly set the delivery window"""

        pickup = self.instance.create_pickup(**self.task_data)
        dropoff = self.instance.create_dropoff(**self.task_data)

        self.assertEqual((0, 60), pickup.delivery_window)
        self.assertEqual(10, pickup.delivery_window_right_margin)
        self.assertEqual((0, 60), dropoff.delivery_window)
        self.assertEqual(10, dropoff.delivery_window_right_margin)

    def test_case_1(self):
        """Raise exception when right endpoint is smaller than left endpoin"""

        self.task_data["delivery_window"] = (10, 9)
        self.assertRaises(ValidationError, lambda: self.instance.create_pickup(**self.task_data))
        self.assertRaises(ValidationError, lambda: self.instance.create_dropoff(**self.task_data))

    def test_case_2(self):
        """Raise exception when right endpoint is smaller than left endpoint include the margin"""

        self.task_data["delivery_window"] = (10, 19)
        self.assertRaises(ValidationError, lambda: self.instance.create_pickup(**self.task_data))
        self.assertRaises(ValidationError, lambda: self.instance.create_dropoff(**self.task_data))

    def test_case_3(self):
        """Raise exception when left endpoint is negative"""

        self.task_data["delivery_window"] = (-10, 0)
        self.assertRaises(ValueError, lambda: self.instance.create_pickup(**self.task_data))
        self.assertRaises(ValueError, lambda: self.instance.create_dropoff(**self.task_data))
