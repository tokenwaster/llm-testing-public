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
        token = tokens[index]
        index += 1
        return token

    def parse_number():
        num_str = ""
        while index < len(tokens) and tokens[index].isdigit() or tokens[index] == ".":
            num_str += tokens[index]
            index += 1
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

    def parse_factor():
        token = peek()
        if token is None:
            raise ValueError("Unexpected end of expression")

        if token == '(':
            consume()
            result = parse_expression()
            if peek() != ')':
                raise ValueError("Unbalanced parentheses")
            consume()
            return result
        elif isinstance(token, str) and token.isdigit() or ('.' in token and all(c.isdigit() or c == '.' for c in token)):
            return parse_number()
        elif token == '+':
            consume()
            return parse_unary_minus()
        elif token == '-':
            consume()
            return parse_unary_minus()
        else:
            if token in variables:
                value = variables[token]
                if not isinstance(value, (int, float)):
                    raise ValueError("Variable must be a number")

                return value
            else:
                raise ValueError("Unknown variable")

    def parse_expression():
        result = parse_factor()

        while index < len(tokens) and is_operator(peek()):
            op = consume()
            if op == '+':
                result += parse_factor()
            elif op == '-':
                result -= parse_factor()
            elif op == '*':
                result *= parse_factor()
            elif op == '/':
                divisor = parse_factor()
                if divisor == 0:
                    raise ValueError("Division by zero")
                result /= divisor
            elif op == '%':
                divisor = parse_factor()
                if divisor == 0:
                    raise ValueError("Modulo by zero")
                result %= divisor
            elif op == '^':  # Right-associative exponentiation
                right = parse_factor()
                if right == 0:
                     return result**1 # handles case of 0^x where x is integer.
                result **= right
        return result

    def tokenize(expr):
        tokens = []
        current_token = ""
        for char in expr:
            if char.isspace():
                if current_token != "":
                    tokens.append(current_token)
                    current_token = ""
            elif char.isdigit() or char == '.':
                current_token += char
            elif char in "+-*/^":
                if current_token != "":
                    tokens.append(current_token)
                    current_token = ""
                tokens.append(char)
            elif char == "(":
                if current_token != "":
                    tokens.append(current_token)
                    current_token = ""
                tokens.append("(")
            elif char == ")":
                if current_token != "":
                    tokens.append(current_token)
                    current_token = ""
                tokens.append(")")
            elif char.isalpha() or char.isdigit():
                 current_token += char

            else:
                raise ValueError("Malformed syntax")

        if current_token != "":
            tokens.append(current_token)
        return tokens


    def is_operator(token):
        return token in "+-*/^"

    try:
        return parse_expression()
    except ValueError as e:
        raise e
