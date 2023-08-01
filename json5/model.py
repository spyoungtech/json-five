from __future__ import annotations

import math
from typing import Any
from typing import Literal

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


class Node:
    excluded_names = ['excluded_names', 'wsc_before', 'wsc_after', 'leading_wsc']

    def __init__(self) -> None:
        # Whitespace/Comments before/after the node
        self.wsc_before: list[str | Comment] = []
        self.wsc_after: list[str | Comment] = []

    def __repr__(self) -> str:
        rep = (
            f"{self.__class__.__name__}("
            + ", ".join(
                f"{key}={repr(value)}" for key, value in self.__dict__.items() if key not in self.excluded_names
            )
            + ")"
        )
        return rep


class JSONText(Node):
    def __init__(self, value: Value):
        assert isinstance(value, Value)
        self.value: Value = value
        super().__init__()


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
    ):
        kvps = list(key_value_pairs)
        for kvp in kvps:
            assert isinstance(kvp, KeyValuePair), f"Expected key value pair, got {type(kvp)}"
        assert leading_wsc is None or all(isinstance(item, str) or isinstance(item, Comment) for item in leading_wsc)
        self.key_value_pairs: list[KeyValuePair] = kvps
        self.trailing_comma: TrailingComma | None = trailing_comma
        self.leading_wsc: list[str | Comment] = leading_wsc or []
        self.tok: JSON5Token | None = tok
        super().__init__()


class JSONArray(Value):
    def __init__(
        self,
        *values: Value,
        trailing_comma: TrailingComma | None = None,
        leading_wsc: list[str | Comment] | None = None,
        tok: JSON5Token | None = None,
    ):
        vals = list(values)
        for value in vals:
            assert isinstance(value, Value), f"Was expecting object with type Value. Got {type(value)}"
        assert leading_wsc is None or all(isinstance(item, str) or isinstance(item, Comment) for item in leading_wsc)
        self.values: list[Value] = vals
        self.trailing_comma: TrailingComma | None = trailing_comma
        self.leading_wsc: list[str | Comment] = leading_wsc or []
        self.tok: JSON5Token | None = tok
        super().__init__()


class KeyValuePair(Node):
    def __init__(self, key: Key, value: Value, tok: JSON5Token | None = None):
        assert isinstance(key, Key)
        assert isinstance(value, Value)
        self.key: Key = key
        self.value: Value = value
        self.tok: JSON5Token | None = tok
        super().__init__()


class Identifier(Key):
    def __init__(self, name: str, raw_value: str | None = None, tok: JSON5Token | None = None):
        assert isinstance(name, str)
        if raw_value is None:
            raw_value = name
        assert isinstance(raw_value, str)
        assert len(name) > 0
        self.name: str = name
        self.raw_value: str = raw_value
        self.tok: JSON5Token | None = tok
        super().__init__()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        return hash(self) == hash(other)


class Number(Value):
    ...


class Integer(Number):
    def __init__(self, raw_value: str, is_hex: bool = False, is_octal: bool = False, tok: JSON5Token | None = None):
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
        self.tok: JSON5Token | None = tok
        super().__init__()


class Float(Number):
    def __init__(self, raw_value: str, exp_notation: str | None = None, tok: JSON5Token | None = None):
        value = float(raw_value)
        assert exp_notation is None or exp_notation in ('e', 'E')
        self.raw_value: str = raw_value
        self.exp_notation: str | None = exp_notation
        self.tok: JSON5Token | None = tok
        self.value: float = value
        super().__init__()


class Infinity(Number):
    def __init__(self, negative: bool = False, tok: JSON5Token | None = None):
        self.negative: bool = negative
        self.tok: JSON5Token | None = tok
        super().__init__()

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
    def __init__(self, tok: JSON5Token | None = None):
        self.tok: JSON5Token | None = tok
        super().__init__()

    @property
    def value(self) -> float:
        return math.nan

    @property
    def const(self) -> Literal['NaN']:
        return 'NaN'


class String(Value, Key):
    ...


class DoubleQuotedString(String):
    def __init__(self, characters: str, raw_value: str, tok: JSON5Token | None = None):
        assert isinstance(raw_value, str)
        assert isinstance(characters, str)
        self.characters: str = characters
        self.raw_value: str = raw_value
        self.tok: JSON5Token | None = tok
        super().__init__()


class SingleQuotedString(String):
    def __init__(self, characters: str, raw_value: str, tok: JSON5Token | None = None):
        assert isinstance(raw_value, str)
        assert isinstance(characters, str)
        self.characters: str = characters
        self.raw_value: str = raw_value
        self.tok: JSON5Token | None = tok
        super().__init__()


class BooleanLiteral(Value):
    def __init__(self, value: bool, tok: JSON5Token | None = None):
        assert value in (True, False)
        self.value: bool = value
        self.tok: JSON5Token | None = tok
        super().__init__()


class NullLiteral(Value):
    value = None

    def __init__(self, tok: JSON5Token | None = None):
        self.tok: JSON5Token | None = None
        super().__init__()


class UnaryOp(Value):
    def __init__(self, op: Literal['-', '+'], value: Number, tok: JSON5Token | None = None):
        assert op in ('-', '+')
        assert isinstance(value, Number)
        self.op: Literal['-', '+'] = op
        self.value: Number = value
        self.tok: JSON5Token | None = tok
        super().__init__()


class TrailingComma(Node):
    def __init__(self, tok: JSON5Token | None = None):
        self.tok = tok
        super().__init__()


class Comment(Node):
    def __init__(self, value: str, tok: JSON5Token | None = None):
        assert isinstance(value, str), f"Expected str got {type(value)}"
        self.value: str = value
        self.tok: JSON5Token | None = tok
        super().__init__()


class LineComment(Comment):
    ...


class BlockComment(Comment):
    ...
