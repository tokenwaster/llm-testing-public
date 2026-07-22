import math

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    # Tokenize the expression
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
            continue
        
        # Check for number (integer or decimal)
        if expr[i] in '0123456789.':
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            num_str = expr[i:j]
            # Convert to float for consistency
            tokens.append(float(num_str))
            i = j
        elif expr[i] in '+-*/%^':
            tokens.append(expr[i])
            i += 1
        else:
            # Variable or other characters (should be resolved from dict)
            if expr[i].isalpha() or expr[i] == '_':
                var_name = expr[i]
                if var_name not in variables:
                    raise ValueError(f"Unknown variable: {var_name}")
                tokens.append(var_name)
                i += 1
            else:
                raise ValueError("Invalid character")
    
    # Shunting-yard algorithm to convert infix to postfix
    def precedence(op):
        if op == '^':
            return 3
        elif op in ('*', '/'):
            return 2
        elif op in ('+', '-'):
            return 1
        else:
            return 0
    
    def is_right_associative(op):
        return op == '^'
    
    def apply_op(op, a, b):
        if op == '+':
            return a + b
        elif op == '-':
            return a - b
        elif op == '*':
            return a * b
        elif op == '/':
            if b == 0:
                raise ValueError("Division by zero")
            return a / b
        elif op == '%':
            if b == 0:
                raise ValueError("Modulo by zero")
            return a % b
        else:
            raise ValueError(f"Unknown operator: {op}")
    
    output = []
    op_stack = []
    
    for token in tokens:
        if isinstance(token, float):
            output.append(token)
        elif token == '(':
            op_stack.append(token)
        elif token == ')':
            while op_stack and op_stack[-1] != '(':
                output.append(op_stack.pop())
            if not op_stack or op_stack[-1] != '(':
                raise ValueError("Unbalanced parentheses")
            op_stack.pop()  # remove '('
        elif token in ('+', '-', '*', '/', '%'):
            while op_stack and op_stack[-1] in ('*', '/') and (is_right_associative(op_stack[-1]) or precedence(op_stack[-1]) >= precedence(token)):
                output.append(op_stack.pop())
            op_stack.append(token)
        elif token == '^':
            while op_stack and op_stack[-1] in ('*', '/') and (is_right_associative(op_stack[-1]) or precedence(op_stack[-1]) >= precedence(token)):
                output.append(op_stack.pop())
            if is_right_associative(token) and len(op_stack) < 2:
                op_stack.append(token)
        else:  # variable token
            var_name = token
            if var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            output.append(var_name)
    
    while op_stack:
        top_op = op_stack.pop()
        if top_op == '(' or top_op == ')':
            raise ValueError("Unbalanced parentheses")
        output.append(top_op)
    
    # Evaluate postfix expression
    def eval_postfix(postfix):
        stack = []
        for token in postfix:
            if isinstance(token, float):
                stack.append(float(token))
            else:  # operator
                b = stack.pop()
                a = stack.pop()
                try:
                    result = apply_op(token, a, b)
                    stack.append(result)
                except ValueError as e:
                    raise ValueError(f"Error evaluating expression: {e}")
        return stack[0]
    
    postfix_expr = output
    if variables is not None:
        for var in postfix_expr:
            if var not in variables:
                raise ValueError(f"Unknown variable: {var}")
    
    return eval_postfix(postfix_expr)
