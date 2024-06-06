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


def load(key, value):
    def decorator(function):
        def wrapper(*args, **kwargs):
            injector.register_arg(function, key, value)
            return injector.inject(function, *args, **kwargs)
        return wrapper
    return decorator


@load(key="a", value=42)
@load(key="b", value=44)
def decorated_function(a, b):
    print(a, b)

decorated_function()