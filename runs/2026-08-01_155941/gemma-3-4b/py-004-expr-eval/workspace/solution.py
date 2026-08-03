def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluates arithmetic expressions without using eval(), exec(), ast, or parsing libraries."""

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
            return None

    def parse_variable():
        var_name = consume()
        if var_name is None:
            raise ValueError("Expected variable name")
        if variables and var_name in variables:
            return variables[var_name]
        else:
            raise ValueError(f"Unknown variable: {var_name}")

    def parse_unary_minus():
        if peek() == '-':
            consume()
            return -parse_expression()
        else:
            raise ValueError("Expected unary minus")

    def parse_primary():
        token = peek()
        if token is None:
            raise ValueError("Unexpected end of expression")

        if token.isdigit() or ('.' in token and all(c.isdigit() or c == '.' for c in token)):
            return parse_number()
        elif token == '(':
            consume()
            result = parse_expression()
            if peek() != ')':
                raise ValueError("Expected closing parenthesis")
            consume()
            return result
        elif token in ['+', '-', '*', '/', '%', '^']:
            return parse_binary_operator()
        elif token.isalpha():
            return parse_variable()
        else:
            raise ValueError(f"Unexpected token: {token}")

    def parse_expression():
        result = parse_unary_minus()
        while True:
            op = peek()
            if op is None:
                return result
            if op in ['+', '-', '*', '/', '%', '^']:
                next_token = consume()
                if next_token is None:
                    raise ValueError("Expected operand after operator")
                result = parse_binary_operator(op, result, next_token)
            else:
                return result

    def parse_binary_operator(op=None, left=None, right=None):
        if op is None:
          op = peek()

        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if right == 0:
                raise ValueError("Division by zero")
            return left / right
        elif op == '%':
            if right == 0:
                raise ValueError("Modulo by zero")
            return left % right
        elif op == '^':  # Right-associative exponentiation
            if right is None:
                return left ** left # Handles single exponentiation
            else:
                return left ** right
        else:
            raise ValueError(f"Unknown operator: {op}")

    try:
        result = parse_expression()
        if peek() is not None:
            raise ValueError("Unexpected token at end of expression")
        return result
    except ValueError as e:
        raise e


def tokenize(expr):
    tokens = []
    i = 0
    while i < len(expr):
        char = expr[i]
        if char.isspace():
            i += 1
            continue
        elif char.isdigit() or ('.' in char and all(c.isdigit() or c == '.' for c in char)):
            num_end = i
            while num_end < len(expr) and (expr[num_end].isdigit() or expr[num_end] == '.'):
                num_end += 1
            tokens.append(expr[i:num_end])
            i = num_end
        elif char in ['+', '-', '*', '/', '%', '^', '(', ')']:
            tokens.append(char)
            i += 1
        elif char.isalpha():
            name_end = i
            while name_end < len(expr) and (expr[name_end].isalnum() or expr[name_end] == '_'):
                name_end += 1
            tokens.append(expr[i:name_end])
            i = name_end
        else:
            raise ValueError(f"Unexpected character: {char}")

    return tokens
