from time import process_time


class SimulatorInterface(object):

    def __init__(self, fk_instance, start_time, end_time, init_group_fraction=0.5, group_size=1):
        """
        Abstract class for a generic simulator.

        Its main purpose is to simulate the dynamic arrival of new deliveries and keep track of the
        time needed to process them.

        It receives as argument the full knowledge instance with all the future data and the time horizon
        of the simulation (start_time, end_time).

        To perform a simulation just call the method run which performs the following operations:
        - it calls the init_event method passing an initial fraction of deliveries, the vehicle types and the vehicles
        - it iteratively calls the new_deliveries_event method passing the time and a new group of deliveries.

        Note the id of the delivery and task passed to the event callbacks are always sequential, this implies that
        the original ids are not preserved.
        """

        self.fk_instance = fk_instance
        self.start_time = start_time
        self.end_time = end_time
        self.init_cpu_seconds = 0
        self.events_cpu_seconds = []
        self.init_group_fraction = init_group_fraction
        self.group_size = group_size

        # The following variables keeps track of the next id to use and the map between old id and new id
        self.next_delivery_id = 0
        self.next_task_id = 0
        self.delivery_id_map = {}
        self.task_id_map = {}

    def run(self):
        """
        Run the simulation.
        """
        deliveries = list(self.fk_instance.deliveries.values())
        last_index = int(len(deliveries) * self.init_group_fraction)
        init_deliveries = deliveries[0: last_index]

        # Sort the remaining delivery so as they will be coherent with the event time
        future_deliveries = sorted(
            deliveries[last_index:],
            key=lambda d: self.fk_instance.get_delivery_window(d.pickup_id)[0]
        )
        event_groups = [[i, min(i + self.group_size, len(future_deliveries))] for i in
                        range(0, len(future_deliveries), self.group_size)]

        # Init event
        config = self._prepare_config_data()
        data = self._prepare_init_data(init_deliveries)
        t_start = process_time()
        self.init_event(config, data)
        t_end = process_time()
        self.init_cpu_seconds = t_end - t_start

        # Sequence of events
        # Set the smallest event time for the current iteration
        smallest_event_time = 0
        for group in event_groups:
            # compute event time as the average between the
            first_delivery = future_deliveries[group[0]]
            largest_event_time = self.fk_instance.get_delivery_window(first_delivery.pickup_id)[0]
            event_time = int((largest_event_time + smallest_event_time) / 2)

            # update the smallest event time for the next iteration
            if group[1] < len(future_deliveries):
                last_delivery = future_deliveries[group[1] - 1]
                smallest_event_time = self.fk_instance.get_delivery_window(last_delivery.pickup_id)[0]

            # generate the event
            data = self._prepare_delivery_data(future_deliveries[group[0]:group[1]])
            t_start = process_time()
            self.new_deliveries_event(event_time, data)
            t_end = process_time()
            self.events_cpu_seconds.append(t_end - t_start)

    def overall_events_cpu_seconds(self):
        return sum(self.events_cpu_seconds)

    def cpu_seconds(self):
        return self.init_cpu_seconds + self.overall_events_cpu_seconds()

    def init_event(self, deliveries, config):
        raise NotImplemented("The init_event function should be implemented into the child")

    def new_deliveries_event(self, event_time, deliveries):
        raise NotImplemented("The event function should be implemented into the child")

    def _prepare_config_data(self):
        return {
            "delivery_window_penalty": self.fk_instance.delivery_window_penalty,
            "drop_penalty": self.fk_instance.drop_penalty,
            "drop_penalty_delta": self.fk_instance.drop_penalty_delta,
            "drop_penalty_slope": self.fk_instance.drop_penalty_slope,
            "delivery_window_right_margin": self.fk_instance.delivery_window_right_margin,
            "max_lag_penalty": self.fk_instance.max_lag_penalty,
        }

    def _prepare_init_data(self, deliveries):
        return {
            "vehicles": [{
                "id": v.id,
                "vehicle_type_id": v.vehicle_type_id,
                "work_shift": v.work_shift,
                "max_weight": v.max_weight,
                "max_volume": v.max_volume,
                "stop_cost": v.stop_cost,
                "unit_distance_cost": v.unit_distance_cost,
                "skills": v.skills
            } for v in self.fk_instance.vehicles.values()],
            "vehicle_types": [{
                "id": t.id,
                "stop_time": t.stop_time
            } for t in self.fk_instance.vehicle_types.values()],
            **self._prepare_delivery_data(deliveries)
        }

    def _prepare_delivery_data(self, deliveries):
        deliveries_list = []
        distance_list = []
        travel_time_list = []

        for delivery in deliveries:
            pickup = self.fk_instance.tasks[delivery.pickup_id]
            dropoff = self.fk_instance.tasks[delivery.dropoff_id]

            delivery_id = self.next_delivery_id
            pickup_id = self.next_task_id
            dropoff_id = self.next_task_id + 1
            self.delivery_id_map[delivery.id] = delivery_id
            self.task_id_map[delivery.pickup_id] = pickup_id
            self.task_id_map[delivery.dropoff_id] = dropoff_id

            self.next_delivery_id += 1
            self.next_task_id += 2

            deliveries_list.append({
                "max_lag": delivery.max_lag,
                "weight": delivery.weight,
                "volume": delivery.volume,
                "skills": delivery.skills,
                "delivery_group_id": delivery.delivery_group_id,
                "id": delivery_id,

                "pickup": {
                    "delivery_window": pickup.delivery_window,
                    "geo_hash": pickup.geo_hash,
                    "service_time": pickup.service_time,
                    "coordinates": pickup.coordinates,
                    "id": pickup_id
                },

                "dropoff": {
                    "delivery_window": dropoff.delivery_window,
                    "geo_hash": dropoff.geo_hash,
                    "service_time": dropoff.service_time,
                    "coordinates": dropoff.coordinates,
                    "id": dropoff_id
                }
            })

            for key, value in self.fk_instance.distance.items():
                from_id, to_id, vehicle_type_id = key
                if from_id == delivery.pickup_id and to_id in self.task_id_map:
                    distance_list.append((pickup_id, self.task_id_map[to_id], vehicle_type_id, value))
                if to_id == delivery.pickup_id and from_id in self.task_id_map:
                    distance_list.append((self.task_id_map[from_id], pickup_id, vehicle_type_id, value))
                if from_id == delivery.dropoff_id and to_id in self.task_id_map:
                    distance_list.append((dropoff_id, self.task_id_map[to_id], vehicle_type_id, value))
                if to_id == delivery.dropoff_id and from_id in self.task_id_map:
                    distance_list.append((self.task_id_map[from_id], dropoff_id, vehicle_type_id, value))

            for key, value in self.fk_instance.travel_time.items():
                from_id, to_id, vehicle_type_id = key
                if from_id == delivery.pickup_id and to_id in self.task_id_map:
                    travel_time_list.append((pickup_id, self.task_id_map[to_id], vehicle_type_id, value))
                if to_id == delivery.pickup_id and from_id in self.task_id_map:
                    travel_time_list.append((self.task_id_map[from_id], pickup_id, vehicle_type_id, value))
                if from_id == delivery.dropoff_id and to_id in self.task_id_map:
                    travel_time_list.append((dropoff_id, self.task_id_map[to_id], vehicle_type_id, value))
                if to_id == delivery.dropoff_id and from_id in self.task_id_map:
                    travel_time_list.append((self.task_id_map[from_id], dropoff_id, vehicle_type_id, value))

        return {
            "deliveries": deliveries_list,
            "distance": distance_list,
            "travel_time": travel_time_list,
        }
