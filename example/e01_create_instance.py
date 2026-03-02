"""
*Create instance*

This is a simple script that demonstrates how to create an instance
with data stored in a config dictionary and in a data dictionary.
"""

import routing

# A dictionary with the configuration
config = {
    "delivery_window_penalty": 1,
    "drop_penalty": 1000,
    "max_lag_penalty": 5,
    "delivery_window_right_margin": 5,
    "span_penalty": 10,
}

# A dictionary with the instance data
vehicle_data = {
    "vehicle_types": [
        {"id": 0, "stop_time": 5},
        {"id": 1, "stop_time": 10},
    ],
    "vehicles": [
        {
            "id": 0, "vehicle_type_id": 0, "work_shift": (0, 100),
            "max_weight": 50,
            "max_volume": 50,
            "stop_cost": 10,
            "unit_distance_cost": 1,
            "skills": (0, 1, 2),
        }
    ],
}

# A dictionary with the deliveries data
deliveries_data = {
    "deliveries": [
        {
            "weight": 10,
            "volume": 5,
            "max_lag": 30,
            "skills": (0, 1),
            "pickup": {
                "id": 0,
                "delivery_window": (0, 120),
                "coordinates": (21, -157),
                "service_time": 5,
                "geo_hash": 0
            },
            "dropoff": {
                "id": 1,
                "delivery_window": (60, 180),
                "coordinates": (21, -158),
                "service_time": 3,
                "geo_hash": 1
            }
        }
    ],
    "distance": [
        (0, 1, 0, 11),
        (1, 0, 0, 9),
        (0, 1, 1, 11),
        (1, 0, 1, 9)
    ],
    "travel_time": [
        (0, 1, 0, 12),
        (1, 0, 0, 45),
        (0, 1, 1, 36),
        (1, 0, 1, 24)
    ]
}

# Create an instance with an initial configuration
instance = routing.Instance(**config)

# Add the vehicle data
instance.update(**vehicle_data)

# Add the deliveries data
instance.update(**deliveries_data)

