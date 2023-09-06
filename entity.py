class If_node:
    def __init__(self,type,compare_statement) -> None:
        self.type = type
        self.compare_statement = compare_statement
        self.children: list[If_node] = []

    def __repr__(self) -> str:
        return f'{self.type}({self.compare_statement})'