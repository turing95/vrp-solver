from routing import Instance
from routing.utils.compute_distance import compute_distance


def create_test_instance(delivery_window_right_margin=0, max_lag=100):
    """
    Set up an instance with 1 vehicle and 4 deliveries, 1 completed and the other partially completed,
    stop_time = 1
    service_time = 3
    stop_cost = 2
    unit_distance_cost = 3

    The travel times and distances are all equal and computed based on the position of the task.
    There are five deliveries:
        - 0 -> pickup 0 e dropoff 1 (Completed)
        - 1 -> pickup 2 and dropoff 3 (Pickup completed dropoff not)
        - 2 -> pickup 4 and dropoff 5
        - 3 -> pickup 6 and dropoff 7

    The tasks are positioned along a line as follows:

        0 ----- 2 ----- 1 ----- 4 ----- 6 ----- 3 ----- 7 ----- 5

    The distance between two consecutive tasks is 5.

    The above sequence is also the best one to complete all the tasks.

    The only job present is [0, 2, 1, 4], the executing task is 4
    and the arrival times of the competed task are:
        - 0 -> 0
        - 2 -> 9
        - 1 -> 18
        - 4 -> 29 (27 expected + 2 time units of delay)
    """

    instance = Instance(
        delivery_window_penalty=5,
        drop_penalty=100,
        delivery_window_right_margin=delivery_window_right_margin,
        max_lag_penalty=2,
    )

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

    # Delivery 0
    p = instance.create_pickup(delivery_window=(0, 70), coordinates=(0, 0), service_time=3, geo_hash=0)
    d = instance.create_pickup(delivery_window=(0, 70), coordinates=(0, 10), service_time=3, geo_hash=1)
    instance.create_delivery(
        pickup_id=p.id, dropoff_id=d.id, weight=5, volume=3, max_lag=max_lag, skills=[]
    )

    # Delivery 1
    p = instance.create_pickup(delivery_window=(0, 70), coordinates=(0, 5), service_time=3, geo_hash=2)
    d = instance.create_pickup(delivery_window=(0, 70), coordinates=(0, 25), service_time=3, geo_hash=3)
    instance.create_delivery(
        pickup_id=p.id, dropoff_id=d.id, weight=5, volume=3, max_lag=max_lag, skills=[]
    )

    # Delivery 2
    p = instance.create_pickup(delivery_window=(0, 70), coordinates=(0, 15), service_time=3, geo_hash=4)
    d = instance.create_pickup(delivery_window=(0, 70), coordinates=(0, 35), service_time=3, geo_hash=5)
    instance.create_delivery(
        pickup_id=p.id, dropoff_id=d.id, weight=5, volume=3, max_lag=max_lag, skills=[]
    )

    # Delivery 3
    p = instance.create_pickup(delivery_window=(0, 70), coordinates=(0, 20), service_time=3, geo_hash=6)
    d = instance.create_pickup(delivery_window=(0, 70), coordinates=(0, 30), service_time=3, geo_hash=7)
    instance.create_delivery(
        pickup_id=p.id, dropoff_id=d.id, weight=5, volume=3, max_lag=max_lag, skills=[]
    )

    # Compute distance and travel time
    compute_distance(instance)

    instance.plan.set_tasks(job_id=0, route=[(0, 0, 4), (2, 9, 13), (1, 18, 22), (4, 29, 33)])
    instance.plan.set_executing_task(job_id=0, task_id=4)

    return instance
