from __future__ import annotations
import math
from typing import Optional, Union, List, Literal, Any
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
        self.wsc_before: List[Union[str, Comment]] = []
        self.wsc_after: List[Union[str, Comment]] = []

    def __repr__(self) -> str:
        rep = (
            f"{self.__class__.__name__}("
            + ", ".join(
                "{key}={value}".format(key=key, value=repr(value))
                for key, value in self.__dict__.items() if key not in self.excluded_names
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
    def __init__(self, *key_value_pairs: KeyValuePair, trailing_comma: Optional[TrailingComma] = None, leading_wsc: Optional[List[Union[str, Comment]]] = None, tok: Optional[JSON5Token] = None):
        kvps = list(key_value_pairs)
        for kvp in kvps:
            assert isinstance(kvp, KeyValuePair), f"Expected key value pair, got {type(kvp)}"
        assert leading_wsc is None or all(isinstance(item, str) or isinstance(item, Comment) for item in leading_wsc)
        self.key_value_pairs: List[KeyValuePair] = kvps
        self.trailing_comma: Optional[TrailingComma] = trailing_comma
        self.leading_wsc: List[Union[str, Comment]] = leading_wsc or []
        self.tok: Optional[JSON5Token] = tok
        super().__init__()


class JSONArray(Value):
    def __init__(self, *values: Value, trailing_comma: Optional[TrailingComma] = None, leading_wsc: Optional[List[Union[str, Comment]]] = None, tok: Optional[JSON5Token] = None):
        vals = list(values)
        for value in vals:
            assert isinstance(value, Value), f"Was expecting object with type Value. Got {type(value)}"
        assert leading_wsc is None or all(isinstance(item, str) or isinstance(item, Comment) for item in leading_wsc)
        self.values: List[Value] = vals
        self.trailing_comma: Optional[TrailingComma] = trailing_comma
        self.leading_wsc: List[Union[str, Comment]] = leading_wsc or []
        self.tok: Optional[JSON5Token] = tok
        super().__init__()


class KeyValuePair(Node):
    def __init__(self, key: Key, value: Value, tok: Optional[JSON5Token] = None):
        assert isinstance(key, Key)
        assert isinstance(value, Value)
        self.key: Key = key
        self.value: Value = value
        self.tok: Optional[JSON5Token] = tok
        super().__init__()


class Identifier(Key):
    def __init__(self, name: str, raw_value: Optional[str] = None, tok: Optional[JSON5Token] = None):
        assert isinstance(name, str)
        if raw_value is None:
            raw_value = name
        assert isinstance(raw_value, str)
        assert len(name) > 0
        self.name: str = name
        self.raw_value: str = raw_value
        self.tok: Optional[JSON5Token] = tok
        super().__init__()

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        return hash(self) == hash(other)


class Number(Value):
    ...


class Integer(Number):
    def __init__(self, raw_value: str, is_hex: bool = False, is_octal: bool = False, tok: Optional[JSON5Token] = None):
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
        self.tok: Optional[JSON5Token] = tok
        super().__init__()


class Float(Number):
    def __init__(self, raw_value: str, exp_notation: Optional[str] = None, tok: Optional[JSON5Token] = None):
        value = float(raw_value)
        assert exp_notation is None or exp_notation in ('e', 'E')
        self.raw_value: str = raw_value
        self.exp_notation: Optional[str] = exp_notation
        self.tok: Optional[JSON5Token] = tok
        self.value: float = value
        super().__init__()




class Infinity(Number):
    def __init__(self, negative: bool = False, tok: Optional[JSON5Token] = None):
        self.negative: bool = negative
        self.tok: Optional[JSON5Token] = tok
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
    def __init__(self, tok: Optional[JSON5Token] = None):
        self.tok: Optional[JSON5Token] = tok
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
    def __init__(self, characters: str, raw_value: str, tok: Optional[JSON5Token] = None):
        assert isinstance(raw_value, str)
        assert isinstance(characters, str)
        self.characters: str = characters
        self.raw_value: str = raw_value
        self.tok: Optional[JSON5Token] = tok
        super().__init__()


class SingleQuotedString(String):
    def __init__(self, characters: str, raw_value: str, tok: Optional[JSON5Token] = None):
        assert isinstance(raw_value, str)
        assert isinstance(characters, str)
        self.characters: str = characters
        self.raw_value: str = raw_value
        self.tok: Optional[JSON5Token] = tok
        super().__init__()


class BooleanLiteral(Value):
    def __init__(self, value: bool, tok: Optional[JSON5Token] = None):
        assert value in (True, False)
        self.value: bool = value
        self.tok: Optional[JSON5Token] = tok
        super().__init__()


class NullLiteral(Value):
    value = None
    def __init__(self, tok: Optional[JSON5Token] = None):
        self.tok: Optional[JSON5Token] = None
        super().__init__()

class UnaryOp(Value):
    def __init__(self, op: Literal['-', '+'], value: Number, tok: Optional[JSON5Token] = None):
        assert op in ('-', '+')
        assert isinstance(value, Number)
        self.op: Literal['-', '+'] = op
        self.value: Number = value
        self.tok: Optional[JSON5Token] = tok
        super().__init__()

class TrailingComma(Node):
    def __init__(self, tok: Optional[JSON5Token] = None):
        self.tok = tok
        super().__init__()

class Comment(Node):
    def __init__(self, value: str, tok: Optional[JSON5Token] = None):
        assert isinstance(value, str), f"Expected str got {type(value)}"
        self.value: str = value
        self.tok: Optional[JSON5Token] = tok
        super().__init__()


class LineComment(Comment):
    ...

class BlockComment(Comment):
    ...
