import sys
from enum import Enum


class CommandType(Enum):
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8


class FileParseError(Exception):
    pass


class Parser(object):
    def __init__(self, file_):
        self.lines = []
        for line in file_.readlines():
            self.lines.append(line)
        self.line_sum = len(self.lines)
        self.now_line = 0
        self.set_command()

    def normalize(self, command):
        return command.split("//")[0]

    def hasMoreCommands(self):
        return self.now_line < self.line_sum - 1

    def set_command(self):
        self.command = self.normalize(self.lines[self.now_line]).strip()

    def advance(self):
        if self.hasMoreCommands():
            self.now_line += 1
            self.set_command()

    def commandType(self):
        command = self.command
        if self.is_artithmetic(command):
            return CommandType.C_ARITHMETIC
        elif self.is_push(command):
            return CommandType.C_PUSH

    def is_artithmetic(self, command):
        op = self.op()
        if op in ("add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"):
            return True
        
        return False

    def is_push(self, command):
        op = self.op()
        if op == "push":
            return True

        return False

    def op(self):
        return self.command.split(" ")[0]
    
    def arg1(self):
        splited_command = self.command.split(" ")
        op = splited_command[0]
        arg1 = splited_command[1]
        if self.commandType() == CommandType.C_ARITHMETIC:
            return op
        elif self.commandType() == CommandType.C_PUSH:
            return arg1

    def arg2(self):
        splited_command = self.command.split(" ")
        arg2 = splited_command[2]
        if self.commandType() == CommandType.C_PUSH:
            return arg2


class CodeWriter(object):
    def __init__(self, name):
        f = open("{}.asm".format(name), "w")
        self.eq_if_use_count = 0
        self.gt_if_use_count = 0
        self.lt_if_use_count = 0
        self.file = f

    def setFileName(self, file_name):
        self.close()
        f = open("{}.asm".format(file_name), "w")
        self.file = f

    def writelines(self, lines):
        lines = map(lambda x: x + "\n", lines)
        self.file.writelines(lines)

    def writeArithmetic(self, op):
        lines = []
        lines.append("@SP")
        lines.append("M=M-1")
        if op == "add":
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=M")
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=D+M")
            lines.append("@SP")
            lines.append("M=M+1")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=D")
        elif op == "sub":
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=-M")
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=D+M")
        elif op == "neg":
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=-M")
        elif op == "eq":
            self.eq_if_use_count += 1
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=M")
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=D-M")
            lines.append("@EQIF{}".format(self.eq_if_use_count))
            lines.append("D;JEQ")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=0")
            lines.append("(EQIF{})".format(self.eq_if_use_count))
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=1")
        elif op == "gt":
            self.gt_if_use_count += 1
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=M")
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=D-M")
            lines.append("@GTIF{}".format(self.gt_if_use_count))
            lines.append("D;JGT")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=0")
            lines.append("(GTIF{})".format(self.gt_if_use_count))
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=1")
        elif op == "lt":
            self.lt_if_use_count += 1
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=M")
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=D-M")
            lines.append("@LTIF{}".format(self.lt_if_use_count))
            lines.append("D;JLT")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=0")
            lines.append("(LTIF{})".format(self.lt_if_use_count))
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=1")
        elif op == "and":
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=M")
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=D&M")
        elif op == "or":
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=M")
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=D|M")
        elif op == "not":
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=!M")

        lines.append("@SP")
        lines.append("M=M+1")

        self.writelines(lines)

    def writePushPop(self, op, segment, index):
        lines = []
        if op == "push":
            if segment == "constant":
                lines.append("@{}".format(index))
                lines.append("D=A")
                lines.append("@SP")
                lines.append("A=M")
                lines.append("M=D")
                lines.append("@SP")
                lines.append("M=M+1")

        self.writelines(lines)

    def close(self):
        lines = []
        lines.append("(END)")
        lines.append("@END")
        lines.append("0;JMP")
        self.writelines(lines)
        self.file.close()


def main():
    f = file_open()
    write_file_name = f.name.split(".")[0]
    parser = Parser(f)
    writer = CodeWriter(write_file_name)
    while True:
        commandType = parser.commandType()
        if commandType == CommandType.C_ARITHMETIC:
            writer.writeArithmetic(parser.command)
        elif commandType in (CommandType.C_PUSH, CommandType.C_POP):
            writer.writePushPop(parser.op(), parser.arg1(), parser.arg2())

        if not parser.hasMoreCommands():
            break
        
        parser.advance()

    writer.close()

def file_open():
    value = sys.argv
    if 1 >= len(value):
        raise FileParseError("対象ファイルが指定されていません。")
    
    file_name = value[1]
    print(file_name)
    splited_file_name = file_name.split(".")
    if 1 >= len(splited_file_name):
        raise FileParseError("拡張子が指定されていません。")
    
    if "vm" != splited_file_name[-1]:
        raise FileParseError("vmファイルが指定されていません。")
    f = open(file_name, "r")
    return f

if __name__ == "__main__":
    main()
