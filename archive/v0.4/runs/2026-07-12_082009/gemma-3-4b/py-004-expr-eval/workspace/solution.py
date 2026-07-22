def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluates arithmetic expressions without using eval, exec, ast, or parsing libraries."""

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
        while peek() and (peek().isdigit() or peek() == '.'):
            num_str += peek()
        try:
            return float(num_str)
        except ValueError:
            raise ValueError("Invalid number format")

    def parse_unary_minus():
        if peek() == '-':
            consume()
            return -parse_expression()
        else:
            raise ValueError("Expected unary minus")

    def parse_parentheses():
        if peek() != '(':
            raise ValueError("Expected opening parenthesis")
        consume()
        result = parse_expression()
        if peek() != ')':
            raise ValueError("Expected closing parenthesis")
        consume()
        return result

    def parse_expression():
        term = parse_unary_minus()

        while True:
            op_token = peek()
            if op_token is None:
                break

            if op_token in '+-*/%^':
                op = op_token
                consume()

                next_term = parse_term()

                if op == '+':
                    term = term + next_term
                elif op == '-':
                    term = term - next_term
                elif op == '*':
                    term *= next_term
                elif op == '/':
                    if next_term == 0:
                        raise ValueError("Division by zero")
                    term /= next_term
                elif op == '%':
                    if next_term == 0:
                        raise ValueError("Modulo by zero")
                    term %= next_term
                elif op == '^':
                    if next_term == 0:
                        raise ValueError("Exponentiation by zero")
                    term **= next_term

            else:
                break  # Invalid token

        return term

    def parse_term():
        token = peek()
        if token is None:
            raise ValueError("Unexpected end of expression")

        if token.isdigit() or ('.' in token and token.replace('.', '', 1).isdigit()):
            return parse_number()
        elif token == '(':
            return parse_parentheses()
        else:
            if variables is not None and token in variables:
                return variables[token]
            else:
                raise ValueError(f"Unknown variable: {token}")

    result = parse_expression()
    if index < len(tokens):
        raise ValueError("Unexpected tokens at the end of expression")

    return result


def tokenize(expr: str) -> list[str] | None:
    """Tokenizes an arithmetic expression."""
    tokens = []
    current_token = ""
    for char in expr:
        if char.isspace():
            if current_token:
                tokens.append(current_token)
                current_token = ""
        elif char.isdigit() or char == '.':
            current_token += char
        elif char in '+-*/%^(':
            if current_token:
                tokens.append(current_token)
                current_token = ""
            tokens.append(char)
        elif char == '-':
            if current_token and current_token != '(':
                tokens.append(current_token)
                current_token = ""
            tokens.append(char)
        else:
            return None  # Invalid character

    if current_token:
        tokens.append(current_token)

    return tokens
