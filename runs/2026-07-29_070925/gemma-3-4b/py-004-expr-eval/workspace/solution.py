def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluates an arithmetic expression without using eval, exec, ast, or parsing libraries."""

    tokens = tokenize(expr)
    if tokens is None:
        raise ValueError("Malformed syntax")

    precedence = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '%': 2,
        '^': 3
    }

    def precedence_helper(op):
        return precedence.get(op, 0)

    output = []
    operators = []

    for token in tokens:
        if isinstance(token, int) or isinstance(token, float):
            output.append(token)
        elif token == '(':
            operators.append(token)
        elif token == ')':
            while operators and operators[-1] != '(':
                op = operators.pop()
                operand2 = output.pop()
                operand1 = output.pop()
                if op == '^' and precedence_helper(token) < precedence_helper(op):
                    output.append(operand1 ** operand2)
                else:
                    output.append(operand1 + operand2 if op == '+' or op == '-' else operand1 * operand2 if op == '*' or op == '/' else operand1 % operand2 if op == '%' else operand1 ** operand2)

            if not operators:
                raise ValueError("Unbalanced parentheses")
            operators.pop()  # Pop the '('
        elif token in precedence:
            while (operators and operators[-1] != '(' and
                   precedence_helper(token) <= precedence_helper(operators[-1])):
                op = operators.pop()
                operand2 = output.pop()
                operand1 = output.pop()
                if op == '^' and precedence_helper(token) < precedence_helper(op):
                    output.append(operand1 ** operand2)
                else:
                    output.append(operand1 + operand2 if op == '+' or op == '-' else operand1 * operand2 if op == '*' or op == '/' else operand1 % operand2 if op == '%' else operand1 ** operand2)
            operators.append(token)
        elif token.isalpha():
            if variables is None:
                raise ValueError(f"Unknown variable: {token}")
            output.append(variables[token])
        elif token == '-':
             if len(output) == 0:
                 output.append(token)
             else:
                  operand = output.pop()
                  if token == '-':
                      output.append(-operand)

                  else:
                     output.append(operand)
        else:
            raise ValueError(f"Malformed syntax: {token}")

    while operators:
        op = operators.pop()
        operand2 = output.pop()
        operand1 = output.pop()
        if op == '^' and precedence_helper(op) < precedence_helper('^'):
            output.append(operand1 ** operand2)
        else:
            output.append(operand1 + operand2 if op == '+' or op == '-' else operand1 * operand2 if op == '*' or op == '/' else operand1 % operand2 if op == '%' else operand1 ** operand2)

    if len(output) != 1:
        raise ValueError("Invalid expression")

    return float(output[0])


def tokenize(expr: str) -> list[str | int | float] | None:
    """Tokenizes an arithmetic expression."""
    tokens = []
    current_number = ""
    for char in expr:
        if char.isdigit() or char == '.':
            current_number += char
        elif char in '+-*/%^() ':
            if current_number:
                try:
                    tokens.append(float(current_number))
                    current_number = ""
                except ValueError:
                    return None
            tokens.append(char)
        elif char == '-':
             if len(tokens) == 0 :
                 current_number += char
             else:
                 tokens.append(char)

        else:
            return None  # Malformed syntax

    if current_number:
        try:
            tokens.append(float(current_number))
        except ValueError:
            return None
    return tokens
