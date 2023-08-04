from __future__ import annotations

import math
import typing
from collections import deque
from typing import Any
from typing import Literal
from typing import NamedTuple

from .tokenizer import JSON5Token

__all__ = [
    'Node',
    'JSONText',
    'Value',
    'Key',
    'JSONObject',
    'JSONArray',
    'KeyValuePair',
    'Identifier',
    'Number',
    'Integer',
    'Float',
    'Infinity',
    'NaN',
    'String',
    'DoubleQuotedString',
    'SingleQuotedString',
    'BooleanLiteral',
    'NullLiteral',
    'UnaryOp',
    'TrailingComma',
    'Comment',
    'LineComment',
    'BlockComment',
]


class KeyValuePair(NamedTuple):
    key: Key
    value: Value


def walk(root: Node) -> typing.Generator[Node, None, None]:
    todo = deque([root])
    while todo:
        node: Node = todo.popleft()
        todo.extend(iter_child_nodes(node))
        yield node


def iter_child_nodes(node: Node) -> typing.Generator[Node, None, None]:
    for attr, value in iter_fields(node):
        if isinstance(value, Node):
            yield value
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, Node):
                    yield item


def iter_fields(node: Node) -> typing.Generator[tuple[str, Any], None, None]:
    for field_name in node._fields:
        try:
            value = getattr(node, field_name)
            yield field_name, value
        except AttributeError:
            pass


class Node:
    excluded_names = ['excluded_names', 'wsc_before', 'wsc_after', 'leading_wsc', 'tok', 'end_tok']

    def __init__(self, tok: JSON5Token | None = None, end_tok: JSON5Token | None = None):
        # Whitespace/Comments before/after the node
        self.wsc_before: list[str | Comment] = []
        self.wsc_after: list[str | Comment] = []
        self._tok: JSON5Token | None = tok
        self._end_tok: JSON5Token | None = end_tok

    @property
    def col_offset(self) -> int | None:
        if self._tok is None:
            return None
        return self._tok.colno

    @property
    def end_col_offset(self) -> int | None:
        if self._end_tok is None:
            return None
        return self._end_tok.end_colno

    @property
    def lineno(self) -> int | None:
        if self._tok is None:
            return None
        return self._tok.lineno

    @property
    def end_lineno(self) -> int | None:
        if self._end_tok is None:
            return None
        r = self._end_tok.end_lineno
        return r

    def __repr__(self) -> str:
        rep = (
            f"{self.__class__.__name__}("
            + ", ".join(
                f"{key}={repr(value)}"
                for key, value in self.__dict__.items()
                if not key.startswith('_') and key not in self.excluded_names
            )
            + ")"
        )
        return rep

    @property
    def _fields(self) -> list[str]:
        fields = [item for item in list(self.__dict__) if not item.startswith('_') and item not in self.excluded_names]
        fields.extend(['wsc_before', 'wsc_after'])
        return fields


class JSONText(Node):
    def __init__(self, value: Value, tok: JSON5Token | None = None, end_tok: JSON5Token | None = None):
        assert isinstance(value, Value)
        self.value: Value = value
        super().__init__(tok=tok, end_tok=tok)


class Value(Node):
    pass


class Key(Node):
    ...


class JSONObject(Value):
    def __init__(
        self,
        *key_value_pairs: KeyValuePair,
        trailing_comma: TrailingComma | None = None,
        leading_wsc: list[str | Comment] | None = None,
        tok: JSON5Token | None = None,
        end_tok: JSON5Token | None = None,
    ):
        keys: list[Key] = []
        values: list[Value] = []
        for key, value in key_value_pairs:
            assert isinstance(key, Key)
            assert isinstance(value, Value)
            keys.append(key)
            values.append(value)
        assert len(keys) == len(values)
        self.keys: list[Key] = keys
        self.values: list[Value] = values
        assert leading_wsc is None or all(isinstance(item, str) or isinstance(item, Comment) for item in leading_wsc)
        self.trailing_comma: TrailingComma | None = trailing_comma
        self.leading_wsc: list[str | Comment] = leading_wsc or []

        super().__init__(tok=tok, end_tok=end_tok)

    @property
    def key_value_pairs(self) -> list[KeyValuePair]:
        return list(KeyValuePair(key, value) for key, value in zip(self.keys, self.values))


class JSONArray(Value):
    def __init__(
        self,
        *values: Value,
        trailing_comma: TrailingComma | None = None,
        leading_wsc: list[str | Comment] | None = None,
        tok: JSON5Token | None = None,
        end_tok: JSON5Token | None = None,
    ):
        vals = list(values)
        for value in vals:
            assert isinstance(value, Value), f"Was expecting object with type Value. Got {type(value)}"
        assert leading_wsc is None or all(isinstance(item, str) or isinstance(item, Comment) for item in leading_wsc)
        self.values: list[Value] = vals
        self.trailing_comma: TrailingComma | None = trailing_comma
        self.leading_wsc: list[str | Comment] = leading_wsc or []

        super().__init__(tok=tok, end_tok=end_tok)


