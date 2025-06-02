from __future__ import annotations

import ast
import sys
import typing
from functools import lru_cache
from typing import Any
from typing import Literal
from typing import Protocol

import regex as re
from sly import Parser  # type: ignore
from sly.yacc import SlyLogger  # type: ignore

from .model import BlockComment
from .model import BooleanLiteral
from .model import Comment
from .model import DoubleQuotedString
from .model import Float
from .model import Identifier
from .model import Infinity
from .model import Integer
from .model import JSONArray
from .model import JSONObject
from .model import JSONText
from .model import Key
from .model import KeyValuePair
from .model import LineComment
from .model import NaN
from .model import NullLiteral
from .model import SingleQuotedString
from .model import TrailingComma
from .model import UnaryOp
from .model import Value
from .tokenizer import JSON5Token
from .tokenizer import JSONLexer
from .tokenizer import tokenize
from .utils import JSON5DecodeError


class QuietSlyLogger(SlyLogger):  # type: ignore[misc]
    def warning(self, *args: Any, **kwargs: Any) -> None:
        return

    debug = warning
    info = warning


ESCAPE_SEQUENCES = {
    'b': '\u0008',
    'f': '\u000c',
    'n': '\u000a',
    'r': '\u000d',
    't': '\u0009',
    'v': '\u000b',
    '0': '\u0000',
    '\\': '\u005c',
    '"': '\u0022',
    "'": '\u0027',
}

# class TrailingComma:
#     pass


def replace_escape_literals(matchobj: re.Match[str]) -> str:
    s = matchobj.group(0)
    if s.startswith('\\0') and len(s) == 3:
        raise JSON5DecodeError("'\\0' MUST NOT be followed by a decimal digit", None)
    seq = matchobj.group(1)
    return ESCAPE_SEQUENCES.get(seq, seq)


@lru_cache(maxsize=1024)
def _latin_escape_replace(s: str) -> str:
    if s.startswith('\\x') and len(s) != 4:
        raise JSON5DecodeError("'\\x' MUST be followed by two hexadecimal digits", None)
    val: str = ast.literal_eval(f'"{s}"')
    if val == '\\':
        val = '\\\\'  # this is important; the subsequent regex will sub it back to \\
    return val


def latin_unicode_escape_replace(matchobj: re.Match[str]) -> str:
    s = matchobj.group(0)
    return _latin_escape_replace(s)


def _unicode_escape_replace(s: str) -> str:
    ret: str = ast.literal_eval(f'"{s}"')
    return ret


def unicode_escape_replace(matchobj: re.Match[str]) -> str:
    s = matchobj.group(0)
    return _unicode_escape_replace(s)


class T_TokenSlice(Protocol):
    def __getitem__(self, item: int) -> JSON5Token: ...


class T_AnyProduction(Protocol):
    _slice: T_TokenSlice


class T_TextProduction(Protocol):
    wsc0: list[Comment | str]
    wsc1: list[Comment | str]
    value: Value

    def __getitem__(self, i: Literal[1]) -> Value: ...


class T_FirstKeyValuePairProduction(Protocol):
    wsc0: list[Comment | str]
    wsc1: list[Comment | str]
    wsc2: list[Comment | str]
    key: Key
    value: Value
    _slice: T_TokenSlice

    def __getitem__(self, item: int) -> Key | Value: ...


class T_WSCProduction(Protocol):
    _slice: T_TokenSlice

    def __getitem__(self, item: Literal[0]) -> str | Comment: ...


class T_CommentProduction(Protocol):
    _slice: T_TokenSlice

    def __getitem__(self, item: Literal[0]) -> str: ...


class T_KeyValuePairsProduction(Protocol):
    _slice: T_TokenSlice
    first_key_value_pair: KeyValuePair
    subsequent_key_value_pair: list[KeyValuePair]


class T_JsonObjectProduction(Protocol):
    _slice: T_TokenSlice
    key_value_pairs: tuple[list[KeyValuePair], TrailingComma | None] | None
    wsc: list[Comment | str]


