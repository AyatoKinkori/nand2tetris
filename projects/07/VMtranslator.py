import os
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

class FileNotExistError(Exception):
    pass

class FileParseError(Exception):
    pass

SEG_CONS = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}


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
        elif self.is_pop(command):
            return CommandType.C_POP
        elif self.is_label(command):
            return CommandType.C_LABEL
        elif self.is_call(command):
            return CommandType.C_CALL
        elif self.is_function(command):
            return CommandType.C_FUNCTION
        elif self.is_goto(command):
            return CommandType.C_GOTO
        elif self.is_return(command):
            return CommandType.C_RETURN
        elif self.is_call(command):
            return CommandType.C_CALL
        elif self.is_if(command):
            return CommandType.C_IF

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

    def is_label(self, command):
        op = self.op()
        if op == "label":
            return True

        return False

    def is_pop(self, command):
        op = self.op()
        if op == "pop":
            return True

        return False

    def is_call(self, command):
        op = self.op()
        if op == "call":
            return True

        return False

    def is_goto(self, command):
        op = self.op()
        if op == "goto":
            return True

        return False

    def is_if(self, command):
        op = self.op()
        if op == "if-goto":
            return True
  
        return False

    def is_function(self, command):
        op = self.op()
        if op == "function":
            return True

        return False

    def is_return(self, command):
        op = self.op()
        if op == "return":
            return True 

        return False

    def is_call(self, command):
        op = self.op()
        if op == "call":
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
        elif self.commandType() == CommandType.C_POP:
            return arg1
        else:
            return arg1

    def arg2(self):
        splited_command = self.command.split(" ")
        arg2 = splited_command[2]
        if self.commandType() == CommandType.C_PUSH:
            return arg2
        elif self.commandType() == CommandType.C_POP:
            return arg2
        elif self.commandType() == CommandType.C_FUNCTION:
            return arg2
        elif self.commandType() == CommandType.C_RETURN:
            return arg2
        elif self.commandType() == CommandType.C_CALL:
            return arg2


