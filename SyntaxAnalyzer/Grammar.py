from Lexer import LexerUtils
from Production import ProductionRule


class Grammar:
    def __init__(self, grammar_file_path):
        self.production_list = []
        self.production_table = {}
        self.terminals = set('$')
        self.non_terminals = set()
        self.first_table = {}
        self.follow_table = {}
        self.start = None

        self.__read_production_table__(grammar_file_path)
        self.__init_first_table__()
        self.__init_follow_table__()

    def __read_production_table__(self, file_path):
        file = open(file_path, encoding='utf-8')
        for production in file:
            head, bodies = production.split("->")
            head = head.strip()
            assert head[0].isupper(), "非终结符首字母必须大写, %s" % head
            self.non_terminals.add(head)
            if not bodies:
                bodies = 'ε'
            bodies = bodies.strip().split(' ')
            for body in bodies:
                if not str.isalpha(body[0]) or str.islower(body):
                    assert body in LexerUtils.TerminalList, "非法的终结符, %s" % body
                    self.terminals.add(body)
                else:
                    self.non_terminals.add(body)
            if not self.production_table.get(head):
                self.production_table[head] = []
            production = ProductionRule(head, bodies)
            self.production_table[head].append(production)
            self.production_list.append(production)
        self.start = self.production_list[0]

    def __first(self, beta):  # beta: x1,x2,x3...xn
        result = []
        for x in beta:
            x_produces_empty = False
            for f in self.first_table[x]:
                if f == 'ε':
                    x_produces_empty = True
                else:
                    if f not in result:
                        result.append(f)
            if not x_produces_empty:
                break
        else:
            result.append('ε')
        return result

    def __init_first_table__(self):
        for x in self.terminals:
            self.first_table[x] = [x]
        for x in self.non_terminals:
            self.first_table[x] = []

        while True:  # 利用迭代的方式求解 First 集合，避免左递归带来的无穷递归
            some_change = False
            for nt in self.non_terminals:
                for production in self.production_table[nt]:
                    for f in self.__first(production.body):
                        if f not in self.first_table[nt]:
                            self.first_table[nt].append(f)
                            some_change = True
            if not some_change:
                break

    def __init_follow_table__(self):
        for nt in self.non_terminals:
            self.follow_table[nt] = []
        self.follow_table[self.start.head] = ['$']

        while True:
            some_change = False
            for p in self.production_list:
                for i, body in enumerate(p.body):
                    if body in self.non_terminals:
                        fst = self.__first(p.body[i + 1:])
                        has_empty = False
                        for f in fst:
                            if f != 'ε' and f not in self.follow_table[body]:
                                self.follow_table[body].append(f)
                                some_change = True
                            if f == 'ε':
                                has_empty = True
                        if has_empty or i == (len(p.body) - 1):
                            for f in self.follow_table[p.head]:
                                if f not in self.follow_table[body]:
                                    self.follow_table[body].append(f)
                                    some_change = True
            if not some_change:
                break


if __name__ == '__main__':
    G = Grammar('grammar.txt')
    for p in G.production_list:
        print(p)
    print(G.non_terminals)
    print(G.terminals)
    print(G.first_table)
    print(G.follow_table)
