class IO:
    """Base class for IO operations."""
    def __init__(self, suffix: str):
        self._suffix = suffix

    @property
    def suffix(self) -> str:
        return self._suffix
    
    def serialize(self, *args, **kwargs) -> None:
        """Serialize data to a file."""
        pass

    def deserialize(self, *args, **kwargs) -> None:
        """Deserialize data from a file."""
        pass
