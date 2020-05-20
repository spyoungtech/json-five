from json5.model import Identifier
from json5.dumper import modelize
def test_identifier_can_hash_like_string():
    d = {Identifier('foo'): 'bar'}
    assert d['foo'] == 'bar'

def test_identifier_equals_like_string():
    assert Identifier('foo') == 'foo'


def test_repr_does_not_contain_wsc():
    model = modelize({'foo': 'bar'})
    assert 'wsc' not in repr(model)
