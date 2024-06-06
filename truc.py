def load(key, value):
    def decorator(func):
        if not hasattr(func, '_defaults'):
            func._defaults = {}
        func._defaults[key] = value
        return func
    return decorator

def inject_params(func):
    def wrapper(*args, **kwargs):
        if hasattr(func, '_defaults'):
            kwargs = {**func._defaults, **kwargs}
        return func(*args, **kwargs)
    return wrapper

@load(key="a", value=42)
@load(key="b", value=44)
def decorated_function(a, b):
    print(a, b)

decorated_function()
