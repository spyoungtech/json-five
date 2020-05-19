import math

import pytest
from json5.loader import loads, JsonIdentifier, ModelLoader
from sly.lex import LexError
from json5.dumper import dumps, ModelDumper



@pytest.mark.parametrize('json_string', [
"""{"foo":"bar"}""",
"""{"foo": "bar"}""",
"""{"foo":"bar","bacon":"eggs"}""",
"""{"foo":  "bar", "bacon" :  "eggs"}""",
"""["foo","bar","baz"]""",
"""[ "foo", "bar"  , "baz"   ]""",
"""{"foo":\n "bar"\n}""",
"""{"foo": {"bacon": "eggs"}}""",
"""   {"foo":"bar"}""",
"""{"foo": "bar"}   """,
"""{'foo': 'bar'}""",
"""{"foo": 'bar'}""",
"""{"foo": "bar",}""",
"""["foo","bar", "baz",]""",
"""["foo", "bar", "baz", ]""",
"""["foo", "bar", "baz"  ,]""",
"""[["foo"], ["foo","bar"], "baz"]""",
"""{unquoted: "foo"}""",
"""{unquoted: "foo"}""",
"""["foo"]""",
"""["foo" , ]""",
])
def test_round_trip_model_load_dump(json_string):
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


#
#
# def test_object_string_key_value_pair():
#     json_string = """{"foo":"bar"}"""
#     assert loads(json_string, loader=ModelLoader()) == {"foo": "bar"}
#
#
# def test_object_string_key_value_pair_with_whitespace_before_value():
#     json_string = """{"foo": "bar"}"""
#     assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string
#
#
# def test_multiple_key_values():
#     json_string = """{"foo":"bar","bacon":"eggs"}"""
#     assert loads(json_string, loader=ModelLoader()) == {"foo": "bar", "bacon": "eggs"}
#
#
# def test_multiple_string_key_values_with_whitespace():
#     json_string = """{"foo":  "bar", "bacon" :  "eggs"}"""
#     assert loads(json_string, loader=ModelLoader()) == {"foo": "bar", "bacon": "eggs"}
#
#
# def test_array_load():
#     json_string = """["foo","bar","baz"]"""
#     assert loads(json_string, loader=ModelLoader()) == ["foo", "bar", "baz"]
#
#
# def test_array_load_with_whitespace():
#     json_string = """[ "foo", "bar"  , "baz"   ]"""
#     assert loads(json_string, loader=ModelLoader()) == ["foo", "bar", "baz"]
#
#
# def test_object_load_with_newlines():
#     json_string = """{"foo":\n "bar"\n}"""
#     assert loads(json_string, loader=ModelLoader()) == {"foo": "bar"}
#
#
# def test_object_load_with_line_comment():
#     json_string = """{ // line comment
#     "foo": "bar"
#     }"""
#     assert loads(json_string, loader=ModelLoader()) == {"foo": "bar"}
#
#
# def test_object_with_multiline_comment():
#     json_string = """{ /* foo bar
#     */ "foo": "bar"
#     }"""
#     assert loads(json_string, loader=ModelLoader()) == {"foo": "bar"}
#
#
# def test_nested_object():
#     json_string = """{"foo": {"bacon": "eggs"}}"""
#     assert loads(json_string, loader=ModelLoader()) == {"foo": {"bacon": "eggs"}}
#
#
# def test_leading_whitespace_object():
#     json_string = """   {"foo":"bar"}"""
#     assert loads(json_string, loader=ModelLoader()) == {"foo": "bar"}
#
#
# def test_trailing_whitespace_object():
#     json_string = """{"foo": "bar"}   """
#     assert loads(json_string, loader=ModelLoader()) == {"foo": "bar"}
#
#
# def test_single_quoted_string():
#     json_string = """{'foo': 'bar'}"""
#     assert loads(json_string, loader=ModelLoader()) == {"foo": "bar"}
#
#
# def test_mixed_usage_quotes():
#     json_string = """{"foo": 'bar'}"""
#     assert loads(json_string, loader=ModelLoader()) == {"foo": "bar"}
#
#
# def test_trailing_comma_object():
#     json_string = """{"foo": "bar",}"""
#     assert loads(json_string, loader=ModelLoader()) == {"foo": "bar"}
#
#
# def test_trailing_comma_array():
#     json_string = """["foo","bar", "baz",]"""
#     assert loads(json_string, loader=ModelLoader()) == ["foo", "bar", "baz"]
#
#
# def test_trailing_comma_array_with_trailing_whitespace():
#     json_string = """["foo", "bar", "baz", ]"""
#     assert loads(json_string, loader=ModelLoader()) == ["foo", "bar", "baz"]
#
#
# def test_trailing_comma_array_with_leading_whitespace_before_comma():
#     json_string = """["foo", "bar", "baz"  ,]"""
#     assert loads(json_string, loader=ModelLoader()) == ["foo", "bar", "baz"]
#
#
# def test_nested_arrays():
#     json_string = """[["foo"], ["foo","bar"], "baz"]"""
#     assert loads(json_string, loader=ModelLoader()) == [["foo"], ["foo", "bar"], "baz"]
#
#
# def test_single_quote_with_escape_single_quote():
#     json_string = r"""{'fo\'o': 'bar'}"""
#     assert loads(json_string, loader=ModelLoader()) == {"fo'o": "bar"}
#
#
# def test_double_quote_with_escape_double_quote():
#     json_string = r"""{"fo\"o": "bar"}"""
#     assert loads(json_string, loader=ModelLoader()) == {'fo"o': "bar"}
#
#
# def test_escape_sequence_strings():
#     json_string = r"""'\A\C\/\D\C'"""
#     assert loads(json_string, loader=ModelLoader()) == "AC/DC"
#
#
# def test_line_continuations():
#     json_string = r"""'Hello \
# world!'"""
#     assert loads(json_string, loader=ModelLoader()) == "Hello world!"
#
#
# @pytest.mark.parametrize("terminator", ["\r\n", "\n", "\u2028", "\u2029"])
# def test_line_continuations_alternate_terminators(terminator):
#     json_string = f"""'Hello \\{terminator}world!'"""
#     assert loads(json_string, loader=ModelLoader()) == "Hello world!"
#
#
# def test_linebreak_without_continuation_fails():
#     json_string = """'Hello
# world!"""
#     with pytest.raises(LexError) as exc_info:
#         loads(json_string, loader=ModelLoader())
#     assert "Illegal character" in str(exc_info.value)
#
#
# def test_number_literals_inf_nan():
#     json_string = """{
#     "positiveInfinity": Infinity,
#     "negativeInfinity": -Infinity,
#     "notANumber": NaN,}"""
#     assert loads(json_string, loader=ModelLoader()) == {
#         "positiveInfinity": math.inf,
#         "negativeInfinity": -math.inf,
#         "notANumber": math.nan,
#     }
#
#
# def test_number_literals():
#     json_string = """{
#     "integer": 123,
#     "withFractionPart": 123.456,
#     "onlyFractionPart": .456,
#     "withExponent": 123e-2}"""
#     assert loads(json_string, loader=ModelLoader()) == {
#         "integer": 123,
#         "withFractionPart": 123.456,
#         "onlyFractionPart": 0.456,
#         "withExponent": 123e-2,
#     }
#
#
# def test_escape_sequences():
#     json_string = r"""{
#     "foo": "foo\nbar\nbaz",
#     "bar": "foo\\bar\\baz",
#     "baz": "foo\tbar\tbaz"}"""
#     assert loads(json_string, loader=ModelLoader()) == {
#         "foo": "foo\nbar\nbaz",
#         "bar": "foo\\bar\\baz",
#         "baz": "foo\tbar\tbaz",
#     }
#
#
# def test_empty_object():
#     json_string = "{}"
#     assert loads(json_string, loader=ModelLoader()) == {}
#
#
# def test_empty_array():
#     json_string = "[]"
#     assert loads(json_string, loader=ModelLoader()) == []
#
#
# @pytest.mark.parametrize(
#     "json_string",
#     ['{"foo": "bar", "bar" "baz"', '["foo" "bar"]', "[,]", "{,}", "!", '{"foo": "bar" "bacon": "eggs"}',],
# )
# def test_invalid_json(json_string):
#     with pytest.raises(Exception):
#         loads(json_string, loader=ModelLoader())
#
#
# def test_object_with_identifier_key():
#     json_string = """{unquoted: "foo"}"""
#     assert loads(json_string, loader=ModelLoader()) == {"unquoted": "foo"}
#
#
# def test_identifier_persists_load():
#     json_string = """{unquoted: "foo"}"""
#     assert isinstance(list(loads(json_string, loader=ModelLoader()).keys())[0], JsonIdentifier)
#
#
# def test_single_item_array():
#     json_string = """["foo"]"""
#     assert loads(json_string, loader=ModelLoader()) == ["foo"]
#
#
# def test_single_item_array_with_trailing_comma():
#     json_string = """["foo" , ]"""
#     assert loads(json_string, loader=ModelLoader()) == ["foo"]
#
#
# def test_hexadecimal_load():
#     json_string = """
#     {
#     positiveHex: 0xdecaf,
#     negativeHex: -0xC0FFEE,}"""
#     assert loads(json_string, loader=ModelLoader()) == {"positiveHex": 0xDECAF, "negativeHex": -0xC0FFEE}
