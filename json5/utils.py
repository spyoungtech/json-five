from functools import singledispatch, update_wrapper
from json import JSONDecodeError
try:
    from functools import singledispatchmethod
except ImportError:
    def singledispatchmethod(func):
        dispatcher = singledispatch(func)

        def wrapper(*args, **kwargs):
            return dispatcher.dispatch(args[1].__class__)(*args, **kwargs)

        wrapper.register = dispatcher.register
        update_wrapper(wrapper, func)
        return wrapper


class JSON5DecodeError(JSONDecodeError):
    def __init__(self, msg, token):
        lineno = getattr(token, 'lineno', 0)
        index = getattr(token, 'index', 0)
        if token:
            errmsg = f'{msg}: at line {lineno} index {index} token={token.type}'
        else:
            errmsg = msg
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.lineno = lineno
        self.index = index
        self.token = token

    def __reduce__(self):
        return self.__class__, (self.msg, self.token)
