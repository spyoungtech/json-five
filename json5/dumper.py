import sys
from functools import singledispatch
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


def dumps(obj, indent=0):
    env = Environment()
    env.indent = indent
    model = _dump(obj, env)
    env.outfile.seek(0)
    return env.outfile.read()


@singledispatch
def _dump(obj, env):
    raise NotImplementedError(f"Cannot dump node {repr(obj)}")

to_json = _dump.register

@to_json(dict)
def dict_to_json(d, env):
    env.write('{', indent=0)
    if env.indent:
        env.write('\n')
        env.indent_level += 1
    for index, (key, value) in enumerate(d.items(), start=1):
        if env.indent:
            env.write('')
        _dump(key, env)
        env.write(': ', indent=0)
        _dump(value, env)
        if index == len(d):
            break
        if env.indent:
            env.write(',', indent=0)
            env.write('\n', indent=0)
        else:
            env.write(', ', indent=0)

    if env.indent:
        env.indent_level -= 1
        env.write('\n')
        env.write('}')
    else:
        env.write('}', indent=0)


@to_json(int)
def int_to_json(i, env):
    env.write(str(i), indent=0)


@to_json(str)
def str_to_json(s, env):
    env.write(json.dumps(s), indent=0)
    # if isinstance(s, JsonIdentifier):
    #     quote_char = None
    # elif "'" in s:
    #     quote_char = '"'
    # else:
    #     quote_char = "'"
    #
    # if quote_char:
    #     env.write(quote_char, indent=0)
    # env.write(s, indent=0)
    # if quote_char:
    #     env.write(quote_char, indent=0)


@to_json(list)
def list_to_json(l, env):
    env.write('[', indent=0)
    if env.indent:
        env.indent_level += 1
        env.write('\n', indent=0)
    list_length = len(l)
    for index, item in enumerate(l, start=1):
        if env.indent:
            env.write('')
        _dump(item, env)
        if index != list_length:
            if env.indent:
                env.write(',', indent=0)
            else:
                env.write(', ', indent=0)
        if env.indent:
            env.write('\n', indent=0)
    if env.indent:
        env.indent_level -= 1
    env.write(']')


@to_json(float)
def float_to_json(f, env):
    if f == math.inf:
        env.write('Infinity', indent=0)
    elif f == -math.inf:
        env.write('-Infinity', indent=0)
    elif f is math.nan:
        env.write('NaN', indent=0)
    else:
        env.write(str(f), indent=0)

