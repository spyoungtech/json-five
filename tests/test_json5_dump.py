import json
import math
from io import StringIO

from json5 import dump
from json5 import dumps
from json5.dumper import ModelDumper
from json5.model import Integer
from json5.model import UnaryOp


def test_json_dump_empty_object():
    d = {}
    assert dumps(d) == '{}'


def test_json_dump_empty_array():
    d = []
    assert dumps(d) == '[]'


def test_single_key_value_dump():
    d = {'foo': 'bar'}
    assert dumps(d) == json.dumps(d)


def test_dump_same_as_json():
    d = {
        "strings": ["foo", "bar", "baz"],
        "numbers": [1, -1, 1.0, math.inf, -math.inf, math.nan],
        "lists": ['foo', ['nested_list']],
    }
    assert dumps(d) == json.dumps(d)


def test_dump_indent_same_as_json():
    d = {
        "strings": ["foo", "bar", "baz"],
        "numbers": [1, -1, 1.0, math.inf, -math.inf, math.nan],
        "lists": ['foo', ['nested_list']],
    }
    assert dumps(d, indent=4) == json.dumps(d, indent=4)


def test_dump_boolean():
    d = {'foo': True}
    assert dumps(d) == json.dumps(d)


def test_dump_bool_false():
    d = {'foo': False}
    assert dumps(d) == json.dumps(d)


def test_dump_none():
    d = {'foo': None}
    assert dumps(d) == json.dumps(d)


def test_dump_unary_plus():
    assert dumps(UnaryOp('+', Integer('1')), dumper=ModelDumper()) == '+1'


def test_dump_file():
    f = StringIO()
    dump("foo", f)
    f.seek(0)
    assert f.read() == '"foo"'
