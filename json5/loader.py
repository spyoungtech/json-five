from __future__ import annotations

import logging
import typing
from abc import abstractmethod
from typing import Callable
from typing import Literal

from json5.model import BooleanLiteral
from json5.model import Comment
from json5.model import DoubleQuotedString
from json5.model import Float
from json5.model import Identifier
from json5.model import Infinity
from json5.model import Integer
from json5.model import JSONArray
from json5.model import JSONObject
from json5.model import JSONText
from json5.model import NaN
from json5.model import Node
from json5.model import NullLiteral
from json5.model import SingleQuotedString
from json5.model import String
from json5.model import UnaryOp
from json5.parser import parse_source
from json5.utils import singledispatchmethod

logger = logging.getLogger(__name__)
# logger.setLevel(level=logging.DEBUG)
# logger.addHandler(logging.StreamHandler(stream=sys.stderr))


class Environment:
    def __init__(
        self,
        object_hook: Callable[[dict[typing.Any, typing.Any]], typing.Any] | None = None,
        parse_float: Callable[[str], typing.Any] | None = None,
        parse_int: Callable[[str], typing.Any] | None = None,
        parse_constant: Callable[[Literal['-Infinity', 'Infinity', 'NaN']], typing.Any] | None = None,
        strict: bool = True,
        object_pairs_hook: Callable[[list[tuple[str | JsonIdentifier, typing.Any]]], typing.Any] | None = None,
        parse_json5_identifiers: Callable[[JsonIdentifier], typing.Any] | None = None,
    ):
        self.object_hook: Callable[[dict[typing.Any, typing.Any]], typing.Any] | None = object_hook
        self.parse_float: Callable[[str], typing.Any] | None = parse_float
        self.parse_int: Callable[[str], typing.Any] | None = parse_int
        self.parse_constant: Callable[[Literal['-Infinity', 'Infinity', 'NaN']], typing.Any] | None = parse_constant
        self.strict: bool = strict
        self.object_pairs_hook: None | (
            Callable[[list[tuple[str | JsonIdentifier, typing.Any]]], typing.Any]
        ) = object_pairs_hook
        self.parse_json5_identifiers: Callable[[JsonIdentifier], typing.Any] | None = parse_json5_identifiers


class JsonIdentifier(str):
    ...


def load(
    f: typing.TextIO,
    *,
    loader: LoaderBase | None = None,
    object_hook: Callable[[dict[typing.Any, typing.Any]], typing.Any] | None = None,
    parse_float: Callable[[str], typing.Any] | None = None,
    parse_int: Callable[[str], typing.Any] | None = None,
    parse_constant: Callable[[Literal['-Infinity', 'Infinity', 'NaN']], typing.Any] | None = None,
    strict: bool = True,
    object_pairs_hook: Callable[[list[tuple[str | JsonIdentifier, typing.Any]]], typing.Any] | None = None,
    parse_json5_identifiers: Callable[[JsonIdentifier], typing.Any] | None = None,
) -> typing.Any:
    """
    Like loads, but takes a file-like object with a read method.

    :param f:
    :param kwargs:
    :return:
    """
    text = f.read()
    return loads(
        text,
        loader=loader,
        object_hook=object_hook,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant,
        strict=strict,
        object_pairs_hook=object_pairs_hook,
        parse_json5_identifiers=parse_json5_identifiers,
    )


