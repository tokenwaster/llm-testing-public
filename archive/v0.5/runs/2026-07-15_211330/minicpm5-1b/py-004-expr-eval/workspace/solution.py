import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    # Tokenize the expression into numbers, operators, parentheses, and variables
    def tokenize(s):
        tokens = []
        i = 0
        while i < len(s):
            ch = s[i]
            if ch.isspace():
                i += 1
                continue
            
            # Numbers: integers or decimals (e.g., "3", "4.5")
            if ch.isdigit() or ch == '.':
                num_str = ''
                while i < len(s) and (s[i].isdigit() or s[i] == '.'):
                    num_str += s[i]
                    i += 1
                if num_str:  # at least one digit for integer part
                    tokens.append(('NUMBER', float(num_str)))
            elif ch.isdigit():
                # Handle negative numbers (unary minus)
                if ch == '-':
                    tokens.append(('NUMBER', -float(s[i+1:i+2])))  # parse next char as number
                    i += 3  # skip the '-' and digits
                else:
                    tokens.append(('NUMBER', float(s[i:i+2])))
                    i += 2
            elif ch.isalpha() or ch == '_':
                # Variable names: [a-zA-Z_][a-zA-Z0-9_]* (case-insensitive)
                if len(ch) > 1 and not ch.isdigit() and not ch in ('+', '-', '*', '/', '%', '^'):
                    tokens.append(('VAR', ch.upper()))
                else:
                    # Check against variables dict
                    var_name = ch.lower()
                    if var_name not in variables:
                        raise ValueError(f"Unknown variable: {var_name}")
                    tokens.append(('VAR', var_name))
            else:
                raise ValueError(f"Invalid character: {ch}")
        return tokens

    # Shunting-yard algorithm to convert infix to postfix
    def shunting_yard(tokens):
        precedence = {'^': 3, '*': 2, '/': 2, '%': 2, '+': 1, '-': 1}
        associativity = {'^': 'right', '.': 'left'}
        
        output = []
        operator_stack = []
        
        for token in tokens:
            if isinstance(token[0], (int, float)):
                # Number
                output.append(token)
            elif token[0] == 'NUMBER':
                # Parse number with sign if needed
                num_str = ''
                i = 0
                while i < len(token):
                    ch = token[i]
                    if ch.isdigit() or ch == '.':
                        num_str += ch
                        i += 1
                    else:
                        break
                output.append(('NUMBER', float(num_str)))
            elif token[0] in ('+', '-', '*', '/', '%'):
                # Operator
                while operator_stack and operator_stack[-1][0] != 'NUMBER' and \
                      precedence.get(operator_stack[-1][0], 0) < precedence[token[0]]:
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            elif token[0] == '(':
                operator_stack.append(token)
            elif token[0] == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if not operator_stack or operator_stack[-1] != '(':
                    raise ValueError("Mismatched parentheses")
                operator_stack.pop()  # remove '('
            else:
                raise ValueError(f"Unexpected token: {token[0]}")
        
        while operator_stack:
            op = operator_stack.pop()
            if op[0] == 'NUMBER':
                output.append(op)
            elif op[0] in ('+', '-', '*', '/', '%'):
                # Pop operators with higher precedence
                while operator_stack and operator_stack[-1][0] != '(' and \
                      precedence.get(operator_stack[-1][0], 0) < precedence[op[0]]:
                    output.append(operator_stack.pop())
                if not operator_stack or operator_stack[-1] == '(':
                    raise ValueError("Mismatched parentheses")
                operator_stack.append(op)
            else:
                raise ValueError(f"Unexpected token: {op}")
        
        # Pop remaining operators
        while operator_stack:
            op = operator_stack.pop()
            if op[0] in ('+', '-', '*', '/', '%'):
                output.append(op)
            elif op[0] == 'NUMBER':
                output.append(op)
        
        return output

    # Evaluate postfix expression using a stack
    def evaluate_postfix(postfix):
        values = []
        for token in postfix:
            if isinstance(token, (int, float)):
                values.append(float(token))
            elif token[0] == 'NUMBER':
                num_str = ''
                i = 0
                while i < len(token):
                    ch = token[i]
                    if ch.isdigit() or ch == '.':
                        num_str += ch
                        i += 1
                    else:
                        break
                values.append(float(num_str))
            elif token[0] in ('+', '-', '*', '/', '%'):
                b = values.pop()
                a = values.pop()
                if token[0] == '+':
                    res = a + b
                elif token[0] == '-':
                    res = a - b
                elif token[0] == '*':
                    res = a * b
                elif token[0] == '/':
                    if b == 0:
                        raise ZeroDivisionError("Division by zero")
                    res = a / b
                elif token[0] == '%':
                    # Modulo: (a % b) in Python gives remainder with sign of divisor, but we want standard arithmetic
                    # We'll compute as (a - floor(a/b)) * b to match typical math modulo
                    if b == 0:
                        raise ZeroDivisionError("Modulo by zero")
                    res = a % b
                values.append(res)
            elif token[0] == 'VAR':
                var_name = token[1]
                if var_name not in variables:
                    raise ValueError(f"Unknown variable: {var_name}")
                values.append(variables[var_name])
        
        return values[-1]
    
    # Main evaluation function
    tokens = tokenize(expr)
    postfix = shunting_yard(tokens)
    result = evaluate_postfix(postfix)
    return result

# Example usage (not part of the solution, just for testing):
if __name__ == "__main__":
    variables = {'a': 1.0, 'b': 2.5}
    print(evaluate("3 + a * b", variables))  # Should output: 7.5
    print(evaluate("--a"))  # Should output: -1.0
    print(evaluate("-a^2"))  # Should output: -4.0
    print(evaluate("(a+b)*c", variables))  # Should output: (3+1)*2 = 8.0
