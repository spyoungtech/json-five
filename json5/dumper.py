import sys
from .utils import singledispatchmethod
from json5.model import *
from json5.loader import JsonIdentifier
from collections import UserDict
import json
import io

class Environment(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outfile = io.StringIO()
        self.indent_level = 0
        self.indent = 0


    def write(self, s, indent=None):
        if indent is None:
            indent = self.indent_level
        whitespace = ' ' * self.indent * indent
        s = f'{whitespace}{s}'
        self.outfile.write(s)


def dump(obj, f, **kwargs):
    text = dumps(obj, **kwargs)
    return f.write(text)


def dumps(obj, dumper=None, indent=0):
    env = Environment()
    env.indent = indent
    if dumper is None:
        dumper = DefaultDumper(env=env)
    model = dumper.dump(obj)
    dumper.env.outfile.seek(0)
    return dumper.env.outfile.read()

class DefaultDumper:
    def __init__(self, env=None):
        if env is None:
            env = Environment()
        self.env = env

    @singledispatchmethod
    def dump(self, obj):
        raise NotImplementedError(f"Cannot dump node {repr(obj)}")
    
    to_json = dump.register
    
    @to_json(dict)
    def dict_to_json(self, d):
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
    def int_to_json(self, i):
        self.env.write(str(i), indent=0)
    
    
    @to_json(str)
    def str_to_json(self, s):
        self.env.write(json.dumps(s), indent=0)
        # if isinstance(s, JsonIdentifier):
        #     quote_char = None
        # elif "'" in s:
        #     quote_char = '"'
        # else:
        #     quote_char = "'"
        #
        # if quote_char:
        #     self.env.write(quote_char, indent=0)
        # self.env.write(s, indent=0)
        # if quote_char:
        #     self.env.write(quote_char, indent=0)
    
    
    @to_json(list)
    def list_to_json(self, l):
        self.env.write('[', indent=0)
        if self.env.indent:
            self.env.indent_level += 1
            self.env.write('\n', indent=0)
        list_length = len(l)
        for index, item in enumerate(l, start=1):
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
    def float_to_json(self, f):
        if f == math.inf:
            self.env.write('Infinity', indent=0)
        elif f == -math.inf:
            self.env.write('-Infinity', indent=0)
        elif f is math.nan:
            self.env.write('NaN', indent=0)
        else:
            self.env.write(str(f), indent=0)


class ModelDumper:
    def __init__(self, env=None):
        #  any provided environment is ignored
        self.env = Environment()


    def process_wsc_before(self, node):
        for wsc in node.wsc_before:
            if isinstance(wsc, Comment):
                self.dump(wsc)
            elif isinstance(wsc, str):
                self.env.write(wsc)
            else:
                raise ValueError(f"Did not expect {type(node)}")

    def process_wsc_after(self, node):
        for wsc in node.wsc_after:
            if isinstance(wsc, Comment):
                self.dump(wsc)
            elif isinstance(wsc, str):
                self.env.write(wsc)
            else:
                raise ValueError(f"Did not expect {type(node)}")


    @singledispatchmethod
    def dump(self, node):
        raise NotImplementedError('foo')

    to_json = dump.register

    @to_json(JSONText)
    def json_model_to_json(self, node):
        self.process_wsc_before(node)
        self.dump(node.value)
        self.process_wsc_after(node)

    @to_json(JSONObject)
    def json_object_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write('{')
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
    def json_array_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write('[')
        for index, value in enumerate(node.values, start=1):
            self.dump(value)
            if index != len(node.values):
                self.env.write(',')
        if node.trailing_comma:
            self.dump(node.trailing_comma)
        self.env.write(']')
        self.process_wsc_after(node)

    @to_json(Identifier)
    def identifier_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write(node.name)
        self.process_wsc_after(node)

    @to_json(Integer)
    def integer_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write(node.raw_value)
        self.process_wsc_after(node)

    @to_json(Float)
    def float_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write(node.raw_value)
        self.process_wsc_after(node)

    @to_json(UnaryOp)
    def unary_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write(node.op)
        self.dump(node.value)
        self.process_wsc_after(node)

    # @to_json(String)
    # def string_to_json(self, node):
    #     self.process_wsc_before(node)
    #
    #     self.process_wsc_after(node)

    @to_json(SingleQuotedString)
    def single_quoted_string_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write("'")
        self.env.write(node.characters)  # Need to properly escape this
        self.env.write("'")
        self.process_wsc_after(node)

    @to_json(DoubleQuotedString)
    def double_quoted_string_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write('"')
        self.env.write(node.characters)  # Need to escape; what about line continuations?
        self.env.write('"')
        self.process_wsc_after(node)

    @to_json(NullLiteral)
    def null_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write('null')
        self.process_wsc_after(node)

    @to_json(BooleanLiteral)
    def boolean_to_json(self, node):
        self.process_wsc_before(node)
        if node.value:
            self.env.write('true')
        else:
            self.env.write('false')
        self.process_wsc_after(node)

    @to_json(LineComment)
    def line_comment_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write(node.value)
        self.process_wsc_after(node)

    @to_json(BlockComment)
    def block_comment_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write(node.value)
        self.process_wsc_after(node)

    @to_json(TrailingComma)
    def trailing_comma_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write(',')
        self.process_wsc_after(node)