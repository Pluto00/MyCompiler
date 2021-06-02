from .Utils import Utils


class Lexer:
    """
    词法分析器，读取代码文件输出，解析此词法单元
    """

    def __init__(self):
        self.code_input = None
        self.lineno = 0
        self.line = None
        self.line_len = None
        self.line_pos = None
        self.tokens = []  # 保存解析到的词法单元

    def read(self):  # 读取下一个字符
        if self.line_pos >= self.line_len:
            self.readline()
        self.line_pos += 1
        if self.line_pos >= self.line_len:
            return -1
        return self.line[self.line_pos]

    def readline(self):  # 读取下一行
        self.line = self.code_input.readline()
        self.line_len = len(self.line)
        self.line_pos = -1
        self.lineno += 1
        self.tokens.append(Utils.GetLineFeedElement())

    def pre_end(self, c):  # 预读终止
        if not c:
            return
        if Utils.is_digit(c):
            ele = Utils.StringToIntegerLiteral(c)
        elif Utils.is_alpha(c) or c == "_":
            ele = Utils.StringToIdentifierElement(c)
        else:
            ele = Utils.StringToNonWordMap.get(c)
        if ele:
            self.tokens.append(ele)

    def pre_read(self, c=None):  # 预读下一个字符
        ta = self.read()
        if ta == -1:
            self.pre_end(c)
        return ta

    def __match_non_word__(self, cur, forward):  # 匹配非关键字
        c = self.pre_read(cur)
        if c == -1:
            return c
        if c in forward:
            cur += c
            c = self.pre_read()
        if cur == '//':  # 处理注释
            self.readline()
            c = self.pre_read()
        else:
            self.tokens.append(Utils.StringToNonWordMap[cur])
        return c

    def __match_string__(self):  # 匹配字符串
        t = ""
        success = True
        while True:
            c = self.read()
            if c == -1 or c == '\n':  # 错误，读入下一行
                self.tokens.append(Utils.GetErrorElement(self.lineno, "invalid string"))
                self.readline()
                success = False
                break
            if c != '"':
                t += c
            else:
                break
        if success:
            self.tokens.append(Utils.StringToStringLiteral(t))
        return self.pre_read()

    def __match_number__(self, c):  # 匹配数字
        success = True
        num = c
        base = 10
        c = self.pre_read(c)
        if c == -1:
            return c
        if num == '0' and Utils.is_Hex(c):
            num += c
            base = 16
            c = self.read()
        elif num == '0' and Utils.is_digit(c):
            base = 8
        while c != -1:
            if base == 16 and (Utils.is_digit(c) or 'a' < c < 'f' or 'A' < c < 'F'):
                num += c
            elif base == 10 and (Utils.is_digit(c) or c == '.'):
                num += c
            elif base == 8 and (Utils.is_digit(c) and '0' < c < '9'):
                num += c
            else:
                if Utils.is_alpha(c):
                    success = False
                break
            c = self.pre_read()
        if not success:
            self.tokens.append(Utils.GetErrorElement(self.lineno, "invalid number"))
            self.readline()
            return self.pre_read()
        if '.' in num and base == 10:  # 小数
            self.tokens.append(Utils.StringToFloatLiteral(num))
        else:  # 整数
            self.tokens.append(Utils.StringToIntegerLiteral(num, base))
        return c

    def __match__identifier__(self, c):  # 匹配标识符（也有可能是关键字）
        ans = c
        c = self.pre_read()
        while c != -1 and (c == '_' or Utils.is_digit(c) or Utils.is_alpha(c)):
            ans += c
            c = self.pre_read(ans)
        if c == -1:
            return c
        if c in "$@~":  # 不会出现在标识符后面的字符
            self.tokens.append(Utils.GetErrorElement(self.lineno, "invalid identifier"))
        else:
            ans = ans.lower()
            self.tokens.append(Utils.StringToKeyWordMap.get(ans) or Utils.StringToIdentifierElement(ans))
        return c

    def analyse(self):  # 词法分析过程
        c = self.read()
        while c != -1:
            while True:  # 处理非法字符，空白和换行
                if c == '\uFFFF':  # INVALID CHARACTER
                    return
                elif c == ' ' or c == '\t':  # 空白，跳过
                    pass
                elif c == '\n' or c == '\r':  # 换行，读入下一行
                    self.readline()
                else:  # 其他的字符进入匹配
                    valid = True
                    break
                c = self.read()
                if c == -1:
                    return
            if c == '-':
                c = self.__match_non_word__(c, ['-', '='])
                if c == -1:
                    return
                valid = False
            elif c == '+':
                c = self.__match_non_word__(c, ['+', '='])
                if c == -1:
                    return
                valid = False
            elif c == '*':
                c = self.__match_non_word__(c, ['='])
                if c == -1:
                    return
                valid = False
            elif c == '/':
                c = self.__match_non_word__(c, ['=', '/'])
                if c == -1:
                    return
                valid = False
            elif c == '|':
                c = self.__match_non_word__(c, ['|'])
                if c == -1:
                    return
                valid = False
            elif c == '&':
                c = self.__match_non_word__(c, ['&'])
                if c == -1:
                    return
                valid = False
            elif c == '<':
                c = self.__match_non_word__(c, ['=', '>', '<'])
                if c == -1:
                    return
                valid = False
            elif c == '>':
                c = self.__match_non_word__(c, ['=', '>'])
                if c == -1:
                    return
                valid = False
            elif c == ':':
                c = self.__match_non_word__(c, ['='])
                if c == -1:
                    return
                valid = False
            elif c == '!':
                c = self.__match_non_word__(c, ['='])
                if c == -1:
                    return
                valid = False
            elif c == '=':
                c = self.__match_non_word__(c, ['='])
                if c == -1:
                    return
                valid = False
            elif c in ';()[]{},^':
                c = self.__match_non_word__(c, [])
                if c == -1:
                    return
                valid = False
            elif c == '"':
                c = self.__match_string__()
                if c == -1:
                    return
                valid = False
            if valid:
                if Utils.is_digit(c):
                    c = self.__match_number__(c)
                    if c == -1:
                        return
                elif Utils.is_alpha(c) or c == '_':
                    c = self.__match__identifier__(c)
                    if c == -1:
                        return
                else:
                    self.tokens.append(Utils.GetErrorElement(self.lineno, "invalid identifier"))
                    self.readline()
                    c = self.pre_read()
                    if c == -1:
                        return c

    def parse(self, code_file):  # 杜文文件输入
        # 初始化参数
        self.code_input = code_file
        self.lineno = 0
        self.readline()
        self.tokens = []
        # 开始分析
        self.analyse()
        # 返回解析结果
        return Utils.ParseTokens(self.tokens)


if __name__ == '__main__':
    lex = Lexer()
    print(lex.parse(open('../code.mc', encoding='utf-8')))
