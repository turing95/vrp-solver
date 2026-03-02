from routing import Instance
from routing.utils import compute_distance


def load_instance() -> Instance:
    """Build a small deterministic instance for examples and smoke tests."""
    instance = Instance(
        drop_penalty=5000,
        delivery_window_penalty=2,
        max_lag_penalty=1,
        delivery_window_right_margin=0,
    )

    bike_type = instance.create_vehicle_type(stop_time=2)
    car_type = instance.create_vehicle_type(stop_time=3)

    instance.create_vehicle(
        vehicle_type_id=bike_type.id,
        max_weight=0,
        max_volume=40,
        unit_distance_cost=1.0,
        work_shift=(0, 240),
        stop_cost=5,
    )
    instance.create_vehicle(
        vehicle_type_id=car_type.id,
        max_weight=0,
        max_volume=60,
        unit_distance_cost=1.2,
        work_shift=(0, 240),
        stop_cost=8,
    )

    # (pickup_coord, dropoff_coord, pickup_window, dropoff_window, volume)
    deliveries = [
        ((0, 0), (5, 1), (0, 80), (20, 120), 8),
        ((1, 7), (6, 8), (10, 100), (45, 160), 10),
        ((3, 2), (8, 3), (15, 120), (60, 180), 6),
        ((2, 10), (9, 11), (25, 130), (70, 210), 7),
        ((7, 0), (11, 2), (35, 140), (80, 220), 9),
        ((4, 6), (10, 7), (40, 150), (90, 230), 5),
    ]

    for idx, (pickup_coord, dropoff_coord, pickup_window, dropoff_window, volume) in enumerate(deliveries):
        pickup = instance.create_pickup(
            delivery_window=pickup_window,
            coordinates=pickup_coord,
            service_time=3,
            geo_hash=2 * idx,
        )
        dropoff = instance.create_dropoff(
            delivery_window=dropoff_window,
            coordinates=dropoff_coord,
            service_time=3,
            geo_hash=2 * idx + 1,
        )
        instance.create_delivery(
            pickup_id=pickup.id,
            dropoff_id=dropoff.id,
            volume=volume,
            max_lag=180,
        )

    compute_distance(instance)
    return instance
