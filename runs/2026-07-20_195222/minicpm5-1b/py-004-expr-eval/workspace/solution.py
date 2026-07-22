class Token:
    def __init__(self, kind):
        self.kind = kind  # 'NUMBER', 'OPERATOR', 'PAREN', or 'VARIABLE'
        self.value = None


def evaluate(expr: str, variables=None) -> float:
    """
    Evaluates arithmetic expressions without using eval/exec/ast.
    Grammar supported: numbers (int/decimal), operators (+ - * / % ^),
    parentheses, unary minus, variables from dict, whitespace.
    Raises ValueError for malformed syntax, unbalanced parentheses,
    division by zero, unknown variables.
    """

    # ---------- tokenization ----------
    tokens = []
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue

        elif ch.isdigit() or ch == '.':
            # parse a number (integer or decimal)
            num_str = ''
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                if expr[i] == '.':
                    num_str += '.'
                else:
                    num_str += expr[i]
                i += 1
            tokens.append(Token('NUMBER', num_str))
        elif ch in {'+', '-', '*', '/', '%', '^'}:
            tokens.append(Token('OPERATOR', ch))
            i += 1
        elif ch == '(' or ch == ')':
            tokens.append(Token('PAREN', ch))
            i += 1
        else:
            raise ValueError(f"Unexpected character: {ch}")

    # ---------- shunting-yard algorithm to produce postfix ----------
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 3, '^': 3}
    left_associative = {'+', '-', '*', '/'}
    right_associative = {'^'}

    def is_right_assoc(op):
        return op == '^'

    output = []
    operator_stack = []

    for token in tokens:
        if token.kind == 'NUMBER':
            output.append(token.value)
        elif token.kind == 'PAREN':
            if token.kind == '(':
                operator_stack.append(Token('PAREN'))
            else:  # ')'
                while operator_stack and operator_stack[-1].kind != 'PAREN':
                    output.append(operator_stack.pop().value)
                if not operator_stack or operator_stack[-1].kind == 'PAREN':
                    raise ValueError("Unbalanced parentheses")
                operator_stack.pop()  # remove '('
        elif token.kind == 'OPERATOR':
            while operator_stack and operator_stack[-1].kind != 'PAREN' \
                  and (token.kind in {'+', '-', '*', '/'} or is_right_assoc(operator_stack[-1])):
                top_op = operator_stack[-1]
                if is_right_assoc(top_op) and precedence[top_op] >= precedence[token]:
                    output.append(operator_stack.pop().value)
                else:
                    break
            operator_stack.append(Token('OPERATOR', token))
        elif token.kind == 'VARIABLE':
            var_val = variables.get(token.value, None)
            if var_val is None:
                raise ValueError(f"Unknown variable: {token.value}")
            output.append(float(var_val))
        else:
            raise ValueError(f"Unknown token: {token.kind}")

    # pop remaining operators
    while operator_stack:
        op = operator_stack.pop()
        if op.kind == 'PAREN' or op.kind == 'OPERATOR':
            raise ValueError("Unbalanced parentheses")
        output.append(op.value)

    # ---------- evaluate postfix expression ----------
    stack = []
    for token in output:
        if token.kind == 'NUMBER':
            stack.append(float(token.value))
        else:
            b = stack.pop()
            a = stack.pop()
            if token.kind == '+':
                stack.append(a + b)
            elif token.kind == '-':
                stack.append(a - b)
            elif token.kind == '*':
                stack.append(a * b)
            elif token.kind == '/':
                if b == 0:
                    raise ValueError("Division by zero")
                stack.append(a / b)
            elif token.kind == '%':
                if b == 0:
                    raise ValueError("Modulo by zero")
                stack.append(a % b)
            elif token.kind == '^':
                stack.append(b ** a)
            else:
                raise ValueError(f"Unknown operator: {token}")

    return stack[0]
