from typing import Dict, List, Optional, Tuple, Union

def evaluate(expr: str, variables: Optional[Dict[str, float]] = None) -> float:
    if variables is None:
        variables = {}

    def tokenize(s: str) -> List[Tuple[str, Union[float, str, None]]]:
        tokens: List[Tuple[str, Union[float, str, None]]] = []
        i = 0
        n = len(s)
        while i < n:
            c = s[i]
            if c.isspace():
                i += 1
                continue
            if c.isdigit():
                start = i
                while i < n and s[i].isdigit():
                    i += 1
                if i < n and s[i] == '.':
                    i += 1
                    while i < n and s[i].isdigit():
                        i += 1
                tokens.append(('NUMBER', float(s[start:i])))
                continue
            if c.isalpha() or c == '_':
                start = i
                i += 1
                while i < n and (s[i].isalnum() or s[i] == '_'):
                    i += 1
                tokens.append(('IDENT', s[start:i]))
                continue
            if c in '+-*/%^()':
                tokens.append((c, c))
                i += 1
                continue
            raise ValueError(f"Unexpected character: {c!r}")
        tokens.append(('EOF', None))
        return tokens

    tokens = tokenize(expr)
    pos = 0

    def peek() -> str:
        return tokens[pos][0]

    def advance() -> Tuple[str, Union[float, str, None]]:
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def parse_expression() -> float:
        return parse_sum()

    def parse_sum() -> float:
        left = parse_product()
        while peek() in ('+', '-'):
            op = advance()[0]
            right = parse_product()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left

    def parse_product() -> float:
        left = parse_unary()
        while peek() in ('*', '/', '%'):
            op = advance()[0]
            right = parse_unary()
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0.0:
                    raise ValueError("Division by zero")
                left = left / right
            else:
                if right == 0.0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def parse_unary() -> float:
        if peek() == '-':
            advance()
            return -parse_unary()
        return parse_power()

    def parse_power() -> float:
        base = parse_atom()
        if peek() == '^':
            advance()
            exp = parse_unary()
            result = base ** exp
            if isinstance(result, complex):
                raise ValueError("Complex result not allowed")
            return float(result)
        return base

    def parse_atom() -> float:
        kind = peek()
        if kind == 'NUMBER':
            return float(advance()[1])  # type: ignore
        if kind == 'IDENT':
            name = advance()[1]  # type: ignore
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(variables[name])
        if kind == '(':
            advance()
            val = parse_expression()
            if peek() != ')':
                raise ValueError("Unbalanced parentheses")
            advance()
            return val
        raise ValueError(f"Malformed syntax near {kind!r}")

    result = parse_expression()
    if peek() != 'EOF':
        raise ValueError("Malformed syntax")
    return float(result)
