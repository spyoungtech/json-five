import pytest

from json5 import JSON5DecodeError
from json5 import loads


# These tests used to cause the program to hang indefinitely
def test_no_hang():
    json_string = '{"foo": ["foo", [0o11]}, ["baz"]]'
    with pytest.raises(JSON5DecodeError):
        loads(json_string)


def test_no_hang2():
    json_string = '[{foo:]}'
    with pytest.raises(JSON5DecodeError):
        loads(json_string)


def test_no_hang3():
    json_string = '[true, {foo:]false}'
    with pytest.raises(JSON5DecodeError):
        loads(json_string)
