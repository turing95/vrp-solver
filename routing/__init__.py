"""
The routing module provides the data structures and algorithms to solve
a dynamic vehicle routing pickup-and-delivery problem.

The module provides all the classes to describe an instance of the problem with
deliveries, tasks (both pickups and dropoffs), vehicle typologies, vehicles,
and delivery plans with jobs, along with the algorithms to solve the problem
instance.

The main classes to be used when defining and solving a given problem instance
are given as follows:
 - Instance (`routing.entity.instance.Instance`):
 it represents a single instance of the problem and provides all the methods to
 create and update it. It has also a delivery plan that store the information of
 the delivery jobs and their delivery progress.
 - routing.Policy (`routing.online_opt.policy.Policy`):
 it represents the live dispatching policy associated with an instance.
 Its main purpose is to dispatch a subset of deliveries starting from a potentially
 empty delivery plan.

"""
from routing.entity.instance import Instance
from routing.online_opt.policy import Policy
from routing.simulator import SimulatorInterface
from routing.entity.utils import Encoder

__all__ = ["entity", "utils", "online_opt", "simulator"]
__docformat__ = "google"
__version__ = '1.0.0'
