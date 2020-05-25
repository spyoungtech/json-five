from json5.loader import loads, ModelLoader, DefaultLoader
from json5.dumper import DefaultDumper, ModelDumper, modelize
from json5.model import LineComment, Integer
import pytest
import re

from json5.utils import JSON5DecodeError


def test_loading_comment_raises_runtime_error_default_loader():
    model = LineComment('// foo')
    with pytest.raises(RuntimeError):
        DefaultLoader().load(model)


def test_loading_unknown_node_raises_error():
    class Foo(object):
        ...
    f = Foo()
    with pytest.raises(NotImplementedError):
        DefaultLoader().load(f)


def test_dumping_unknown_node_raises_error():
    class Foo(object):
        ...
    f = Foo()
    with pytest.raises(NotImplementedError):
        DefaultDumper().dump(f)

def test_known_type_in_wsc_raises_error():
    class Foo:
        ...
    f = Foo()
    model = loads('{foo: "bar"}', loader=ModelLoader())
    model.value.key_value_pairs[0].key.wsc_before.append(f)
    with pytest.raises(ValueError):
        ModelDumper().dump(model)
    model = loads('{foo: "bar"}', loader=ModelLoader())
    model.value.key_value_pairs[0].key.wsc_after.append(f)
    with pytest.raises(ValueError):
        ModelDumper().dump(model)


def test_modelizing_unknown_object_raises_error():
    class Foo:
        ...
    f = Foo()
    with pytest.raises(NotImplementedError):
        modelize(f)

def test_model_dumper_raises_error_for_unknown_node():
    class Foo:
        ...
    f = Foo()
    with pytest.raises(NotImplementedError):
        ModelDumper().dump(f)

def test_multiple_errors_all_surface_at_once():
    json_string = """[\n"foo",\n"bar"\n"baz",\n"bacon"\n"eggs"]"""
    # 2 errors due to missing comma  ^                ^
    with pytest.raises(JSON5DecodeError) as exc_info:
        loads(json_string)
    assert str(exc_info.value).count('Syntax Error') == 2


def test_linebreak_without_continuation_fails():
    json_string = """'Hello \nworld!'"""
    with pytest.raises(JSON5DecodeError) as exc_info:
        loads(json_string)
    assert "Illegal" in str(exc_info.value)


def test_linebreak_without_continuation_fails_double():
    json_string = '''"Hello \nworld!"'''
    with pytest.raises(JSON5DecodeError) as exc_info:
        loads(json_string)
    assert "Illegal" in str(exc_info.value)


def test_empty_input_raises_error():
    with pytest.raises(JSON5DecodeError) as exc_info:
        loads("")
    assert "unexpected EOF" in str(exc_info.value)


def test_backslash_x_without_two_hexadecimals_raises_error():
    with pytest.raises(JSON5DecodeError) as exc_info:
        loads(r"'\x1'")
    assert "'\\x' MUST be followed by two hexadecimal digits" in str(exc_info.value)

def test_null_escape_may_not_be_followed_by_decimal_digit():
    with pytest.raises(JSON5DecodeError) as exc_info:
        loads(r"'\01'")
    assert "'\\0' MUST NOT be followed by a decimal digit" in str(exc_info.value)

def test_backslash_x_without_two_hexadecimals_raises_error_but_for_double_quotes():
    with pytest.raises(JSON5DecodeError) as exc_info:
        loads(r'"\x1"')
    assert "'\\x' MUST be followed by two hexadecimal digits" in str(exc_info.value)

def test_null_escape_may_not_be_followed_by_decimal_digit_but_for_double_quotes():
    with pytest.raises(JSON5DecodeError) as exc_info:
        loads(r'"\01"')
    assert "'\\0' MUST NOT be followed by a decimal digit" in str(exc_info.value)

def test_integer_octal_hex_mutually_exclusive():
    with pytest.raises(ValueError):
        Integer(raw_value='0o0', is_hex=True, is_octal=True)

def test_invalid_identifier_via_escape_sequence():
    json_string = """{\\u005Cfoo: 1}"""
    with pytest.raises(JSON5DecodeError) as exc_info:
        loads(json_string)
    assert "Invalid identifier name" in str(exc_info.value)

@pytest.mark.parametrize('json_string', [""""foo \\\nbar baz \\\nbacon \neggs\"""", """'foo \\\nbar baz \\\nbacon \neggs'"""])
def test_illegal_line_terminator_error_message(json_string):

    with pytest.raises(JSON5DecodeError) as exc_info:
        loads(json_string)

    exc_message = str(exc_info.value)
    exc_lineno_match = re.search('line (\d+)', exc_message)
    if exc_lineno_match:
        exc_lineno = int(exc_lineno_match.groups()[0])
    else:
        exc_lineno = None
    exc_col_match = re.search('column (\d+)', exc_message)
    if exc_col_match:
        exc_col = int(exc_col_match.groups()[0])
    else:
        exc_col = None
    exc_index_match = re.search('char (\d+)', exc_message)
    if exc_index_match:
        exc_index = int(exc_index_match.groups()[0])
    else:
        exc_index = None
    assert (3, 7, 23) == (exc_lineno, exc_col, exc_index)