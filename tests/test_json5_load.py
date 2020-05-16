import pytest
from json5.loader import loads

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

