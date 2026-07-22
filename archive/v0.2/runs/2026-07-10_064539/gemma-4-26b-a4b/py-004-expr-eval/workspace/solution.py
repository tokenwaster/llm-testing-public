import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression without using eval, exec, ast, or parsing libraries.
    Supports numbers, variables, binary operators (+, -, *, /, %, ^), unary minus, and parentheses.
    """
    # 1. Tokenize the expression
    try:
        # Remove all whitespace from the expression
        expr_clean = "".join(expr.split())
        # Regex to capture numbers (integers/decimals), variables, and operators/parentheses
        token_pattern = r'(\d+(?:\.\d+)?|[a-zA-Z_][a-zA-Z0-9_]*|[\+\-\*\/\%\^\(\)])'
        tokens = []
        last_end = 0
        for match in re.finditer(token_pattern, expr_clean):
            if match.start() != last_end:
                raise ValueError("Malformed syntax")
            tokens.append(match.group(0))
            last_end = match.end()
        if last_end != len(expr_clean):
            raise ValueError("Malformed syntax")
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError("Malformed syntax")

    # 2. Shunting-yard algorithm (Infix to Postfix)
    output = []
    stack = []
    # Precedence levels: ^ is highest, then unary minus, then *, /, %, then +, -
    prec = {'^': 3, 'u-': 2, '*': 1, '/': 1, '%': 1, '+': 0, '-': 0}
    # Associativity: ^ and u- are right-associative; others are left-associative
    assoc = {'^': 'R', 'u-': '                R', '*': 'L', '/': 'L', '%': 'L', '+': 'L', '-': 'L'}
    prev_token_is_op = True  # Tracks if the next '-' should be treated as unary

    for token in tokens:
        if re.fullmatch(r'\d+(?:\.\d+)?', token):
            output.append(token)
            prev_token_is_op = False
        elif re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', token):
            output.append(token)
            prev_token_is_op = False
        elif token == '(':
            stack.append('(')
            prev_token_is_op = True
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if not stack:
                raise ValueError("Unbalanced parentheses")
            stack.pop()  # Remove '('
            prev_token_is_op = False
        elif token in '+-*/%^':
            op = token
            # Identify unary minus
            if op == '-' and prev_token_is_op:
                op = 'u-'
            
            # Standard Shunting-yard precedence/associativity logic
            while stack and stack[-1] != '(' and (
                prec[stack[-1]] > prec[op] or
                (prec[stack[-1]] == prec[op] and assoc[op] == 'L')
            ):
                output.append(stack.pop())
            stack.append(op)
            prev_token_is_op = True
        else:
            raise ValueError("Malformed syntax")

    while stack:
        if stack[-1] == '(':
            raise ValueError("Unbalanced parentheses")
        output.append(stack.pop())

    # 3. Evaluate the Postfix (RPN) expression
    eval_stack = []
    for token in output:
        if re.fullmatch(r'\d+(?:\.\d+)?', token):
            eval_stack.append(float(token))
        elif re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', token):
            if variables is None or token not in variables:
                raise ValueError(f"Unknown variable: {token}")
            eval_stack.append(float(variables[token]))
        elif token == 'u-':
            if not eval_stack:
                raise ValueError("Malformed syntax")
            val = eval_stack.pop()
            eval_stack.append(-val)
        else:  # Binary operator
            if len(eval_stack) < 2:
                raise ValueError("Malformed syntax")
            b = eval_stack.pop()
            a = eval_stack.pop()
            try:
                if token == '+':
                    eval_stack.append(a + b)
                elif token == '-':
                    eval_stack.append(a - b)
                elif token == '*':
                    eval_stack.append(a * b)
                elif token == '/':
                    if b == 0:
                        raise ValueError("Division by zero")
                    eval_stack.append(a / b)
                elif token == '%':
                    if b == 0:
                        raise ValueError("Division by zero")
                    eval_stack.append(a % b)
                elif token == '^':
                    # Handle potential complex results (e.g., (-2)^0.5)
                    res = a ** b
                    if isinstance(res, complex):
                        raise ValueError("Result is not a real number")
                    eval_stack.append(float(res))
                else:
                    raise ValueError("Malformed syntax")
            except ZeroDivisionError:
                raise ValueError("Division by zero")
            except Exception as e:
                if isinstance(e, ValueError):
                    raise e
                raise ValueError("Malformed syntax")

    if len(eval_stack) != 1:
        raise ValueError("Malformed syntax")
    return float(eval_stack[0])
