class RoutingError(Exception):
    pass


class ValidationError(RoutingError):
    """Raise when an entity or an argument is not valid"""
    pass


class UnexpectedJobId(RoutingError):
    """Raise when a job id passed as argument and either does not exist or is not valid"""
    pass


class UnexpectedTaskId(RoutingError):
    """Raise when a task id passed as argument and either does not exist or is not valid"""
    pass


class UnexpectedDeliveryId(RoutingError):
    """Raise when a delivery id passed as argument and either does not exist or is not valid"""
    pass


class UnexpectedVehicleTypeId(RoutingError):
    """Raise when a vehicle type id passed as argument and either does not exist or is not valid"""
    pass


class TimeOutException(RoutingError):
    """Raise when the available computation time is expired"""
    pass
