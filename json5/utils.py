from __future__ import annotations
import typing
from typing import Callable, Any, Tuple, Type
from functools import singledispatch, update_wrapper
from json import JSONDecodeError
try:
    from functools import singledispatchmethod
except ImportError:
    def singledispatchmethod(func: Callable[..., Any]) -> Any:  # type: ignore[no-redef]
        dispatcher = singledispatch(func)

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return dispatcher.dispatch(args[1].__class__)(*args, **kwargs)

        wrapper.register = dispatcher.register  # type: ignore[attr-defined]
        update_wrapper(wrapper, func)
        return wrapper

__all__ = ['singledispatchmethod', 'JSON5DecodeError']

if typing.TYPE_CHECKING:
    from .tokenizer import JSON5Token


class JSON5DecodeError(JSONDecodeError):
    def __init__(self, msg: str, token: typing.Optional[JSON5Token]):
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

    def __reduce__(self) -> Tuple[Type[JSON5DecodeError], Tuple[str, typing.Optional[JSON5Token]]]:
        return self.__class__, (self.msg, self.token)
