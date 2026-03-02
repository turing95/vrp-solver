"""
*Create instance*

This is a simple script that demonstrates how to create an instance
with one delivery (composed by a pickup task and a dropoff task),
two vehicles type and one vehicle.
"""

import routing

# Create an empty instance
instance = routing.Instance()

# Create two vehicle types
bike_type = instance.create_vehicle_type(stop_time=2)
cargo_bike_type = instance.create_vehicle_type(stop_time=3)

# Create a vehicle
bike_1 = instance.create_vehicle(
    vehicle_type_id=bike_type.id,
    max_weight=100,
    max_volume=50,
    unit_distance_cost=1.2,
    work_shift=(0, 240),
    stop_cost=10
)

# Create a new pickup, a new dropoff, and a new delivery
pickup = instance.create_pickup(
    delivery_window=(0, 120),
    coordinates=(21, -157),
    service_time=5,
    geo_hash=0
)

dropoff = instance.create_dropoff(
    delivery_window=(60, 180),
    coordinates=(21, -158),
    service_time=3,
    geo_hash=1
)

delivery = instance.create_delivery(
    pickup_id=pickup.id,
    dropoff_id=dropoff.id,
    weight=10,
    volume=5,
    max_lag=30,
    skills=[0, 1]
)

instance.add_distances([(pickup.id, dropoff.id, bike_type.id, 11),
                        (dropoff.id, pickup.id, bike_type.id, 9),
                        (pickup.id, dropoff.id, cargo_bike_type.id, 11),
                        (dropoff.id, pickup.id, cargo_bike_type.id, 9)])

instance.add_travel_times([(pickup.id, dropoff.id, bike_type.id, 12),
                           (dropoff.id, pickup.id, bike_type.id, 45),
                           (pickup.id, dropoff.id, cargo_bike_type.id, 36),
                           (dropoff.id, pickup.id, cargo_bike_type.id, 24)])