class SubsequentKeyValuePairProduction(Protocol):
    _slice: T_TokenSlice
    wsc: list[Comment | str]
    first_key_value_pair: KeyValuePair | None


class T_FirstArrayValueProduction(Protocol):
    _slice: T_TokenSlice

    def __getitem__(self, item: Literal[1]) -> Value: ...

    wsc: list[Comment | str]


class T_SubsequentArrayValueProduction(Protocol):
    _slice: T_TokenSlice
    first_array_value: Value | None
    wsc: list[Comment | str]


class T_ArrayValuesProduction(Protocol):
    _slice: T_TokenSlice
    first_array_value: Value
    subsequent_array_value: list[Value]


class T_JsonArrayProduction(Protocol):
    _slice: T_TokenSlice
    array_values: tuple[list[Value], TrailingComma | None] | None
    wsc: list[Comment | str]


class T_IdentifierProduction(Protocol):
    _slice: T_TokenSlice

    def __getitem__(self, item: Literal[0]) -> str: ...


class T_KeyProduction(Protocol):
    def __getitem__(self, item: Literal[1]) -> Identifier | DoubleQuotedString | SingleQuotedString: ...


class T_NumberProduction(Protocol):
    _slice: T_TokenSlice

    def __getitem__(self, item: Literal[0]) -> str: ...


class T_ValueNumberProduction(Protocol):
    _slice: T_TokenSlice
    number: Infinity | NaN | Float | Integer


class T_ExponentNotationProduction(Protocol):
    _slice: T_TokenSlice

    def __getitem__(self, item: int) -> str: ...


class T_StringTokenProduction(Protocol):
    _slice: T_TokenSlice

    def __getitem__(self, item: Literal[0]) -> str: ...


class T_StringProduction(Protocol):
    _slice: T_TokenSlice

    def __getitem__(self, item: Literal[0]) -> DoubleQuotedString | SingleQuotedString: ...


class T_ValueProduction(Protocol):
    _slice: T_TokenSlice

    def __getitem__(
        self, item: Literal[0]
    ) -> (
        DoubleQuotedString
        | SingleQuotedString
        | JSONObject
        | JSONArray
        | BooleanLiteral
        | NullLiteral
        | Infinity
        | Integer
        | Float
        | NaN
    ): ...


T_CallArg = typing.TypeVar('T_CallArg')
_: typing.Callable[..., typing.Callable[[T_CallArg], T_CallArg]]


