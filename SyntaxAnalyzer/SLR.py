from Production import ProductionItem, ProductionRule
from Grammar import Grammar
from Lexer import Lexer
from itertools import chain
from Translator import Translator
import xlwt


class SLRTable:
    def __init__(self, grammar_file_path='resource/grammar.txt', lexer=None, debug=False):
        if lexer is None:
            lexer = Lexer()
        self.lexer = lexer
        self.G = Grammar(grammar_file_path)
        self.states = []  # 构造SLR自动机状态集合
        self.action = []
        self.goto = []
        self.__terminals = list(self.G.terminals)
        self.__non_terminals = list(self.G.non_terminals)

        self.__init_states__()
        self.__init_analysis_table__()

        if debug:
            self.print_states()
            self.save_info_to_excel()

    def __closure(self, I):  # 计算项目集I的闭包
        J = I
        for item in J:  # 遍历项目集中的每一个项目
            if item.dot != len(item.body):  # 表示·不是在最后
                next_dot = item.body[item.dot]  # dot 后面的符号
                if next_dot in self.__non_terminals:
                    for p in self.G.production_table[item.body[item.dot]]:
                        new_item = ProductionItem(p.head, p.body)
                        if new_item not in J:
                            J.append(new_item)
        return J

    def __goto(self, I, x):  # 返回项目集I对应于文法符号X的后继项目集闭包
        J = []
        for item in I:
            if item.dot != len(item.body):
                if x == item.body[item.dot]:
                    obj = ProductionItem(item.head, item.body, item.dot + 1)
                    J.append(obj)
        return self.__closure(J)

    def __init_states__(self):  # 初始化 SLR 自动机状态集合
        self.states = [self.__closure([ProductionItem(self.G.start.head, self.G.start.body)])]
        for states in self.states:
            for x in chain(self.__terminals, self.__non_terminals):
                result = self.__goto(states, x)
                if len(result) > 0 and result not in self.states:
                    self.states.append(result)

    def __init_analysis_table__(self):
        st = 0
        self.action = []  # action集合,可以看作二维数组,如果每个元素也是一个数组,如果数组中没有元素则表示没有对应项目,
        # 可以是rn,sn,n,acc,如果数组中存在多个元素表示有冲突
        # 初始化 action 和 goto 表
        len_states = len(self.states)  # 状态集个数
        len_terminals = len(self.__terminals)  # 终结符个数
        for _ in range(len_states):
            temp = []
            for _ in range(len_terminals):
                temp.append([])
            self.action.append(temp)

        len_non_terminals = len(self.__non_terminals)  # 非终结符个数
        self.goto = []  # goto 集合
        for _ in range(len_states):
            temp = []
            for _ in range(len_non_terminals):
                temp.append([])
            self.goto.append(temp)
        # 开始计算预测分析表
        for state in self.states:  # state 表示项目集闭包
            for item in state:  # item 表示项目集中的每个项目
                if item.dot != len(item.body) and item.body[0] != 'ε':  # 表示非归约状态
                    x = item.body[item.dot]
                    state_x = self.__goto(state, x)
                    if x in self.__terminals:  # x 是终结符, 加入到 self.action 表
                        self.action[st][self.__terminals.index(x)].append('s' + str(self.states.index(state_x)))
                    else:  # 加入到 self.goto 表
                        self.goto[st][self.__non_terminals.index(x)].append(str(self.states.index(state_x)))
                else:  # 归约项目或者接收项目
                    temp_p = ProductionRule(item.head, item.body)
                    if temp_p == self.G.start:
                        self.action[st][self.__terminals.index("$")].append("acc")
                    else:
                        pid = self.G.production_list.index(temp_p)
                        for f in self.G.follow_table[item.head]:
                            self.action[st][self.__terminals.index(f)].append('r' + str(pid))
            st += 1

    def __solve_r_s(self, op1, x1, op2, x2):
        reduce = op1 if op1[0] == 'r' else op2
        shift = op1 if op1[0] == 's' else op2
        if x1 in ['-', '+'] and x2 in ['-', '+']:
            return reduce
        if x1 in ['*', '/'] and x2 in ['*', '/']:
            return reduce
        else:
            if self.__terminals.index(x1) < self.__terminals.index(x2):
                return shift
            else:
                return reduce

        # op_list = ['^', '*', '/', '+', '-', 'else', 'Stmts']
        # return x1 in op_list and x2 in op_list and op_list.index(x1) < op_list.index(x2)
        # return x1 in self.__terminals and x2 in self.__terminals and self.__terminals.index(
        #     x1) < self.__terminals.index(x2)

    def analyze(self, code_file, translate=False):
        result = {'stack': [], 'input': [], 'operations': [], 'matched': [[]]}  # 输出
        if type(code_file) == str:
            code_file = open(code_file, encoding='utf-8')
        self.lexer.parse(code_file)  # 调用词法分析器分析代码文件，获取词法单元
        top = 0
        w = []
        tokens = []
        for token in self.lexer.tokens:  # 解析词法单元
            if token.get():
                w.append(token.get())
                tokens.append(token)
        translator = Translator() if translate else None
        w.append('$')  # 加入终止符
        tokens.append(None)
        w_top = w[top]
        token_top = tokens[top]
        vt = self.__terminals  # 终结符列表
        vn = self.__non_terminals  # 非终结符列表
        action = self.action  # ACTION 表
        goto = self.goto  # GOTO 表
        status_stack = [0]  # 状态栈
        has_error = False
        while True:
            try:
                s = status_stack[-1]  # 获取栈顶
                ops = action[s][vt.index(w_top)]
                op = ops[0]
                if len(ops) >= 2:
                    for _op in ops:
                        if op[0] == 'r' and _op[0] == 'r':  # 规约-规约冲突
                            if int(_op[1:]) > int(op[1:]):
                                op = _op
                        elif (op[0] == 'r' and _op[0] == 's') or (op[0] == 's' and _op[0] == 'r'):  # 规约-移入冲突
                            p = self.G.production_list[int(op[1:])]
                            for x in p.body:
                                if x in self.__terminals:
                                    ret = self.__solve_r_s(op, w_top, _op, x)
                                    if ret:
                                        op = ret
                                    break

                # 记录分析过程
                result['stack'].append(s)
                result['operations'].append(op)
                result['input'].append(w_top)
                result['matched'].append(result['matched'][-1].copy())
                if "s" in op:  # 移入
                    status_stack.append(int(op[1:]))  # 状态入栈
                    result['matched'][-1].append(w_top)
                    if translate:
                        translator.shift_process(token_top)
                    top += 1
                    w_top = w[top]
                    token_top = tokens[top]
                elif 'r' in op:  # 规约
                    b = int(op[1:])
                    p = self.G.production_list[b]  # 选择归于的产生式
                    if p.body[0] != 'ε':
                        for i in range(len(p.body)):
                            status_stack.pop()
                            result['matched'][-1].pop()  # 状态出栈
                    if translate:
                        translator.reduce_process(b, p)
                    c = vn.index(p.head)
                    s = status_stack[-1]
                    status_stack.append(int(goto[s][c][0]))  # 状态入栈
                    result['matched'][-1].append(p.head)  # 记录匹配记过
                    # print(p)
                elif op == "acc":  # 接受
                    result['matched'][-1] = ['S\'']
                    break
                else:
                    result['matched'][-1] = ["语法分析错误，终止分析过程"]  # 发生错误，终止分析
                    break
            except Exception as e:  # 检测异常
                print(e)
                has_error = True
                result['stack'].append(status_stack[-1])
                result['operations'].append('err')
                result['input'].append(w_top)
                result['matched'].append(["语法分析错误，终止分析过程"])
                print(result)
                break
        if translate:
            if has_error:
                return "代码存在语法错误，请检查"
            return translator.gen_code()
        return result

    def print_states(self):
        for i, state in enumerate(self.states):
            print(i)
            for s in state:
                print(s)

    def save_info_to_excel(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('lr0 状态机')
        len_terminals = len(self.__terminals)
        len_non_terminals = len(self.__non_terminals)
        for i in range(len(self.G.production_list)):
            worksheet.write(i, 0, label=str(self.G.production_list[i]))
        for i, state in enumerate(self.states):
            worksheet.write(i, 5, label='; '.join([str(s) for s in state]))
        worksheet = workbook.add_sheet('预测分析表')

        for i in range(len_terminals):
            worksheet.write(0, i, label=self.__terminals[i])
        for i in range(len_non_terminals):
            worksheet.write(0, i + len_terminals, label=self.__non_terminals[i])
        for i in range(len(self.action)):
            for j in range(len_terminals):
                worksheet.write(i + 1, j, label=','.join(list(set(self.action[i][j]))))
            for j in range(len_non_terminals):
                worksheet.write(i + 1, j + len_terminals, label=','.join(list(set(self.goto[i][j]))))
        workbook.save('resource/debug_info.xls')


if __name__ == '__main__':
    slr = SLRTable('resource/grammar.txt', debug=True)
    res = slr.analyze('resource/code2.mc')
    print("输出结果")
    print("%-16s %-16s %-16s %-16s" % tuple(res.keys()))
    l = len(res['stack'])
    for i in range(l):
        print("%-16s %-16s %-16s" % (res['stack'][i], res['input'][i], res['operations'][i]),
              ' '.join(res['matched'][i + 1]))
