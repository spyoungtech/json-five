from __future__ import annotations

import io
import json
import math
import typing
from abc import abstractmethod
from typing import Any

from .loader import JsonIdentifier
from .utils import singledispatchmethod
from json5.model import *


class Environment:
    def __init__(self) -> None:
        self.outfile: typing.TextIO = io.StringIO()
        self.indent_level: int = 0
        self.indent: int = 0

    def write(self, s: str, indent: int | None = None) -> None:
        if indent is None:
            indent = self.indent_level
        whitespace = ' ' * self.indent * indent
        s = f'{whitespace}{s}'
        self.outfile.write(s)


def dump(obj: Any, f: typing.TextIO, **kwargs: Any) -> int:
    text = dumps(obj, **kwargs)
    return f.write(text)


def dumps(obj: Any, dumper: BaseDumper | None = None, indent: int = 0) -> str:
    env = Environment()
    env.indent = indent
    if dumper is None:
        dumper = DefaultDumper(env=env)
    dumper.dump(obj)
    dumper.env.outfile.seek(0)
    ret: str = dumper.env.outfile.read()
    return ret


class BaseDumper:
    def __init__(self, env: Environment | None = None):
        if env is None:
            env = Environment()
        self.env = env

    @singledispatchmethod
    @abstractmethod
    def dump(self, obj: Any) -> Any:
        return NotImplemented


class DefaultDumper(BaseDumper):
    """
    Dump Python objects to a JSON string
    """

    @singledispatchmethod
    def dump(self, obj: Any) -> Any:
        raise NotImplementedError(f"Cannot dump node {repr(obj)}")

    to_json = dump.register

    @to_json(dict)
    def dict_to_json(self, d: dict[Any, Any]) -> Any:
        self.env.write('{', indent=0)
        if self.env.indent:
            self.env.write('\n')
            self.env.indent_level += 1
        for index, (key, value) in enumerate(d.items(), start=1):
            if self.env.indent:
                self.env.write('')
            self.dump(key)
            self.env.write(': ', indent=0)
            self.dump(value)
            if index == len(d):
                break
            if self.env.indent:
                self.env.write(',', indent=0)
                self.env.write('\n', indent=0)
            else:
                self.env.write(', ', indent=0)

        if self.env.indent:
            self.env.indent_level -= 1
            self.env.write('\n')
            self.env.write('}')
        else:
            self.env.write('}', indent=0)

    @to_json(int)
    def int_to_json(self, i: int) -> Any:
        self.env.write(str(i), indent=0)

    @to_json(JsonIdentifier)
    def identifier_to_json(self, s: JsonIdentifier) -> Any:
        self.env.write(s, indent=0)

    @to_json(str)
    def str_to_json(self, s: str) -> Any:
        self.env.write(json.dumps(s), indent=0)

    @to_json(list)
    def list_to_json(self, the_list: list[Any]) -> Any:
        self.env.write('[', indent=0)
        if self.env.indent:
            self.env.indent_level += 1
            self.env.write('\n', indent=0)
        list_length = len(the_list)
        for index, item in enumerate(the_list, start=1):
            if self.env.indent:
                self.env.write('')
            self.dump(item)
            if index != list_length:
                if self.env.indent:
                    self.env.write(',', indent=0)
                else:
                    self.env.write(', ', indent=0)
            if self.env.indent:
                self.env.write('\n', indent=0)
        if self.env.indent:
            self.env.indent_level -= 1
        self.env.write(']')

    @to_json(float)
    def float_to_json(self, f: float) -> Any:
        if f == math.inf:
            self.env.write('Infinity', indent=0)
        elif f == -math.inf:
            self.env.write('-Infinity', indent=0)
        elif f is math.nan:
            self.env.write('NaN', indent=0)
        else:
            self.env.write(str(f), indent=0)

    @to_json(bool)
    def bool_to_json(self, b: bool) -> Any:
        self.env.write(str(b).lower(), indent=0)

    @to_json(type(None))
    def none_to_json(self, _: Any) -> Any:
        self.env.write('null', indent=0)


