import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # Tokenize the expression
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
    tok_regex = '|'.join(f'(?P<{name}>{reg})' for name, reg in token_specification)
    
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
            raise ValueError(f"Unexpected character: {value}")

    # We will use a recursive descent parser.
    # Grammar:
    # Expression -> Term ( ( "+" | "-" ) Term )*
    # Term       -> Factor ( ( "*" | "/" | "%" ) Factor )*
    # Factor     -> Power ( "^" Power )*  [Right-associative, handled via recursion]
    # Power      -> "-" Power | Primary
    # Primary    -> NUMBER | VAR | "(" Expression ")"

    pos = 0
    n = len(tokens)

    def peek():
        if pos < n:
            return tokens[pos]
        return None

    def get_token():
        nonlocal pos
        if pos < n:
            tok = tokens[pos]
            pos += 1
            return tok
        return None

    def parse_expression() -> float:
        val = parse_term()
        while True:
            tok = peek()
            if tok and tok[0] == 'OP' and tok[1] in ('+', '-'):
                op = get_token()[1]
                right = parse_term()
                if op == '+':
                    val += right
                else:
                    val -= right
            else:
                break
        return val

    def parse_term() -> float:
        val = parse_factor()
        while True:
            tok = peek()
            if tok and tok[0] == 'OP' and tok[1] in ('*', '/', '%'):
                op = get_token()[1]
                right = parse_factor()
                if op == '*':
                    val *= right
                elif op == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    val /= right
                else: # op == '%'
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    val %= right
            else:
                break
        return val

    def parse_factor() -> float:
        # Exponentiation is right-associative.
        # Factor -> Power [ "^" Factor ]
        val = parse_power()
        tok = peek()
        if tok and tok[0] == 'OP' and tok[1] == '^':
            get_token() # consume '^'
            right = parse_factor()
            try:
                val = val ** right
            except OverflowError:
                raise ValueError("Overflow in exponentiation")
        return val

    def parse_power() -> float:
        # Power -> "-" Power | Primary
        tok = peek()
        if tok and tok[0] == 'OP' and tok[1] == '-':
            get_token() # consume '-'
            return -parse_power()
        return parse_primary()

    def parse_primary() -> float:
        tok = get_token()
        if not tok:
            raise ValueError("Unexpected end of expression")
        
        if tok[0] == 'NUMBER':
            return tok[1]
        elif tok[0] == 'VAR':
            var_name = tok[1]
            if var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return float(variables[var_name])
        elif tok[0] == 'OP' and tok[1] == '(':
            val = parse_expression()
            next_tok = get_token()
            if not next_tok or next_tok[0] != 'OP' or next_tok[1] != ')':
                raise ValueError("Unbalanced parentheses")
            return val
        else:
            raise ValueError(f"Unexpected token: {tok[1]}")

    if not tokens:
        raise ValueError("Empty expression")

    result = parse_expression()
    if pos < n:
        raise ValueError(f"Unparsed tokens remaining at index {pos}: {tokens[pos:]}")
    return float(result)
