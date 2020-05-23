import re
import sys
from sly import Lexer
from sly.lex import Token
from json5.utils import JSON5DecodeError
import logging

logger = logging.getLogger(__name__)
# logger.addHandler(logging.StreamHandler(stream=sys.stderr))
# logger.setLevel(level=logging.DEBUG)
class JSON5Token(Token):
    '''
    Representation of a single token.
    '''
    def __init__(self, tok, doc):
        self.type = tok.type
        self.value = tok.value
        self.lineno = tok.lineno
        self.index = tok.index
        self.doc = doc
    __slots__ = ('type', 'value', 'lineno', 'index', 'doc')

    def __repr__(self):
        return f'JSON5Token(type={self.type!r}, value={self.value!r}, lineno={self.lineno}, index={self.index})'


class JSONLexer(Lexer):
    reflags = re.DOTALL
    tokens = {LBRACE, RBRACE,
              LBRACKET, RBRACKET,
              DOUBLE_QUOTE_STRING, SINGLE_QUOTE_STRING,
              NAME,
              COMMA,
              BLOCK_COMMENT,
              LINE_COMMENT,
              WHITESPACE,
              TRUE, FALSE, NULL,
              COLON,

              # RESERVED KEYWORDS
              BREAK, DO, INSTANCEOF, TYPEOF, CASE, ELSE, NEW, VAR, CATCH, FINALLY, RETURN, VOID, CONTINUE, FOR, SWITCH, WHILE, DEBUGGER, FUNCTION, THIS, WITH, DEFAULT, IF, THROW, DELETE, IN, TRY,

              # Numbers
              PLUS, MINUS,
              FLOAT, INTEGER,
              INFINITY, NAN, EXPONENT,
              HEXADECIMAL
              }

    def tokenize(self, text, *args, **kwargs):
        for tok in super().tokenize(text, *args, **kwargs):
            tok = JSON5Token(tok, text)
            yield tok

    LBRACE = r'{'
    RBRACE = r'}'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    COLON = r"\:"
    COMMA = r"\,"

    DOUBLE_QUOTE_STRING = r'"(?:[^"\\]|\\.)*"'
    SINGLE_QUOTE_STRING = r"'(?:[^'\\]|\\.)*'"

    LINE_COMMENT = r"//[^\n]*"
    @_(r'/\*((.|\n))*?\*/')
    def BLOCK_COMMENT(self, tok):
        self.lineno += tok.value.count('\n')
        return tok

    @_("[\u0009\u000A\u000B\u000C\u000D\u0020\u00A0\u2028\u2029\ufeff]+")
    def WHITESPACE(self, tok):
        self.lineno += tok.value.count('\n')
        return tok

    MINUS = r'\-'
    PLUS = r'\+'
    EXPONENT = r"(e|E)(\-|\+)?\d+"
    HEXADECIMAL = r'0x[0-9a-fA-F]+'
    FLOAT = r'(\d+\.\d*)|(\d*\.\d+)'      # 23.45
    INTEGER = r'\d+'
    NAME = r'[a-zA-Z_\$]([a-zA-Z_\d\$])*'

    NAME['true'] = TRUE
    NAME['false'] = FALSE
    NAME['null'] = NULL
    NAME['Infinity'] = INFINITY
    NAME['NaN'] = NAN

    # RESERVED KEYWORDS
    NAME['break'] = BREAK
    NAME['do'] = DO
    NAME['instanceof'] = INSTANCEOF
    NAME['typeof'] = TYPEOF
    NAME['case'] = CASE
    NAME['else'] = ELSE
    NAME['new'] = NEW
    NAME['var'] = VAR
    NAME['catch'] = CATCH
    NAME['finally'] = FINALLY
    NAME['return'] = RETURN
    NAME['void'] = VOID
    NAME['continue'] = CONTINUE
    NAME['for'] = FOR
    NAME['switch'] = SWITCH
    NAME['while'] = WHILE
    NAME['debugger'] = DEBUGGER
    NAME['function'] = FUNCTION
    NAME['this'] = THIS
    NAME['with'] = WITH
    NAME['default'] = DEFAULT
    NAME['if'] = IF
    NAME['throw'] = THROW
    NAME['delete'] = DELETE
    NAME['in'] = IN
    NAME['try'] = TRY

    def error(self, t):
        raise JSON5DecodeError(f'Illegal character {t.value[0]!r} at index {self.index}', None)

def tokenize(text):
    lexer = JSONLexer()
    tokens = lexer.tokenize(text)
    return tokens