class ModelDumper:
    """
    Dump a model to a JSON string
    """

    def __init__(self, env: Environment | None = None):
        #  any provided environment is ignored
        self.env = Environment()

    def process_wsc_before(self, node: Node) -> None:
        for wsc in node.wsc_before:
            if isinstance(wsc, Comment):
                self.dump(wsc)
            elif isinstance(wsc, str):
                self.env.write(wsc)
            else:
                raise ValueError(f"Did not expect {type(node)}")

    def process_wsc_after(self, node: Node) -> None:
        for wsc in node.wsc_after:
            if isinstance(wsc, Comment):
                self.dump(wsc)
            elif isinstance(wsc, str):
                self.env.write(wsc)
            else:
                raise ValueError(f"Did not expect {type(wsc)}")

    def process_leading_wsc(self, node: JSONObject | JSONArray) -> None:
        for wsc in node.leading_wsc:
            if isinstance(wsc, Comment):
                self.dump(wsc)
            elif isinstance(wsc, str):
                self.env.write(wsc)
            else:
                raise ValueError(f"Did not expect {type(wsc)}")

    @singledispatchmethod
    def dump(self, node: Node) -> Any:
        raise NotImplementedError('foo')

    to_json = dump.register

    @to_json(JSONText)
    def json_model_to_json(self, node: JSONText) -> Any:
        self.process_wsc_before(node)
        self.dump(node.value)
        self.process_wsc_after(node)

    @to_json(JSONObject)
    def json_object_to_json(self, node: JSONObject) -> Any:
        self.process_wsc_before(node)
        self.env.write('{')
        if node.leading_wsc:
            self.process_leading_wsc(node)
        num_pairs = len(node.key_value_pairs)
        for index, kvp in enumerate(node.key_value_pairs, start=1):
            self.dump(kvp.key)
            self.env.write(':')
            self.dump(kvp.value)
            if index != num_pairs:
                self.env.write(',')
        if node.trailing_comma:
            self.dump(node.trailing_comma)
        self.env.write('}')
        self.process_wsc_after(node)

    @to_json(JSONArray)
    def json_array_to_json(self, node: JSONArray) -> Any:
        self.process_wsc_before(node)
        self.env.write('[')
        if node.leading_wsc:
            self.process_leading_wsc(node)
        for index, value in enumerate(node.values, start=1):
            self.dump(value)
            if index != len(node.values):
                self.env.write(',')
        if node.trailing_comma:
            self.dump(node.trailing_comma)
        self.env.write(']')
        self.process_wsc_after(node)

    @to_json(Identifier)
    def identifier_to_json(self, node: Identifier) -> Any:
        self.process_wsc_before(node)
        self.env.write(node.raw_value)
        self.process_wsc_after(node)

    @to_json(Integer)
    def integer_to_json(self, node: Integer) -> Any:
        self.process_wsc_before(node)
        self.env.write(node.raw_value)
        self.process_wsc_after(node)

    @to_json(Float)
    def float_to_json(self, node: Float) -> Any:
        self.process_wsc_before(node)
        self.env.write(node.raw_value)
        self.process_wsc_after(node)

    @to_json(UnaryOp)
    def unary_to_json(self, node: UnaryOp) -> Any:
        self.process_wsc_before(node)
        self.env.write(node.op)
        self.dump(node.value)
        self.process_wsc_after(node)

    @to_json(String)
    def string_to_json(self, node: SingleQuotedString | DoubleQuotedString) -> Any:
        self.process_wsc_before(node)
        self.env.write(node.raw_value)  # The original value, including any escape sequences or line continuations
        self.process_wsc_after(node)

    @to_json(NullLiteral)
    def null_to_json(self, node: NullLiteral) -> Any:
        self.process_wsc_before(node)
        self.env.write('null')
        self.process_wsc_after(node)

    @to_json(BooleanLiteral)
    def boolean_to_json(self, node: BooleanLiteral) -> Any:
        self.process_wsc_before(node)
        if node.value:
            self.env.write('true')
        else:
            self.env.write('false')
        self.process_wsc_after(node)

    @to_json(LineComment)
    def line_comment_to_json(self, node: LineComment) -> Any:
        self.process_wsc_before(node)
        self.env.write(node.value)
        self.process_wsc_after(node)

    @to_json(BlockComment)
    def block_comment_to_json(self, node: BlockComment) -> Any:
        self.process_wsc_before(node)
        self.env.write(node.value)
        self.process_wsc_after(node)

    @to_json(TrailingComma)
    def trailing_comma_to_json(self, node: TrailingComma) -> Any:
        self.process_wsc_before(node)
        self.env.write(',')
        self.process_wsc_after(node)

    @to_json(Infinity)
    def infinity_to_json(self, node: Infinity) -> Any:
        self.process_wsc_before(node)

        self.env.write('Infinity')
        self.process_wsc_after(node)

    @to_json(NaN)
    def nan_to_json(self, node: NaN) -> Any:
        self.process_wsc_before(node)
        self.env.write('NaN')
        self.process_wsc_after(node)


class Modelizer:
    """
    Turn Python objects into a model
    """

    @singledispatchmethod
    def modelize(self, obj: Any) -> Node:
        raise NotImplementedError(f"Cannot modelize object of type {type(obj)}")

    to_model = modelize.register

    @to_model(str)
    def str_to_model(self, s: str) -> SingleQuotedString | DoubleQuotedString:
        if repr(s).startswith("'"):
            return SingleQuotedString(s, raw_value=repr(s))
        else:
            return DoubleQuotedString(s, raw_value=repr(s))

    @to_model(dict)
    def dict_to_model(self, d: dict[Any, Any]) -> JSONObject:
        kvps: list[KeyValuePair] = []
        for key, value in d.items():
            kvp = KeyValuePair(key=self.modelize(key), value=self.modelize(value))  # type: ignore[arg-type]
            kvps.append(kvp)
        return JSONObject(*kvps)

    @to_model(list)
    def list_to_model(self, lst: list[Any]) -> JSONArray:
        list_values: list[Value] = []
        for v in lst:
            list_values.append(self.modelize(v))  # type: ignore[arg-type]
        return JSONArray(*list_values)

    @to_model(int)
    def int_to_model(self, i: int) -> Integer:
        return Integer(str(i))

    @to_model(float)
    def float_to_model(self, f: float) -> Infinity | NaN | Float | UnaryOp:
        if f == math.inf:
            return Infinity()
        elif f == -math.inf:
            return UnaryOp('-', Infinity())
        elif f is math.nan:
            return NaN()
        else:
            return Float(str(f))

    @to_model(bool)
    def bool_to_model(self, b: bool) -> BooleanLiteral:
        return BooleanLiteral(b)

    @to_model(type(None))
    def none_to_model(self, _: Any) -> NullLiteral:
        return NullLiteral()


def modelize(obj: Any) -> Node:
    """

    :param obj: a python object
    :return: a model representing the python object
    """
    return Modelizer().modelize(obj)
