import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression without using eval, exec, ast, or parsing libraries.
    Supports numbers, binary operators (+, -, *, /, %, ^), unary minus, parentheses, and variables.
    """
    if variables is None:
        variables = {}

    # Tokenizer pattern: matches floats, integers, variable names, and single-character operators/parentheses.
    pattern = r'\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[+\-*/%^()]'
    tokens = []
    last_end = 0

    # Tokenize the expression and check for invalid characters between tokens.
    for match in re.finditer(pattern, expr):
        junk = expr[last_end:match.start()].strip()
        if junk:
            raise ValueError(f"Invalid character found: {junk}")
        
        token = match.group()
        try:
            # Try to convert numeric tokens to float.
            tokens.append(float(token))
        except ValueError:
            # Otherwise, treat as a string (variable or operator).
            tokens.append(token)
        last_end = match.end()

    # Check for invalid characters after the last token.
    junk = expr[last_end:].strip()
    if junk:
        raise ValueError(f"Invalid character found: {junk}")

    if not tokens:
        raise ValueError("Empty expression")

    pos = 0

    def current_token():
        nonlocal pos
        return tokens[pos] if pos < len(tokens) else None

    def consume(expected=None):
        nonlocal pos
        token = current_token()
        if token is None:
            raise ValueError("Unexpected end of expression")
        if expected and token != expected:
            raise ValueError(f"Expected {expected}, but found {token}")
        pos += 1
        return token

    def parse_expr():
        """Handles binary + and - (left-associative, lowest precedence)."""
        val = parse_term()
        while current_token() in ('+', '-'):
            op = consume()
            right = parse_term()
            if op == '+':
                val += right
            else:
                val -= right
        return val

    def parse_term():
        """Handles binary *, /, and % (left-associative, medium precedence)."""
        val = parse_unary()
        while current_token() in ('*', '/', '%'):
            op = consume()
            right = parse_unary()
            if op == '*':
                val *= right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                val /= right
            elif op == '%':
                if right == 0:
                    raise ValueError("Modulo by zero")
                val %= right
        return val

    def parse_unary():
        """Handles unary minus (can be repeated, lower precedence than ^)."""
        if current_token() == '-':
            consume()
            # Recursion allows for multiple unary minuses like --3.
            # By calling parse_unary instead of parse_power, we ensure '-' 
            # is evaluated after '^' (as per the prompt requirement).
            return -parse_unary()
        return parse_power()

    def parse_power():
        """Handles binary ^ (right-associative, highest precedence)."""
        val = parse_atom()
        if current_token() == '^':
            consume()
            # Recursive call on the right side implements right-associativity.
            right = parse_power()
            try:
                return float(val ** right)
            except OverflowError:
                raise ValueError("Result too large (Overflow)")
        return val

    def parse_atom():
        """Handles numbers, variables, and parentheses."""
        token = consume()
        if token == '(':
            val = parse_expr()
            if consume() != ')':
                raise ValueError("Unbalanced parentheses")
            return val
        elif isinstance(token, float):
            return token
        elif isinstance(token, str) and re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', token):
            if token in variables:
                return float(variables[token])
            else:
                raise ValueError(f"Unknown variable: {token}")
        else:
            # If the token is an operator or other unexpected string.
            raise ValueError(f"Malformed syntax: {token}")

    # Start parsing from the lowest precedence level.
    result = parse_expr()

    # Ensure all tokens have been consumed; if not, there's trailing junk.
    if pos < len(tokens):
        raise ValueError("Malformed syntax: extra tokens at end of expression")

    return float(result)
