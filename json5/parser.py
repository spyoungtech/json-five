from sly import Parser
from json5.tokenizer import JSONLexer, tokenize
from json5.model import *

class JSONParser(Parser):
    debugfile = 'parser.out'
    tokens = JSONLexer.tokens


    @_('value')
    def text(self, p):
        return JSONText(value=p[0])


    @_('key { WHITESPACE } COLON { WHITESPACE } value { WHITESPACE }')
    def key_value_pair(self, p):
        return KeyValuePair(key=p.key, value=p.value)

    @_('COMMA { WHITESPACE }')
    def trailing_comma(self, p):
        return None

    @_('key_value_pair { COMMA [ WHITESPACE ] key_value_pair }')
    def key_value_pairs(self, p):
        ret = [p[0],]
        for additional_pair_toks in p[1]:
            pair = additional_pair_toks[-1]
            ret.append(pair)
        return ret


    @_('LBRACE { WHITESPACE } [ key_value_pairs ] [ trailing_comma ] RBRACE ')
    def json_object(self, p):
        return JSONObject(*p.key_value_pairs)

    @_('value { WHITESPACE }')
    def array_value(self, p):
        return p[0]

    @_('array_value { COMMA [ WHITESPACE ] array_value }')
    def array_values(self, p):
        ret = [p[0], ]
        for other_array_toks in p[1]:
            array_value = other_array_toks[-1]
            ret.append(array_value)
        return ret


    @_('LBRACKET { WHITESPACE } [ array_values ] [ trailing_comma ] RBRACKET')
    def json_array(self, p):
        return JSONArray(*p.array_values)

    @_('NAME')
    def identifier(self, p):
        return Identifier(name=p[0])

    @_('identifier',
       'string')
    def key(self, p):
        return p[0]

    @_('INTEGER')
    def number(self, p):
        return Integer(int(p[0]))

    @_('FLOAT')
    def number(self, p):
        return Float(float(p[0]))


    @_('number')
    def value(self, p):
        return p[0]

    @_('MINUS number')
    def value(self, p):
        return UnaryOp(op='-', value=p.number)

    @_('PLUS number')
    def value(self, p):
        return UnaryOp(op='+', value=p.number)

    @_('DOUBLE_QUOTE { DOUBLE_QUOTE_STRING_CHAR } DOUBLE_QUOTE')
    def string(self, p):
        print(p.DOUBLE_QUOTE_STRING_CHAR)
        return DoubleQuotedString(*p.DOUBLE_QUOTE_STRING_CHAR)

    @_('SINGLE_QUOTE_STRING_CHAR { SINGLE_QUOTE_STRING_CHAR }')
    def single_quote_string_content(self, p):
        return p.SINGLE_QUOTE_STRING_CHAR0 + ''.join(p.SINGLE_QUOTE_STRING_CHAR1)

    @_('SINGLE_QUOTE [ single_quote_string_content ] SINGLE_QUOTE')
    def string(self, p):
        return SingleQuotedString(*p.single_quote_string_content)


    @_('TRUE')
    def value(self, p):
        return BooleanLiteral(True)

    @_('FALSE')
    def value(self, p):
        return BooleanLiteral(False)

    @_('NULL')
    def value(self, p):
        return NullLiteral()

    @_('string',
       'json_object',
       'json_array')
    def value(self, p):
        return p[0]

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