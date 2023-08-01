import pytest

from json5.dumper import dumps
from json5.dumper import ModelDumper
from json5.loader import loads
from json5.loader import ModelLoader


@pytest.mark.parametrize(
    'json_string',
    [
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
    ],
)
def test_round_trip_model_load_dump(json_string):
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_object_load_with_line_comment():
    json_string = """{ // line comment
    "foo": "bar"
    }"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_object_with_multiline_comment():
    json_string = """{ /* foo bar
    */ "foo": "bar" // Foobar
    }"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_array_load_with_line_comment():
    json_string = """[ // line comment
    "foo", "bar"
    ]"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_array_with_multiline_comment():
    json_string = """[ /* foo bar
    */ "foo", "bar"
    ]"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_nested_object():
    json_string = """{"foo": {"bacon": "eggs"}}"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_single_quote_with_escape_single_quote():
    json_string = r"""{'fo\'o': 'bar'}"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_double_quote_with_escape_double_quote():
    json_string = r"""{"fo\"o": "bar"}"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_escape_sequence_strings():
    json_string = r"""'\A\C\/\D\C'"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_line_continuations():
    json_string = r"""'Hello \
world!'"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


@pytest.mark.parametrize("terminator", ["\r\n", "\n", "\u2028", "\u2029"])
def test_line_continuations_alternate_terminators(terminator):
    json_string = f"""'Hello \\{terminator}world!'"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_number_literals_inf_nan():
    json_string = """{
    "positiveInfinity": Infinity,
    "negativeInfinity": -Infinity,
    "notANumber": NaN,}"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_number_literals():
    json_string = """{
    "integer": 123,
    "withFractionPart": 123.456,
    "onlyFractionPart": .456,
    "withExponent": 123e-2}"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_escape_sequences():
    json_string = r"""{
    "foo": "foo\nbar\nbaz",
    "bar": "foo\\bar\\baz",
    "baz": "foo\tbar\tbaz"}"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_empty_object():
    json_string = "{}"
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_empty_array():
    json_string = "[]"
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_hexadecimal_load():
    json_string = """
    {
    positiveHex: 0xdecaf,
    negativeHex: -0xC0FFEE,}"""
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_load_empty_array_with_whitespace():
    json_string = "{   }"
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_load_empty_object_wtih_whitespace():
    json_string = "[   ]"
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_load_empty_object_with_comments():
    json_string = "{ // foo \n}"
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string


def test_load_empty_array_with_comments():
    json_string = "[ // foo \n]"
    assert dumps(loads(json_string, loader=ModelLoader()), dumper=ModelDumper()) == json_string
