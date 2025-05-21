class Factory:
    """A factory class to create instances of a specified base class."""
    def __init__(self, base_class, *args, **kwargs):
        self._base_class = base_class
        self._args = args
        self._kwargs = kwargs

    def create(self, cls, *args, **kwargs):
        """Create an instance of the specified class."""
        if not issubclass(cls, self._base_class):
            raise ValueError(f"Class '{cls.__name__}' is not a subclass of '{self._base_class.__name__}'.")
        return cls(*args, *self._args, **{k: kwargs.get(k) or self._kwargs.get(k) for k in kwargs.keys() | self._kwargs.keys()})
