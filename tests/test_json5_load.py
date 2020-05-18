import math

import pytest
from json5.loader import loads
from sly.lex import LexError

def test_object_string_key_value_pair():
    json_string = """{"foo":"bar"}"""
    assert loads(json_string) == {"foo": "bar"}


def test_object_string_key_value_pair_with_whitespace_before_value():
    json_string = """{"foo": "bar"}"""
    assert loads(json_string) == {"foo": "bar"}

def test_multiple_key_values():
    json_string = """{"foo":"bar","bacon":"eggs"}"""
    assert loads(json_string) == {'foo': 'bar', 'bacon': 'eggs'}

def test_multiple_string_key_values_with_whitespace():
    json_string = """{"foo":  "bar", "bacon" :  "eggs"}"""
    assert loads(json_string) == {'foo': 'bar', 'bacon': 'eggs'}

def test_array_load():
    json_string = """["foo","bar","baz"]"""
    assert loads(json_string) == ["foo", "bar", "baz"]

def test_array_load_with_whitespace():
    json_string = """[ "foo", "bar"  , "baz"   ]"""
    assert loads(json_string) == ["foo", "bar", "baz"]

def test_object_load_with_newlines():
    json_string = """{"foo":\n "bar"\n}"""
    assert loads(json_string) == {'foo': 'bar'}

def test_object_load_with_line_comment():
    json_string = """{ // line comment
    "foo": "bar"
    }"""
    assert loads(json_string) == {'foo': 'bar'}


def test_object_with_multiline_comment():
    json_string = """{ /* foo bar
    */ "foo": "bar"
    }"""
    assert loads(json_string) == {'foo': 'bar'}

def test_nested_object():
    json_string = """{"foo": {"bacon": "eggs"}}"""
    assert loads(json_string) == {'foo': {'bacon': 'eggs'}}

def test_leading_whitespace_object():
    json_string = """   {"foo":"bar"}"""
    assert loads(json_string) == {'foo': 'bar'}

def test_trailing_whitespace_object():
    json_string = """{"foo": "bar"}   """
    assert loads(json_string) == {'foo': 'bar'}

def test_single_quoted_string():
    json_string = """{'foo': 'bar'}"""
    assert loads(json_string) == {'foo': 'bar'}

def test_mixed_usage_quotes():
    json_string = """{"foo": 'bar'}"""
    assert loads(json_string) == {'foo': 'bar'}

def test_trailing_comma_object():
    json_string = """{"foo": "bar",}"""
    assert loads(json_string) == {"foo": "bar"}


def test_trailing_comma_array():
    json_string = """["foo", "bar", "baz",]"""
    assert loads(json_string) == ['foo', 'bar', 'baz']


def test_trailing_comma_array_with_trailing_whitespace():
    json_string = """["foo", "bar", "baz", ]"""
    assert loads(json_string) == ['foo', 'bar', 'baz']


def test_trailing_comma_array_with_leading_whitespace_before_comma():
    json_string = """["foo", "bar", "baz"  ,]"""
    assert loads(json_string) == ['foo', 'bar', 'baz']

def test_nested_arrays():
    json_string = """[["foo"], ["foo","bar"], "baz"]"""
    assert loads(json_string) == [['foo'], ['foo', 'bar'], 'baz']


def test_single_quote_with_escape_single_quote():
    json_string = r"""{'fo\'o': 'bar'}"""
    assert loads(json_string) == {"fo\'o": 'bar'}


def test_double_quote_with_escape_double_quote():
    json_string = r"""{"fo\"o": "bar"}"""
    assert loads(json_string) == {"fo\"o": 'bar'}

def test_escape_sequence_strings():
    json_string = r"""'\A\C\/\D\C'"""
    assert loads(json_string) == 'AC/DC'

def test_line_continuations():
    json_string = r"""'Hello \
world!'"""
    assert loads(json_string) == 'Hello world!'

def test_linebreak_without_continuation_fails():
    json_string = """'Hello 
world!"""
    with pytest.raises(LexError) as exc_info:
        loads(json_string)
    assert "Illegal character" in str(exc_info)

def test_number_literals_inf_nan():
    json_string = """{
    "positiveInfinity": Infinity,
    "negativeInfinity": -Infinity,
    "notANumber": NaN,}"""
    assert loads(json_string) == {'positiveInfinity': math.inf,
                                  'negativeInfinity': -math.inf,
                                  'notANumber': math.nan}


def test_number_literals():
    json_string = """{
    "integer": 123,
    "withFractionPart": 123.456,
    "onlyFractionPart": .456,
    "withExponent": 123e-2}"""
    assert loads(json_string) == {
    "integer": 123,
    "withFractionPart": 123.456,
    "onlyFractionPart": .456,
    "withExponent": 123e-2}