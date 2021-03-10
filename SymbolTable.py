class SymbolTableError(Exception):
     pass


class SymbolTable(object):
    def __init__(self):
        self.class_table = {}
        self.class_index = 0
        self.subroutine_table = {}
        self.subroutine_index = 0

    def startSubroutine(self):
        self.subroutine_table = {}
        self.subroutine_index = 0

    def is_class_table(self, kind):
        if kind in ("static", "field"):
            return True
        return False

    def is_subroutine_table(self, kind):
        if kind in ("arg", "var"):
            return True
        return False

    def define(self, name, type, kind):
        if self.is_class_table(kind):
            self.class_table[name] = {"type": type, "kind": kind, "index": self.class_index}
            self.class_index += 1
        elif self.is_subroutine_table(kind):
            self.subroutine_table[name] = {"type": type, "kind": kind, "index": self.subroutine_index}
            self.subroutine_index += 1
        else:
            raise SymbolTableError("{} cant use as kind".format(kind))

    def varCount(self, kind):
        count = 0
        if self.is_class_table(kind):
            for k, v in self.class_table.items():
                if v["kind"] == kind:
                    count += 1
        elif self.is_subroutine_table(kind):
            for k, v in self.subroutine_table.items():
                if v["kind"] == kind:
                    count += 1

        return count

    def kindOf(self, name):
        for k, v in self.subroutine_table.items():
            if name == k:
                return v["kind"]
        for k, v in self.class_table.items():
            if name == k:
                return v["kind"]

        return None

    def typeOf(self, name):
        for k, v in self.subroutine_table.items():
            if name == k:
                return v["type"]
        for k, v in self.class_table.items():
            if name == k:
                return v["type"]

        return None

    def indexOf(self, name):
        for k, v in self.subroutine_table.items():
            if name == k:
                return v["index"]
        for k, v in self.class_table.items():
            if name == k:
                return v["index"]

        return None
