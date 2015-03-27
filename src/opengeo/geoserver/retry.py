from functools import wraps
from geoserver.catalog import Catalog

def retryMethodDecorator(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception, e:
            if "Errno 10053" in unicode(e):
                result = func(*args, **kwargs)
            else:
                raise e
        return result
    return decorator

class RetryCatalog(Catalog):
    def __getattribute__(self, attr_name):
        obj = super(RetryCatalog, self).__getattribute__(attr_name)
        if hasattr(obj, '__call__') and hasattr(obj, '__name__'):
            if not obj.__name__.startswith('__'):
                return retryMethodDecorator(obj)
        return obj

