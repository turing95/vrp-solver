import math


def project_lat_lng(coordinates, center):
    """
    Given a coordinate (latitude, longitude) and a center (latitude0, longitude0) project the coordinate
    with the equirectangular projection.

    Args:
        coordinates: a pair (latitude, longitude)
        center: a pair (latitude, longitude) representing the center of the datum

    Returns:
        a pair of projected coordinate (x, y)
    """
    lat, lon = coordinates
    lat0, lon0 = center

    r = 6371000  # radius of earth in m

    x = int(r * ((lon - lon0) * math.pi / 180) * math.cos((lat0 * math.pi / 180)))
    y = int(r * ((lat - lat0) * math.pi / 180))
    return x, y
