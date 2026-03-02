# VRP Solver

A Python/Cython solver for dynamic vehicle routing pickup-and-delivery instances.

## Highlights
- Cython-accelerated core search/insertion routines
- Rich domain model for tasks, deliveries, vehicles, and plans
- Online dispatch policy (`routing.Policy`) for continuously updated instances
- Simulation helpers and benchmark/example scripts

## Installation
From source:

```bash
pip install git+https://github.com/turing95/vrp-solver.git
```

If you also want plotting helpers:

```bash
pip install "git+https://github.com/turing95/vrp-solver.git#egg=routing[plot]"
```

## Quick Usage
```python
from routing import Policy
from benchmark.sample import load_instance

instance = load_instance()
policy = Policy(instance)
policy.route()

print(instance.plan)
```

## Development
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest -q
```

## Examples
- `example/e00_create_instance.py`: build an instance manually
- `example/e03_solve_instance.py`: solve a sample instance
- `example/e05_simulation.py`: run a simple event simulation

## Documentation
The API docs are generated from docstrings using `pdoc`.

```bash
pip install pdoc
pdoc --docformat google routing
```

## License
Apache 2.0. See `LICENSE`.
