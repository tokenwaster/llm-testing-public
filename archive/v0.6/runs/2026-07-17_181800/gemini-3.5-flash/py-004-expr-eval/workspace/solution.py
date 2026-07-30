import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # Tokenizer
    # Tokens:
    # - Float/Integer: \d+(?:\.\d+)?
    # - Variable: [a-zA-Z_][a-zA-Z0-9_]*
    # - Operators/Parentheses: \+ | - | \* | / | % | \^ | \( | \)
    token_specification = [
        ('NUMBER',   r'\d+(?:\.\d+)?'),
        ('VAR',      r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('OP',       r'[\+\-\*/%\^\(\)]'),
        ('SKIP',     r'\s+'),
        ('MISMATCH', r'.'),
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    
    tokens = []
    for mo in re.finditer(tok_regex, expr):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            tokens.append(('NUMBER', float(value)))
        elif kind == 'VAR':
            tokens.append(('VAR', value))
        elif kind == 'OP':
            tokens.append(('OP', value))
        elif kind == 'SKIP':
            continue
        else:
            raise ValueError(f"Unexpected character: {value!r}")

    # Parser state
    pos = 0
    n = len(tokens)

    def peek():
        if pos < n:
            return tokens[pos]
        return None

    def consume(expected_val=None):
        nonlocal pos
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of input")
        if expected_val is not None:
            if tok[0] != 'OP' or tok[1] != expected_val:
                raise ValueError(f"Expected {expected_val!r}, got {tok[1]!r}")
        pos += 1
        return tok

    # Grammar:
    # Expression -> Term6
    # Term6 (Precedence 1: + -) -> Term5 { ('+' | '-') Term5 }  (Left-associative)
    # Term5 (Precedence 2: * / %) -> Term4 { ('*' | '/' | '%') Term4 } (Left-associative)
    # Term4 (Precedence 3: Unary -) -> '-' Term4 | Term3
    # Term3 (Precedence 4: ^) -> Term2 [ '^' Term3 ] (Right-associative)
    # Term2 (Atom) -> NUMBER | VAR | '(' Expression ')'

    def parse_expression() -> float:
        return parse_term6()

    def parse_term6() -> float:
        val = parse_term5()
        while True:
            tok = peek()
            if tok and tok[0] == 'OP' and tok[1] in ('+', '-'):
                op = consume()[1]
                right = parse_term5()
                if op == '+':
                    val += right
                else:
                    val -= right
            else:
                break
        return val

    def parse_term5() -> float:
        val = parse_term4()
        while True:
            tok = peek()
            if tok and tok[0] == 'OP' and tok[1] in ('*', '/', '%'):
                op = consume()[1]
                right = parse_term4()
                if op == '*':
                    val *= right
                elif op == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    val /= right
                else:
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    val %= right
            else:
                break
        return val

    def parse_term4() -> float:
        tok = peek()
        if tok and tok[0] == 'OP' and tok[1] == '-':
            consume()
            return -parse_term4()
        return parse_term3()

    def parse_term3() -> float:
        val = parse_term2()
        tok = peek()
        if tok and tok[0] == 'OP' and tok[1] == '^':
            consume()
            right = parse_term3()
            try:
                val = val ** right
            except OverflowError:
                raise ValueError("Exponentiation overflow")
            except ZeroDivisionError:
                raise ValueError("Division by zero in exponentiation")
        return val

    def parse_term2() -> float:
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        
        if tok[0] == 'NUMBER':
            consume()
            return tok[1]
        elif tok[0] == 'VAR':
            consume()
            var_name = tok[1]
            if var_name not in variables:
                raise ValueError(f"Undefined variable: {var_name}")
            return float(variables[var_name])
        elif tok[0] == 'OP' and tok[1] == '(':
            consume('(')
            val = parse_expression()
            consume(')')
            return val
        else:
            raise ValueError(f"Unexpected token: {tok[1]!r}")

    if not tokens:
        raise ValueError("Empty expression")

    result = parse_expression()
    if pos < n:
        raise ValueError(f"Unparsed tokens remaining starting at {tokens[pos][1]!r}")
    
    return float(result)
