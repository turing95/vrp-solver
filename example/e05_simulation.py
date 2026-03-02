"""
*Simulation*

This script demonstrates how to use SimulatorInterface with a sample instance.
"""

from datetime import datetime
from pathlib import Path

import routing
from benchmark.sample import load_instance
from routing.simulator import SimulatorInterface
from routing.utils import get_instance_figure


class Simulator(SimulatorInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = None
        self.policy = None

    def init_event(self, config, data):
        self.instance = routing.Instance(**config)
        self.instance.update(**data)
        self.policy = routing.Policy(self.instance)
        self.policy.route(resolution_time=10)
        self.save_plot_instance()

    def new_deliveries_event(self, event_time, data):
        self.instance.update(**data)
        self.instance.plan.set_current_time(event_time, set_executing_task=True)
        self.policy.route(resolution_time=5)
        self.save_plot_instance()

    def save_plot_instance(self):
        fig = get_instance_figure(self.instance)
        Path("figures").mkdir(parents=True, exist_ok=True)
        fig.savefig(f"figures/i-{self.instance.plan.current_time}-{datetime.now().isoformat()}.jpg")

    def finalize_run(self):
        self.instance.plan.set_current_time(self.instance.get_latest_time(), set_executing_task=True)
        self.save_plot_instance()


def main():
    source_instance = load_instance()
    start_time = source_instance.get_earliest_time()
    end_time = source_instance.get_latest_time()

    simulator = Simulator(source_instance, start_time, end_time, group_size=2)
    simulator.run()
    simulator.finalize_run()


if __name__ == "__main__":
    main()
