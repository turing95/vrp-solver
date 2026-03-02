class IdGenerator:
    """
    Class that generate sequential id starting from an initial integer.
    """

    def __init__(self, initial_id: int = 0):
        """
        Initialize the generator.

        Args:
            initial_id: the first id to generate.
        """
        self._next_id = initial_id

    def next_id(self):
        """
        Generate and return the next id.

        Returns: the generated id
        """
        generated_id = self._next_id
        self._next_id += 1
        return generated_id

    def look_ahead(self):
        """
        Look ahead to see which will be the next generated id.

        Returns: the next id that will be generated when calling next_id
        """
        return self._next_id


def validate_int(value, attr=None, allow_none=False, non_negative=False, non_positive=False):
    """
    Given a value check that is an integer and return it.
    """
    if not allow_none:
        if not isinstance(value, int):
            message = f"Expected {attr} to be an int, got {type(value)}" if attr is not None else f"Expected and integer."
            raise ValueError(message)
        elif non_negative and value < 0:
            message = f"Expected {attr} to be a non negative int, got {value}" if attr is not None else f"Expected a non negative integer."
            raise ValueError(message)
        elif non_positive and value > 0:
            message = f"Expected {attr} to be a non positive int, got {value}" if attr is not None else f"Expected a non positive integer."
            raise ValueError(message)
    return value


def validate_float(value, attr=None, allow_none=False, non_negative=False, non_positive=False):
    """
    Given a value check that is a float and return it.
    """
    if not allow_none:
        try:
            value = float(value)
        except ValueError:
            message = f"Expected {attr} to be an float, got {type(value)}" if attr is not None else f"Expected an float."
            raise ValueError(message)
        if non_negative and value < 0:
            message = f"Expected {attr} to be a non negative float, got {value}" if attr is not None else f"Expected a non negative float."
            raise ValueError(message)
        elif non_positive and value > 0:
            message = f"Expected {attr} to be a non positive float, got {value}" if attr is not None else f"Expected a non positive float."
            raise ValueError(message)

        return value


class Encoder:
    """
    A class that encode hashable object to a unique sequential id.
    """

    def __init__(self):
        self.encoded_value = {}  # map an encoded value to its id
        self.id_generator = IdGenerator()

    def _encode(self, value) -> int:
        """
        Given a value return a unique integer identifier.
        The identifier is unique w.r.t a single Encoder, two different encoders can have
        two different identifiers for the same value.

        Args:
            value: a hashable object

        Returns:
            a unique integer identifier for the given value
        """
        if value not in self.encoded_value:
            id = self.id_generator.next_id()
            self.encoded_value[value] = id

        return self.encoded_value[value]

    def encode(self, *values):
        """
        Encode one or multiple values.

        Args:
            *values: one or more values to encode

        Returns: either a single encoded value or a list of encoded values
        """
        if len(values) == 0:
            raise ArithmeticError("Expected at least one value to encode")
        elif len(values) == 1:
            return self._encode(values[0])
        else:
            return list(map(lambda value: self._encode(value), values))
