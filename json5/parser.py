import re

import sys

from sly import Parser
from sly.yacc import SlyLogger
from json5.tokenizer import JSONLexer, tokenize
from json5.model import *
from json5.utils import JSON5DecodeError
import ast
from functools import lru_cache

class QuietSlyLogger(SlyLogger):
    def warning(self, *args, **kwargs):
        return
    debug = warning
    info = warning


ESCAPE_SEQUENCES = {
    'b': '\u0008',
    'f': '\u000C',
    'n': '\u000A',
    'r': '\u000D',
    't': '\u0009',
    'v': '\u000B',
    '0': '\u0000',
    '\\': '\u005c',
    '"': '\u0022',
    "'": '\u0027',
}

# class TrailingComma:
#     pass

def replace_escape_literals(matchobj):
    s = matchobj.group(0)
    if s.startswith('\\0') and len(s) == 3:
        raise JSON5DecodeError("'\\0' MUST NOT be followed by a decimal digit", None)
    seq = matchobj.group(1)
    return ESCAPE_SEQUENCES.get(seq, seq)


@lru_cache(maxsize=1024)
def _latin_escape_replace(s):
    if len(s) != 4:
        raise JSON5DecodeError("'\\x' MUST be followed by two hexadecimal digits", None)
    val = ast.literal_eval(f'"{s}"')
    if val == '\\':
        val = '\\\\'  # this is important; the subsequent regex will sub it back to \\
    return val


def latin_escape_replace(matchobj):
    s = matchobj.group(0)
    return _latin_escape_replace(s)


