import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression without using eval, exec, ast, or any parsing library.
    Supports numbers, binary operators (+, -, *, /, %, ^), unary minus, parentheses, and variables.
    Precedence: Parentheses > Exponentiation (^) > Unary Minus (-) > Multiplication/Division/Modulo (*, /, %) > Addition/Subtraction (+, -).
    Exponentiation is right-associative. Unary minus binds looser than exponentiation.
    """
    variables = variables or {}
    tokens = []
    i = 0
    n = len(expr)

    # Tokenizer
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        
        # Numbers (integers and decimals like 3, 4.5; .5 is not required but handled)
        if c.isdigit() or (c == '.' and i + 1 < n and expr[i+1].isdigit()):
            start = i
            if c == '.':
                i += 1
                while i < n and expr[i].isdigit():
                    i += 1
            else:
                while i < n and (expr[i].isdigit() or expr[i] == '.'):
                    i += 1
            num_str = expr[start:i]
            try:
                tokens.append(('NUM', float(num_str)))
            except ValueError:
                raise ValueError(f"Invalid number: {num_str}")
            continue

        # Variables [a-zA-Z_][a-zA-Z0-9_]*
        if c.isalpha() or c == '_':
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            var_str = expr[start:i]
            if var_str not in variables:
                raise ValueError(f"Unknown variable: {var_str}")
            tokens.append(('VAR', float(variables[var_str])))
            continue

        # Operators and Parentheses
        if c in '+-*/%^()':
            tokens.append(('OP', c))
            i += 1
            continue
        
        raise ValueError(f"Unknown character: {c}")

    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def consume():
        nonlocal pos
        token = peek()
        pos += 1
        return token

    # Recursive Descent Parser Grammar:
    # expression -> term { (+|-) term }
    # term       -> unary_minus_expr { (*|/|%) unary_minus_expr }
    # unary_minus_expr -> - unary_minus_expr | power_expr
    # power_expr  -> primary ^ power_expr | primary
    # primary     -> number | variable | ( expression )

    def parse_expression() -> float:
        node = parse_term()
        while peek() and peek()[1] in ('+', '-'):
            op = consume()[1]
            right = parse_term()
            if op == '+':
                node += right
            else:
                node -= right
        return node

    def parse_term() -> float:
        node = parse_unary_minus_expr()
        while peek() and peek()[1] in ('*', '/', '%'):
            op = consume()[1]
            right = parse_unary_minus_expr()
            if op == '*':
                node *= right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                node /= right
            elif op == '%':
                if right == 0:
                    raise ValueError("Modulo by zero")
                node %= right
        return node

    def parse_unary_minus_expr() -> float:
        if peek() and peek()[1] == '-':
            consume()
            return -parse_unary_minus_expr()
        else:
            return parse_power_expr()

    def parse_power_expr() -> float:
        node = parse_primary()
        if peek() and peek()[1] == '^':
            consume()
            # Right-associativity for ^
            right = parse_power_expr()
            node = node ** right
        return node

    def parse_primary() -> float:
        token = consume()
        if not token:
            raise ValueError("Unexpected end of expression")
        
        if token[0] == 'NUM':
            return token[1]
        elif token[0] == 'VAR':
            return token[1]
        elif token[0] == 'OP' and token[1] == '(':
            node = parse_expression()
            if not peek() or peek()[1] != ')':
                raise ValueError("Unbalanced parentheses")
            consume()  # consume ')'
            return node
        else:
            raise ValueError(f"Unexpected token: {token}")

    try:
        result = parse_expression()
        if pos < len(tokens):
            raise ValueError("Unexpected tokens at end of expression")
        return float(result)
    except (ZeroDivisionError, OverflowError) as e:
        # Handle potential overflow or zero division from power operator if not caught by parser
        raise ValueError(str(e))
