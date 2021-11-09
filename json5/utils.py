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
        doc = getattr(token, 'doc', None)
        self.token = token
        self.index = index
        if token and doc:
            errmsg = f'{msg} in or near token {token.type} at'
            super().__init__(errmsg, doc, index)
        else:
            ValueError.__init__(self, msg)
            self.msg = msg
            self.lineno = lineno

    def __reduce__(self):
        return self.__class__, (self.msg, self.token)
