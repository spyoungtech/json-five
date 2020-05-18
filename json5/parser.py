import re

import sys

from sly import Parser
from json5.tokenizer import JSONLexer, tokenize
from json5.model import *

class JSONParser(Parser):
    debugfile = 'parser.out'
    tokens = JSONLexer.tokens



    @_('value')
    def text(self, p):
        return JSONText(value=p[0])


    @_('key COLON value [ COMMA { WHITESPACE } ]')
    def key_value_pair(self, p):
        return KeyValuePair(key=p.key, value=p.value)


    @_('WHITESPACE',
       'comment')
    def whitespace_andor_comment(self, p):
        return p[0]

    @_('[ WHITESPACE ] BLOCK_COMMENT [ WHITESPACE ]',
       '[ WHITESPACE ] LINE_COMMENT [ WHITESPACE ]')
    def comment(self, p):
        return CommentOrWhiteSpace(p[1])

    @_('key_value_pair { key_value_pair }')
    def key_value_pairs(self, p):
        ret = [p[0],]
        for additional_pair_toks in p[1]:
            pair = additional_pair_toks[-1]
            ret.append(pair)
        return ret


    @_('LBRACE [ key_value_pairs ] RBRACE')
    def json_object(self, p):
        return JSONObject(*p.key_value_pairs)

    @_('value [ COMMA { WHITESPACE } ]')
    def array_value(self, p):
        return p[0]

    @_('array_value { array_value }')
    def array_values(self, p):
        ret = [p[0], ]
        for other_array_toks in p[1]:
            array_value = other_array_toks[-1]
            ret.append(array_value)
        return ret


    @_('LBRACKET [ array_values ] RBRACKET')
    @_('LBRACKET [ array_values ] COMMA RBRACKET')
    def json_array(self, p):
        return JSONArray(*p.array_values)



    @_('NAME')
    def identifier(self, p):
        return Identifier(name=p[0])

    @_('{ whitespace_andor_comment } identifier { whitespace_andor_comment }',
       '{ whitespace_andor_comment } string { whitespace_andor_comment }')
    def key(self, p):
        return p[1]

    @_('INTEGER')
    def number(self, p):
        return Integer(int(p[0]))

    @_('FLOAT')
    def number(self, p):
        return Float(float(p[0]))

    @_('{ whitespace_andor_comment } MINUS number { whitespace_andor_comment }')
    def value(self, p):
        return UnaryOp(op='-', value=p.number)

    @_('{ whitespace_andor_comment } PLUS number { whitespace_andor_comment }')
    def value(self, p):
        return UnaryOp(op='+', value=p.number)


    @_('DOUBLE_QUOTE_STRING')
    def double_quoted_string(self, p):
        contents = p[0][1:-1]
        contents = re.sub('\\\n', '', contents)
        contents = re.sub(r'\\(.)', r'\1', contents)
        return DoubleQuotedString(*contents)

    @_("SINGLE_QUOTE_STRING")
    def single_quoted_string(self, p):
        contents = p[0][1:-1]
        contents = re.sub('\\\n', '', contents)
        contents = re.sub(r'\\(.)', r'\1', contents)
        return SingleQuotedString(*contents)

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
        return p[1]

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
    return model

if __name__ == '__main__':
    fp = sys.argv[1]
    with open(fp) as f:
        text = f.read()
    print(repr(parse_source(text)))