from tree_sitter import Node
from init_parser import *
from entity import If_node
import re

def format_tree(root: Node,if_tree: If_node):
    '''
    这个方法将一个语法树中的if语句抽象出来构造if树,只关注if语句,先忽略if语句块中的其他语句比如赋值和运算
    '''
    for child in root.children:
        if child.type == 'if_statement':
            cc = child.children
            if_tree.children.append(If_node('if',str(cc[1].text, encoding='utf-8')))
            # 递归调用，下一步为if的block块，if_tree当前节点为刚刚加入的子节点
            format_tree(cc[3],if_tree.children[-1])
            # 如果有else和elif，那么必定4项以后
            for c in cc[4:]:
                if c.type == 'elif_clause':
                    if_tree.children.append(If_node(c.type.split('_')[0],str(c.children[1].text, encoding='utf-8')))
                    # 递归调用，下一步为if的block块，if_tree当前节点为刚刚加入的子节点
                    format_tree(c.children[3],if_tree.children[-1])
                if c.type == 'else_clause':
                    if_tree.children.append(If_node(c.type.split('_')[0],None))
                    # 递归调用，下一步为if的block块，if_tree当前节点为刚刚加入的子节点
                    format_tree(c.children[2],if_tree.children[-1])
              

python_parser = init_python_parser()

with open('test_code.py', 'r',encoding='utf-8') as f:
    code = f.read()
    print(code)
    # 没报错就是成功
    format_code = re.sub(r'\n+', '\\n', code)   # 去连续空行
    format_code = re.sub(r'\n$', '', format_code)  # 去末尾空行
    format_code = re.sub(r'^\n', '', format_code) # 去开头空行
    print(format_code)
    tree = python_parser.parse(bytes(code, "utf8"))
    # 注意，root_node 才是可遍历的树节点
    root_node = tree.root_node
    if_tree = If_node('module',None)
    format_tree(root_node,if_tree)
    print()