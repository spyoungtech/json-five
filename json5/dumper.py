from .utils import singledispatchmethod
from json5.model import *
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
    """
    Dump Python objects to a JSON string
    """
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

    @to_json(bool)
    def bool_to_json(self, b):
        self.env.write(str(b).lower(), indent=0)

    @to_json(type(None))
    def none_to_json(self, _):
        self.env.write('null', indent=0)

class ModelDumper:
    """
    Dump a model to a JSON string
    """
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

    @to_json(String)
    def string_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write(node.raw_value)  # The original value, including any escape sequences or line continuations
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

    @to_json(Infinity)
    def infinity_to_json(self, node):
        self.process_wsc_before(node)

        self.env.write('Infinity')
        self.process_wsc_after(node)

    @to_json(NaN)
    def nan_to_json(self, node):
        self.process_wsc_before(node)
        self.env.write('NaN')
        self.process_wsc_after(node)

class Modelizer:
    """
    Turn Python objects into a model
    """
    @singledispatchmethod
    def modelize(self, obj):
        raise NotImplementedError(f"Cannot modelize object of type {type(obj)}")
    
    to_model = modelize.register
    
    @to_model(str)
    def str_to_model(self, s):
        if repr(s).startswith("'"):
            return SingleQuotedString(s, raw_value=repr(s))
        else:
            return DoubleQuotedString(s, raw_value=repr(s))
    
    @to_model(dict)
    def dict_to_model(self, d):
        kvps = []
        for key, value in d.items():
            kvp = KeyValuePair(key=self.modelize(key), value=self.modelize(value))
            kvps.append(kvp)
        return JSONObject(*kvps)
    
    @to_model(list)
    def list_to_model(self, lst):
        list_values = []
        for v in lst:
            list_values.append(self.modelize(v))
        return JSONArray(*list_values)
    
    @to_model(int)
    def int_to_model(self, i):
        return Integer(str(i))


    @to_model(float)
    def float_to_model(self, f):
        if f == math.inf:
            return Infinity()
        elif f == -math.inf:
            return UnaryOp('-', Infinity())
        elif f is math.nan:
            return NaN()
        else:
            return Float(str(f))

    @to_model(bool)
    def bool_to_model(self, b):
        return BooleanLiteral(b)

    @to_model(type(None))
    def none_to_model(self, _):
        return NullLiteral()


def modelize(obj):
    """

    :param obj: a python object
    :return: a model representing the python object
    """
    return Modelizer().modelize(obj)