class Identifier(Key):
    def __init__(
        self, name: str, raw_value: str | None = None, tok: JSON5Token | None = None, end_tok: JSON5Token | None = None
    ):
        assert isinstance(name, str)
        if raw_value is None:
            raw_value = name
        assert isinstance(raw_value, str)
        assert len(name) > 0
        self.name: str = name
        self.raw_value: str = raw_value

        super().__init__(tok=tok, end_tok=tok)

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        return hash(self) == hash(other)


class Number(Value):
    ...


class Integer(Number):
    def __init__(
        self,
        raw_value: str,
        is_hex: bool = False,
        is_octal: bool = False,
        tok: JSON5Token | None = None,
        end_tok: JSON5Token | None = None,
    ):
        assert isinstance(raw_value, str)
        if is_hex and is_octal:
            raise ValueError("is_hex and is_octal are mutually exclusive")
        if is_hex:
            value = int(raw_value, 0)
        elif is_octal:
            if raw_value.startswith('0o'):
                value = int(raw_value, 8)
            else:
                value = int(raw_value.replace('0', '0o', 1), 8)
        else:
            value = int(raw_value)
        self.value: int = value
        self.raw_value: str = raw_value
        self.is_hex: bool = is_hex
        self.is_octal: bool = is_octal

        super().__init__(tok=tok, end_tok=end_tok or tok)


class Float(Number):
    def __init__(
        self,
        raw_value: str,
        exp_notation: str | None = None,
        tok: JSON5Token | None = None,
        end_tok: JSON5Token | None = None,
    ):
        value = float(raw_value)
        assert exp_notation is None or exp_notation in ('e', 'E')
        self.raw_value: str = raw_value
        self.exp_notation: str | None = exp_notation

        self.value: float = value
        super().__init__(tok=tok, end_tok=end_tok or tok)


class Infinity(Number):
    def __init__(self, negative: bool = False, tok: JSON5Token | None = None, end_tok: JSON5Token | None = None):
        self.negative: bool = negative

        super().__init__(tok=tok, end_tok=tok)

    @property
    def value(self) -> float:
        return math.inf if not self.negative else -math.inf

    @property
    def const(self) -> Literal['Infinity', '-Infinity']:
        if self.negative:
            return '-Infinity'
        else:
            return 'Infinity'


class NaN(Number):
    def __init__(self, tok: JSON5Token | None = None, end_tok: JSON5Token | None = None):
        super().__init__(tok=tok, end_tok=tok)

    @property
    def value(self) -> float:
        return math.nan

    @property
    def const(self) -> Literal['NaN']:
        return 'NaN'


class String(Value, Key):
    def __init__(
        self, characters: str, raw_value: str, tok: JSON5Token | None = None, end_tok: JSON5Token | None = None
    ):
        assert isinstance(raw_value, str)
        assert isinstance(characters, str)
        self.characters: str = characters
        self.raw_value: str = raw_value

        super().__init__(tok=tok, end_tok=tok)


class DoubleQuotedString(String):
    ...


class SingleQuotedString(String):
    ...


class BooleanLiteral(Value):
    def __init__(self, value: bool, tok: JSON5Token | None = None, end_tok: JSON5Token | None = None):
        assert value in (True, False)
        self.value: bool = value

        super().__init__(tok=tok, end_tok=tok)


class NullLiteral(Value):
    value = None

    def __init__(self, tok: JSON5Token | None = None, end_tok: JSON5Token | None = None):
        super().__init__(tok=tok, end_tok=tok)


class UnaryOp(Value):
    def __init__(
        self, op: Literal['-', '+'], value: Number, tok: JSON5Token | None = None, end_tok: JSON5Token | None = None
    ):
        assert op in ('-', '+')
        assert isinstance(value, Number)
        self.op: Literal['-', '+'] = op
        self.value: Number = value

        super().__init__(tok=tok, end_tok=end_tok)


class TrailingComma(Node):
    def __init__(self, tok: JSON5Token | None = None, end_tok: JSON5Token | None = None):
        super().__init__(tok=tok, end_tok=tok)  # Trailing comma is always a single COMMA token


class Comment(Node):
    def __init__(self, value: str, tok: JSON5Token | None = None, end_tok: JSON5Token | None = None):
        assert isinstance(value, str), f"Expected str got {type(value)}"
        self.value: str = value
        super().__init__(tok=tok, end_tok=tok)  # Comments are always a single token


class LineComment(Comment):
    ...


class BlockComment(Comment):
    ...
