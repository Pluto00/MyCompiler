from .Tokens import *


class Utils:
    NonWordToStringMap = {nw: nw.value for nw in NonWordType}
    StringToNonWordMap = {nw.value: nw for nw in NonWordType}
    KeyWordToStringMap = {kw: kw.value for kw in KeyWordType}
    StringToKeyWordMap = {kw.value: kw for kw in KeyWordType}

    @staticmethod
    def StringToStringLiteral(s):
        return StringLiteral(s)

    @staticmethod
    def StringToFloatLiteral(s):
        val = float(s)
        return FloatLiteral(val)

    @staticmethod
    def StringToIntegerLiteral(s, base=10):
        val = int(s, base)
        return IntegerLiteral(val)

    @staticmethod
    def StringToIdentifierElement(s):
        return IdentifierElement(s)

    @staticmethod
    def GetLineFeedElement():
        return LineFeedElement()

    @staticmethod
    def GetErrorElement(lineno, reason):
        return ErrorElement(lineno, reason)

    @staticmethod
    def ParseTokens(tokens):
        lineno = 1
        output = "line 1:"
        kws = [kw.value for kw in KeyWordType]
        symbol_table = set()
        for token in tokens:
            if type(token) == LineFeedElement:
                lineno += 1
                output += '\nline %d:' % lineno
            else:
                output += ' %s' % token.describe()
            if type(token) == IdentifierElement:
                symbol_table.add(token.get())
        symbol = ',\t'.join(kws + list(symbol_table))
        return {'symbol': symbol, 'output': output}

    @staticmethod
    def is_alpha(c):
        return str.isalpha(c)

    @staticmethod
    def is_digit(c):
        return str.isdigit(c)

    @staticmethod
    def is_Hex(c):
        return c in 'xX'
