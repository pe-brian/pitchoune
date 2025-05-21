class SuperFactory:
    """A factory class that creates instances of various classes based on the provided class name."""
    def create(self, factory_cls, *args, **kwargs):
        """Create an instance of a class using the registered factory."""
        return factory_cls(*args, **kwargs)
