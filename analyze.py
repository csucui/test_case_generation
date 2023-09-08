from tree_sitter import Language, Parser,Node
from init_parser import *
from entity import If_node, Truth_node,TRUE_TO_FALSE
from z3 import Int,Solver,sat,Z3_parse_smtlib2_string,StringVal
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
                    # 递归调用，下一步为elif的block块，if_tree当前节点为刚刚加入的子节点
                    format_tree(c.children[3],if_tree.children[-1])
                if c.type == 'else_clause':
                    if_tree.children.append(If_node(c.type.split('_')[0],None))
                    # 递归调用，下一步为else的block块，if_tree当前节点为刚刚加入的子节点,else没有判断条件
                    format_tree(c.children[2],if_tree.children[-1])

def get_truth_trees(root: If_node) -> list[Truth_node]:
    # 暂时不考虑嵌套
    def get_tree(root: If_node, tree: Truth_node,where_true: int):
        l = len(root.children)
        for n in range(l):
            if n == where_true:
                truth_node = Truth_node(root.children[n].type,1)
                if root.children[n].compare_statement is not None:
                    truth_node.restrictions.append(root.children[n].compare_statement)
                tree.children.append(truth_node)
            else:
                truth_node = Truth_node(root.children[n].type,0)
                re = replace_keys_with_values(root.children[n].compare_statement,TRUE_TO_FALSE)
                if re is not None:
                    truth_node.restrictions.append(re)
                tree.children.append(truth_node)
        return tree
    
    l = len(root.children)
    trees: list[Truth_node] = []
    for i in range(l):
        tree = Truth_node('root', 1)
        tree = get_tree(root,tree,i)
        trees.append(tree)
    return trees

def get_restrictions(trees: list[Truth_node]):
    restrictions: list = []
    for tree in trees:
        # 因为没有考虑嵌套的问题，所以目前所有的树都只有一层
        restriction: list = []
        for child in tree.children:
            if child.restrictions is not []:
                restriction.extend(child.restrictions)
        restrictions.append(restriction)
    return restrictions
def print_tree(root: If_node,level = 0):
    '''
    一个打印if树的方法
    '''
    print('  ' * level + repr(root))
    for child in root.children:
        print_tree(child, level + 1)

def print_truth_tree(root: Truth_node,level = 0):
    '''
    一个打印真值树的方法
    '''
    print('  ' * level + repr(root))
    for child in root.children:
        print_tree(child, level + 1)

def replace_keys_with_values(string: str, rep_dict: dict):
    if string is None:
        return None
    for key, value in rep_dict.items():
        if key in string:
            string = string.replace(key, value)
            break
    return string

def get_variables(s: str):
    variables = re.findall(r"\b[a-zA-Z]+\b", s)
    variables = list(filter(lambda x: x not in ['and', 'or'], variables))
    return variables

PYTHON_LANGUAGE = Language('build/my-languages.so', 'python')
python_parser = Parser()
python_parser.set_language(PYTHON_LANGUAGE)

with open('test_code.py', 'r',encoding='utf-8') as f:
    code = f.read()
    tree = python_parser.parse(bytes(code, "utf8"))
    # 注意，root_node 才是可遍历的树节点
    root_node = tree.root_node
    if_tree = If_node('module',None)
    format_tree(root_node,if_tree)
    print_tree(if_tree)
    trees = get_truth_trees(if_tree)
    for i in range(trees.__len__()):
        print(f'这是第{i+1}个真值树结构')
        print_truth_tree(trees[i])
    restrictions = get_restrictions(trees)
    letters = set()
    for res in restrictions:
        for r in res:
            v = get_variables(r)
            letters.update(v)
    print(letters)
    variables = {}
    for x in letters:
        variables[x]=Int(x)
    for res in restrictions:
        s = Solver()
        for r in res:
            s.add(eval(r,{},variables))
        if s.check() == sat:
            # 获取一个解
            m = s.model()
            print(m)
        else:
            print("无解")