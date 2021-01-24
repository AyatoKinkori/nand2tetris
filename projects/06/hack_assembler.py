import sys
from enum import Enum

class CommandType(Enum):
    A_COMMAND = 0
    C_COMMAND = 1
    L_COMMAND = 2


class FileParseError(Exception):
    pass

class NotHasSymbol(Exception):
    pass

class NotCOperation(Exception):
    pass

class NotValidOperation(Exception):
    pass

class CodeValidationError(Exception):
    pass


class Parser(object):
    def __init__(self, file_):
        self.lines = []
        for line in file_.readlines():
            self.lines.append(line)

        self.line_sum = len(self.lines)
        self.now_line = 0
        self.set_command()

    def reset(self):
        self.now_line = 0
        self.set_command()

    def normalize(self, command):
        command = command.replace(" ", "")
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
        if not self.command:
            return None

        if self.check_is_a_command():
            return CommandType.A_COMMAND
        elif self.check_is_c_command():
            return CommandType.C_COMMAND
        elif self.check_is_l_command():
            return CommandType.L_COMMAND

    def check_is_a_command(self):
        if self.command[0] == "@":
            return True

    def check_is_c_command(self):
        split_equal = self.command.split("=")
        split_semi_colon = self.command.split(";")
        comp = ""
        if len(split_equal) > 1:
            dest = split_equal[0]
            if dest not in ("M", "D", "MD", "A", "AM", "AD", "AMD"):
                return False

            comp = split_equal[1]
        elif len(split_semi_colon) > 1:
            jump = split_semi_colon[1]
            if jump not in ("JGT", "JEQ", "JGE", "JLT", "JNE", "JLE", "JMP"):
                return False

            comp = split_semi_colon[0]
        else:
            return False

        if len(comp) > 0:
            comp = comp.strip()
        if comp in ("0", "1", "-1", "D", "A", "!D", "!A", "-D", "-A", "D+1", "A+1", "D-1", "D+A", "D-A", "A-D", "D&A", "D|A",
                "M", "!M", "-M", "M+1", "M-1", "D+M", "D-M", "M-D", "D&M", "D|M"):
            return True

        return False

    def check_is_l_command(self):
        return self.command[0] == "(" and self.command[-1] == ")"

    def l_command(self):
        return self.command[1:-1]

    def symbol(self):
        if self.commandType() == CommandType.A_COMMAND:
            return self.command.split("@")[1]
        elif self.commandType() == CommandType.L_COMMAND:
            return self.command
        else:
            raise NotHasSymbol("?V???{?????L?????????????????")

    def dest(self):
        if self.commandType() != CommandType.C_COMMAND:
            raise NotCOperation("C?????????????????g?B????????")
        split_equal = self.command.split("=")
        if len(split_equal) > 1:
            dest = split_equal[0]
            if dest not in ("M", "D", "MD", "A", "AM", "AD", "AMD"):
                raise NotValidOperation("dest????????????`?????B???????")

            return dest

        else:
            return None

    def comp(self):
        if self.commandType() != CommandType.C_COMMAND:
            raise NotCOperation("C?????????????????g?B????????")
        split_equal = self.command.split("=")
        split_semi_colon = None
        comp = None
        if len(split_equal) > 1:
            split_semi_colon = split_equal[1].split(";")
        else:
            split_semi_colon = self.command.split(";")

        comp = split_semi_colon[0].strip()
        if comp not in ("0", "1", "-1", "D", "A", "!D", "!A", "-D", "-A", "D+1", "A+1", "D-1", "D+A", "D-A", "A-D", "D&A", "D|A",
                "M", "!M", "-M", "M+1", "M-1", "D+M", "D-M", "M-D", "D&M", "D|M"):
            return None

        return comp

    def jump(self):
        if self.commandType() != CommandType.C_COMMAND:
            raise NotCOperation("C?????????????????g?B????????")
        split_semi_colon = self.command.split(";")
        if 1 >= len(split_semi_colon):
            return None

        jump = split_semi_colon[1]
        return jump
            

class Code(object):
    def __init__(self, dest, comp, jump):
        self.dest_ = dest
        self.comp_ = comp
        self.jump_ = jump

    def dest(self):
        if not self.dest_:
            return "000"
        
        dest = self.dest_
        if dest == "M":
            return "001"
        elif dest == "D":
            return "010"
        elif dest == "MD":
            return "011"
        elif dest == "A":
            return "100"
        elif dest == "AM":
            return "101"
        elif dest == "AD":
            return "110"
        elif dest == "AMD":
            return "111"

    def comp(self):
        if not self.comp_:
            return None

        comp = self.comp_
        if comp == "0":
            return "0101010"
        elif comp == "1":
            return "0111111"
        elif comp == "-1":
            return "0111010"
        elif comp == "D":
            return "0001100"
        elif comp in ("A", "M"):
            if comp == "A":
                return "0110000"
            else:
                return "1110000"
        elif comp == "!D":
            return "0001101"
        elif comp in ("!A", "!M"):
            if comp == "!A":
                return "0110001"
            else:
                return "1110001"
        elif comp == "-D":
            return "0001111"
        elif comp in ("-A", "-M"):
            if comp == "-A":
                return "0110011"
            else:
                return "1110011"
        elif comp == "D+1":
            return "0011111"
        elif comp in ("A+1", "M+1"):
            if comp == "A+1":
                return "0110111"
            else:
                return "1110111"
        elif comp == "D-1":
            return "0001110"
        elif comp in ("A-1", "M-1"):
            if comp == "A-1":
                return "0110010"
            else:
                return "1110010"
        elif comp in ("D+A", "D+M"):
            if comp == "D+A":
                return "0000010"
            else:
                return "1000010"
        elif comp in ("D-A", "D-M"):
            if comp == "D-A":
                return "0010011"
            else:
                return "1010011"
        elif comp in ("A-D", "M-D"):
            if comp == "A-D":
                return "0010011"
            else:
                return "1010011"
        elif comp in ("D&A", "D&M"):
            if comp == "D&A":
                return "0000000"
            else:
                return "1000000"
        elif comp in ("D|A", "D|M"):
            if comp == "D|A":
                return "0010101"
            else:
                return "1010101"
        else:
            raise CodeValidationError("?w????????comp?R?[?h???")

    def jump(self):
        if not self.jump_:
            return "000"
        jump = self.jump_
        if jump == "JGT":
            return "001"
        elif jump == "JEQ":
            return "010"
        elif jump == "JGE":
            return "011"
        elif jump == "JLT":
            return "100"
        elif jump == "JNE":
            return "101"
        elif jump == "JLE":
            return "110"
        elif jump == "JMP":
            return "111"


