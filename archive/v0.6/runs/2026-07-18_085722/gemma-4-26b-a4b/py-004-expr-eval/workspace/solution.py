class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.variables = variables if variables is not None else {}
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_val=None):
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        if expected_ast_val := expected_val:
            if token[1] != expected_ast_val:
                raise ValueError(f"Expected {expected_ast_val}, got {token[1]}")
        self.pos += 1
        return token

    def parse_expr(self):
        # expr = term { ('+' | '-') term }
        node = self.parse_term()
        while self.peek() and self.peek()[1] in ('+', '-'):
            op = self.consume()[1]
            right = self.parse_term()
            node = (op, node, right)
        return node

    def parse_term(self):
        # term = unary_minus_part { ('*' | '/' | '%') unary_minus_part }
        node = self.parse_unary_minus_part()
        while self.peek() and self.peek()[1] in ('*', '/', '%'):
            op = self.consume()[1]
            right = self.parse_unary_minus_part()
            node = (op, node, right)
        return node

    def parse_unary_minus_part(self):
        # unary_minus_part = power | '-' unary_minus_part
        if self.peek() and self.peek()[1] == '-':
            self.consume('-')
            node = self.parse_unary_minus_part()
            return ('u-', node)
        else:
            return self.parse_power()

    def parse_power(self):
        # power = atom { '^' power } (Right-associative)
        node = self.parse_atom()
        if self.peek() and self.peek()[1] == '^':
            op = self.consume()[1]
            right = self.parse_power()
            node = (op, node, right)
        return node

    def parse_atom(self):
        # atom = NUMBER | VARIABLE | '(' expr ')'
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        
        t_type, t_val = token
        if t_type == 'NUM':
            return self.consume()[1]
        elif t_type == 'VAR':
            var_name = self.consume()[1]
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return float(self.variables[var_name])
        elif t_type == 'OP' and t_val == '(':
            self.consume('(')
            node = self.parse_expr()
            self.consume(')')
            return node
        else:
            raise ValueError("Malformed syntax")

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    # Tokenizer
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
            continue
        if expr[int(i)].isdigit() or (expr[i] == '.' and i + 1 < len(expr) and expr[i+1].isdigit()):
            start = i
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                i += 1
            tokens.append(('NUM', float(expr[start:i])))
            continue
        if expr[i].isalpha() or expr[i] == '_':
            start = i
            while i < len(expr) and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            tokens.append(('VAR', expr[start:i]))
            continue
        if expr[i] in '+-*/%^()':
            tokens.append(('OP', expr[i]))
            i += 1
            continue
        raise ValueError("Malformed syntax")

    # Parser and Evaluator
    parser = Parser(tokens, variables)
    try:
        ast = parser.parse_expr()
        if parser.pos < len(tokens):
            raise ValueError("Malformed syntax")
    except (IndexError, KeyError):
        raise ValueError("Malformed syntax")

    def eval_ast(node):
        if not isinstance(node, tuple):
            return node
        
        op = node[0]
        if op == 'u-':
            return -eval_ast(node[1])
        
        left = eval_ast(node[1])
        right = eval_ast(node[2])
        
        if op == '+': return left + right
        if op == '-': return left - right
        if op == '*': return left * right
        if op == '/':
            if right == 0: raise ValueError("Division by zero")
            return left / right
        if op == '%':
            if right == 0: raise ValueError("Modulo by zero")
            return left % right
        if op == '^':
            try:
                return float(left ** right)
            except ZeroDivisionError:
                raise ValueError("Division by zero")
            except Exception:
                # Handle complex number errors or overflow if necessary
                raise ValueError("Malformed syntax")
        raise ValueError("Malformed syntax")

    result = eval_ast(ast)
    return float(result)