class JSONParser(Parser):  # type: ignore[misc]
    # debugfile = 'parser.out'
    tokens = JSONLexer.tokens
    log = QuietSlyLogger(sys.stderr)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.errors: list[JSON5DecodeError] = []
        self.last_token: JSON5Token | None = None
        self.seen_tokens: list[JSON5Token] = []
        self.expecting: list[list[str]] = []

    @_('{ wsc } value { wsc }')
    def text(self, p: T_TextProduction) -> JSONText:
        node = JSONText(value=p[1], tok=p.value._tok)
        for wsc in p.wsc0:
            node.wsc_before.append(wsc)
        for wsc in p.wsc1:
            node.wsc_after.append(wsc)
        return node

    @_('key { wsc } seen_colon COLON { wsc } object_value_seen value { wsc }')
    def first_key_value_pair(self, p: T_FirstKeyValuePairProduction) -> KeyValuePair:
        key = p[0]
        for wsc in p.wsc0:
            key.wsc_after.append(wsc)
        value = p[6]
        for wsc in p.wsc1:
            value.wsc_before.append(wsc)
        for wsc in p.wsc2:
            value.wsc_after.append(wsc)
        return KeyValuePair(key=p.key, value=p.value)

    @_('object_delimiter_seen COMMA { wsc } [ first_key_value_pair ]')
    def subsequent_key_value_pair(self, p: SubsequentKeyValuePairProduction) -> KeyValuePair | TrailingComma:
        node: KeyValuePair | TrailingComma
        if p.first_key_value_pair:
            node = p.first_key_value_pair
            for wsc in p.wsc:
                node.key.wsc_before.append(wsc)
        else:
            node = TrailingComma(tok=p._slice[1])
            for wsc in p.wsc:
                node.wsc_after.append(wsc)
        return node

    @_('WHITESPACE', 'comment')
    def wsc(self, p: T_WSCProduction) -> str | Comment:
        return p[0]

    @_('BLOCK_COMMENT')
    def comment(self, p: T_CommentProduction) -> BlockComment:
        return BlockComment(p[0], tok=p._slice[0])

    @_('LINE_COMMENT')  # type: ignore[no-redef]
    def comment(self, p: T_CommentProduction):
        return LineComment(p[0], tok=p._slice[0])

    @_('first_key_value_pair { subsequent_key_value_pair }')
    def key_value_pairs(self, p: T_KeyValuePairsProduction) -> tuple[list[KeyValuePair], TrailingComma | None]:
        ret = [
            p.first_key_value_pair,
        ]
        num_sqvp = len(p.subsequent_key_value_pair)
        for index, value in enumerate(p.subsequent_key_value_pair):
            if isinstance(value, TrailingComma):
                if index + 1 != num_sqvp:
                    offending_token = value._tok
                    self.errors.append(JSON5DecodeError("Syntax Error: multiple trailing commas", offending_token))
                return ret, value
            else:
                ret.append(value)
        return ret, None

    @_('')
    def seen_LBRACE(self, p: Any) -> None:
        self.expecting.append(['RBRACE', 'key'])

    @_('')
    def seen_key(self, p: Any) -> None:
        self.expecting.pop()
        self.expecting.append(['COLON'])

    @_('')
    def seen_colon(self, p: Any) -> None:
        self.expecting.pop()
        self.expecting.append(['value'])

    @_('')
    def object_value_seen(self, p: Any) -> None:
        self.expecting.pop()
        self.expecting.append(['COMMA', 'RBRACE'])

    @_('')
    def object_delimiter_seen(self, p: Any) -> None:
        self.expecting.pop()
        self.expecting.append(['RBRACE', 'key'])

    @_('')
    def seen_RBRACE(self, p: Any) -> None:
        self.expecting.pop()

    @_('seen_LBRACE LBRACE { wsc } [ key_value_pairs ] seen_RBRACE RBRACE')
    def json_object(self, p: T_JsonObjectProduction) -> JSONObject:
        if not p.key_value_pairs:
            node = JSONObject(leading_wsc=list(p.wsc or []), tok=p._slice[1], end_tok=p._slice[5])
        else:
            kvps, trailing_comma = p.key_value_pairs
            node = JSONObject(
                *kvps,
                trailing_comma=trailing_comma,
                leading_wsc=list(p.wsc or []),
                tok=p._slice[1],
                end_tok=p._slice[5],
            )

        return node

    @_('array_value_seen value { wsc }')
    def first_array_value(self, p: T_FirstArrayValueProduction) -> Value:
        node = p[1]
        for wsc in p.wsc:
            node.wsc_after.append(wsc)
        return node

    @_('array_delimiter_seen COMMA { wsc } [ first_array_value ]')
    def subsequent_array_value(self, p: T_SubsequentArrayValueProduction) -> Value | TrailingComma:
        node: Value | TrailingComma
        if p.first_array_value:
            node = p.first_array_value
            for wsc in p.wsc:
                node.wsc_before.append(wsc)
        else:
            node = TrailingComma(tok=p._slice[1])
            for wsc in p.wsc:
                node.wsc_after.append(wsc)
        return node

    @_('first_array_value { subsequent_array_value }')
    def array_values(self, p: T_ArrayValuesProduction) -> tuple[list[Value], TrailingComma | None]:
        ret = [
            p.first_array_value,
        ]
        num_values = len(p.subsequent_array_value)
        for index, value in enumerate(p.subsequent_array_value):
            if isinstance(value, TrailingComma):
                if index + 1 != num_values:
                    self.errors.append(JSON5DecodeError("Syntax Error: multiple trailing commas", value._tok))
                    return ret, value
                return ret, value
            else:
                ret.append(value)
        return ret, None

    @_('seen_LBRACKET LBRACKET { wsc } [ array_values ] seen_RBRACKET RBRACKET')
    def json_array(self, p: T_JsonArrayProduction) -> JSONArray:
        if not p.array_values:
            node = JSONArray(tok=p._slice[1], end_tok=p._slice[5])
        else:
            values, trailing_comma = p.array_values
            node = JSONArray(*values, trailing_comma=trailing_comma, tok=p._slice[1], end_tok=p._slice[5])

        for wsc in p.wsc:
            node.leading_wsc.append(wsc)

        return node

    @_('')
    def seen_LBRACKET(self, p: Any) -> None:
        self.expecting.append(['RBRACKET', 'value'])

    @_('')
    def seen_RBRACKET(self, p: Any) -> None:
        self.expecting.pop()

    @_('')
    def array_delimiter_seen(self, p: Any) -> None:
        assert len(self.expecting[-1]) == 2
        self.expecting[-1].pop()
        self.expecting[-1].append('value')

    @_('')
    def array_value_seen(self, p: Any) -> None:
        assert len(self.expecting[-1]) == 2
        assert self.expecting[-1][-1] == 'value'
        self.expecting[-1].pop()
        self.expecting[-1].append('COMMA')

    @_('NAME')
    def identifier(self, p: T_IdentifierProduction) -> Identifier:
        raw_value = p[0]
        name = re.sub(r'\\u[0-9a-fA-F]{4}', unicode_escape_replace, raw_value)
        pattern = r'[\w_\$]([\w_\d\$\p{Pc}\p{Mn}\p{Mc}\u200C\u200D])*'
        if not re.fullmatch(pattern, name):
            self.errors.append(JSON5DecodeError("Invalid identifier name", p._slice[0]))
        return Identifier(name=name, raw_value=raw_value, tok=p._slice[0])

    @_('seen_key identifier', 'seen_key string')
    def key(self, p: T_KeyProduction) -> Identifier | DoubleQuotedString | SingleQuotedString:
        node = p[1]
        return node

    @_('INTEGER')
    def number(self, p: T_NumberProduction):
        return Integer(p[0], tok=p._slice[0])

    @_('FLOAT')  # type: ignore[no-redef]
    def number(self, p: T_NumberProduction):
        return Float(p[0], tok=p._slice[0])

    @_('OCTAL')  # type: ignore[no-redef]
    def number(self, p: T_NumberProduction):
        self.errors.append(JSON5DecodeError("Invalid integer literal. Octals are not allowed", p._slice[0]))
        raw_value = p[0]
        if re.search(r'[89]+', raw_value):
            self.errors.append(JSON5DecodeError("Invalid octal format. Octal digits must be in range 0-7", p._slice[0]))
            return Integer(raw_value=oct(0), is_octal=True, tok=p._slice[0])
        return Integer(raw_value, is_octal=True, tok=p._slice[0])

    @_('INFINITY')  # type: ignore[no-redef]
    def number(self, p: T_AnyProduction) -> Infinity:
        return Infinity(tok=p._slice[0])

    @_('NAN')  # type: ignore[no-redef]
    def number(self, p: T_AnyProduction) -> NaN:
        return NaN(tok=p._slice[0])

    @_('MINUS number')
    def value(self, p: T_ValueNumberProduction) -> UnaryOp:
        if isinstance(p.number, Infinity):
            p.number.negative = True
        node = UnaryOp(op='-', value=p.number, tok=p._slice[0], end_tok=p.number._end_tok)
        return node

    @_('PLUS number')  # type: ignore[no-redef]
    def value(self, p: T_ValueNumberProduction):
        node = UnaryOp(op='+', value=p.number, tok=p._slice[0], end_tok=p.number._end_tok)
        return node

    @_('INTEGER EXPONENT', 'FLOAT EXPONENT')  # type: ignore[no-redef]
    def number(self, p: T_ExponentNotationProduction) -> Float:
        exp_notation = p[1][0]  # e or E
        return Float(p[0] + p[1], exp_notation=exp_notation, tok=p._slice[0], end_tok=p._slice[1])

    @_('HEXADECIMAL')  # type: ignore[no-redef]
    def number(self, p: T_NumberProduction) -> Integer:
        return Integer(p[0], is_hex=True, tok=p._slice[0])

    @_('DOUBLE_QUOTE_STRING')
    def double_quoted_string(self, p: T_StringTokenProduction) -> DoubleQuotedString:
        raw_value = p[0]
        contents = raw_value[1:-1]
        terminator_in_string = re.search(r'(?<!\\)([\u000D\u2028\u2029]|(?<!\r)\n)', contents)
        if terminator_in_string:
            end = terminator_in_string.span()[0]
            before_terminator = terminator_in_string.string[:end]
            tok = p._slice[0]
            pos = tok.index + len(before_terminator)
            doc = tok.doc
            lineno = doc.count('\n', 0, pos) + 1
            colno = pos - doc.rfind('\n', 0, pos) + 1
            index = pos + 1
            errmsg = f"Illegal line terminator (line {lineno} column {colno} (char {index}) without continuation"
            self.errors.append(JSON5DecodeError(errmsg, tok))
        contents = re.sub(r'\\(\r\n|[\u000A\u000D\u2028\u2029])', '', contents)
        try:
            contents = re.sub(r'(\\x[a-fA-F0-9]{0,2}|\\u[0-9a-fA-F]{4})', latin_unicode_escape_replace, contents)
        except JSON5DecodeError as exc:
            self.errors.append(JSON5DecodeError(exc.args[0], p._slice[0]))
        try:
            contents = re.sub(r'\\(0\d|.)', replace_escape_literals, contents)
        except JSON5DecodeError as exc:
            self.errors.append(JSON5DecodeError(exc.args[0], p._slice[0]))
        return DoubleQuotedString(contents, raw_value=raw_value, tok=p._slice[0])

    @_("SINGLE_QUOTE_STRING")
    def single_quoted_string(self, p: T_StringTokenProduction) -> SingleQuotedString:
        raw_value = p[0]
        contents = raw_value[1:-1]
        terminator_in_string = re.search(r'(?<!\\)([\u000D\u2028\u2029]|(?<!\r)\n)', contents)
        if terminator_in_string:
            end = terminator_in_string.span()[0]
            before_terminator = terminator_in_string.string[:end]
            tok = p._slice[0]
            pos = tok.index + len(before_terminator)
            doc = tok.doc
            lineno = doc.count('\n', 0, pos) + 1
            colno = pos - doc.rfind('\n', 0, pos) + 1
            index = pos + 1
            errmsg = f"Illegal line terminator (line {lineno} column {colno} (char {index}) without continuation"
            self.errors.append(JSON5DecodeError(errmsg, tok))
        contents = re.sub(r'\\(\r\n|[\u000A\u000D\u2028\u2029])', '', contents)
        try:
            contents = re.sub(r'(\\x[a-fA-F0-9]{0,2}|\\u[0-9a-fA-F]{4})', latin_unicode_escape_replace, contents)
        except JSON5DecodeError as exc:
            self.errors.append(JSON5DecodeError(exc.args[0], p._slice[0]))
        try:
            contents = re.sub(r'\\(0\d|.)', replace_escape_literals, contents)
        except JSON5DecodeError as exc:
            self.errors.append(JSON5DecodeError(exc.args[0], p._slice[0]))
        return SingleQuotedString(contents, raw_value=raw_value, tok=p._slice[0])

    @_('double_quoted_string', 'single_quoted_string')
    def string(self, p: T_StringProduction) -> SingleQuotedString | DoubleQuotedString:
        return p[0]

    @_('TRUE')
    def boolean(self, p: T_AnyProduction) -> BooleanLiteral:
        return BooleanLiteral(True, tok=p._slice[0])

    @_('FALSE')  # type: ignore[no-redef]
    def boolean(self, p: T_AnyProduction) -> BooleanLiteral:
        return BooleanLiteral(False, tok=p._slice[0])

    @_('NULL')
    def null(self, p: T_AnyProduction) -> NullLiteral:
        return NullLiteral(tok=p._slice[0])

    @_(  # type: ignore[no-redef]
        'string',
        'json_object',
        'json_array',
        'boolean',
        'null',
        'number',
    )
    def value(
        self, p: T_ValueProduction
    ) -> (
        DoubleQuotedString
        | SingleQuotedString
        | JSONObject
        | JSONArray
        | BooleanLiteral
        | NullLiteral
        | Infinity
        | Integer
        | Float
        | NaN
    ):
        node = p[0]
        return node

    @_('UNTERMINATED_SINGLE_QUOTE_STRING', 'UNTERMINATED_DOUBLE_QUOTE_STRING')  # type: ignore[no-redef]
    def string(self, p: T_StringTokenProduction) -> SingleQuotedString | DoubleQuotedString:
        self.error(p._slice[0])
        raw = p[0]
        if raw.startswith('"'):
            return DoubleQuotedString(raw[1:], raw_value=raw, tok=p._slice[0])
        return SingleQuotedString(raw[1:], raw_value=raw, tok=p._slice[0])

    def error(self, token: JSON5Token | None) -> JSON5Token | None:
        if token:
            if self.expecting:
                expected = self.expecting[-1]

                message = f"Syntax Error. Was expecting {' or '.join(expected)}"
            else:
                message = 'Syntax Error'

            self.errors.append(JSON5DecodeError(message, token))
            try:
                return next(self.tokens)  # type: ignore
            except StopIteration:
                # EOF
                class tok:
                    type = '$end'
                    value = None
                    lineno = None
                    index = None
                    end = None

                return JSON5Token(tok(), None)  # type: ignore[arg-type]
        elif self.last_token:
            doc = self.last_token.doc
            pos = len(doc)
            lineno = doc.count('\n', 0, pos) + 1
            colno = pos - doc.rfind('\n', 0, pos)
            message = f'Expecting value. Unexpected EOF at: ' f'line {lineno} column {colno} (char {pos})'
            if self.expecting:
                expected = self.expecting[-1]
                message += f'. Was expecting {f" or ".join(expected)}'
            self.errors.append(JSON5DecodeError(message, None))
        else:
            #  Empty file
            self.errors.append(JSON5DecodeError('Expecting value. Received unexpected EOF', None))
        return None

    def _token_gen(self, tokens: typing.Iterable[JSON5Token]) -> typing.Generator[JSON5Token]:
        for tok in tokens:
            self.last_token = tok
            self.seen_tokens.append(tok)
            yield tok

    def parse(self, tokens: typing.Iterable[JSON5Token]) -> JSONText:
        tokens = self._token_gen(tokens)
        model: JSONText = super().parse(tokens)
        if self.errors:
            if len(self.errors) > 1:
                primary_error = self.errors[0]
                msg = (
                    "There were multiple errors parsing the JSON5 document.\n"
                    "The primary error was: \n\t{}\n"
                    "Additionally, the following errors were also detected:\n\t{}"
                )

                num_additional_errors = len(self.errors) - 1
                additional_errors = '\n\t'.join(err.args[0] for err in self.errors[1:6])
                if num_additional_errors > 5:
                    additional_errors += f'\n\t{num_additional_errors - 5} additional error(s) truncated'
                msg = msg.format(primary_error.args[0], additional_errors)
                err = JSON5DecodeError(msg, None)
                err.lineno = primary_error.lineno
                err.token = primary_error.token
                err.index = primary_error.index
                raise err
            else:
                raise self.errors[0]
        return model


def parse_tokens(raw_tokens: typing.Iterable[JSON5Token]) -> JSONText:
    parser = JSONParser()
    return parser.parse(raw_tokens)


def parse_source(text: str) -> JSONText:
    tokens = tokenize(text)
    model = parse_tokens(tokens)
    return model
