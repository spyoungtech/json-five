import json
from decimal import Decimal

import json5


def int_plus_one(int_string):
    assert isinstance(int_string, str)
    return int(int_string) + 1


def float_to_decimal(float_string):
    assert isinstance(float_string, str)
    return Decimal(float_string)


def const_to_silly(const_string):
    assert isinstance(const_string, str)
    return f'Something Silly {const_string}'


def true_object_hook(d):
    return {k: True for k in d}


def true_object_pair_hook(kvpairs):
    return {k: True for k, v in kvpairs}


def test_parse_int():
    json_string = """{"foo": 5}"""
    assert json5.loads(json_string, parse_int=int_plus_one) == json.loads(json_string, parse_int=int_plus_one)
    assert json5.loads(json_string, parse_int=int_plus_one)['foo'] == 6


def test_parse_float():
    json_string = """{"foo": 5.0}"""
    assert json5.loads(json_string, parse_float=float_to_decimal) == json.loads(
        json_string, parse_float=float_to_decimal
    )


def test_parse_constant_nan():
    json_string = """{"foo": NaN}"""
    assert json5.loads(json_string, parse_constant=const_to_silly) == {'foo': 'Something Silly NaN'}
    assert json5.loads(json_string, parse_constant=const_to_silly) == json.loads(
        json_string, parse_constant=const_to_silly
    )


def test_parse_constant_positive_infinity():
    json_string = """{"foo": Infinity}"""
    assert json5.loads(json_string, parse_constant=const_to_silly) == {'foo': 'Something Silly Infinity'}
    assert json5.loads(json_string, parse_constant=const_to_silly) == json.loads(
        json_string, parse_constant=const_to_silly
    )


def test_parse_constant_negative_infinity():
    json_string = """{"foo": -Infinity}"""
    assert json5.loads(json_string, parse_constant=const_to_silly) == {'foo': 'Something Silly -Infinity'}
    assert json5.loads(json_string, parse_constant=const_to_silly) == json.loads(
        json_string, parse_constant=const_to_silly
    )


def test_object_hook():
    json_string = """{"foo": "bar", "bacon": "eggs"}"""
    result = json5.loads(json_string, object_hook=true_object_hook)
    assert result == json.loads(json_string, object_hook=true_object_hook)
    assert all(value is True for key, value in result.items())


def test_object_pairs_hook():
    json_string = """{"foo": "bar", "bacon": "eggs"}"""
    result = json5.loads(json_string, object_pairs_hook=true_object_pair_hook)
    assert result == json.loads(json_string, object_pairs_hook=true_object_pair_hook)
    assert all(value is True for key, value in result.items())
