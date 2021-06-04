class ProductionRule:
    def __init__(self, head, body):
        self.head = head
        assert type(body) == list, "body 类型必须为 list"
        self.body = body

    def __str__(self):
        return f"{self.head} -> {' '.join(self.body)}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.head == other.head and self.body == other.body


class ProductionItem(ProductionRule):
    def __init__(self, head, body, dot=0):
        super().__init__(head, body)
        assert 0 <= dot <= len(self.body), "dot 的位置不合法"
        self.dot = dot

    def __str__(self):
        return f"{self.head} -> {' '.join(self.body[0:self.dot] + ['·'] + self.body[self.dot:])}"

    def __eq__(self, other):
        return self.head == other.head and self.body == other.body and self.dot == other.dot
