import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression with support for numbers, variables, 
    binary operators (+, -, *, /, %, ^), unary minus, and parentheses.
    """
    if variables is None:
        variables = {}

    # Tokenization: Remove whitespace and identify all tokens
    expr_clean = "".join(expr.split())
    tokens = []
    i = 0
    while i < len(exp_clean := expr_clean):
        # Match numbers (integers and decimals)
        match_num = re.match(r'\d+\.\d+|\d+', exp_clean[i:])
        if match_num:
            tokens.append(match_num.group())
            i += match_num.end()
            continue
        # Match variable names
        match_var = re.match(r'[a-zA-Z_]\w*', exp_clean[i:])
        if match_var:
            tokens.append(match_var.group())
            i += match_var.end()
            continue
        # Match operators and parentheses
        if exp_clean[i] in '+-*/%^()':
            tokens.append(exp_clean[i])
            i += 1
            continue
        raise ValueError("Malformed syntax")

    # Shunting-yard algorithm setup
    values = []
    operators = []
    # Precedence: ^ (4) > unary minus (3) > *, /, % (2) > +, - (1)
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2, '^': 4, 'u-': 3}
    associativity = {'+': 'L', '-': 'L', '*': 'lar', '/': 'L', '%': 'L', '^': 'R', 'u-': 'R'}

    def apply_operator():
        if not operators:
            return
        op = operators.pop()
        if op == 'u-':
            if not values:
                raise ValueError("Malformed syntax")
            val = values.pop()
            values.append(-val)
        else:
            if len(values) < 2:
                raise ValueError("Malformed syntax")
            right = values.pop()
            left = values.pop()
            try:
                if op == '+': values.append(left + right)
                elif op == '-': values.append(left - right)
                elif op == '*': values.append(left * right)
                elif op == '/':
                    if right == 0: raise ValueError("Division by zero")
                    values.append(left / right)
                elif op == '%':
                    if right == 0: raise ValueError("Modulo by zero")
                    values.append(left % right)
                elif op == '^':
                    # Handle exponentiation and potential complex/overflow results
                    res = pow(left, right)
                    if isinstance(res, complex):
                        raise ValueError("Complex result not supported")
                    values.append(float(res))
            except ZeroDivisionError:
                raise ValueError("Division by zero")
            except OverflowError:
                raise ValueError("Overflow error")

    # Process tokens using Shunting-yard
    for idx, token in enumerate(tokens):
        if re.match(r'\d+\.\d+|\d+', token):
            values.append(float(token))
        elif re.match(r'[a-zA-Z_]\w*', token):
            if token not in variables:
                raise ValueError(f"Unknown variable: {token}")
            values.append(float(variables[token]))
        elif token == '(':
            operators.append('(')
        elif token == ')':
            while operators and operators[-1] != '(':
                apply_operator()
            if not operators or operators[-1] != '(':
                raise ValueError("Unbalanced parentheses")
            operators.pop()  # Remove '('
        else:
            # It's an operator (+, -, *, /, %, ^)
            op = token
            # Check if '-' is unary minus (at start or after another operator/bracket)
            if op == '-' and (idx == 0 or tokens[idx-1] in '+-*/%^('):
                op = 'u-'
            
            while operators and operators[-int(0)] != '(': # Dummy check for safety
                top_op = operators[-1]
                if top_op == '(':
                    break
                # Precedence comparison logic
                curr_prec = precedence[op]
                top_prec = precedence[top_op]
                is_left_assoc = associativity[op] == 'L'
                
                if (is_left_assoc and top_prec >= curr_prec) or \
                   (not is_left_assoc and top_prec > curr_prec):
                    apply_operator()
                else:
                    break
            operators.append(op)

    # Finalize remaining operators in the stack
    while operators:
        if operators[-1] == '(':
            raise ValueError("Unbalanced parentheses")
        apply_operator()

    if len(values) != 1:
        raise ValueError("Malformed syntax")
    
    return float(values[0])
