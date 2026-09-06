import math
import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = list(tokenize(expr))
    pos = [0]
    
    # parse_expr parses additive level (+, -)
    def parse_expr():
        left = parse_term()
        while pos[0] < len(tokens) and tokens[pos[0]] in ['+', '-']:
            op = tokens[pos[0]]
            pos[0] += 1
            right = parse_term()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left

    # parse_term parses multiplicative level (*, /, %)
    def parse_term():
        left = parse_power()
        while pos[0] < len(tokens) and tokens[pos[0]] in ['*', '/', '%']:
            op = tokens[pos[0]]
            pos[0] += 1
            right = parse_power()
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            elif op == '%':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left % right
        return left

    # parse_power parses exponentiation (^) right-associative
    # unary minus binds looser than ^
    def parse_power():
        left = parse_unary()
        if pos[0] < len(tokens) and tokens[pos[0]] == '^':
            pos[0] += 1
            right = parse_power()
            left = math.pow(left, right)
        return left

    # parse_unary handles unary minus (-), higher than binary +/- but lower than ^
    def parse_unary():
        if pos[0] < len(tokens) and tokens[pos[0]] == '-':
            pos[0] += 1
            val = parse_unary()
            return -val
        return parse_primary()

    # parse_primary handles literals, variables, parentheses
    def parse_primary():
        if pos[0] >= len(tokens):
            raise ValueError("Unexpected end of expression")
        token = tokens[pos[0]]
        if token == '(':
            pos[0] += 1
            val = parse_expr()
            if pos[0] >= len(tokens) or tokens[pos[0]] != ')':
                raise ValueError("Unbalanced parentheses")
            pos[0] += 1
            return val
        elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token):
            if variables is None or token not in variables:
                raise ValueError(f"Unknown variable: {token}")
            pos[0] += 1
            return float(variables[token])
        else:
            pos[0] += 1
            return float(token)

    result = parse_expr()
    if pos[0] < len(tokens):
        raise ValueError("Malformed syntax")
    return result

def tokenize(expr: str):
    tokens = []
    i = 0
    n = len(expr)
    var_pat = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    num_pat = re.compile(r'\d+(\.\d*)?|\.\d+')
    ops = {'+', '-', '*', '/', '%', '^', '(', ')'}

    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in ops:
            tokens.append(c)
            i += 1
            continue
        if c.isdigit() or c == '.':
            match = num_pat.match(expr, i)
            if match:
                tokens.append(match.group())
                i = match.end()
                continue
        if c.isalpha() or c == '_':
            match = var_pat.match(expr, i)
            if match:
                tokens.append(match.group())
                i = match.end()
                continue
        raise ValueError("Malformed syntax")

    # Post-check for balanced parentheses
    stack = []
    for t in tokens:
        if t == '(':
            stack.append(t)
        elif t == ')':
            if not stack:
                raise ValueError("Unbalanced parentheses")
            stack.pop()
    if stack:
        raise ValueError("Unbalanced parentheses")

    return tokens
