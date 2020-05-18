from json5 import dumps, loads
import json
import math


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