class CodeWriter(object):
    def __init__(self, name):
        f = open("{}.asm".format(name), "w")
        self.eq_if_use_count = 0
        self.gt_if_use_count = 0
        self.lt_if_use_count = 0
        self.file = f
        self.full_path = name
        self.file_name = name.split("/")[-1]
        self.call_count = 0
        self.sys_init()

    def _get_call_count(self):
        count = self.call_count
        self.call_count += 1
        return count

    def sys_init(self):
        lines = []
        # SP init
        lines.append("@256")
        lines.append("D=A")
        lines.append("@SP")
        lines.append("M=D")
        self.writelines(lines)
        self.writeCall("Sys.init", "0")

    #def setFileName(self, file_path):
        #f = open("{}.asm".format(file_path), "w")
        #self.file = f

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
            lines.append("@EQELSE{}".format(self.eq_if_use_count))
            lines.append("0;JMP")
            lines.append("(EQIF{})".format(self.eq_if_use_count))
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=1")
            lines.append("@EQEND{}".format(self.eq_if_use_count))
            lines.append("0;JMP")
            lines.append("(EQELSE{})".format(self.eq_if_use_count))
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=0")
            lines.append("@EQEND{}".format(self.eq_if_use_count))
            lines.append("0;JMP")
            lines.append("(EQEND{})".format(self.eq_if_use_count))
        elif op == "gt":
            self.gt_if_use_count += 1
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=M")
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=M-D")
            lines.append("@GTIF{}".format(self.gt_if_use_count))
            lines.append("D;JGT")
            lines.append("@GTELSE{}".format(self.gt_if_use_count))
            lines.append("0;JMP")
            lines.append("(GTIF{})".format(self.gt_if_use_count))
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=1")
            lines.append("@GTEND{}".format(self.gt_if_use_count))
            lines.append("0;JMP")
            lines.append("(GTELSE{})".format(self.gt_if_use_count))
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=0")
            lines.append("@GTEND{}".format(self.gt_if_use_count))
            lines.append("0;JMP")
            lines.append("(GTEND{})".format(self.gt_if_use_count))
        elif op == "lt":
            self.lt_if_use_count += 1
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=M")
            lines.append("@SP")
            lines.append("M=M-1")
            lines.append("@SP")
            lines.append("A=M")
            lines.append("D=M-D")
            lines.append("@LTIF{}".format(self.lt_if_use_count))
            lines.append("D;JLT")
            lines.append("@LTELSE{}".format(self.lt_if_use_count))
            lines.append("0;JMP")
            lines.append("(LTIF{})".format(self.lt_if_use_count))
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=1")
            lines.append("@LTEND{}".format(self.lt_if_use_count))
            lines.append("0;JMP")
            lines.append("(LTELSE{})".format(self.lt_if_use_count))
            lines.append("@SP")
            lines.append("A=M")
            lines.append("M=0")
            lines.append("@LTEND{}".format(self.lt_if_use_count))
            lines.append("0;JMP")
            lines.append("(LTEND{})".format(self.lt_if_use_count))
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

    def _push_constant(self, index):
        lines = []
        lines.append("@{}".format(index))
        lines.append("D=A")
        lines.append("@SP")
        lines.append("A=M")
        lines.append("M=D")
        lines.append("@SP")
        lines.append("M=M+1")
        return lines

    def _push_segment(self, segment, index):
        lines = []
        lines.append("@{}".format(index))
        lines.append("D=A")
        lines.append("@{}".format(SEG_CONS[segment]))
        lines.append("A=M+D")
        lines.append("D=M")
        lines.append("@SP")
        lines.append("A=M")
        lines.append("M=D")
        lines.append("@SP")
        lines.append("M=M+1")
        return lines

    def _pop_segment(self, segment, index):
        lines = []
        # sp decrement
        lines.append("@SP")
        lines.append("M=M-1")
        # add arg + index
        lines.append("@{}".format(index))
        lines.append("D=A")
        lines.append("@{}".format(SEG_CONS[segment]))
        lines.append("D=M+D")
        lines.append("@13")
        lines.append("M=D")
        lines.append("@SP")
        lines.append("A=M")
        lines.append("D=M")
        # set (arg + i) sp value
        lines.append("@13")
        lines.append("A=M")
        lines.append("M=D")
        return lines

    def writePushPop(self, op, segment, index):
        lines = []
        if op == "push":
            if segment == "constant":
                lines.extend(self._push_constant(index))
            elif segment in ("local", "argument", "this", "that"):
                lines.extend(self._push_segment(segment, index))
            elif segment == "temp":
                lines.append("@5")
                lines.append("D=A")
                lines.append("@{}".format(index))
                lines.append("A=A+D")
                lines.append("D=M")
                lines.append("@SP")
                lines.append("A=M")
                lines.append("M=D")
                lines.append("@SP")
                lines.append("M=M+1")
            elif segment == "pointer":
                lines.append("@3")
                lines.append("D=A")
                lines.append("@{}".format(index))
                lines.append("A=A+D")
                lines.append("D=M")
                lines.append("@SP")
                lines.append("A=M")
                lines.append("M=D")
                lines.append("@SP")
                lines.append("M=M+1")
            elif segment == "static":
                lines.append("@{}.{}".format(self.file_name, index))
                lines.append("D=M")
                lines.append("@SP")
                lines.append("A=M")
                lines.append("M=D")
                lines.append("@SP")
                lines.append("M=M+1")
        elif op == "pop":
            if segment in ("local", "argument", "this", "that"):
                lines.extend(self._pop_segment(segment, index))
            elif segment == "temp":
                lines.append("@SP")
                lines.append("M=M-1")
                lines.append("@5")
                lines.append("D=A")
                lines.append("@{}".format(index))
                lines.append("D=D+A")
                lines.append("@13")
                lines.append("M=D")
                lines.append("@SP")
                lines.append("A=M")
                lines.append("D=M")
                lines.append("@13")
                lines.append("A=M")
                lines.append("M=D")
            elif segment == "pointer":
                lines.append("@SP")
                lines.append("M=M-1")
                lines.append("@3")
                lines.append("D=A")
                lines.append("@{}".format(index))
                lines.append("D=D+A")
                lines.append("@13")
                lines.append("M=D")
                lines.append("@SP")
                lines.append("A=M")
                lines.append("D=M")
                lines.append("@13")
                lines.append("A=M")
                lines.append("M=D")
            elif segment == "static":
                lines.append("@SP")
                lines.append("M=M-1")
                lines.append("@SP")
                lines.append("A=M")
                lines.append("D=M")
                lines.append("@{}.{}".format(self.file_name, index))
                lines.append("M=D")

        self.writelines(lines)

    def writeLabel(self, label):
        lines = []
        lines.append("({})".format(label))
        self.writelines(lines)
 
    def writeGoto(self, label):
        lines = []
        lines.append("@{}".format(label))
        lines.append("0;JMP")
        self.writelines(lines)

    def writeIf(self, label):
        lines = []
        lines.append("@SP")
        lines.append("AM=M-1")
        lines.append("D=M")
        lines.append("@{}".format(label))
        lines.append("D;JNE")
        self.writelines(lines)

    def writeFunction(self, functionName, argsCountstr):
        lines = []
        lines.append("({})".format(functionName))
        argsCount = int(argsCountstr)
        while argsCount > 0:
            self._push_constant(0)
            argsCount -= 1
        self.writelines(lines)

    def writeCall(self, functionName, args):
        lines = []
        return_address = "{}f{}.c{}".format(self.file_name, functionName, self._get_call_count())
        # add return address sp
        lines.append("@{}".format(return_address))
        lines.append("D=A")
        lines.append("@SP")
        lines.append("A=M")
        lines.append("M=D")
        lines.append("@SP")
        lines.append("M=M+1")
        # push segments
        segments = ["local", "argument", "this", "that"]
        for segment in segments:
            self._push_segment(segment, 0)
        # ARG = SP - n - 5
        lines.append("@{}".format(5 + int(args)))
        lines.append("D=A")
        lines.append("@SP")
        lines.append("D=M-D")
        lines.append("@ARG")
        lines.append("M=D")
        # LCL = SP
        lines.append("@SP")
        lines.append("D=M")
        lines.append("@LCL")
        lines.append("M=D")
        # jump function
        lines.append("@{}".format(functionName))
        lines.append("0;JMP")
        # write return address label
        lines.append("({})".format(return_address))
        self.writelines(lines)

    def _set_symbol_value_to_dreg(self, symbol):
        lines = []
        lines.append("@{}".format(symbol))
        lines.append("D=M")
        return lines

    def _sub_dreg_value(self, index):
        lines = []
        lines.append("@{}".format(index))
        lines.append("D=D-A")
        return lines
        
    def writeReturn(self):
        lines = []
        # save lcl address to r13
        lines.append("@{}".format(SEG_CONS["local"]))
        lines.append("D=M")
        lines.append("@R13")
        lines.append("M=D")
        # get return address and save to r14
        lines.append("@5")
        lines.append("A=D-A")
        lines.append("D=M") 
        lines.append("@R14")
        lines.append("M=D")
        # return value move
        lines.append("@SP")
        lines.append("A=M-1")
        lines.append("D=M")
        lines.append("@ARG")
        lines.append("A=M")
        lines.append("M=D")
        lines.append("@ARG")
        lines.append("D=M+1")
        lines.append("@SP")
        lines.append("M=D")
        # set saved that 
        lines.extend(self._set_symbol_value_to_dreg("R13"))
        lines.extend(self._sub_dreg_value(1))
        lines.append("A=D")
        lines.append("D=M")
        lines.append("@THAT")
        lines.append("M=D")
        # set saved this
        lines.extend(self._set_symbol_value_to_dreg("R13"))
        lines.extend(self._sub_dreg_value(2))
        lines.append("A=D")
        lines.append("D=M")
        lines.append("@THIS")
        lines.append("M=D")
        # set saved arg
        lines.extend(self._set_symbol_value_to_dreg("R13"))
        lines.extend(self._sub_dreg_value(3))
        lines.append("A=D")
        lines.append("D=M")
        lines.append("@ARG")
        lines.append("M=D")
        # set saved lcl
        lines.extend(self._set_symbol_value_to_dreg("R13"))
        lines.extend(self._sub_dreg_value(4))
        lines.append("A=D")
        lines.append("D=M")
        lines.append("@LCL")
        lines.append("M=D")
        self.writelines(lines)
        lines.append("@R14")
        lines.append("A=M")
        lines.append("0;JMP")

    def close(self):
        lines = []
        lines.append("(END)")
        lines.append("@END")
        lines.append("0;JMP")
        self.writelines(lines)
        self.file.close()


