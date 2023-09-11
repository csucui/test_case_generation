from tree_sitter import Language, Parser, Node
from init_parser import *
from entity import If_node, Truth_node, TRUE_TO_FALSE
from util import merge_var_change
from z3 import Int, Solver, sat
import re
from copy import deepcopy

def format_tree(root: Node, if_tree: If_node, vars: dict[str,str]):
    '''
    这个方法将一个语法树中的if语句抽象出来构造if树,只关注if语句,先忽略if语句块中的其他语句比如赋值和运算
    '''
    for child in root.children:
        # 这一步是查询出所有在if之前的对变量的修改
        if child.children.__len__() == 1:  # 是一就可能是赋值语句
            child1 = child.children[0]
            if child1.type == 'assignment':
                # 赋值语句的左值和右值
                l_value = str(child1.children[0].text, encoding='utf-8')
                r_value = str(child1.children[2].text, encoding='utf-8')
                # 如果赋值的右值是调用函数,说明是初始化变量，暂时不考虑使用函数进行变量修改
                if child1.children[2].type == 'call':
                    vars[l_value] = l_value
                else:
                    if l_value in vars:
                        vars[l_value] = vars[l_value].replace(l_value,f'({r_value})')
                    else:
                        vars[l_value] = r_value
        if child.type == 'if_statement':
            cc = child.children
            if_tree.children.append(If_node('if', merge_var_change(str(cc[1].text, encoding='utf-8'),vars)))
            # 递归调用，下一步为if的block块，if_tree当前节点为刚刚加入的子节点
            format_tree(cc[3], if_tree.children[-1],deepcopy(vars))
            # 如果有else和elif，那么必定4项以后
            for c in cc[4:]:
                if c.type == 'elif_clause':
                    if_tree.children.append(If_node(c.type.split('_')[0], merge_var_change(str(c.children[1].text, encoding='utf-8'),vars)))
                    # 递归调用，下一步为elif的block块，if_tree当前节点为刚刚加入的子节点
                    format_tree(c.children[3], if_tree.children[-1],deepcopy(vars))
                if c.type == 'else_clause':
                    if_tree.children.append(If_node(c.type.split('_')[0], None))
                    # 递归调用，下一步为else的block块，if_tree当前节点为刚刚加入的子节点,else没有判断条件
                    format_tree(c.children[2], if_tree.children[-1],deepcopy(vars))


def get_truth_trees(root: If_node):
    '''
    使用路径覆盖
    '''
    # 考虑嵌套
    #路径覆盖可以直接获得约束条件
    def get_re(root: If_node,prefix: list,res: list[list[str]]):
        if root.compare_statement != None:
            prefix.append(root.compare_statement)
        i = root.children.__len__()
        if i == 0:
            if prefix != []:
                res.append(prefix)
            return
        for ii in range(i):
            get_re(root.children[ii],deepcopy(prefix),res)
            if root.children[ii].compare_statement != None:
                prefix.append(replace_keys_with_values(root.children[ii].compare_statement,TRUE_TO_FALSE))

    l = len(root.children)
    res: list[list[str]] = []
    prefix = [] # 到达这个分支需要的前置条件
    for i in range(l):
        get_re(root.children[i],deepcopy(prefix),res)
        if root.children[i].compare_statement != None:
            prefix.append(replace_keys_with_values(root.children[i].compare_statement,TRUE_TO_FALSE))
    return res


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


def print_tree(root: If_node, level=0):
    '''
    一个打印if树的方法
    '''
    print('  ' * level + repr(root))
    for child in root.children:
        print_tree(child, level + 1)


def print_truth_tree(root: Truth_node, level=0):
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

with open('test_code.py', 'r', encoding='utf-8') as f:
    code = f.read()
    tree = python_parser.parse(bytes(code, "utf8"))
    # 注意，root_node 才是可遍历的树节点
    root_node = tree.root_node
    if_tree = If_node('module', None)
    format_tree(root_node, if_tree,{})
    print_tree(if_tree)
    restrictions = get_truth_trees(if_tree)
    print(restrictions)
    letters = set()
    for res in restrictions:
        for r in res:
            v = get_variables(r)
            letters.update(v)
    print(letters)
    variables = {}
    for x in letters:
        variables[x] = Int(x)
    for res in restrictions:
        s = Solver()
        for r in res:
            s.add(eval(r, {}, variables))
        if s.check() == sat:
            # 获取一个解
            m = s.model()
            print(m)
        else:
            print("无解")
