import math

import pytest

from json5.dumper import dumps
from json5.dumper import ModelDumper
from json5.dumper import modelize
from json5.loader import loads


@pytest.mark.parametrize(
    'obj',
    [
        {'foo': 'bar', 'bacon': 'eggs'},
        ['foo', 'bar', 'baz'],
        {},
        [],
        ['foo'],
        {'foo': 'bar'},
        "Hello world!",
        123,
        1.0,
        -1.0,
        -2,
        math.inf,
        -math.inf,
        True,
        False,
        None,
    ],
)
def test_modelize_objects(obj):
    assert loads(dumps(modelize(obj), dumper=ModelDumper())) == obj


def test_modelize_nan():
    obj = math.nan
    assert loads(dumps(modelize(obj), dumper=ModelDumper())) is obj


def test_modelize_double_quote_string():
    s = "'"
    assert loads(dumps(modelize(s), dumper=ModelDumper())) == s
