import html
import os
import re
import sys
from enum import Enum

IDENTIFIER_RE = re.compile("^[^\"\d]+\w*")
INTEGER_CONSTANT_RE = re.compile("^\d+")
STRING_CONSTANT_RE = re.compile("^\"[^\"\n]+\"")

KEYWORDS = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false",
    "null", "this", "let", "do", "if", "else", "while", "return"
]


SYMBOLS = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]

class TokenType(Enum):
    KEYWORD = 0
    SYMBOL = 1
    IDENTIFIER = 2
    INT_CONST = 3
    STRING_CONST = 4

    def get_tag(self):
        if self.name == "INT_CONST":
            return "integerConstant"
        elif self.name == "STRING_CONST":
            return "stringConstant"
        else:
            return self.name.lower()

class KeywordType(Enum):
    CLASS = 0
    METHOD = 1
    FUNCTION = 2
    CONSTRUCTOR = 3
    INT = 4
    BOOLEAN = 5
    CHAR = 6
    VOID = 7
    VAR = 8
    STATIC = 9
    FIELD = 10
    LET = 11
    DO = 12
    IF = 13
    ELSE = 14
    WHILE = 15
    RETURN = 16
    TRUE = 17
    FALSE = 18
    NULL = 19
    THIS = 20

KEYWORDS_TABLE = {
    "class": KeywordType.CLASS,
    "method": KeywordType.METHOD,
    "function": KeywordType.FUNCTION,
    "constructor": KeywordType.CONSTRUCTOR,
    "int": KeywordType.INT,
    "boolean": KeywordType.BOOLEAN,
    "char": KeywordType.CHAR,
    "void": KeywordType.VOID,
    "var": KeywordType.VAR,
    "static": KeywordType.STATIC,
    "field": KeywordType.FIELD,
    "let": KeywordType.LET,
    "do": KeywordType.DO,
    "if": KeywordType.IF,
    "else": KeywordType.ELSE,
    "while": KeywordType.WHILE,
    "return": KeywordType.RETURN,
    "true": KeywordType.TRUE,
    "false": KeywordType.FALSE,
    "null": KeywordType.NULL,
    "this": KeywordType.THIS
}

class FileNotExistError(Exception):
    pass


class FileParseError(Exception):
    pass

class TokenizeError(Exception):
    pass

class JackTokenizer(object):
    def __init__(self, file_):
        self.lines = []
        comment_line = False
        for line in file_.readlines():
            if "/*" in line:
                comment_line = True
            if "*/" in line:
                line = line.split("*/")[-1]
                comment_line = False
            if not comment_line:
                self.lines.append(line)
        self._split_tokens()
        self.token_sum = len(self.tokens)
        self.now_token = 0
        self._set_token()

    def _split_line_include_quote_line(self, line):
        is_quoted = False
        splited_line = []
        w2 = ""
        for w in line:
            if is_quoted:
                w2 += w
                if w == "\"":
                    splited_line.append(w2)
                    is_quoted = False
                    w2 = ""
            elif w == "\"":
                if len(w2) > 0:
                    splited_line.append(w2)
                is_quoted = True
                w2 = "\""
            elif w == " ":
                if len(w2) > 0:
                    splited_line.append(w2)
                    w2 = ""
            else:
                w2 += w
        if len(w2) > 0:
            splited_line.append(w2)
        return splited_line

    def _split_tokens(self):
        tokens = []
        for line in self.lines:
            normalized_line = self._normalize(line)
            words = None
            if "\"" in normalized_line:
                words = self._split_line_include_quote_line(normalized_line)
            else:
                words = normalized_line.split(" ")
            for word in words:
                # check token keyword
                if word in KEYWORDS:
                    tokens.append(word)
                    continue
                tokens.extend(self._word_split_tokens(word))
        self.tokens = tokens

    def _word_split_tokens(self, word):
        tokens = []
        w2 = ""
        for w in word:
            if w in SYMBOLS:
                if len(w2) > 0:
                    tokens.append(w2)
                    w2 = ""
                tokens.append(w)
                continue
            else:
                w2 += w 
        if len(w2) > 0:
            tokens.append(w2)
        return tokens
            
    def _normalize(self, line):
        line = line.split("//")[0].strip()
        return line.split("/*")[0].strip()

    def _set_token(self):
        self.token = self.tokens[self.now_token]

    def advance(self):
        if self.hasMoreTokens():
            self.now_token += 1
            self._set_token()

    def hasMoreTokens(self):
        return self.now_token < self.token_sum - 1

    def tokenType(self):
        token = self.token
        if self.is_keyword(token):
            return TokenType.KEYWORD
        elif self.is_symbol(token):
            return TokenType.SYMBOL
        elif self.is_identifier(token):
            return TokenType.IDENTIFIER
        elif self.is_integer_constant(token):
            return TokenType.INT_CONST
        elif self.is_string_constant(token):
            return TokenType.STRING_CONST

    def is_keyword(self, token):
        if token in KEYWORDS:
            return True
        return False

    def is_symbol(self, token):
        if token in SYMBOLS:
            return True
        return False

    def is_identifier(self, token):
        if IDENTIFIER_RE.match(token):
            return True
        return False

    def is_integer_constant(self, token):
        if INTEGER_CONSTANT_RE.match(token):
            return True
        return False

    def is_string_constant(self, token):
        if STRING_CONSTANT_RE.match(token):
            return True
        return False

    def keyword(self):
        return self.token

    def write_token(self, token, tokenType, wf):
        tag_name = tokenType.get_tag()
        wf.write("<{}> {} </{}>\n".format(tag_name, html.escape(str(token)), tag_name))


