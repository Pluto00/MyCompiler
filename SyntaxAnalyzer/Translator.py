class Attribute:
    def __init__(self, type="", value="", addr="null", trueList=None, falseList=None, instr=-1,
                 nextList=None, arrType=0, preList=None):
        if preList is None:
            preList = []
        self.type = type
        self.value = value
        self.addr = addr
        self.trueList = trueList
        self.falseList = falseList
        self.instr = instr
        self.nextList = nextList
        self.arrType = arrType
        self.preList = preList


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
        self.hasError = False

    def shift_process(self, tok):
        if tok.name != 'id' and tok.name != 'float' and tok.name != 'integer':
            self.attributes.append(Attribute(tok.value, tok.value))
        else:
            self.attributes.append(Attribute(tok.name, tok.value))

    def reduce_process(self, b, p):
        left = p.head
        right = ' '.join(p.body)
        eval("self.action{}(left, right)".format(b))

    def action0(left, right):
        pass

    def action1(self, left, right):
        # S -> program id stmts
        right = len(right.split(" "))
        for i in range(right):
            self.attributes.pop()
        self.attributes.append(Attribute(left, "null", "null"))

    def action2(self, left, right):
        # stmts -> { stmt M }
        self.attributes.pop()
        M = self.attributes.pop().instr
        stmts = self.attributes.pop().nextList
        self.attributes.pop()
        self.backpatch(stmts, M)
        self.attributes.append(Attribute(left, "null", "null"))

    def action3(self, left, right):
        # stmt -> stmts
        stmts = self.attributes.pop().nextList
        self.attributes.append(Attribute(left, "null", "null", nextList=stmts))

    def action4(self, left, right):
        # stmt -> stmt M stmts
        stmts = self.attributes.pop().nextList
        M = self.attributes.pop().instr
        stmt = self.attributes.pop().nextList
        self.backpatch(stmt, M)
        self.attributes.append(Attribute(left, "null", "null", nextList=stmts))

    def action5(self, left, right):
        # stmts -> id = expr ;
        self.attributes.pop()
        expr = self.attributes.pop().addr
        self.attributes.pop()
        ids = self.attributes.pop().value
        self.attributes.append(Attribute(left, "null", ids))
        self.codes.append(Code("=", expr, "null", ids))

    def action6(self, left, right):
        # stmts -> id := expr ;
        self.action5(left, right)

    def action7(self, left, right):
        # stmts -> L = expr ;
        self.attributes.pop()
        expr = self.attributes.pop().addr
        self.attributes.pop()
        ids = self.attributes[-1].addr
        array = self.attributes.pop().value
        self.attributes.append(Attribute(left, "null", ids))
        self.codes.append(Code("[]=", ids, expr, array))

    def action8(self, left, right):
        # stmts -> id += expr ;
        self.attributes.pop()
        expr = self.attributes.pop().addr
        op = self.attributes.pop().type
        ids = self.attributes.pop().value
        self.attributes.append(Attribute(left, "null", ids))
        self.codes.append(Code(op, ids, expr, ids))

    def action9(self, left, right):
        # stmts -> id -= expr
        self.action8(left, right)

    def action10(self, left, right):
        # stmts -> id *= expr
        self.action8(left, right)

    def action11(self, left, right):
        # stmts -> id /= expr
        self.action8(left, right)

    def action12(self, left, right):
        # stmts -> if ( bool )  M stmts N else M stmts
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
        self.backpatch(B.trueList, M1.instr)
        self.backpatch(B.falseList, M2.instr)
        nextList = self.merge(stmt1.nextList, N.nextList)
        nextList = self.merge(nextList, stmt2.nextList)
        self.attributes.append(Attribute(left, "null", "null", None, None, -1, nextList))

    def action13(self, left, right):
        # stmts -> if ( bool ) M stmts
        stmt1 = self.attributes.pop()
        M = self.attributes.pop()
        self.attributes.pop()
        B = self.attributes.pop()
        self.attributes.pop()
        self.attributes.pop()
        self.backpatch(B.trueList, M.instr)
        nextList = self.merge(B.falseList, stmt1.nextList)
        self.attributes.append(Attribute(left, "null", "null", None, None, -1, nextList))

    def action14(self, left, right):
        # while_stmt -> while M ( bool ) M stmts
        stmt = self.attributes.pop().nextList
        M2 = self.attributes.pop().instr
        self.attributes.pop()
        trueList = self.attributes[-1].trueList
        falseList = self.attributes.pop().falseList
        self.attributes.pop()
        M1 = self.attributes.pop().instr
        self.attributes.pop()
        self.backpatch(stmt, M1)
        self.backpatch(trueList, M2)
        self.attributes.append(Attribute(left, "null", "null", None, None, -1, falseList))
        self.codes.append(Code("goto", "null", "null", str(M1 + 100)))

    def action15(self, left, right):
        # bool -> bool || M bool
        B2 = self.attributes.pop()
        M = self.attributes.pop()
        self.attributes.pop()
        B1 = self.attributes.pop()
        self.backpatch(B1.falseList, M.instr)
        trueList = self.merge(B1.trueList, B2.trueList)
        self.attributes.append(Attribute(left, "null", "null", trueList, B2.falseList, -1))

    def action16(self, left, right):
        # bool -> bool && M bool
        B2 = self.attributes.pop()
        M = self.attributes.pop()
        self.attributes.pop()
        B1 = self.attributes.pop()
        self.backpatch(B1.trueList, M.instr)
        falseList = self.merge(B1.falseList, B2.falseList)
        self.attributes.append(Attribute(left, "null", "null", B2.trueList, falseList, -1))

    def action17(self, left, right):
        # bool -> ! bool
        B1 = self.attributes.pop()
        trueList = B1.falseList
        falseList = B1.trueList
        self.attributes.append(Attribute(left, "null", "null", trueList, falseList, -1))

    def action18(self, left, right):
        # bool -> expr NE|LEQ|<|LE|>|GE expr```
        expr2 = self.attributes.pop().addr
        op = self.attributes.pop().type
        expr1 = self.attributes.pop().addr
        trueList = []
        trueList.append(len(self.codes))
        falseList = []
        falseList.append(len(self.codes) + 1)
        self.attributes.append(Attribute(left, "null", "null", trueList, falseList))
        self.codes.append(Code(op, expr1, expr2, "_"))
        self.codes.append(Code("goto", "null", "null", "_"))

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
        # expr -> expr +|-|*|/|êxpr
        factor = self.attributes.pop().addr
        op = self.attributes.pop().type
        term1 = self.attributes.pop().addr
        term = self.get_temp()
        self.attributes.append(Attribute(left, "null", term))
        self.codes.append(Code(op, term1, factor, term))

    def action25(self, left, right):
        self.action24(left, right)

    def action26(self, left, right):
        self.action24(left, right)

    def action27(self, left, right):
        self.action24(left, right)

    def action28(self, left, right):
        self.action24(left, right)

    def action29(self, left, right):
        # expr -> factor
        tmp = self.attributes[-1].addr
        self.attributes.pop()
        self.attributes.append(Attribute(left, "null", tmp))

    def action30(self, left, right):
        # factor -> id | number
        tmp = self.attributes[-1].value
        self.attributes.pop()
        self.attributes.append(Attribute(left, "null", tmp))

    def action31(self, left, right):
        # factor -> id | number
        self.action30(left, right)

    def action32(self, left, right):
        # factor -> ( expr )
        self.attributes.pop()
        expr = self.attributes.pop().addr
        self.attributes.pop()
        self.attributes.append(Attribute(left, "null", expr))

    def action33(self, left, right):
        # M -> <empty>
        self.attributes.append(Attribute(left, "null", "null", None, None, len(self.codes)))

    def action34(self, left, right):
        # N -> <empty>
        nextList = []
        nextList.append(len(self.codes))
        self.attributes.append(Attribute(left, "null", "null", None, None, -1, nextList))
        self.codes.append(Code("goto", "null", "null", "_"))

    def action35(self, left, right):
        # expr -> L
        term = self.get_temp()
        L = self.attributes[-1].addr
        ids = self.attributes.pop().value
        self.attributes.append(Attribute(left, ids, term))
        self.codes.append(Code("=[]", ids, L, term))

    def action36(self, left, right):
        # L -> id [ expr ]
        self.attributes.pop()
        expr = self.attributes.pop()
        self.attributes.pop()
        ids = self.attributes.pop()
        addr = self.get_temp()
        code = Code("*", expr.addr, 4, addr)
        preList = []
        preList.append(code)
        self.attributes.append(Attribute(left, ids, addr, arrType=1, preList=preList))
        self.codes.append(code)

    def action37(self, left, right):
        # L -> L [ expr ]
        self.attributes.pop()
        expr = self.attributes.pop()
        self.attributes.pop()
        L1 = self.attributes.pop()
        t = self.get_temp()
        addr = self.get_temp()
        arrType = -1
        code = Code("*", expr.addr, 4, t)
        preList = []
        if L1.arrType == 1:
            preList = L1.preList
            preList[0].arg2 = 80
            preList.append(code)
            arrType = 2
        elif L1.arrType == 2:
            arrType = 3
            preList = L1.preList
            preList[0].arg2 = 2400
            preList[1].arg2 = 120
            preList.append(code)

        else:
            arrType = 4
            preList = L1.preList
            if not self.hasError:
                # err = error('不支持更高维的数组')
                hasError = True
        sym = Attribute(left, L1.value, addr, arrType=arrType, preList=preList)
        # print(sym.arrType)
        self.attributes.append(sym)
        self.codes.append(code)
        self.codes.append(Code("+", L1.addr, t, addr))

    def action38(self, left, right):
        pass

    def action39(self, left, right):
        pass

    def backpatch(self, lists, m):
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
