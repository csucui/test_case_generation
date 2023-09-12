import re

def merge_var_change(expression: str,changes: dict[str,str]):
    for k,v in changes.items():
        expression = expression.replace(k, v)
    return expression

def format_compare(s: str):
    '''
    包含括号的字符串格式化,不支持嵌套括号
    '''
    result = []
    pattern = re.compile(r"(?<!And)(?<!Or)(?<!Not)\((.*?(?:and|or|not).*?)\)")
    matches = pattern.finditer(s)
    for match1 in matches:
        group = match1.group(1)
        result.append(group)
    for res in result:
        format_r = format_compare(res)
        s = s.replace(f'({res})',format_r)
    # 先将条件以or分割
    or_state = s.split('or')
    # 如果为1，那么说明这个语句里面没有or
    if or_state.__len__() == 1:
        # 将条件以and分割
        and_state = s.split('and')
        if and_state.__len__() == 1:
            if 'not' in s:
                return f"Not({s.split('not')[1]})"
            else:
                return s
        else:
            return f"And({','.join([format_compare(state) for state in and_state])})"
    else:
        return f"Or({','.join([format_compare(state) for state in or_state])})"