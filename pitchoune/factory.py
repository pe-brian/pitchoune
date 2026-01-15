class Factory:
    """ A factory class to create instances of a specified base class.
    """
    
    def __init__(
        self,
        base_class,
        *args,
        **kwargs
    ):
        self._base_class = base_class
        self._args = args
        self._kwargs = kwargs

    def create(
        self,
        cls,
        *args,
        **kwargs
    ):
        """ Create an instance of the specified class.
        """
        if not issubclass(cls, self._base_class):
            raise ValueError(
                f"Class '{cls.__name__}' is not a subclass of '{self._base_class.__name__}'."
            )
        
        # Arguments de la factory d'abord, puis ceux de create()
        merged_args = self._args + args
        
        # kwargs de create() écrasent ceux de la factory (comportement standard)
        merged_kwargs = {**self._kwargs, **kwargs}
        
        return cls(*merged_args, **merged_kwargs)