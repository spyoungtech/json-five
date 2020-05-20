from json5.dumper import modelize, ModelDumper, dumps
from json5.loader import DefaultLoader, ModelLoader, loads
import pytest, math

@pytest.mark.parametrize('obj', [
    {'foo': 'bar', 'bacon': 'eggs'},
    ['foo', 'bar', 'baz'],
    {},
    [],
    ['foo'],
    {'foo':'bar'},
    "Hello world!",
    123,
    1.0,
    -1.0,
    -2,
    math.inf,
    -math.inf,
])
def test_modelize_objects(obj):
    assert loads(dumps(modelize(obj), dumper=ModelDumper())) == obj


def test_modelize_nan():
    obj = math.nan
    assert loads(dumps(modelize(obj), dumper=ModelDumper())) is obj

