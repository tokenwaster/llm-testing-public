import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression with support for numbers, variables, 
    standard operators (+, -, *, /, %, ^), unary minus, and parentheses.
    Returns a float. Raises ValueError on syntax errors or math errors.
    """
    if variables is None:
        variables = {}

    # Tokenizer implementation using regular expressions
    tokens = []
    # Order matters: match variables before operators/numbers if they share characters
    token_pattern = re.compile(r'\s*([a-zA-Z_][a-zA-Z0-9_]*|\d+(\.\d+)?|[+\-*/%^()])')
    pos = 0
    while pos < len(expr):
        match = token_pattern.match(expr, pos)
        if not match:
            raise ValueError(f"Invalid character at position {pos}")
        # We take the first capturing group which is the whole token
        tokens.append(match.group(1))
        pos = match.end()

    current_idx = 0

    def peek():
        nonlocal current_idx
        return tokens[current_idx] if current_idx < len(tokens) else None

    def consume(expected=None):
        nonlocal current_idx
        token = peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        if expected and token != expected:
            raise ValueError(f"Expected {expected}, got {token}")
        current_idx += 1
        return token

    def parse_expression():
        """Lowest precedence: Addition and Subtraction (Left-associative)"""
        left = parse_term()
        while peek() in ('+', '-'):
            op = consume()
            right = parse_term()
            if op == '+':
                left += right
            else:
                left -= right
        return left

    def parse_term():
        """Medium precedence: Multiplication, Division, and Modulo (Left-associative)"""
        left = parse_unary()
        while peek() in ('*', '/', '%'):
            op = consume()
            right = parse_unary()
            if op == '*':
                left *= right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left /= right
            elif op == '%':
                if right == 0:
                    raise ValueError("Modulo by zero")
                left %= right
        return left

    def parse_unary():
        """Unary minus (Right-associative, binds looser than exponentiation)"""
        if peek() == '-':
            consume('-')
            # Recursively call unary to support multiple leading minuses (e.g., --3)
            return -parse_unary()
        return parse_power()

    def parse_power():
        """Exponentiation (Right-associative)"""
        left = parse_atom()
        if peek() == '^':
            consume('^')
            # Recursion for right-associativity: 2^3^2 is 2^(3^2)
            right = parse_power()
            try:
                left = left ** right
            except OverflowError:
                raise ValueError("Numerical overflow in exponentiation")
        return left

    def parse_atom():
        """Highest precedence: Parentheses, Numbers, and Variables"""
        token = peek()
        if token == '(':
            consume('(')
            res = parse_expression()
            consume(')')
            return res
        elif token is not None and (token[0].isdigit()):
            # We only support numbers starting with digits as per requirement ".5 NOT required"
            consume()
            try:
                return float(token)
            except ValueError:
                raise ValueError(f"Invalid number format: {token}")
        elif token is not None and (token[0].isalpha() or token[0] == '_'):
            var_name = consume()
            if var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return float(variables[var_name])
        else:
            raise ValueError(f"Unexpected token or malformed syntax at '{token}'")

    # Start parsing from the lowest precedence rule
    if not tokens:
        raise ValueError("Empty expression")
    
    result = parse_expression()
    
    # Ensure no leftover tokens remain (indicates syntax error like "2 + 3 4")
    if current_idx < len(tokens):
        raise ValueError(f"Trailing characters in expression: {tokens[current_idx:]}")
        
    return float(result)
