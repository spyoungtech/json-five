from json5.dumper import modelize
from json5.model import Identifier


def test_identifier_can_hash_like_string():
    d = {Identifier('foo', raw_value='foo'): 'bar'}
    assert d['foo'] == 'bar'


def test_identifier_equals_like_string():
    assert Identifier('foo', raw_value='foo') == 'foo'


def test_repr_does_not_contain_wsc():
    model = modelize({'foo': 'bar'})
    assert 'wsc' not in repr(model)


def test_identifier_does_not_need_explicit_raw_value():
    assert Identifier('foo').raw_value == 'foo'
