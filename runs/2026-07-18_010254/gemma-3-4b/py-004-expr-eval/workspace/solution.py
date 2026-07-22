def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluates arithmetic expressions without using eval, exec, ast, or parsing libraries."""

    tokens = tokenize(expr)
    if not tokens:
        raise ValueError("Invalid expression")

    values = []
    operators = []

    precedence = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '%': 2,
        '^': 3  # Right-associative exponentiation
    }

    def apply_op():
        if not operators:
            return values[0]

        op = operators.pop()
        right = values.pop()
        left = values.pop()

        if op == '^':
            result = left ** right
        else:
            result = left + right if op in ('+', '-') else \
                    left * right if op in ('*', '/') else \
                    left % right if op == '%' else \
                    left  # Handle other operators

        values.append(result)

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token.isdigit() or (token.startswith('.') and token[1:].isdigit()):
            values.append(float(token))
        elif token == '(':
            operators.append(token)
        elif token == ')':
            while operators and operators[-1] != '(':
                apply_op()
            if not operators:
                raise ValueError("Unbalanced parentheses")
            operators.pop()  # Pop the '('
        elif token in precedence:
            while operators and operators[-1] != '(' and \
                  precedence[operators[-1]] >= precedence[token]:
                apply_op()
            operators.append(token)
        elif token == '-':
            if i > 0 and tokens[i - 1].isdigit() or (tokens[i-1].startswith('.') and tokens[i-1][1:].isdigit()):
                values[-1] = -values[-1]
            else:
                operators.append(token)
        else:
            raise ValueError(f"Unknown token: {token}")

        i += 1

    while operators:
        apply_op()

    if len(values) != 1:
        raise ValueError("Invalid expression")

    return values[0]


def tokenize(expr: str) -> list[str]:
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
        elif char in '+-*/^(':
            if current_token:
                tokens.append(current_token)
                current_token = ""
            tokens.append(char)
        elif char == '-':
            if not current_token:
                current_token += char
            else:
                tokens.append(current_token)
                current_token = char
        else:
            raise ValueError(f"Invalid character: {char}")

    if current_token:
        tokens.append(current_token)

    return tokens
