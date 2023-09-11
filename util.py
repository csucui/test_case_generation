def merge_var_change(expression: str,changes: dict[str,str]):
    for k,v in changes.items():
        expression = expression.replace(k, v)
    return expression
