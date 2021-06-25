class Attribute:
    def __init__(self, type="", value="", addr="null", true_list=None, false_list=None, instr=-1,
                 next_list=None, array_depth=0, pre_list=None):
        if pre_list is None:
            pre_list = []
        self.type = type
        self.value = value
        self.addr = addr
        self.true_list = true_list
        self.false_list = false_list
        self.instr = instr
        self.next_list = next_list
        self.array_depth = array_depth
        self.pre_list = pre_list


class Code:
    def __init__(self, op, arg1, arg2, result):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result


class Translator:
    def __init__(self):
        self.attributes = []
        self.codes = []
        self.temp_number = 1

    def shift_process(self, tok):
        if tok.name != 'id' and tok.name != 'float' and tok.name != 'integer':
            self.attributes.append(Attribute(tok.value, tok.value))
        else:
            self.attributes.append(Attribute(tok.name, tok.value))

    def reduce_process(self, b, p):
        left = p.head
        right = p.body
        getattr(self, 'action' + str(b))(left, right)

    def action0(self, left, right):
        # S' -> S
        pass

    def action1(self, left, right):
        # S -> program id S
        for i in range(len(right)):
            self.attributes.pop()
        self.attributes.append(Attribute(left, "null", "null"))

    def action2(self, left, right):
        # S -> { L M }
        self.attributes.pop()
        M = self.attributes.pop()
        L = self.attributes.pop()
        self.attributes.pop()
        self.back_patch(L.next_list, M.instr)
        self.attributes.append(Attribute(left, "null", "null"))

    def action3(self, left, right):
        # L -> S
        S = self.attributes.pop()
        self.attributes.append(Attribute(left, "null", "null", next_list=S.next_list))

    def action4(self, left, right):
        # L -> L M S
        S = self.attributes.pop()
        M = self.attributes.pop()
        L = self.attributes.pop()
        self.back_patch(L.next_list, M.instr)
        self.attributes.append(Attribute(left, "null", "null", next_list=S.next_list))

    def action5(self, left, right):
        # S -> id =|:= E ;
        self.attributes.pop()
        E = self.attributes.pop()
        self.attributes.pop()
        ids = self.attributes.pop()
        self.attributes.append(Attribute(left, "null", ids.value))
        self.codes.append(Code("=", E.addr, "null", ids.value))

    def action6(self, left, right):
        self.action5(left, right)

    def action7(self, left, right):
        # S -> Arr = E ;
        self.attributes.pop()
        E = self.attributes.pop()
        self.attributes.pop()
        Arr = self.attributes.pop()
        addr = Arr.addr  # 数组的地址
        array = Arr.value  # 数组的标识符
        self.attributes.append(Attribute(left, "null", addr))
        self.codes.append(Code("[]=", addr, E.addr, array))

    def action8(self, left, right):
        # S -> id +=|-=|*=|/= E ;
        self.attributes.pop()
        E = self.attributes.pop()
        op = self.attributes.pop().type
        ids = self.attributes.pop()
        self.attributes.append(Attribute(left, "null", ids.value))
        self.codes.append(Code(op, ids, E.addr, ids.value))

    def action9(self, left, right):
        self.action8(left, right)

    def action10(self, left, right):
        self.action8(left, right)

    def action11(self, left, right):
        self.action8(left, right)

    def action12(self, left, right):
        # S -> if ( B ) M S N else M S
        stmt2 = self.attributes.pop()
        M2 = self.attributes.pop()
        self.attributes.pop()
        N = self.attributes.pop()
        stmt1 = self.attributes.pop()
        M1 = self.attributes.pop()
        self.attributes.pop()
        B = self.attributes[-1]
        self.attributes.pop()
        self.attributes.pop()
        self.back_patch(B.true_list, M1.instr)
        self.back_patch(B.false_list, M2.instr)
        next_list = self.merge(stmt1.next_list, N.next_list)
        next_list = self.merge(next_list, stmt2.next_list)
        self.attributes.append(Attribute(left, "null", "null", None, None, -1, next_list))

    def action13(self, left, right):
        # S -> if ( B ) M S
        S = self.attributes.pop()
        M = self.attributes.pop()
        self.attributes.pop()
        B = self.attributes.pop()
        self.attributes.pop()
        self.attributes.pop()
        self.back_patch(B.true_list, M.instr)
        next_list = self.merge(B.false_list, S.next_list)
        self.attributes.append(Attribute(left, "null", "null", None, None, -1, next_list))

    def action14(self, left, right):
        # L -> while M ( B ) M S
        S = self.attributes.pop()
        M2 = self.attributes.pop().instr
        self.attributes.pop()
        B = self.attributes.pop()
        self.attributes.pop()
        M1 = self.attributes.pop().instr
        self.attributes.pop()
        self.back_patch(S.next_list, M1)
        self.back_patch(B.true_list, M2)
        self.attributes.append(Attribute(left, "null", "null", None, None, -1, B.false_list))
        self.codes.append(Code("goto", "null", "null", str(M1 + 100)))

    def action15(self, left, right):
        # B -> B || M B
        B2 = self.attributes.pop()
        M = self.attributes.pop()
        self.attributes.pop()
        B1 = self.attributes.pop()
        self.back_patch(B1.false_list, M.instr)
        true_list = self.merge(B1.true_list, B2.true_list)
        self.attributes.append(Attribute(left, "null", "null", true_list, B2.false_list, -1))

    def action16(self, left, right):
        # B -> B && M B
        B2 = self.attributes.pop()
        M = self.attributes.pop()
        self.attributes.pop()
        B1 = self.attributes.pop()
        self.back_patch(B1.true_list, M.instr)
        false_list = self.merge(B1.false_list, B2.false_list)
        self.attributes.append(Attribute(left, "null", "null", B2.true_list, false_list, -1))

    def action17(self, left, right):
        # B -> ! B
        B1 = self.attributes.pop()
        self.attributes.append(Attribute(left, "null", "null", B1.true_list, B1.false_list, -1))

    def action18(self, left, right):
        # B -> E !=|==|<=|<|>|>= E
        E2 = self.attributes.pop().addr
        op = self.attributes.pop().type
        E1 = self.attributes.pop().addr
        true_list = [len(self.codes)]
        false_list = [len(self.codes) + 1]
        self.attributes.append(Attribute(left, "null", "null", true_list, false_list))
        self.codes.append(Code(op, E1, E2, "_"))  # true_list: if ( expr1 REL expr2 ) goto _
        self.codes.append(Code("goto", "null", "null", "_"))  # false_list: goto _

    def action19(self, left, right):
        self.action18(left, right)

    def action20(self, left, right):
        self.action18(left, right)

    def action21(self, left, right):
        self.action18(left, right)

    def action22(self, left, right):
        self.action18(left, right)

    def action23(self, left, right):
        self.action18(left, right)

    def action24(self, left, right):
        # E -> E +|-|*|/|^ E
        E2 = self.attributes.pop()
        op = self.attributes.pop().type
        E1 = self.attributes.pop()
        tmp = self.get_temp()
        self.attributes.append(Attribute(left, "null", addr=tmp))
        self.codes.append(Code(op, E1.addr, E2.addr, tmp))

    def action25(self, left, right):
        self.action24(left, right)

    def action26(self, left, right):
        self.action24(left, right)

    def action27(self, left, right):
        self.action24(left, right)

    def action28(self, left, right):
        self.action24(left, right)

    def action29(self, left, right):
        # E -> F
        F = self.attributes.pop()
        self.attributes.append(Attribute(left, "null", addr=F.addr))

    def action30(self, left, right):
        # F -> id
        ids = self.attributes.pop()
        self.attributes.append(Attribute(left, "null", addr=ids.value))

    def action31(self, left, right):
        # F -> Num
        self.action30(left, right)

    def action32(self, left, right):
        # F -> ( E )
        self.attributes.pop()
        E = self.attributes.pop()
        self.attributes.pop()
        self.attributes.append(Attribute(left, "null", addr=E.addr))

    def action33(self, left, right):
        # M -> ε
        # 生成下一条指令的序号，放在综合属性 instr 中
        self.attributes.append(Attribute(left, "null", instr=len(self.codes)))

    def action34(self, left, right):
        # N -> ε
        next_list = [len(self.codes)]
        self.attributes.append(Attribute(left, "null", next_list=next_list))
        self.codes.append(Code("goto", "null", "null", "_"))

    def action35(self, left, right):
        # E -> Arr
        tmp = self.get_temp()
        Arr = self.attributes.pop()
        addr = Arr.addr  # 数组的地址
        ids = Arr.value  # 数组的标识符
        self.attributes.append(Attribute(left, ids, tmp))
        self.codes.append(Code("=[]", ids, addr, tmp))  # tmp = ids[addr]

    def action36(self, left, right):
        # Arr -> id [ E ]
        self.attributes.pop()
        E = self.attributes.pop()
        self.attributes.pop()
        ids = self.attributes.pop()
        addr = self.get_temp()
        code = Code("*", E.addr, 4, addr)
        pre_list = [code]
        self.attributes.append(Attribute(left, ids, addr, array_depth=1, pre_list=pre_list))
        self.codes.append(code)

    def action37(self, left, right):
        # Arr -> Arr [ E ]
        self.attributes.pop()
        E = self.attributes.pop()
        self.attributes.pop()
        Arr = self.attributes.pop()
        t = self.get_temp()
        addr = self.get_temp()
        code = Code("*", E.addr, 4, t)
        default_len = [i * 10 for i in range(1, 9)]  # 默认数组维度 int [10][20][30][40][50]...
        current_width = default_len[Arr.array_depth]
        # l * 4
        # k * 4 * 40
        # j * 4 * 30 * 40
        # i * 4 * 20 * 30 * 40
        for pl in Arr.pre_list:
            pl.arg2 *= current_width
        pre_list = Arr.pre_list + [code]
        self.attributes.append(Attribute(left, Arr.value, addr, array_depth=Arr.array_depth + 1, pre_list=pre_list))
        self.codes.append(code)
        self.codes.append(Code("+", Arr.addr, t, addr))

    def action38(self, left, right):
        # Num -> integer
        pass

    def action39(self, left, right):
        # Num -> float
        pass

    def back_patch(self, lists, m):
        if lists is not None and len(lists) != 0:
            for i in lists:
                self.codes[i].result = int(m + 100)

    def get_temp(self):
        ret = "t" + str(self.temp_number)
        self.temp_number += 1
        return ret

    def merge(self, list1, list2):
        if list1 is None:
            return list2
        if list2 is None:
            return list1
        return list1 + list2

    def gen_code(self):
        res = []
        addr = 0
        for i in range(len(self.codes)):
            s = ""
            x = self.codes[i]
            addr = i + 100
            if isinstance(x.result, Attribute):
                x.result = x.result.value
            if isinstance(x.arg1, Attribute):
                x.arg1 = x.arg1.value
            if isinstance(x.arg2, Attribute):
                x.arg2 = x.arg2.value
            if x.op == "+" or x.op == "-" or x.op == "*" or x.op == "/" or x.op == "^":
                s = s + str(x.result) + " = " + str(x.arg1) + " " + x.op + " " + str(x.arg2)
            elif x.op == "=":
                s = s + str(x.result) + " = " + str(x.arg1)
            elif x.op == "+=" or x.op == "-=" or x.op == "*=" or x.op == "/=":
                h = x.op
                op1 = h[0] + ""
                s = s + str(x.result) + " = " + str(x.arg1) + op1 + str(x.arg2)
            elif x.op == "[]=":
                s = s + str(x.result) + "[" + str(x.arg1) + "] = " + str(x.arg2)
            elif x.op == "=[]":
                s = s + str(x.result) + " = " + str(x.arg1) + "[" + str(x.arg2) + "]"
            elif x.op == "<" or x.op == ">" or x.op == "<=" or x.op == ">=" or x.op == "==" or x.op == "!=":
                s = s + "if (" + str(x.arg1) + " " + x.op + " " + str(x.arg2) + ") goto " + str(x.result)
            elif x.op == "goto":
                s = s + "goto " + str(x.result)
            else:
                continue
            res.append("{}: {}".format(addr, s))
        res.append("{}: ".format(addr + 1))
        return '\n'.join(res)
