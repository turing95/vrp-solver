from routing import Instance
from routing.utils.compute_distance import compute_distance


def create_test_instance():
    """
    Set up an instance with 3 deliveries and 1 vehicle.
    stop_time = 1
    service_time = 3
    stop_cost = 2
    unit_distance_cost = 3

    The travel times and distances are all equal and computed based on the position of the task.
    There are three deliveries:
        - 0 -> pickup 0 e dropoff 1
        - 1 -> pickup 2 and dropoff 3
        - 2 -> pickup 4 and dropoff 5

    The tasks are positioned along a line as follows:

        0 ---(5)--- 2 ---(5)--- 4 ---(5)--- 3 ---(5)--- 5 ---(5)--- 1

    Between brackets is indicated the distance from one task to another.

    The above sequence is also the best one to complete all the tasks.

    The only job present is empty.
    """

    instance = Instance(
        delivery_window_penalty=5,
        drop_penalty=100)

    vehicle_type_1 = instance.create_vehicle_type(stop_time=1)

    _, job = instance.create_vehicle(
        vehicle_type_id=vehicle_type_1.id,
        max_weight=15,
        max_volume=9,
        unit_distance_cost=3,
        skills=[1, 2],
        work_shift=(0, 100),
        stop_cost=2
    )

    # Delivery 1
    p1 = instance.create_pickup(delivery_window=(0, 60), coordinates=(0, 0), service_time=3, geo_hash=0)
    d1 = instance.create_pickup(delivery_window=(0, 60), coordinates=(0, 25), service_time=3, geo_hash=1)
    instance.create_delivery(
        pickup_id=p1.id, dropoff_id=d1.id, weight=5, volume=3, max_lag=100, skills=[]
    )

    # Delivery 2
    p2 = instance.create_pickup(delivery_window=(0, 60), coordinates=(0, 5), service_time=3, geo_hash=2)
    d2 = instance.create_pickup(delivery_window=(0, 60), coordinates=(0, 15), service_time=3, geo_hash=3)
    instance.create_delivery(
        pickup_id=p2.id, dropoff_id=d2.id, weight=5, volume=3, max_lag=100, skills=[]
    )

    # Delivery 3
    p3 = instance.create_pickup(delivery_window=(0, 60), coordinates=(0, 10), service_time=3, geo_hash=4)
    d3 = instance.create_pickup(delivery_window=(0, 60), coordinates=(0, 20), service_time=3, geo_hash=5)
    instance.create_delivery(
        pickup_id=p3.id, dropoff_id=d3.id, weight=5, volume=3, max_lag=100, skills=[]
    )

    # Compute distance and travel time
    compute_distance(instance)

    return instance