class JSONParser(Parser):
    # debugfile = 'parser.out'
    tokens = JSONLexer.tokens
    log = QuietSlyLogger(sys.stderr)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = []


    @_('{ wsc } value { wsc }')
    def text(self, p):
        node = JSONText(value=p[1])
        for wsc in p.wsc0:
            node.wsc_before.append(wsc)
        for wsc in p.wsc1:
            node.wsc_after.append(wsc)
        return node

    @_('key { wsc } COLON { wsc } value { wsc }')
    def first_key_value_pair(self, p):
        key = p[0]
        for wsc in p.wsc0:
            key.wsc_after.append(wsc)
        value = p[4]
        for wsc in p.wsc1:
            value.wsc_before.append(wsc)
        for wsc in p.wsc2:
            value.wsc_after.append(wsc)
        return KeyValuePair(key=p.key, value=p.value)


    @_('COMMA { wsc } [ first_key_value_pair ]')
    def subsequent_key_value_pair(self, p):
        if p.first_key_value_pair:
            node = p.first_key_value_pair
            for wsc in p.wsc:
                node.key.wsc_before.append(wsc)
        else:
            node = TrailingComma()
            for wsc in p.wsc:
                node.wsc_after.append(wsc)
        return node


    @_('WHITESPACE',
       'comment')
    def wsc(self, p):
        return p[0]

    @_('BLOCK_COMMENT')
    def comment(self, p):
        return BlockComment(p[0])


    @_('LINE_COMMENT')
    def comment(self, p):
        return LineComment(p[0])



    @_('first_key_value_pair { subsequent_key_value_pair }')
    def key_value_pairs(self, p):
        ret = [p.first_key_value_pair, ]
        for kvp in p.subsequent_key_value_pair:
            if isinstance(kvp, TrailingComma):
                return ret, kvp
            ret.append(kvp)
        return ret, None



    @_('LBRACE { wsc } [ key_value_pairs ] RBRACE')
    def json_object(self, p):
        if not p.key_value_pairs:
            node = JSONObject(leading_wsc=list(p.wsc or []))
        else:
            kvps, trailing_comma = p.key_value_pairs
            node = JSONObject(*kvps, trailing_comma=trailing_comma, leading_wsc=list(p.wsc or []))

        return node

    @_('value { wsc }')
    def first_array_value(self, p):
        node = p[0]
        for wsc in p.wsc:
            node.wsc_after.append(wsc)
        return node

    @_('COMMA { wsc } [ first_array_value ]')
    def subsequent_array_value(self, p):
        if p.first_array_value:
            node = p.first_array_value
            for wsc in p.wsc:
                node.wsc_before.append(wsc)
        else:
            node = TrailingComma()
            for wsc in p.wsc:
                node.wsc_after.append(wsc)
        return node

    @_('first_array_value { subsequent_array_value }')
    def array_values(self, p):
        ret = [p.first_array_value, ]
        for value in p.subsequent_array_value:
            if isinstance(value, TrailingComma):
                return ret, value
            ret.append(value)
        return ret, None


    @_('LBRACKET { wsc } [ array_values ] RBRACKET')
    def json_array(self, p):
        if not p.array_values:
            node = JSONArray()
        else:
            values, trailing_comma = p.array_values
            node = JSONArray(*values, trailing_comma=trailing_comma)

        for wsc in p.wsc:
            node.leading_wsc.append(wsc)

        return node

    @_('NAME')
    def identifier(self, p):
        return Identifier(name=p[0])

    @_('identifier',
       'string')
    def key(self, p):
        node = p[0]
        return node

    @_('INTEGER')
    def number(self, p):
        return Integer(p[0])

    @_('FLOAT')
    def number(self, p):
        return Float(p[0])

    @_('INFINITY')
    def number(self, p):
        return Infinity()

    @_('NAN')
    def number(self, p):
        return NaN()

    @_('MINUS number')
    def value(self, p):
        if isinstance(p.number, Infinity):
            p.number.negative = True
        node = UnaryOp(op='-', value=p.number)
        return node

    @_('PLUS number')
    def value(self, p):
        node = UnaryOp(op='+', value=p.number)
        return node

    @_('INTEGER EXPONENT',
       'FLOAT EXPONENT')
    def number(self, p):
        exp_notation = p[1][0]  # e or E
        return Float(p[0]+p[1], exp_notation=exp_notation)

    @_('HEXADECIMAL')
    def number(self, p):
        return Integer(p[0], is_hex=True)

    @_('DOUBLE_QUOTE_STRING')
    def double_quoted_string(self, p):
        raw_value = p[0]
        contents = raw_value[1:-1]
        if re.search(r'(?<!\\)([\u000D\u2028\u2029]|(?<!\r)\n)', contents):
            errmsg = f"Illegal line terminator without continuation"
            self.errors.append(JSON5DecodeError(errmsg, p._slice[0]))
        contents = re.sub(r'\\(\r\n|[\u000A\u000D\u2028\u2029])', '', contents)
        try:
            contents = re.sub(r'\\x[a-fA-F0-9]{0,2}', latin_escape_replace, contents)
        except JSON5DecodeError as exc:
            self.errors.append(JSON5DecodeError(exc.args[0], p._slice[0]))
        try:
            contents = re.sub(r'\\(0\d|.)', replace_escape_literals, contents)
        except JSON5DecodeError as exc:
            self.errors.append(JSON5DecodeError(exc.args[0], p._slice[0]))
        return DoubleQuotedString(contents, raw_value=raw_value)

    @_("SINGLE_QUOTE_STRING")
    def single_quoted_string(self, p):
        raw_value = p[0]
        contents = raw_value[1:-1]
        if re.search(r'(?<!\\)([\u000D\u2028\u2029]|(?<!\r)\n)', contents):
            errmsg = f"Illegal line terminator without continuation"
            self.errors.append(JSON5DecodeError(errmsg, p._slice[0]))
        contents = re.sub(r'\\(\r\n|[\u000A\u000D\u2028\u2029])', '', contents)
        try:
            contents = re.sub(r'\\x[a-fA-F0-9]{0,2}', latin_escape_replace, contents)
        except JSON5DecodeError as exc:
            self.errors.append(JSON5DecodeError(exc.args[0], p._slice[0]))
        try:
            contents = re.sub(r'\\(0\d|.)', replace_escape_literals, contents)
        except JSON5DecodeError as exc:
            self.errors.append(JSON5DecodeError(exc.args[0], p._slice[0]))
        return SingleQuotedString(contents, raw_value=raw_value)

    @_('double_quoted_string',
       'single_quoted_string')
    def string(self, p):
        return p[0]

    @_('TRUE')
    def boolean(self, p):
        return BooleanLiteral(True)

    @_('FALSE')
    def boolean(self, p):
        return BooleanLiteral(False)

    @_('NULL')
    def null(self, p):
        return NullLiteral()

    @_('string',
       'json_object',
       'json_array',
       'boolean',
       'null',
       'number',)
    def value(self, p):
        node = p[0]
        return node

    @_('BREAK',
    'DO',
    'INSTANCEOF',
    'TYPEOF',
    'CASE',
    'ELSE',
    'NEW',
    'VAR',
    'CATCH',
    'FINALLY',
    'RETURN',
    'VOID',
    'CONTINUE',
    'FOR',
    'SWITCH',
    'WHILE',
    'DEBUGGER',
    'FUNCTION',
    'THIS',
    'WITH',
    'DEFAULT',
    'IF',
    'THROW',
    'DELETE',
    'IN',
    'TRY',)
    def identifier(self, p):
        err = JSON5DecodeError(f"Illegal name ({p[0]}) is a reserved keyword and may not be used", p._slice[0])
        self.errors.append(err)
        return Identifier(name=p[0])

    def error(self, token):
        if token:
            self.errors.append(JSON5DecodeError('Syntax Error', token))
        else:
            self.errors.append(JSON5DecodeError('Expecting value. Received unexpected EOF', None))

    def parse(self, *args, **kwargs):
        model = super().parse(*args, **kwargs)
        if self.errors:
            if len(self.errors) > 1:
                primary_error = self.errors[0]
                additional_errors = '\n\t'.join(err.args[0] for err in self.errors[1:])
                msg = "There were multiple errors parsing the JSON5 document.\n" \
                      "The primary error was: \n\t{}\n" \
                      "Additionally, the following errors were also detected:\n\t {}"
                msg = msg.format(primary_error.args[0], additional_errors)
                err = JSON5DecodeError(msg, None)
                err.lineno = primary_error.lineno
                err.token = primary_error.token
                err.index = primary_error.index
                raise err
            else:
                raise self.errors[0]
        return model


def parse_tokens(raw_tokens):
    parser = JSONParser()
    return parser.parse(raw_tokens)


def parse_source(text):
    tokens = tokenize(text)
    model = parse_tokens(tokens)
    return model