def loads(
    s: str,
    *,
    loader: LoaderBase | None = None,
    object_hook: Callable[[dict[typing.Any, typing.Any]], typing.Any] | None = None,
    parse_float: Callable[[str], typing.Any] | None = None,
    parse_int: Callable[[str], typing.Any] | None = None,
    parse_constant: Callable[[Literal['-Infinity', 'Infinity', 'NaN']], typing.Any] | None = None,
    strict: bool = True,
    object_pairs_hook: Callable[[list[tuple[str | JsonIdentifier, typing.Any]]], typing.Any] | None = None,
    parse_json5_identifiers: Callable[[JsonIdentifier], typing.Any] | None = None,
) -> typing.Any:
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
    :param parse_json5_identifiers: callable that is passed a JsonIdentifer. The return value of the callable is used to load JSON Identifiers (unquoted keys) in JSON5 objects
    :return:
    """
    model = parse_source(s)
    # logger.debug('Model is %r', model)
    if loader is None:
        loader = DefaultLoader(
            object_hook=object_hook,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            strict=strict,
            object_pairs_hook=object_pairs_hook,
            parse_json5_identifiers=parse_json5_identifiers,
        )
    return loader.load(model)


class LoaderBase:
    def __init__(self, env: Environment | None = None, **env_kwargs: typing.Any):
        if env is None:
            env = Environment(**env_kwargs)
        self.env: Environment = env

    @singledispatchmethod
    @abstractmethod
    def load(self, node: Node) -> typing.Any:
        return NotImplemented


class DefaultLoader(LoaderBase):
    @singledispatchmethod
    def load(self, node: Node) -> typing.Any:
        raise NotImplementedError(f"Can't load node {node}")

    to_python = load.register

    @to_python(JSONText)
    def json_model_to_python(self, node: JSONText) -> typing.Any:
        logger.debug('json_model_to_python evaluating node %r', node)
        return self.load(node.value)

    @to_python(JSONObject)
    def json_object_to_python(self, node: JSONObject) -> typing.Any:
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
    def json_array_to_python(self, node: JSONArray) -> list[typing.Any]:
        logger.debug('json_array_to_python evaluating node %r', node)
        return [self.load(value) for value in node.values]

    @to_python(Identifier)
    def identifier_to_python(self, node: Identifier) -> typing.Any:
        logger.debug('identifier_to_python evaluating node %r', node)
        res = JsonIdentifier(node.name)
        if self.env.parse_json5_identifiers:
            return self.env.parse_json5_identifiers(res)
        return res

    @to_python(Infinity)  # NaN/Infinity are covered here
    def inf_to_python(self, node: Infinity) -> typing.Any:
        logger.debug('inf_to_python evaluating node %r', node)
        if self.env.parse_constant:
            return self.env.parse_constant(node.const)
        return node.value

    @to_python(NaN)  # NaN/Infinity are covered here
    def nan_to_python(self, node: NaN) -> typing.Any:
        logger.debug('nan_to_python evaluating node %r', node)
        if self.env.parse_constant:
            return self.env.parse_constant(node.const)
        return node.value

    @to_python(Integer)
    def integer_to_python(self, node: Integer) -> typing.Any:
        if self.env.parse_int:
            return self.env.parse_int(node.raw_value)
        else:
            return node.value

    @to_python(Float)
    def float_to_python(self, node: Float) -> typing.Any:
        if self.env.parse_float:
            return self.env.parse_float(node.raw_value)
        else:
            return node.value

    @to_python(UnaryOp)
    def unary_to_python(self, node: UnaryOp) -> typing.Any:
        logger.debug('unary_to_python evaluating node %r', node)
        if isinstance(node.value, Infinity):
            return self.load(node.value)
        value = self.load(node.value)
        if node.op == '-':
            return value * -1
        else:
            return value

    @to_python(String)
    def string_to_python(self, node: DoubleQuotedString | SingleQuotedString) -> str:
        logger.debug('string_to_python evaluating node %r', node)
        ret: str = node.characters
        return ret

    @to_python(NullLiteral)
    def null_to_python(self, node: NullLiteral) -> None:
        logger.debug('null_to_python evaluating node %r', node)
        return None

    @to_python(BooleanLiteral)
    def boolean_to_python(self, node: BooleanLiteral) -> bool:
        logger.debug('boolean_to_python evaluating node %r', node)
        return node.value

    @to_python(Comment)
    def comment_or_whitespace_to_python(self, node: Comment) -> typing.NoReturn:
        raise RuntimeError("Comments are not supported in the default loader!")


class ModelLoader(LoaderBase):
    @singledispatchmethod
    def load(self, node: Node) -> typing.Any:
        return node
