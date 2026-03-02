import math


def compute_distance(instance):
    instance.distance = {}
    instance.travel_time = {}
    distances = []

    for vehicle_type in instance.vehicle_types.values():
        for task_i in instance.tasks.values():
            for task_j in instance.tasks.values():
                distance = int(math.sqrt((task_i.coordinates[0] - task_j.coordinates[0]) ** 2
                                         + (task_i.coordinates[1] - task_j.coordinates[1]) ** 2))
                distances.append((task_i.id, task_j.id, vehicle_type.id, distance))

    instance.add_distances(distances)
    instance.add_travel_times(distances)
