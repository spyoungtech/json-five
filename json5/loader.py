import sys

from json5.parser import parse_source
from json5.model import *
from functools import singledispatch
from collections import UserString

import logging
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stderr))

class JsonIdentifier(UserString):
    ...

def load(f):
    text = f.read()
    return loads(text)

def loads(s):
    environment = {}
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
    return d


@to_python(JSONArray)
def json_array_to_python(node, env):
    logger.debug('json_array_to_python evaluating node %r', node)
    return [_load(value, env) for value in node.values]

@to_python(Identifier)
def identifier_to_python(node, env):
    logger.debug('identifier_to_python evaluating node %r', node)
    return JsonIdentifier(node.name)


@to_python(Number)
def number_to_python(node, env):
    logger.debug('number_to_python evaluating node %r', node)
    return node.value


@to_python(UnaryOp)
def unary_to_python(node, env):
    logger.debug('unary_to_python evaluating node %r', node)
    value = _load(node.value, env)
    if node.op == '-':
        return value * -1
    else:
        return value

@to_python(String)
def string_to_python(node, env):
    logger.debug('string_to_python evaluating node %r', node)
    return ''.join(node.characters)


@to_python(NullLiteral)
def null_to_python(node, env):
    logger.debug('null_to_python evaluating node %r', node)
    return None

@to_python(CommentOrWhiteSpace)
def comment_or_whitespace_to_python(node, env):
    raise RuntimeError("It's a comment")

if __name__ == '__main__':
    fp = sys.argv[1]
    with open(fp) as f:
        text = f.read()
    print(repr(loads(text)))