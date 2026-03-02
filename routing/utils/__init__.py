from .compute_distance import compute_distance
from .projecion import project_lat_lng


def get_instance_figure(*args, **kwargs):
    # Lazy import so matplotlib is only required when plotting utilities are used.
    from .plot_instance import get_instance_figure as _get_instance_figure
    return _get_instance_figure(*args, **kwargs)


__all__ = ["compute_distance", "project_lat_lng", "get_instance_figure"]
