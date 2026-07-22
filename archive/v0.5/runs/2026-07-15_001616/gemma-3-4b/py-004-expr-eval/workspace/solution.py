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
        return 0.0

    def parse_parentheses():
        if peek() != '(':
            raise ValueError("Unbalanced parentheses")
        consume()
        result = parse_expression()
        if peek() != ')':
            raise ValueError("Unbalanced parentheses")
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
                    term += next_term
                elif op == '-':
                    term -= next_term
                elif op == '*':
                    term *= next_term
                elif op == '/':
                    if next_term == 0.0:
                        raise ValueError("Division by zero")
                    term /= next_term
                elif op == '%':
                    if next_term == 0.0:
                        raise ValueError("Modulo by zero")
                    term %= next_term
                elif op == '^':
                    if next_term == 0.0:
                        return term  # Handle exponentiation with 0 as base
                    term **= next_term

            else:
                break

        return term

    def parse_term():
        token = peek()
        if token is None:
            raise ValueError("Unexpected end of expression")

        if token.isalpha():
            var_name = token
            if variables and var_name in variables:
                return variables[var_name]
            elif var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            else:
                return 0.0  # Handle undefined variables as zero

        else:
            return parse_number()

    result = parse_expression()
    if peek() is not None:
        raise ValueError("Unexpected token at end of expression")

    return result


def tokenize(expr):
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
            if not current_token:
                current_token += char
            else:
                tokens.append(current_token)
                current_token = ""
                tokens.append(char)
        elif char == ')':
            if current_token:
                tokens.append(current_token)
                current_token = ""
            tokens.append(')')
        else:
            raise ValueError("Malformed syntax")

    if current_token:
        tokens.append(current_token)

    return tokens
