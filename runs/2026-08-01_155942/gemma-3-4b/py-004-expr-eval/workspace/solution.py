def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluates arithmetic expressions without using eval, exec, ast, or any parsing library."""

    tokens = tokenize(expr)
    if tokens is None:
        raise ValueError("Malformed syntax")

    index = 0

    def peek():
        nonlocal index
        if index < len(tokens):
            return tokens[index]
        return None

    def consume():
        nonlocal index
        token = peek()
        if token is not None:
            index += 1
            return token
        return None

    def parse_number():
        num_str = ""
        while peek() is not None and peek().isdigit() or peek() == '.':
            num_str += peek()
            consume()
        try:
            return float(num_str)
        except ValueError:
            raise ValueError("Invalid number format")

    def parse_unary_minus():
        if peek() is not None and peek() == '-':
            consume()
            return -parse_expression()
        return 0.0

    def parse_parentheses():
        if peek() is not None and peek() == '(':
            consume()
            result = parse_expression()
            if consume() is not None and consume() == ')':
                return result
            else:
                raise ValueError("Unbalanced parentheses")
        return result

    def parse_term():
        token = peek()
        if token is None:
            raise ValueError("Unexpected end of expression")

        if token == '(':
            return parse_parentheses()
        elif token == '-':
            return parse_unary_minus()
        elif token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
            return parse_number()
        else:
            raise ValueError(f"Unexpected token: {token}")

    def parse_expression():
        result = parse_term()
        while True:
            token = peek()
            if token is None:
                break
            if token in ['+', '-']:
                consume()
                result += parse_term()
            elif token in ['*', '/', '%']:
                consume()
                result *= parse_term()
            elif token == '^':
                consume()
                if peek() is not None and peek() == '^':
                    return parse_expression()
                else:
                    result **= parse_term()
            else:
                break
        return result

    result = parse_expression()

    if index < len(tokens):
        raise ValueError("Unexpected tokens at the end of expression")

    if variables is not None:
        for var in variables:
            if var in result:
                result = result.replace(var, str(variables[var]))
    return float(result)


def tokenize(expr: str) -> list[str] | None:
    """Tokenizes the input string."""
    tokens = []
    current_token = ""
    for char in expr:
        if char.isspace():
            if current_token:
                tokens.append(current_token)
                current_token = ""
        elif char.isdigit() or char == '.':
            current_token += char
        elif char in ['+', '-', '*', '/', '%', '^', '(', ')']:
            if current_token:
                tokens.append(current_token)
                current_token = ""
            tokens.append(char)
        else:
            raise ValueError("Malformed syntax")

    if current_token:
        tokens.append(current_token)

    return tokens
