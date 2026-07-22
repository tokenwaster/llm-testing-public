def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # Tokenize the expression
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in '()+-*/%^':
            tokens.append(c)
            i += 1
        elif c.isalpha() or c == '_':
            j = i + 1
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            var_name = expr[i:j]
            if var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            tokens.append(('var', var_name))
            i = j
        elif c.isdigit():
            j = i + 1
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            num_str = expr[i:j]
            if '.' in num_str:
                tokens.append(('num', float(num_str)))
            else:
                tokens.append(('num', int(num_str)))
            i = j
        else:
            raise ValueError(f"Invalid character: {c}")

    # Convert infix to postfix notation (Reverse Polish Notation)
    output = []
    operators = []
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2, '^': 3}
    associativity = {'+': 'left', '-': 'left', '*': 'left', '/': 'left', '%': 'left', '^': 'right'}

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if isinstance(token, tuple) and token[0] == 'num':
            output.append(token)
            i += 1
        elif isinstance(token, tuple) and token[0] == 'var':
            var_name = token[1]
            value = variables[var_name]
            output.append(('num', value))
            i += 1
        elif token == '(':
            operators.append(token)
            i += 1
        elif token == ')':
            while operators and operators[-1] != '(':
                output.append(operators.pop())
            if not operators or operators[-1] != '(':
                raise ValueError("Mismatched parentheses")
            operators.pop()  # Remove the '('
            i += 1
        else:  # Operator
            while (operators and operators[-1] != '(' and
                   ((associativity[token] == 'left' and precedence[token] <= precedence[operators[-1]]) or
                    (associativity[token] == 'right' and precedence[token] < precedence[operators[-1]]))):
                output.append(operators.pop())
            operators.append(token)
            i += 1

    while operators:
        if operators[-1] == '(':
            raise ValueError("Mismatched parentheses")
        output.append(operators.pop())

    # Evaluate postfix expression
    stack = []
    for token in output:
        if isinstance(token, tuple) and token[0] == 'num':
            stack.append(token[1])
        else:  # Operator
            if len(stack) < 2:
                raise ValueError("Invalid expression")
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                res = a + b
            elif token == '-':
                res = a - b
            elif token == '*':
                res = a * b
            elif token == '/':
                if b == 0:
                    raise ValueError("Division by zero")
                res = a / b
            elif token == '%':
                if b == 0:
                    raise ValueError("Modulo by zero")
                res = a % b
            elif token == '^':
                res = a ** b
            stack.append(res)

    if len(stack) != 1:
        raise ValueError("Invalid expression")

    return float(stack[0])
