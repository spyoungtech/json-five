import re
import sys
from sly import Lexer

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stderr))
logger.setLevel(level=logging.DEBUG)

class JSONLexer(Lexer):
    # reflags = re.MULTILINE
    tokens = {LBRACE, RBRACE,
              LBRACKET, RBRACKET,
              PLUS, MINUS,
              FLOAT, INTEGER,
              #DOUBLE_QUOTE, SINGLE_QUOTE,
              #DOUBLE_QUOTE_STRING_CHAR, SINGLE_QUOTE_STRING_CHAR,
              DOUBLE_QUOTE_STRING, SINGLE_QUOTE_STRING,
              # DECIMAL,
              NAME,
              COMMA,
              # DOLLAR,
              # UNDERSCORE,
              #LINE_COMMENT_START, BLOCK_COMMENT_START, BLOCK_COMMENT_END,
              BLOCK_COMMENT,
              LINE_COMMENT,
              WHITESPACE,
              TRUE, FALSE, NULL,
              COLON,

              # RESERVED KEYWORDS
              BREAK, DO, INSTANCEOF, TYPEOF, CASE, ELSE, NEW, VAR, CATCH, FINALLY, RETURN, VOID, CONTINUE, FOR, SWITCH, WHILE, DEBUGGER, FUNCTION, THIS, WITH, DEFAULT, IF, THROW, DELETE, IN, TRY,
              }



    #ignore_line_comment_eof = r'//.*$'




    LBRACE = r'{'
    RBRACE = r'}'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    # DOLLAR = r'\$'
    COLON = r"\:"
    COMMA = r"\,"

    DOUBLE_QUOTE_STRING = r'\"[^\"]+\"'
    SINGLE_QUOTE_STRING = r"\'[^\']+\'"

    # DOUBLE_QUOTE = r'\"'
    # SINGLE_QUOTE = r"\'"
    LINE_COMMENT = r"//.*"
    _BLOCK_COMMENT_START = r"\/\*"
    _BLOCK_COMMENT_END = r"\*\/"
    BLOCK_COMMENT = r'/\*((.|\n))*?\*/'
    WHITESPACE = "[\u0009\u000A\u000B\u000C\u000D\u0020\u00A0\u2028\u2029\ufeff]+"
    print(repr(BLOCK_COMMENT))

    # DOUBLE_QUOTE_STRING_CHAR = r'[^\"]'  # needs work for escapes
    # SINGLE_QUOTE_STRING_CHAR = r"[^\']"  # needs work for escapes
    # UNDERSCORE = r"_"
    FLOAT = r'(\d+\.\d*)|(\d*\.\d+)'      # 23.45
    INTEGER = r'\d+'
    NAME = r'[a-zA-Z_\$]([a-zA-Z_\d\$])*'

    NAME['true'] = TRUE
    NAME['false'] = FALSE
    NAME['null'] = NULL

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
    for tok in tokens:
        logger.debug(tok)
    return lexer.tokenize(text)

if __name__ == '__main__':
    fp = sys.argv[1]
    with open(fp) as f:
        text = f.read()
    tokenize(text)