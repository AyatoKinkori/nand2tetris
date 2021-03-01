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

class CompilationError(Exception):
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
        self.lines = []
        for line in f.readlines():
            self.lines.append(line)
        self.now_line = 0
        self.write_lines = []

    def advance(self):
        self.now_line += 1

    def get_line(self):
        return self.lines[now_line]

    def _get_token(self, line):
        return line.split(" ")[1]

    def _get_tag(self, line):
        return line.split(">")[0].strip("<")

    def _start_non_terminal(self, non_term):
        self.write_lines.append("<{}>".format(non_term))

    def _end_non_terminal(self, non_term):
        self.write_lines.append("</{}>".format(non_term))

    def _write_line(self, line):
        self.write_lines.append(line)

    def is_type(self, line):
        if self._get_tag(self.now_line) not in ("keyword", "identifier"):
            return False
        if self._get_token(self.now_line) not in ("int", "char", "boolean"):
            return False
        return True
        
    def compile(self):
        line = self.lines[self.now_line]
        if line.strip("<").strip(">") != "token":
            raise CompilationError("xml is not started with 'tokens'")
        self.advance()
        self.compileClass()
        self.lines[self.now_line]
        if line.strip("<").strip(">") != "/token":
            raise CompilationError("xml is not end with '/tokens'")

    def compileClass(self):
        token = self._get_token(self.get_line())
        if token != "class":
            raise CompilationError("programm is not started with 'class'")
        self._start_non_terminal("class")
        self.advance()
        self._compileClassName()
        self.advance()
        if self.get_token(self.now_line) != "{":
            raise CompilationError("class body is not started with '{'")
        self._write_line(self.now_line)
        self.advance()
        while self.now_line != "}":
            # compile class variable and subroutineDec
            if self._get_token(self.now_line) in ("static", "field"):
                self.compileClassVarDec()
            elif self._get_token(self.now_line) in ("constructor", "function", "method"):
                self.compileSubroutineDec()
            else:
                raise CompilationError("contain disable definition in class")
        self._write_line(self.now_line)
        self._end_non_terminal("class")

    def compileClassVarDec(self):
        if self._get_token(self.now_line) not in ("static", "field"):
            raise CompilationError("class var dec is not started with 'static' or 'field'")
        self._start_non_terminal("classVarDec")
        self._write_line(self.now_line)
        self.advance()
        if self._get_tag(self.now_line) not in ("keyword", "identifier"):
            raise CompilationError("type is supported 'keyword' or 'identifier'")
        self._write_line(self.now_line)
        self.advance()
        if self._get_tag(self.now_line) != "identifier":
            raise CompilationError("'varName' need to be identifier") 
        self.write_line(self.now_line)
        self.advance()
        while self._get_tag(self.now_line) == "identifier" || self.get_token(self.now_line) == ",":
            self.write_line(self.now_line)
            self.advance()
        if self._get_token(self.now_line) != ";":
            raise CompilationError("';' need end of class var") 
	self.write_line(self.now_line)
        self.advance()
        self._end_non_terminal("classVarDec")

    def compileSubroutineDec(self):
        self._start_non_terminal("subroutineDec")
        self.write_line(self.now_line)
        self.advance()
        if self._get_token(self.now_line) not in ("void", "type"):
            raise CompilationError("subroutine return type undefined")
        self.write_line(self.now_line)
        self.advance()
        if self._get_tag(self.now_line) != "identifier":
            raise CompilationError("subroutine needs subroutineName")
        self.write_line(self.now_line)
        self.advance()
        if self._get_tag(self.now_line) "= "(":
            raise CompilationError("subroutine needs '('")
        self.write_line(self.now_line)
        self.advance()
        self.compileParameterList()
        self.write_line(self.now_line)
        self.advance()
        self.compileSubroutineBody()
        self._end_non_terminal("subroutineDec")

    def compileSubroutineBody(self):
        self._start_non_terminal("subroutineBody")
        if self._get_token(self.now_line) != "{";
            raise CompilationError("subroutine body needs '{'")
        self.write_line(self.now_line)
        self.advance()
        while self._get_token(self.now_line) == "var":
            self.compileVarDec()
        self.compileStatements()
        self._end_non_terminal("subroutineBody")

    def compileVarDec(self):
        self._start_non_terminal("varDec")
        if self._get_token(self.now_line) != "var":
            raise CompilationError("var dec needs to be started with 'var'")
        self.write_line(self.now_line)
        self.advance()
        if self._get_tag(self.now_line) not in ("keyword", "identifier"):
            raise CompilationError("type is supported 'keyword' or 'identifier'")
        self.write_line(self.now_line)
        self.advance()
        if self._get_tag(self.now_line) != "identifier":
            raise CompilationError("varName is supported only 'identifier'")
        self.write_line(self.now_line)
        self.advance()
        while self._get_token(self.now_line) == ",":
            self.write_line(self.now_line)
            self.advance()
            if self._get_tag(self.now_line) != "identifier":
                raise CompilationError("varName is supported only 'identifier'")
            self.write_line(self.now_line)
            self.advance()
        if self._get_token(self.now_line) != ";":
            raise CompilationError("varName needs to be ended with ';'")
        self.write_line(self.now_line)
        self.advance()
        self._end_non_terminal("varDec")

    def compileStatements(self):
        self._start_non_terminal("statements")
        while self.is_statement():
            self.compileStatement()
        self._end_non_terminal("statements")

    def is_statement(self):
        token = self._get_token(self.now_line)
        if token in ("let", "if", "while", "do", "return"):
            return True
        return False

    def compileStatement(self):
        token = self._get_token(self.now_line)
        if token == "let":
            self.compileLet()
        elif token == "do":
            self.compileDo()
        elif token == "while":
            self.compileWhile()
        elif token == "return":
            self.compileReturn()
        elif token == "if":
            self.compileIf()

    def compileLet(self):
        self._start_non_terminal("letStatement")
        self.write_line(self.now_line)
        self.advance()
        if self._get_tag(self.now_line) != "identifier":
            raise CompilationError("varName is supported only 'identifier'")
        self.write_line(self.now_line)
        self.advance()
        if self._get_tag(self.now_line) == "[":
            self.write_line(self.now_line)
            self.advance()
            self.compileExpression()
        if self._get_token(self.now_line) != "=":
            raise CompilationError("let needs '=' to assign variable")
        self.write_line(self.now_line)
        self.advance()
        self.compileExpression()
        if self._get_token(self.now_line) != ";":
            raise CompilationError("let needs ';' to end let")
        self.write_line(self.now_line)
        self.advance()
        self._end_non_terminal("letStatement")

    def compileExpression(self):
        self._start_non_terminal("expression")
        self.compileTerm()
        while self.is_op(self.now_line):
            self.compileOp()
            self.compileTerm()
        self._end_non_terminal("expression")

    def compileOp():
        if self._get_token(self.now_line) not in ("+", "-", "*", "/", "&", "|", "<", ">", "="):
            raise CompiletaionError("{} is not supported opration".format(self._get_token(self.now_line)))
        self.write_line(self.now_line)
        self.advance()

    def compileTerm(self):
        self._start_non_terminal("term")
        if self.is_unaryOp():
            self.write_line(self.now_line)
            self.advance()
            self.compileTerm()
        elif self._get_tag(self.now_line) in ("integerConstant", "stringConstant", "keywordConstant"):
            self.write_line(self.now_line)
            self.advance()
        else:
            pass
        self._end_non_terminal("term")

    def is_unaryOp(self):
        if self._get_token(self.now_line) in ("-", "~"):
             return True
        return False
        
    def compileParameterList(self):
        self._start_non_terminal("parameterList")
        if self._get_tag(self.now_line) not in ("keyword", "identifier"):
            pass
        else:
            self.write_line(self.now_line)
            self.advance()
            if self._get_tag(self.now_line) not "identifier":
                raise CompilationError("varName is supported 'identifier'")
            self.write_line(self.now_line)
            self.advance()
            while self._get_token(self.now_line) == ",":
                self.write_line(self.now_line)
                self.advance()
                self.write_line(self.now_line)
                self.advance()
        self._end_non_terminal("parameterList")

    def _compileClassName(self):
        tag = self._get_tag(self.get_line())
        if tag != "identifier":
            raise CompilationError("'class' is undefined 'className'")
        self._write_line(self.get_line())
        


def write(wf, content):
    wf.write(content + "\n")
       

def tokenizer(files):
    wf = None
    tokenized_file_list = []
    for file_path in files:
        f = file_open(file_path)
        tokenizer = JackTokenizer(f)
        write_file_name = file_path.rstrip(".jack")
        write_file_path = "{}_T.xml".format(write_file_name)
        wf = open(write_file_path, "w")
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
        tokenized_file_list.append(write_file_path)
    return tokenized_file_list


def compilate(files):
    for file_path in files:
        f = file_open(file_path)
        compile_engine = CompilationEngine(f)
        write_file_name = file_path.rstrip(".xml")
        write_file_path = "{}_C.xml".format(write_file_name)
        wf = open(write_file_path, "w")


def main():
    files = get_files()
    if not files:
        raise FileNotExistError("not passed target files")
    tokenized_file_list = tokenizer()
    compilate(tokenized_file_list)


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
