"""
*Solve instance with pre-filled plan*

This script demonstrates how to start from a partial plan and re-dispatch.
"""

from routing import Policy
from benchmark.sample import load_instance
from routing.utils import get_instance_figure

instance = load_instance()
policy = Policy(instance)

# Build two partial job routes using existing task ids.
all_task_ids = sorted(instance.tasks.keys())
job0_route = [(tid, 20 + idx * 10, 25 + idx * 10) for idx, tid in enumerate(all_task_ids[:4])]
job1_route = [(tid, 30 + idx * 12, 35 + idx * 12) for idx, tid in enumerate(all_task_ids[4:8])]

instance.plan.set_tasks(job_id=0, route=job0_route)
instance.plan.set_tasks(job_id=1, route=job1_route)
instance.plan.set_current_time(80, set_executing_task=True)

print("Before routing")
print(instance.plan)

policy.route()

print("After routing")
print(instance.plan)

fig = get_instance_figure(instance)
fig.show()
