import types

import sys

from json5.parser import parse_source
from json5.model import *
from json5.utils import singledispatchmethod
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
    """
    Like loads, but takes a file-like object with a read method.

    :param f:
    :param kwargs:
    :return:
    """
    text = f.read()
    return loads(text)

def loads(s, *args, loader=None, **kwargs):
    """
    Take a string of JSON text and deserialize it

    :param s:
    :param loader: The loader class to use
    :param object_hook: same meaning as in ``json.loads``
    :param parse_float: same meaning as in ``json.loads``
    :param parse_int: same meaning as in ``json.loads``
    :param parse_constant: same meaning as in ``json.loads``
    :param strict: same meaning as in ``json.loads`` (currently has no effect)
    :param object_pairs_hook: same meaning as in ``json.loads``
    :return:
    """
    model = parse_source(s)
    # logger.debug('Model is %r', model)
    if loader is None:
        loader = DefaultLoader(**kwargs)
    return loader.load(model)

class DefaultLoader:
    def __init__(self, env=None, **env_kwargs):
        if env is None:
            env = Environment(**env_kwargs)
        self.env = env

    @singledispatchmethod
    def load(self, node):
        raise NotImplementedError(f"Can't load node {node}")

    to_python = load.register

    @to_python(JSONText)
    def json_model_to_python(self, node):
        logger.debug('json_model_to_python evaluating node %r', node)
        return self.load(node.value)

    @to_python(JSONObject)
    def json_object_to_python(self, node):
        logger.debug('json_object_to_python evaluating node %r', node)
        d = {}
        for key_value_pair in node.key_value_pairs:
            key = self.load(key_value_pair.key)
            value = self.load(key_value_pair.value)
            d[key] = value
        if self.env.object_pairs_hook:
            return self.env.object_pairs_hook(list(d.items()))
        elif self.env.object_hook:
            return self.env.object_hook(d)
        else:
            return d


    @to_python(JSONArray)
    def json_array_to_python(self, node):
        logger.debug('json_array_to_python evaluating node %r', node)
        return [self.load(value) for value in node.values]

    @to_python(Identifier)
    def identifier_to_python(self, node):
        logger.debug('identifier_to_python evaluating node %r', node)
        return JsonIdentifier(node.name)


    @to_python(Number)  # NaN/Infinity are covered here
    def number_to_python(self, node):
        logger.debug('number_to_python evaluating node %r', node)
        if self.env.parse_constant:
            return self.env.parse_constant(node.const)
        return node.value

    @to_python(Integer)
    def integer_to_python(self, node):
        if self.env.parse_int:
            return self.env.parse_int(node.raw_value)
        else:
            return node.value

    @to_python(Float)
    def float_to_python(self, node):
        if self.env.parse_float:
            return self.env.parse_float(node.raw_value)
        else:
            return node.value

    @to_python(UnaryOp)
    def unary_to_python(self, node):
        logger.debug('unary_to_python evaluating node %r', node)
        if isinstance(node.value, Infinity):
            return self.load(node.value)
        value = self.load(node.value)
        if node.op == '-':
            return value * -1
        else:
            return value

    @to_python(String)
    def string_to_python(self, node):
        logger.debug('string_to_python evaluating node %r', node)
        return node.characters


    @to_python(NullLiteral)
    def null_to_python(self, node):
        logger.debug('null_to_python evaluating node %r', node)
        return None

    @to_python(BooleanLiteral)
    def boolean_to_python(self, node):
        logger.debug('boolean_to_python evaluating node %r', node)
        return node.value

    @to_python(Comment)
    def comment_or_whitespace_to_python(self, node):
        raise RuntimeError("Comments are not supported in the default loader!")


class ModelLoader(DefaultLoader):
    def load(self, node):
        return node
