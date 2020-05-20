import re
import sys
from sly import Lexer

import logging

logger = logging.getLogger(__name__)
# logger.addHandler(logging.StreamHandler(stream=sys.stderr))
# logger.setLevel(level=logging.DEBUG)

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

    LBRACE = r'{'
    RBRACE = r'}'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    COLON = r"\:"
    COMMA = r"\,"

    DOUBLE_QUOTE_STRING = r'"(?:[^"\\]|\\.)*"'
    SINGLE_QUOTE_STRING = r"'(?:[^'\\]|\\.)*'"

    LINE_COMMENT = r"//[^\n]*"
    _BLOCK_COMMENT_START = r"\/\*"
    _BLOCK_COMMENT_END = r"\*\/"
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


def tokenize(text):
    lexer = JSONLexer()
    tokens = lexer.tokenize(text)
    return tokens
