class Lexer:
    words = ["switch", "case", "do", "else", "for", "goto", "if", "then", "until", "while", "continue", "break"]

    def __init__(self, code_file):
        self.code_input = code_file
        self.lineno = 0
        self.line = None
        self.line_len = None
        self.line_pos = None
        self.symbol_table = None
        self.output = ""

    @staticmethod
    def is_alpha(c):
        return str.isalpha(c)

    @staticmethod
    def is_digit(c):
        return str.isdigit(c)

    @staticmethod
    def is_Hex(c):
        return c in 'xX'

    def read(self):
        if self.line_pos >= self.line_len:
            self.readline()
        self.line_pos += 1
        if self.line_pos >= self.line_len:
            return -1
        return self.line[self.line_pos]

    def readline(self):
        self.line = self.code_input.readline()
        self.line_len = len(self.line)
        self.line_pos = -1
        self.lineno += 1
        if self.lineno != 1:
            self.log('', end='\n')
        self.log("line %d: " % self.lineno)

    def log(self, msg, end=' '):
        print(msg, end=end)
        self.output += (msg + end)

    def pre_end(self, c):
        if Lexer.is_digit(c):
            self.log("<num," + c + ">")
        elif Lexer.is_alpha(c) or c == "_":
            self.log("<id," + c + ">")
        else:
            self.log("<" + c + ">")

    def analyse(self):
        self.symbol_table = set()
        self.readline()
        c = self.read()
        if c == -1:
            return
        while c != -1:
            if c == '\uFFFF':
                break
            valid = False
            while not valid:
                if c == ' ' or c == '\t':
                    c = self.read()
                    if c == -1:
                        return
                elif c == '\n' or c == '\r':
                    self.readline()
                    c = self.read()
                    if c == -1:
                        return
                else:
                    valid = True
            if c == '-':
                c = self.read()
                if c == -1:
                    self.pre_end(c)
                    return
                if c == '-':
                    self.log("<-->")
                    c = self.read()
                elif c == '=':
                    self.log("<-=>")
                    c = self.read()
                else:
                    self.log("<->")
                valid = False
            elif c == '+':
                c = self.read()
                if c == -1:
                    self.pre_end(c)
                    return
                if c == '+':
                    self.log("<++>")
                    c = self.read()
                elif c == '=':
                    self.log("<+=>")
                    c = self.read()
                else:
                    self.log("<+>")
                valid = False
            elif c == '*':
                c = self.read()
                if c == -1:
                    self.pre_end(c)
                    return
                elif c == '=':
                    self.log("<*=>")
                    c = self.read()
                else:
                    self.log("<*>")
                valid = False
            elif c == '/':
                c = self.read()
                if c == -1:
                    self.pre_end(c)
                    return
                elif c == '=':
                    self.log("</=>")
                    c = self.read()
                    if c == -1:
                        self.pre_end(c)
                        return
                elif c == '/':
                    self.readline()
                    c = self.read()
                    if c == -1:
                        self.pre_end(c)
                        return
                else:
                    self.log("</>")
                valid = False
            elif c == '|':
                c = self.read()
                if c == -1:
                    self.pre_end(c)
                    return
                if c == '|':
                    self.log("<||>")
                    c = self.read()
                    if c == -1:
                        self.pre_end(c)
                else:
                    self.log("<|>")
                valid = False
            elif c == '&':
                c = self.read()
                if c == -1:
                    self.pre_end(c)
                    return
                if c == '&':
                    self.log("<&&>")
                    c = self.read()
                    if c == -1:
                        self.pre_end(c)
                else:
                    self.log("<&>")
                valid = False
            elif c == '<':
                c = self.read()
                if c == -1:
                    self.pre_end(c)
                    return
                if c == '=':
                    self.log("<<=>")
                    c = self.read()
                    if c == -1:
                        self.pre_end(c)
                        return
                elif c == '>':
                    self.log("<<>>")
                    c = self.read()
                    if c == -1:
                        self.pre_end(c)
                        return
                elif c == '<':
                    self.log("<<<>")
                    c = self.read()
                    if c == -1:
                        self.pre_end(c)
                        return
                else:
                    self.log("<<>")
                valid = False
            elif c == '>':
                c = self.read()
                if c == -1:
                    self.pre_end(c)
                    return
                if c == '=':
                    self.log("<>=>")
                    c = self.read()
                    if c == -1:
                        self.pre_end(c)
                        return
                elif c == '>':
                    self.log("<>>>")
                    c = self.read()
                    if c == -1:
                        self.pre_end(c)
                        return
                else:
                    self.log("<<>")
            elif c == ':':
                c = self.read()
                if c == -1:
                    self.pre_end(c)
                    return
                if c == '=':
                    self.log("<:=>")
                    c = self.read()
                    if c == -1:
                        self.pre_end(c)
                        return
                else:
                    self.log('<:>')
                valid = False
            elif c == '"':
                t = "\""
                success = True
                while True:
                    c = self.read()
                    if c == -1:
                        self.log("error line %d: invalid string" % self.lineno)
                        return
                    if c == '\n':
                        self.log("error line %d: invalid string" % self.lineno)
                        self.readline()
                        success = False
                        break
                    elif c != '"':
                        t += c
                    else:
                        t += "\""
                        break
                if success:
                    self.log("<string, %s>" % t)
                c = self.read()
                if c == -1:
                    return
                valid = False
            elif c == '!':
                c = self.read()
                if c == -1:
                    self.pre_end(c)
                    return
                if c == '=':
                    self.log("<!=>")
                    c = self.read()
                    if c == -1:
                        self.pre_end(c)
                        return
                else:
                    self.log("<!>")
                valid = False
            elif c == '=':
                c = self.read()
                if c == -1:
                    self.pre_end(c)
                    return
                if c == '=':
                    self.log("<==>")
                    c = self.read()
                    if c == -1:
                        self.pre_end(c)
                        return
                else:
                    self.log("<=>")
                valid = False
            elif c in ';()[]{},^':
                self.log("<%c>" % c)
                c = self.read()
                if c == -1:
                    return
                valid = False
            else:
                pass
            if valid:
                if Lexer.is_digit(c):
                    success = True
                    ansNum = c
                    ansBase = 10
                    c = self.read()
                    if c == -1:
                        self.pre_end(c)
                        return
                    if ansNum == '0' and Lexer.is_Hex(c):
                        ansNum += c
                        ansBase = 16
                        c = self.read()
                    elif ansNum == '0' and Lexer.is_digit(c):
                        ansBase = 8
                    while c != -1:
                        if ansBase == 16 and (Lexer.is_digit(c) or 'a' < c < 'f' or 'A' < c < 'F'):
                            ansNum += c
                        elif ansBase == 10 and (Lexer.is_digit(c) or c == '.'):
                            ansNum += c
                        elif ansBase == 8 and (Lexer.is_digit(c) and '0' < c < '9'):
                            ansNum += c
                        else:
                            if Lexer.is_alpha(c):
                                success = False
                            break
                        c = self.read()
                    if not success:
                        self.log("error line %d: invalid number" % self.lineno)
                        self.readline()
                        c = self.read()
                        if c == -1:
                            return
                    elif c == -1:
                        self.pre_end(c)
                        return
                    elif '.' in ansNum and ansBase == 10:
                        ansNum = float(ansNum)
                        self.log("<float, %f>" % ansNum)
                    else:
                        ansNum = int(ansNum, ansBase)
                        self.log("<int, %d>" % ansNum)

                elif Lexer.is_alpha(c) or c == '_':
                    ans = c
                    c = self.read()
                    while c != -1 and (c == '_' or Lexer.is_digit(c) or Lexer.is_alpha(c)):
                        ans += c
                        c = self.read()
                    if c == -1:
                        self.pre_end(c)
                        return
                    ans = ans.lower()
                    if ans in self.words:
                        self.log("<%s>" % ans)
                    else:
                        self.symbol_table.add(ans)
                        self.log("<id, %s>" % ans)
                else:
                    self.log("error line %d: invalid identifier" % self.lineno)
                    self.readline()
                    c = self.read()
                    if c == -1:
                        return

    def parse(self):
        self.analyse()
        return {'output': self.output, 'symbol': ',\t'.join(self.words + list(self.symbol_table))}
        # print()
        # print(self.words, self.symbol_table)


if __name__ == '__main__':
    Lexer(open('code.mc', encoding='utf-8')).parse()
