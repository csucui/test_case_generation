import ast
from anytree import Node, RenderTree


def generate_tree(node, parent=None):
    node_name = get_node_name(node)
    current_node = Node(node_name, parent=parent)

    for child in ast.iter_child_nodes(node):
        generate_tree(child, parent=current_node)

    return current_node


def get_node_name(node):
    if isinstance(node, ast.Module):
        return 'Module'
    elif isinstance(node, ast.FunctionDef):
        return f'FunctionDef: {node.name}'
    elif isinstance(node, ast.ClassDef):
        return f'ClassDef: {node.name}'
    elif isinstance(node, ast.Expr):
        return 'Expr'
    elif isinstance(node, ast.Call):
        return f'Call: {node.func.id}'
    elif isinstance(node, ast.BinOp):
        return f'BinOp: {type(node.op).__name__}'
    elif isinstance(node, ast.Constant):
        return f'Constant: {repr(node.value)}'
    elif isinstance(node, ast.Name):
        return f'Name: {node.id}'
    elif isinstance(node, ast.Assign):
        return 'Assign'
    elif isinstance(node, ast.If):
        return 'If'
    elif isinstance(node, ast.For):
        return 'For'
    elif isinstance(node, ast.While):
        return 'While'
    elif isinstance(node, ast.Return):
        return 'Return'
    elif isinstance(node, ast.Import):
        return 'Import'
    elif isinstance(node, ast.ImportFrom):
        return 'ImportFrom'
    else:
        return node.__class__.__name__


# 你的代码示例
code = '''
a = int(input())
b = int(input())
a = a + 1
b = b + 2
print(b)
if a > 9:
    a = a + 1
    if a > 10:
        print('')
elif b >= a + 5:
    print('22222')
else:
    print('33333')
'''

# 解析代码为AST
tree = ast.parse(code)

# 生成AST树
ast_tree = generate_tree(tree)

# 打印树形结构
for pre, fill, node in RenderTree(ast_tree):
    print(f"{pre}{node.name}")