def main():
    files = get_files()
    if not files:
        raise FileNotExistError("not passed target files")
    writer = None
    for file_path in files:
        f = file_open(file_path)
        write_file_name = file_path.rstrip(".vm")
        parser = Parser(f)
        if not writer:
            writer = CodeWriter(write_file_name)
        while True:
            commandType = parser.commandType()
            if commandType == CommandType.C_ARITHMETIC:
                writer.writeArithmetic(parser.command)
            elif commandType in (CommandType.C_PUSH, CommandType.C_POP):
                writer.writePushPop(parser.op(), parser.arg1(), parser.arg2())
            elif commandType == CommandType.C_LABEL:
                writer.writeLabel(parser.arg1())
            elif commandType == CommandType.C_GOTO:
                writer.writeGoto(parser.arg1())
            elif commandType == CommandType.C_CALL:
                writer.writeCall(parser.arg1(), parser.arg2())
            elif commandType == CommandType.C_IF:
                writer.writeIf(parser.arg1())
            elif commandType == CommandType.C_RETURN:
                writer.writeReturn()
            elif commandType == CommandType.C_FUNCTION:
                writer.writeFunction(parser.arg1(), parser.arg2())

            if not parser.hasMoreCommands():
                break
        
            parser.advance()
    writer.close()

def get_files():
    path = sys.argv[1]
    files = []
    if os.path.isdir(path):
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    split_name = entry.name.split(".")
                    if "vm" == split_name[-1]:
                        files.append(entry.path)
    else:
        files.append(path)
    
    return files

def file_open(file_path):
    splited_file_name = file_path.split(".")
    if 1 >= len(splited_file_name):
        raise FileParseError("拡張子が指定されていません。")
    
    if "vm" != splited_file_name[-1]:
        raise FileParseError("vmファイルが指定されていません。")
    f = open(file_path, "r")
    return f

if __name__ == "__main__":
    main()
