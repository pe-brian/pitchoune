class Injector:

    def __init__(self) -> None:
        self._functions = {}

    def register_arg(self, function, key, value):
        if not function in self._functions:
            self._functions[function.__name__] = {}
        self._functions[function.__name__][key] = value

    def inject(self, function, *args, **kwargs):
        return function(*args, **kwargs, **self._functions[function.__name__])


injector = Injector()
