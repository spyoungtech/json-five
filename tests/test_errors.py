from json5.loader import loads, ModelLoader, DefaultLoader
from json5.dumper import DefaultDumper, ModelDumper, modelize
from json5.model import LineComment
import pytest

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


def test_reserved_keywords_raise_error():
    json_string = """{break: "not good!"}"""
    with pytest.raises(JSON5DecodeError):
        loads(json_string)


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