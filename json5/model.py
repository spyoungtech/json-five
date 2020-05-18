import math
from types import SimpleNamespace
from functools import lru_cache
from decimal import Decimal

@lru_cache(maxsize=1024)
def black_format_code(source):
    import black
    kwargs = {
        'line_length': 120,
    }
    reformatted_source = black.format_file_contents(
        source, fast=True, mode=black.FileMode(**kwargs)
    )
    return reformatted_source

class Node(SimpleNamespace):
    def __repr__(self):
        rep = (
            f"{self.__class__.__name__}("
            + ", ".join(
                "{key}={value}".format(key=key, value=repr(value))
                for key, value in self.__dict__.items()
            )
            + ")"
        )
        return rep
        try:
            return black_format_code(rep)
        except ImportError as e:
            # Just in case you don't have `black` installed :-)
            return rep
        except Exception as e:
            print('WARN: Unexpected error formatting code ', e)
            return rep


class JSONText(Node):
    def __init__(self, value):
        assert isinstance(value, Value)
        super().__init__(value=value)


class Value(Node):
    pass

class Key(Node):
    ...


class JSONObject(Value):
    def __init__(self, *key_value_pairs, trailing_comma=None):
        key_value_pairs = list(key_value_pairs)
        for kvp in key_value_pairs:
            assert isinstance(kvp, KeyValuePair), f"Expected key value pair, got {type(kvp)}"
        super().__init__(key_value_pairs=key_value_pairs, trailing_comma=trailing_comma)


class JSONArray(Value):
    def __init__(self, *values, trailing_comma=None):
        values = list(values)
        for value in values:
            assert isinstance(value, Value), f"Was expecting object with type Value. Got {type(value)}"
        super().__init__(values=values, trailing_comma=trailing_comma)


class KeyValuePair(Node):
    def __init__(self, key, value):
        assert isinstance(key, Key)
        assert isinstance(value, Value)
        super().__init__(key=key, value=value)


class Identifier(Key):
    def __init__(self, name):
        assert isinstance(name, str)
        assert len(name) > 0
        super().__init__(name=name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return hash(self) == hash(other)


class Number(Value):
    ...


class Integer(Number):
    def __init__(self, value, is_hex=False):
        assert isinstance(value, int)
        super().__init__(value=value, is_hex=is_hex)


class Float(Number):
    def __init__(self, value, exp_notation=None):
        assert isinstance(value, float)
        assert exp_notation is None or exp_notation in ('e', 'E')
        super().__init__(value=value, exp_notation=exp_notation)


class Infinity(Number):
    def __init__(self):
        super().__init__(value=math.inf)


class NaN(Number):
    def __init__(self):
        super().__init__(value=math.nan)

class String(Value, Key):
    ...

class DoubleQuotedString(String):
    def __init__(self, characters):
        characters = characters
        assert isinstance(characters, str)
        super().__init__(characters=characters)


class SingleQuotedString(String):
    def __init__(self, characters):
        characters = characters
        assert isinstance(characters, str)
        super().__init__(characters=characters)


class BooleanLiteral(Value):
    def __init__(self, value):
        assert value in (True, False)
        super().__init__(value=value)


class NullLiteral(Value):
    def __init__(self):
        super().__init__(value=None)


class UnaryOp(Value):
    def __init__(self, op, value):
        assert op in ('-', '+')
        assert isinstance(value, Number)
        super().__init__(op=op, value=value)


class CommentOrWhiteSpace(Node):
    def __init__(self, value):
        assert isinstance(value, str), f"Expected str got {type(value)}"
        super().__init__(value=value)