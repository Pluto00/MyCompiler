from enum import Enum


class LexicalElement:
    def get(self):
        return self.value

    def __repr__(self):
        return f"<{self.value}>"

    def describe(self):
        return self.__repr__()


class KeyWordType(LexicalElement, Enum):
    Do = "do"
    While = "while"
    Switch = "switch"
    Case = "case"
    If = "if"
    Then = "then"
    Else = "else"
    Until = "until"
    For = "for"
    Continue = "continue"
    Break = "break"
    Goto = "goto"
    Program = "program"


class NonWordType(LexicalElement, Enum):
    Addition = "+"
    Increment = "++"
    Subtraction = "-"
    Multiplication = "*"
    Division = "/"
    Modulus = "%"
    Decrement = "--"
    Equal = "="
    NotEqual = "<>"
    AddEqual = "+="
    SubEqual = "-="
    MulEqual = "*="
    DivEqual = "/="
    ModEqual = "%="
    ShiftLeft = "<<"
    ShiftRight = ">>"
    Less = "<"
    Greater = ">"
    LE = "<="
    GE = ">="
    LeftSquareBracket = "["
    RightSquareBracket = "]"
    Dot = "."
    Comma = ","
    Assign = ":="
    Colon = ":"
    Semicolon = ";"
    LeftParentheses = "("
    RightParentheses = ")"
    LogicalAND = "&&"
    LogicalOr = "||"
    LogicalNot = "!"
    LogicalNotEqual = "!="
    LogicalEqual = "=="
    BinaryXor = "^"
    BinaryAND = "&"
    BinaryOr = "|"
    LeftCurlyBracket = "{"
    RightCurlyBracket = "}"


class LiteralElement(LexicalElement):
    def __repr__(self):
        return f"<{self.name}, {self.value}>"

    def get(self):
        return self.name


class IntegerLiteral(LiteralElement):
    def __init__(self, val):
        assert type(val) == int
        self.name = "integer"
        self.value = val


class FloatLiteral(LiteralElement):
    def __init__(self, val):
        assert type(val) == float
        self.name = "float"
        self.value = val


class StringLiteral(LiteralElement):
    def __init__(self, val):
        assert type(val) == str
        self.name = "string"
        self.value = val


class IdentifierElement(LexicalElement):
    def __init__(self, val):
        self.name = "id"
        self.value = val

    def __repr__(self):
        return f"<{self.name}, {self.value}>"

    def get(self):
        return self.name


class LineFeedElement(LexicalElement):
    def __init__(self):
        self.value = "\n"

    def __repr__(self):
        return '\n'

    def get(self):
        return None


class ErrorElement(LexicalElement):
    def __init__(self, lineno, reason):
        self.lineno = lineno
        self.reason = reason

    def __repr__(self):
        return "error line %d: %s" % (self.lineno, self.reason)

    def get(self):
        return None
