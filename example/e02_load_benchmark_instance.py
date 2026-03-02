"""
*Load sample instance*

This script demonstrates how to load the built-in sample instance.
"""

from benchmark.sample import load_instance

instance = load_instance()
print(f"tasks={len(instance.tasks)}, deliveries={len(instance.deliveries)}, vehicles={len(instance.vehicles)}")
