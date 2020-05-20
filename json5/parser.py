import re

import sys

from sly import Parser
from json5.tokenizer import JSONLexer, tokenize
from json5.model import *

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
    seq = matchobj.group(1)
    return ESCAPE_SEQUENCES.get(seq, seq)


class JSONParser(Parser):
    # debugfile = 'parser.out'
    tokens = JSONLexer.tokens


    @_('value')
    def text(self, p):
        return JSONText(value=p[0])


    @_('key COLON value')
    def first_key_value_pair(self, p):
        return KeyValuePair(key=p.key, value=p.value)

    @_('COMMA { whitespace_andor_comment } [ key COLON value ]')
    def subsequent_key_value_pair(self, p):
        if p.key and p.value:
            for wsc in p.whitespace_andor_comment:
                p.key.wsc_before.append(wsc)
            return KeyValuePair(key=p.key, value=p.value)
        else:
            node = TrailingComma()
            for wsc in p.whitespace_andor_comment:
                node.wsc_after.append(wsc)
            return node


    @_('WHITESPACE',
       'comment')
    def whitespace_andor_comment(self, p):
        return p[0]

    @_('[ WHITESPACE ] BLOCK_COMMENT [ WHITESPACE ]')
    def comment(self, p):
        node = BlockComment(p[1])
        if p.WHITESPACE0:
            node.wsc_before.append(p.WHITESPACE0)
        if p.WHITESPACE1:
            node.wsc_after.append(p.WHITESPACE1)
        return node

    @_('[ WHITESPACE ] LINE_COMMENT [ WHITESPACE ]')
    def comment(self, p):
        node = LineComment(p[1])
        if p.WHITESPACE0:
            node.wsc_before.append(p.WHITESPACE0)
        if p.WHITESPACE1:
            node.wsc_after.append(p.WHITESPACE1)
        return node


    @_('first_key_value_pair { subsequent_key_value_pair }')
    def key_value_pairs(self, p):
        ret = [p.first_key_value_pair, ]
        for kvp in p.subsequent_key_value_pair:
            if isinstance(kvp, TrailingComma):
                return ret, kvp
            ret.append(kvp)
        return ret, None



    @_('LBRACE [ key_value_pairs ] RBRACE')
    def json_object(self, p):
        if not p.key_value_pairs:
            return JSONObject()
        kvps, trailing_comma = p.key_value_pairs
        return JSONObject(*kvps, trailing_comma=trailing_comma)

    @_('value')
    def first_array_value(self, p):
        return p[0]

    @_('COMMA { whitespace_andor_comment } [ value ]')
    def subsequent_array_value(self, p):
        if p.value:
            node = p.value
            for wsc in p.whitespace_andor_comment:
                node.wsc_before.append(wsc)  # Wouldn't the value already take care of this? reduce...reduce....
        else:
            node = TrailingComma()
            for wsc in p.whitespace_andor_comment:
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


    @_('LBRACKET [ array_values ] RBRACKET')
    def json_array(self, p):
        if not p.array_values:
            return JSONArray()
        values, trailing_comma = p.array_values
        return JSONArray(*values, trailing_comma=trailing_comma)



    @_('NAME')
    def identifier(self, p):
        return Identifier(name=p[0])

    @_('{ whitespace_andor_comment } identifier { whitespace_andor_comment }',
       '{ whitespace_andor_comment } string { whitespace_andor_comment }')
    def key(self, p):
        node = p[1]
        for wsc in p.whitespace_andor_comment0:
            node.wsc_before.append(wsc)
        for wsc in p.whitespace_andor_comment1:
            node.wsc_after.append(wsc)
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

    @_('{ whitespace_andor_comment } MINUS number { whitespace_andor_comment }')
    def value(self, p):
        if isinstance(p.number, Infinity):
            p.number.negative = True
        node = UnaryOp(op='-', value=p.number)
        for wsc in p.whitespace_andor_comment0:
            node.wsc_before.append(wsc)
        for wsc in p.whitespace_andor_comment1:
            node.wsc_after.append(wsc)
        return node

    @_('{ whitespace_andor_comment } PLUS number { whitespace_andor_comment }')
    def value(self, p):
        node = UnaryOp(op='+', value=p.number)
        for wsc in p.whitespace_andor_comment0:
            node.wsc_before.append(wsc)
        for wsc in p.whitespace_andor_comment1:
            node.wsc_after.append(wsc)
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
        contents = re.sub(r'\\(\r\n|[\u000A\u000D\u2028\u2029])', '', contents)
        contents = re.sub(r'\\(.)', replace_escape_literals, contents)
        return DoubleQuotedString(contents, raw_value=raw_value)

    @_("SINGLE_QUOTE_STRING")
    def single_quoted_string(self, p):
        raw_value = p[0]
        contents = raw_value[1:-1]
        contents = re.sub(r'\\(\r\n|[\u000A\u000D\u2028\u2029])', '', contents)
        contents = re.sub(r'\\(.)', replace_escape_literals, contents)
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

    @_('{ whitespace_andor_comment } string { whitespace_andor_comment }',
       '{ whitespace_andor_comment } json_object { whitespace_andor_comment }',
       '{ whitespace_andor_comment } json_array { whitespace_andor_comment }',
       '{ whitespace_andor_comment } boolean { whitespace_andor_comment }',
       '{ whitespace_andor_comment } null { whitespace_andor_comment }',
       '{ whitespace_andor_comment } number { whitespace_andor_comment }',)
    def value(self, p):
        node = p[1]
        for wsc in p.whitespace_andor_comment0:
            node.wsc_before.append(wsc)
        for wsc in p.whitespace_andor_comment1:
            node.wsc_after.append(wsc)
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
        raise SyntaxError(f"{p[0]} is a reserved keyword and may not be used")


def parse_tokens(raw_tokens):
    parser = JSONParser()
    return parser.parse(raw_tokens)


def parse_source(text):
    tokens = tokenize(text)
    model = parse_tokens(tokens)
    if model is None:
        raise SyntaxError('Was expecting a JSON value, got none. This was probably due to a syntax error while parsing')
    return model
