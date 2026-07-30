import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression with support for basic operators,
    exponentiation (right-associative), unary minus, parentheses, and variables.
    """
    if variables is None:
        variables = {}

    # 1. Tokenization
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        char = expr[i]
        if char.isspace():
            i += 1
            continue
        
        if char.isdigit() or (char == '.' and i + 1 < n and expr[i+1].isdigit()):
            start = i
            has_dot = False
            if char == '.':
                has_dot = True
                i += 1
            while i < n and (expr[i].isdigit() or expr[i] == '.'):
                if expr[i] == '.':
                    if has_dot:
                        raise ValueError("Malformed number: multiple decimal points")
                    has_dot = True
                i += 1
            tokens.append(('NUM', float(expr[start:i])))
        elif char.isalpha() or char == '_':
            start = i
            i += 1
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            tokens.append(('VAR', expr[start:i]))
        elif char in '+-*/%^()':
            tokens.append(('OP', char))
            i += 1
        else:
            raise ValueError(f"Malformed syntax: unexpected character '{char}'")

    # 2. Shunting-yard algorithm to convert to RPN (Reverse Polish Notation)
    output_queue = []
    operator_stack = []
    
    # Precedence levels and associativity
    # Higher number means higher precedence.
    # '^' is right-associative, unary '-' is handled as a special operator 'u-'
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2, '^': 4, 'u-': 3}
    associativity = {'+': 'L', '-': 'L', '*': 'L', '/': 'L', '%': 'L', '^': 'R', 'u-': 'R'}

    last_token_is_op_or_open_paren = True # For detecting unary minus at start or after operator
    
    for token in tokens:
        t_type, t_val = token
        
        if t_type == 'NUM' or t_type == 'VAR':
            output_queue.append(token)
            last_token_is_op_or_open_paren = False
        elif t_val == '(':
            operator_stack.append('(')
            last_token_is_op_or_open_paren = True
        elif t_val == ')':
            while operator_stack and operator_stack[-1] != '(':
                output_queue.append(('OP', operator_stack.pop()))
            if not operator_stack:
                raise ValueError("Unbalanced parentheses")
            operator_stack.pop()  # Pop '('
            last_token_is_op_or_open_paren = False
        else: # Operator
            actual_op = t_val
            if actual_op == '-' and last_token_is_op_or_open_paren:
                actual_op = 'u-'
            
            while operator_stack and operator_stack[-1] != '(':
                top_op = operator_stack[-1]
                # Precedence rule for Shunting-yard
                if (associativity[actual_op] == 'L' and precedence[actual_op] <= precedence[top_op]) or \
                   (associativity[actual_op] == 'R' and precedence[actual_op] < precedence[top_op]):
                    output_queue.append(('OP', operator_stack.pop()))
                else:
                    break
            operator_stack.append(actual_op)
            last_token_is_op_or_open_paren = True

    while operator_stack:
        top = operator_stack.pop()
        if top == '(':
            raise ValueError("Unbalanced parentheses")
        output_queue.append(('OP', top))

    # 3. Evaluate RPN
    eval_stack = []
    for t_type, t_val in output_queue:
        if t_type == 'NUM':
            eval_stack.append(t_val)
        elif t_type == 'VAR':
            if t_val not in variables:
                raise ValueError(f"Unknown variable: {t_val}")
            eval_stack.append(float(variables[t_val]))
        else:  # Operator
            if t_val == 'u-':
                if not eval_stack:
                    raise ValueError("Malformed syntax")
                a = eval_stack.pop()
                eval_stack.append(-a)
            else:
                if len(eval_stack) < 2:
                    raise ValueError("Malformed syntax")
                b = eval_stack.pop() # second operand
                a = eval_stack.pop() # first operand
                if t_val == '+':
                    eval_stack.append(a + b)
                elif t_val == '-':
                    eval_stack.append(a - b)
                elif t_val == '*':
                    eval_stack.append(a * b)
                elif t_val == '/':
                    if b == 0:
                        raise ValueError("Division by zero")
                    eval_stack.append(a / b)
                elif t_val == '%':
                    if b == 0:
                        raise ValueError("Modulo by zero")
                    eval_stack.append(a % b)
                elif t_val == '^':
                    try:
                        # Use Python's pow for float exponentiation
                        eval_stack.append(float(pow(a, b)))
                    except ZeroDivisionError:
                        raise ValueError("Division by zero (exponentiation)")
                    except OverflowError:
                        raise ValueError("Result too large")
                    except Exception as e:
                        # Catching potential complex number results from negative bases and fractional exponents
                        if isinstance(e, ZeroDivisionError): raise ValueError("Division by zero")
                        raise ValueError(f"Math error in exponentiation: {str(e)}")

    if len(eval_stack) != 1:
        raise ValueError("Malformed syntax: expression did not reduce to a single value")
    
    return float(eval_stack[0])
