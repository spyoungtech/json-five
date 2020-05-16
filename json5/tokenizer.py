import re

import sys

from sly import Lexer

class JSONLexer(Lexer):
    reflags = re.MULTILINE
    tokens = {LBRACE, RBRACE,
              LBRACKET, RBRACKET,
              PLUS, MINUS,
              FLOAT, INTEGER,
              DOUBLE_QUOTE, SINGLE_QUOTE,
              DOUBLE_QUOTE_STRING_CHAR, SINGLE_QUOTE_STRING_CHAR,
              # DECIMAL,
              NAME,
              COMMA,
              # DOLLAR,
              # UNDERSCORE,
              # LINE_COMMENT_START, BLOCK_COMMENT_START, BLOCK_COMMENT_END,
              WHITESPACE,
              TRUE, FALSE, NULL,
              COLON,

              # RESERVED KEYWORDS
              BREAK,DO,INSTANCEOF,TYPEOF,CASE,ELSE,NEW,VAR,CATCH,FINALLY,RETURN,VOID,CONTINUE,FOR,SWITCH,WHILE,DEBUGGER,FUNCTION,THIS,WITH,DEFAULT,IF,THROW,DELETE,IN,TRY,
              }

    ignore_line_comment = r'//.*'


    @_(r'\n+')
    def ignore_newline(self, tok):
        self.lineno += tok.value.count('\n')


    @_(r'/\*((.|\n))*?\*/')
    def ignore_block_comment(self, tok):
        self.lineno += tok.value.count('\n')


    #ignore_line_comment_eof = r'//.*$'




    LBRACE = r'{'
    RBRACE = r'}'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    # DOLLAR = r'\$'
    COLON = r"\:"
    COMMA = r"\,"

    DOUBLE_QUOTE = r'\"'
    SINGLE_QUOTE = r"\'"
    WHITESPACE = "[\u0009\u000A\u000B\u000C\u000D\u0020\u00A0\u2028\u2029\ufeff]+"

    DOUBLE_QUOTE_STRING_CHAR = r'[^\"]'  # needs work for escapes
    SINGLE_QUOTE_STRING_CHAR = r"[^\']"  # needs work for escapes
    # UNDERSCORE = r"_"
    FLOAT = r'(\d+\.\d*)|(\d*\.\d+)'      # 23.45
    INTEGER = r'\d+'
    # LINE_COMMENT_START = r"\/\/"
    # BLOCK_COMMENT_START = r"\/\*"
    # BLOCK_COMMENT_END = r"\*\/"
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
    return lexer.tokenize(text)

if __name__ == '__main__':
    fp = sys.argv[1]
    with open(fp) as f:
        text = f.read()
    for tok in tokenize(text):
        print(tok)