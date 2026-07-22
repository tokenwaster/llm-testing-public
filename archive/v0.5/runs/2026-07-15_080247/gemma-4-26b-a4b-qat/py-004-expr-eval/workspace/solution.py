import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression with support for:
    - Numbers (integers and decimals)
    - Binary operators: +, -, *, /, %, ^ (right-associative)
    - Unary minus (binds looser than ^)
    - Parentheses (arbitrarily nested)
    - Variables (resolved from the variables dict)
    - Whitespace anywhere between tokens
    """
    if variables is None:
        variables = {}

    # Tokenizer using regex to identify all valid tokens
    # Number: \d+\.\d*|\.\d+|\d+
    # Variable: [a-zA-Z_][a-zA-Z0-9_]*
    # Operators and Parentheses: \+|-|\*|/|%|\^|\(|\)
    pattern = r'(\d+\.\d*|\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|\+|\-|\*|/|%|\^|\(|\))'
    tokens = []
    last_end = 0
    
    # Find all matches and check for invalid characters between them
    for match in re.finditer(pattern, expr):
        if expr[last_end:match.start()].strip():
            raise ValueError("Malformed syntax")
        
        token_str = match.group()
        if token_str in '+-*/%^()':
            tokens.append(token_str)
        elif token_str[0].isalpha() or token_str[0] == '_':
            tokens.append(token_str)
        else:
            tokens.append(float(token_str))
        last_end = match.end()
    
    if expr[last_end:].strip():
        raise ValueError("Malformed syntax")
    
    # Ensure the reconstructed string (ignoring whitespace) matches the original
    reconstructed = "".join(match.group() for match in re.finditer(pattern, expr))
    if reconstructed != expr.replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", ""):
        raise ValueError("Malformed syntax")

    def parse_expr(tokens_list):
        """expr -> term { (+|-) term }"""
        res = parse_term(tokens_list)
        while tokens_list and tokens_list[0] in ('+', '-'):
            op = tokens_list.pop(0)
            term2 = parse_term(tokens_list)
            if op == '+':
                res += term2
            else:
                res -= term2
        return res

    def parse_term(tokens_list):
        """term -> factor { (*|/|%) factor }"""
        res = parse_factor(tokens_list)
        while tokens_list and tokens_list[0] in ('*', '/', '%'):
            op = tokens_list.pop(0)
            factor2 = parse_factor(tokens_list)
            if op == '*':
                res *= factor2
            elif op == '/':
                if factor2 == 0:
                    raise ValueError("Division by zero")
                res /= factor2
            elif op == '%':
                if factor2 == 0:
                    raise ValueError("Modulo by zero")
                res %= factor2
        return res

    def parse_factor(tokens_list):
        """factor -> - factor | power"""
        if tokens_list and tokens_list[0] == '-':
            tokens_list.pop(0)
            return -parse_factor(tokens_list)
        else:
            return parse_power(tokens_list)

    def parse_power(tokens_list):
        """power -> primary [ ^ factor ] (right-associative)"""
        res = parse_primary(tokens_list)
        if tokens_list and tokens_list[0] == '^':
            tokens_list.pop(0)
            # Right-associativity: the right-hand side is a factor (which can be unary)
            res = res ** parse_factor(tokens_list)
        return res

    def parse_primary(tokens_list):
        """primary -> ( expr ) | number | variable"""
        if not tokens_list:
            raise ValueError("Malformed syntax")
        
        token = tokens_list.pop(0)
        if token == '(':
            res = parse_expr(tokens_list)
            if not tokens_list or tokens_list.pop(0) != ')':
                raise ValueError("Unbalanced parentheses")
            return res
        elif isinstance(token, float):
            return token
        elif isinstance(token, str):
            if token in variables:
                return float(variables[token])
            else:
                raise ValueError(f"Unknown variable: {token}")
        else:
            raise ValueError("Malformed syntax")

    try:
        result = parse_expr(tokens)
        if tokens:
            raise ValueError("Malformed syntax")
        return float(result)
    except ZeroDivisionError:
        raise ValueError("Division by zero")
    except (IndexError, TypeError):
        raise ValueError("Malformed syntax")