class CompilationEngine(object):
    def __init__(self, name):
        f = open("{}.xml".format(name), "w") 
        self.file = f

    def compile_token(self, token, tokenType):
        if tokenType == TokenType.KEYWORD:
            self.compile_keyword(token)

    def compileClass(self):
        pass

    def compile_keyword(self, token):
        if token == KeywordType.CLASS:
            self.compileClass()
        elif token in (KeywordType.METHOD, KeywordType.FUNCTION, KeywordType.CONSTRUCTOR):
            self.compileSubroutine(token)
        elif token in (KeywordType.STATIC, FIELD):
            self.compileClassVarDec(token)
        elif token in (KeywordType.VAR):
            self.compileVarDec()
        elif token == KeywordType.DO:
            self.compileDo()
        elif token == KeywordType.LET:
            self.compileLet()
        elif token == KeywordType.WHILE:
            self.compileWhile()
        elif token == KeywordType.RETURN:
            self.compileReturn()
        elif token in (KeywordType.IF, KeywordType.ELSE):
            self.compileIf()

def write(wf, content):
    wf.write(content + "\n")
       

def main():
    files = get_files()
    if not files:
        raise FileNotExistError("not passed target files")
    wf = None
    for file_path in files:
        f = file_open(file_path)
        tokenizer = JackTokenizer(f)
        write_file_name = file_path.rstrip(".jack")
        wf = open("{}_T.xml".format(write_file_name), "w")
        write(wf, "<tokens>")
        #compile_engine = CompilationEngine(write_file_name)
        while True:
            tokenType = tokenizer.tokenType()
            token = None
            if tokenType == TokenType.KEYWORD:
                token = tokenizer.keyword()
            elif tokenType == TokenType.INT_CONST:
                token = int(tokenizer.token)
            elif tokenType == TokenType.STRING_CONST:
                token = tokenizer.token.strip("\"")
            elif tokenType in (TokenType.SYMBOL, TokenType.IDENTIFIER):
                token = tokenizer.token   
            else:
                raise TokenizeError("cant parse token {}".format(tokenizer.token))
            tokenizer.write_token(token, tokenType, wf)
            #tokenizer.compile_token(token, tokenType)

            if not tokenizer.hasMoreTokens():
                break

            tokenizer.advance()
        write(wf, "</tokens>")
        wf.close()

def get_files():
    path = sys.argv[1]
    files = []
    if os.path.isdir(path):
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    split_name = entry.name.split(".")
                    if "jack" == split_name[-1]:
                        files.append(entry.path)
    else:
        files.append(path)
    
    return files

def file_open(file_path):
    splited_file_name = file_path.split(".")
    if 1 >= len(splited_file_name):
        raise FileParseError("拡張子が指定されていません。")
    
    if "jack" != splited_file_name[-1]:
        raise FileParseError("vmファイルが指定されていません。")
    f = open(file_path, "r")
    return f

if __name__ == "__main__":
    main()
