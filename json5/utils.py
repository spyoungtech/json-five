from __future__ import annotations

import typing
from json import JSONDecodeError

__all__ = ['JSON5DecodeError']

if typing.TYPE_CHECKING:
    from .tokenizer import JSON5Token


class JSON5DecodeError(JSONDecodeError):
    def __init__(self, msg: str, token: JSON5Token | None):
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

    def __reduce__(self) -> tuple[type[JSON5DecodeError], tuple[str, JSON5Token | None]]:
        return self.__class__, (self.msg, self.token)
