class If_node:
    def __init__(self,type,compare_statement: str) -> None:
        self.type = type
        self.compare_statement = compare_statement
        self.children: list[If_node] = []

    def __repr__(self) -> str:
        return f'{self.type}({self.compare_statement})'
    
class Truth_node:
    """
    这个类表明了真值树的一个节点
    type: 这个节点的类型:root,if, elif, else
    is_true: 这个节点代表的if分支是否成立
    chrildren: 这个节点的子节点
    restrictions: 这个节点的约束条件，可能有多个，所以是列表   
    """    
    def __init__(self,type,is_true) -> None:
        self.type = type
        self.is_true = is_true
        self.children: list[Truth_node] = []
        self.restrictions: list[str] = []
        
    def __repr__(self) -> str:
        return f'{self.type}({self.restrictions})'
    
TRUE_TO_FALSE = {
    '==': '!=',
    '>=': '<',
    '<=': '>',
    '>': '<=',
    '<': '>='
}