class SymbolTable(object):
    def __init__(self):
        self.table = {
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "R0": 0,
            "R1": 1,
            "R2": 2,
            "R3": 3,
            "R4": 4,
            "R5": 5,
            "R6": 6,
            "R7": 7,
            "R8": 8,
            "R9": 9,
            "R10": 10,
            "R11": 11,
            "R12": 12,
            "R13": 13,
            "R14": 14,
            "R15": 15,
            "SCREEN": 16384,
            "KBD": 24576,
        }

    def addEntry(self, symbol, address):
        self.table[symbol] = address

    def contains(self, symbol):
        return (symbol in self.table)

    def getAddress(self, symbol):
        if not self.contains(symbol):
            return None

        return self.table[symbol]


def main():
    f = file_open()
    parser = Parser(f)
    write_file = write_file_open()
    write_lines = []

    # 1 pass
    symbol_table = SymbolTable()
    row_num = 0
    while True:
        commandType = parser.commandType()
        if commandType in (CommandType.A_COMMAND, CommandType.C_COMMAND):
            row_num += 1
        elif commandType == CommandType.L_COMMAND:
            symbol_table.addEntry(parser.l_command(), row_num)

        if not parser.hasMoreCommands():
            break

        parser.advance()
    # 2 pass
    parser.reset()
    ram_address = 16
    while True:
        commandType = parser.commandType()
        row = ""
        if commandType == CommandType.A_COMMAND:
            symbol = parser.symbol()
            if not symbol.isdecimal():
                if not symbol_table.contains(symbol):
                    symbol_table.addEntry(symbol, ram_address)
                    symbol = symbol_table.getAddress(symbol)
                    ram_address += 1
                    symbol_binary = symbol_to_decimal_binary(symbol)
                    row = symbol_binary_to_row(symbol_binary)
                else:
                    symbol = symbol_table.getAddress(symbol)
                    symbol_binary = symbol_to_decimal_binary(symbol)
                    row = symbol_binary_to_row(symbol_binary)
            else:
                symbol_binary = symbol_to_decimal_binary(symbol)
                row = symbol_binary_to_row(symbol_binary)


        elif commandType == CommandType.C_COMMAND:
            dest = parser.dest()
            comp = parser.comp()
            jump = parser.jump()
            c = Code(dest, comp, jump)
            comp_binary = c.comp()
            dest_binary = c.dest()
            jump_binary = c.jump()
            row = "111{} {}{}{}{} {}{}{}{} {}{}{}{}".format(
                    comp_binary[0], comp_binary[1], comp_binary[2], comp_binary[3], comp_binary[4], comp_binary[5], comp_binary[6],
                    dest_binary[0], dest_binary[1], dest_binary[2],
                    jump_binary[0], jump_binary[1], jump_binary[2]
                    )

        row = row.strip()
        if len(row) > 0:
            write_lines.append(row + "\n")

        if not parser.hasMoreCommands():
            break

        parser.advance()


    write_file.writelines(write_lines)
    write_file.close()


def symbol_to_decimal_binary(num):
    decimal = int(num)
    symbol_binary = bin(decimal)[2:]
    length = len(symbol_binary)
    miss = 16 - length
    fill = "".join(["0" for i in range(0, miss)])
    symbol_binary = fill + symbol_binary
    return symbol_binary

def symbol_binary_to_row(symbol_binary):
    row = "{}{}{}{} {}{}{}{} {}{}{}{} {}{}{}{}".format(
            symbol_binary[0], symbol_binary[1], symbol_binary[2],
            symbol_binary[3], symbol_binary[4], symbol_binary[5],
            symbol_binary[6], symbol_binary[7], symbol_binary[8],
            symbol_binary[9], symbol_binary[10], symbol_binary[11],
            symbol_binary[12], symbol_binary[13], symbol_binary[14],
            symbol_binary[15]
            )
    return row

def file_open():
    value = sys.argv
    if 1 >= len(value):
        raise FileParseError("?t?@?C?????w????????????")
    file_name = value[1]
    splited_file_name = file_name.split(".")
    if 1 >= len(splited_file_name):
        raise FileParseError("?g???q???w????????????")

    if "asm" != splited_file_name[1]:
        raise FileParseError("asm?t?@?C?????w???????????")

    f = open(file_name, "r")
    return f

def write_file_open():
    value = sys.argv
    if 1 >= len(value):
        raise FileParseError("?t?@?C?????w????????????")
    file_name = value[1]
    splited_file_name = file_name.split(".")
    if 1 >= len(splited_file_name):
        raise FileParseError("?g???q???w????????????")

    if "asm" != splited_file_name[1]:
        raise FileParseError("asm?t?@?C?????w???????????")

    f = open("{}.hack".format(splited_file_name[0]), "w")
    return f


if __name__ == "__main__":
    main()
