"""
*Solve sample instance*

This script demonstrates how to use routing.Policy to
solve an instance.
"""

from routing import Policy
from benchmark.sample import load_instance
from routing.utils import get_instance_figure

instance = load_instance()
policy = Policy(instance)

sol = policy.route()  # Internal solution object, useful for debugging.
print(sol.compute_cost())
print(instance.plan)

fig = get_instance_figure(instance)
fig.show()
