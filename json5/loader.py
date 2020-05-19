import types

import sys

from json5.parser import parse_source
from json5.model import *
from functools import singledispatch
from collections import UserString

import logging
logger = logging.getLogger(__name__)
# logger.setLevel(level=logging.DEBUG)
# logger.addHandler(logging.StreamHandler(stream=sys.stderr))

class Environment(types.SimpleNamespace):
    def __init__(self, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, strict=True, object_pairs_hook=None):
        super().__init__(object_hook=object_hook, parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, strict=strict, object_pairs_hook=object_pairs_hook)


class JsonIdentifier(UserString):
    ...

def load(f, **kwargs):
    text = f.read()
    return loads(text)

def loads(s, *args, **kwargs):
    """
    :param s:
    :param object_hook: same meaning as in ``json.loads``
    :param parse_float: same meaning as in ``json.loads``
    :param parse_int: same meaning as in ``json.loads``
    :param parse_constant: same meaning as in ``json.loads``
    :param strict: same meaning as in ``json.loads`` (currently has no effect)
    :param object_pairs_hook: same meaning as in ``json.loads``
    :return:
    """
    environment = Environment(**kwargs)
    model = parse_source(s)
    # logger.debug('Model is %r', model)
    return _load(model, environment)


@singledispatch
def _load(node, env):
    raise NotImplementedError(f"Can't load node {node}")

to_python = _load.register

@to_python(JSONText)
def json_model_to_python(node, env):
    logger.debug('json_model_to_python evaluating node %r', node)
    return _load(node.value, env)

@to_python(JSONObject)
def json_object_to_python(node, env):
    logger.debug('json_object_to_python evaluating node %r', node)
    d = {}
    for key_value_pair in node.key_value_pairs:
        key = _load(key_value_pair.key, env)
        value = _load(key_value_pair.value, env)
        d[key] = value
    if env.object_pairs_hook:
        return env.object_pairs_hook(list(d.items()))
    elif env.object_hook:
        return env.object_hook(d)
    else:
        return d


@to_python(JSONArray)
def json_array_to_python(node, env):
    logger.debug('json_array_to_python evaluating node %r', node)
    return [_load(value, env) for value in node.values]

@to_python(Identifier)
def identifier_to_python(node, env):
    logger.debug('identifier_to_python evaluating node %r', node)
    return JsonIdentifier(node.name)


@to_python(Number)  # NaN/Infinity are covered here
def number_to_python(node, env):
    logger.debug('number_to_python evaluating node %r', node)
    if env.parse_constant:
        return env.parse_constant(node.const)
    return node.value

@to_python(Integer)
def integer_to_python(node, env):
    if env.parse_int:
        return env.parse_int(node.raw_value)
    else:
        return node.value

@to_python(Float)
def float_to_python(node, env):
    if env.parse_float:
        return env.parse_float(node.raw_value)
    else:
        return node.value

@to_python(UnaryOp)
def unary_to_python(node, env):
    logger.debug('unary_to_python evaluating node %r', node)
    if isinstance(node.value, Infinity):
        return _load(node.value, env)
    value = _load(node.value, env)
    if node.op == '-':
        return value * -1
    else:
        return value

@to_python(String)
def string_to_python(node, env):
    logger.debug('string_to_python evaluating node %r', node)
    return node.characters


@to_python(NullLiteral)
def null_to_python(node, env):
    logger.debug('null_to_python evaluating node %r', node)
    return None

@to_python(BooleanLiteral)
def boolean_to_python(node, env):
    logger.debug('boolean_to_python evaluating node %r', node)
    return node.value

@to_python(CommentOrWhiteSpace)
def comment_or_whitespace_to_python(node, env):
    raise RuntimeError("It's a comment")

if __name__ == '__main__':
    fp = sys.argv[1]
    with open(fp) as f:
        text = f.read()
    print(repr(loads(text)))