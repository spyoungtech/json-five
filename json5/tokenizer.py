from __future__ import annotations

import logging
import typing
from typing import Generator
from typing import NoReturn

import regex as re
from sly import Lexer  # type: ignore
from sly.lex import Token  # type: ignore

from .utils import JSON5DecodeError

logger = logging.getLogger(__name__)
# logger.addHandler(logging.StreamHandler(stream=sys.stderr))
# logger.setLevel(level=logging.DEBUG)


class JSON5Token(Token):  # type: ignore[misc]
    '''
    Representation of a single token.
    '''

    def __init__(self, tok: Token, doc: str):
        self.type: str | None = tok.type
        self.value: str = tok.value
        self.lineno: int = tok.lineno
        self.index: int = tok.index
        self.doc: str = doc
        self.end: int = tok.end

    @property
    def colno(self) -> int:
        line_start_index = self.doc.rfind('\n', 0, self.index) + 1
        return self.index - line_start_index

    @property
    def end_colno(self) -> int:
        return self.colno + self.end - self.index

    @property
    def end_lineno(self) -> int:
        return self.lineno + self.value.count('\n')

    __slots__ = ('type', 'value', 'lineno', 'index', 'doc', 'end')

    def __str__(self) -> str:
        if self.value:
            return self.value
        else:
            return ''

    def __repr__(self) -> str:
        return f'JSON5Token(type={self.type!r}, value={self.value!r}, lineno={self.lineno}, index={self.index}, end={self.end})'


T_CallArg = typing.TypeVar('T_CallArg')
_: typing.Callable[[str], typing.Callable[[T_CallArg], T_CallArg]]


class JSONLexer(Lexer):  # type: ignore[misc]
    regex_module = re
    reflags = re.DOTALL
    tokens = {
        LBRACE,
        RBRACE,
        LBRACKET,
        RBRACKET,
        DOUBLE_QUOTE_STRING,
        SINGLE_QUOTE_STRING,
        UNTERMINATED_DOUBLE_QUOTE_STRING,
        UNTERMINATED_SINGLE_QUOTE_STRING,
        NAME,
        COMMA,
        BLOCK_COMMENT,
        LINE_COMMENT,
        WHITESPACE,
        TRUE,
        FALSE,
        NULL,
        COLON,
        # Numbers
        PLUS,
        MINUS,
        FLOAT,
        INTEGER,
        INFINITY,
        NAN,
        EXPONENT,
        HEXADECIMAL,
        OCTAL,  # Not allowed, but we capture as a token to raise error later
    }

    def tokenize(self, text: str, lineno: int = 1, index: int = 0) -> Generator[JSON5Token, None, None]:
        for tok in super().tokenize(text, lineno, index):
            tok = JSON5Token(tok, text)
            yield tok

    LBRACE = r'{'
    RBRACE = r'}'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    COLON = r"\:"
    COMMA = r"\,"

    @_(r'"(?:[^"\\]|\\.)*"')
    def DOUBLE_QUOTE_STRING(self, tok: JSON5Token) -> JSON5Token:
        self.lineno += tok.value.count('\n')
        return tok

    @_(r"'(?:[^'\\]|\\.)*'")
    def SINGLE_QUOTE_STRING(self, tok: JSON5Token) -> JSON5Token:
        self.lineno += tok.value.count('\n')
        return tok

    LINE_COMMENT = r"//[^\n]*"

    @_(r'/\*((.|\n))*?\*/')
    def BLOCK_COMMENT(self, tok: JSON5Token) -> JSON5Token:
        self.lineno += tok.value.count('\n')
        return tok

    @_("[\u0009\u000A\u000B\u000C\u000D\u0020\u00A0\u2028\u2029\ufeff]+")
    def WHITESPACE(self, tok: JSON5Token) -> JSON5Token:
        self.lineno += tok.value.count('\n')
        return tok

    MINUS = r'\-'
    PLUS = r'\+'
    EXPONENT = r"(e|E)(\-|\+)?\d+"
    HEXADECIMAL = r'0(x|X)[0-9a-fA-F]+'
    OCTAL = r'(0\d+|0o\d+)'
    FLOAT = r'(\d+\.\d*)|(\d*\.\d+)'  # 23.45
    INTEGER = r'\d+'
    NAME = r'[\w_\$\\]([\w_\d\$\\\p{Pc}\p{Mn}\p{Mc}\u200C\u200D])*'

    NAME['true'] = TRUE  # type: ignore[index]
    NAME['false'] = FALSE  # type: ignore[index]
    NAME['null'] = NULL  # type: ignore[index]
    NAME['Infinity'] = INFINITY  # type: ignore[index]
    NAME['NaN'] = NAN  # type: ignore[index]

    UNTERMINATED_DOUBLE_QUOTE_STRING = r'"(?:[^"\\]|\\.)*'
    UNTERMINATED_SINGLE_QUOTE_STRING = r"'(?:[^'\\]|\\.)*"

    def error(self, t: JSON5Token) -> NoReturn:
        raise JSON5DecodeError(f'Illegal character {t.value[0]!r} at index {self.index}', None)


def tokenize(text: str) -> Generator[JSON5Token, None, None]:
    lexer = JSONLexer()
    tokens = lexer.tokenize(text)
    return tokens


def reversed_enumerate(tokens: typing.Sequence[JSON5Token]) -> typing.Generator[tuple[int, JSON5Token], None, None]:
    for i in reversed(range(len(tokens))):
        tok = tokens[i]
        yield i, tok
