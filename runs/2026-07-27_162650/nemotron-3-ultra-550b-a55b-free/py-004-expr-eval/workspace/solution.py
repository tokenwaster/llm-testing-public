class Token:
    __slots__ = ('type', 'value')
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __repr__(self):
        return f'Token({self.type}, {self.value!r})'

class Tokenizer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ''
        dot_count = 0
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            result += self.current_char
            self.advance()
        if result == '' or result == '.':
            raise ValueError("Invalid number format")
        return float(result)

    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit() or self.current_char == '.':
                return Token('NUMBER', self.number())
            if self.current_char.isalpha() or self.current_char == '_':
                ident = self.identifier()
                return Token('IDENTIFIER', ident)
            if self.current_char == '+':
                self.advance()
                return Token('PLUS', '+')
            if self.current_char == '-':
                self.advance()
                return Token('MINUS', '-')
            if self.current_char == '*':
                self.advance()
                return Token('MUL', '*')
            if self.current_char == '/':
                self.advance()
                return Token('DIV', '/')
            if self.current_char == '%':
                self.advance()
                return Token('MOD', '%')
            if self.current_char == '^':
                self.advance()
                return Token('POW', '^')
            if self.current_char == '(':
                self.advance()
                return Token('LPAREN', '(')
            if self.current_char == ')':
                self.advance()
                return Token('RPAREN', ')')
            raise ValueError(f"Invalid character: {self.current_char}")
        return Token('EOF', None)

class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.current_token = self.tokenizer.get_next_token()

    def advance(self):
        self.current_token = self.tokenizer.get_next_token()

    def parse(self):
        node = self.parse_expression()
        if self.current_token.type != 'EOF':
            raise ValueError("Unexpected token at end of expression")
        return node

    def parse_expression(self):
        node = self.parse_term()
        while self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token.type
            self.advance()
            right = self.parse_term()
            node = BinOp(node, op, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token.type in ('MUL', 'DIV', 'MOD'):
            op = self.current_token.type
            self.advance()
            right = self.parse_factor()
            node = BinOp(node, op, right)
        return node

    def parse_factor(self):
        if self.current_token.type == 'MINUS':
            self.advance()
            operand = self.parse_factor()
            return UnaryOp('-', operand)
        return self.parse_power()

    def parse_power(self):
        node = self.parse_primary()
        if self.current_token.type == 'POW':
            self.advance()
            exponent = self.parse_factor()
            node = BinOp(node, '^', exponent)
        return node

    def parse_primary(self):
        token = self.current_token
        if token.type == 'NUMBER':
            self.advance()
            return Num(token.value)
        elif token.type == 'IDENTIFIER':
            self.advance()
            return Var(token.value)
        elif token.type == 'LPAREN':
            self.advance()
            node = self.parse_expression()
            if self.current_token.type != 'RPAREN':
                raise ValueError("Unbalanced parentheses")
            self.advance()
            return node
        else:
            raise ValueError(f"Unexpected token: {token.type}")

class Num:
    __slots__ = ('value',)
    def __init__(self, value):
        self.value = value

class Var:
    __slots__ = ('name',)
    def __init__(self, name):
        self.name = name

class BinOp:
    __slots__ = ('left', 'op', 'right')
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp:
    __slots__ = ('op', 'operand')
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class Evaluator:
    def __init__(self, variables):
        self.variables = variables or {}

    def evaluate(self, node):
        if isinstance(node, Num):
            return node.value
        elif isinstance(node, Var):
            name = node.name
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(self.variables[name])
        elif isinstance(node, UnaryOp):
            if node.op == '-':
                return -self.evaluate(node.operand)
            else:
                raise ValueError(f"Unknown unary operator: {node.op}")
        elif isinstance(node, BinOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == '+':
                return left + right
            elif node.op == '-':
                return left - right
            elif node.op == '*':
                return left * right
            elif node.op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                return left / right
            elif node.op == '%':
                if right == 0:
                    raise ValueError("Modulo by zero")
                return left % right
            elif node.op == '^':
                try:
                    result = left ** right
                except ZeroDivisionError:
                    raise ValueError("Division by zero in exponentiation")
                except OverflowError:
                    raise ValueError("Overflow in exponentiation")
                if isinstance(result, complex):
                    raise ValueError("Complex result not allowed")
                return float(result)
            else:
                raise ValueError(f"Unknown binary operator: {node.op}")
        else:
            raise ValueError(f"Unknown node type: {type(node)}")

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokenizer = Tokenizer(expr)
    parser = Parser(tokenizer)
    ast = parser.parse()
    evaluator = Evaluator(variables)
    return evaluator.evaluate(ast)
