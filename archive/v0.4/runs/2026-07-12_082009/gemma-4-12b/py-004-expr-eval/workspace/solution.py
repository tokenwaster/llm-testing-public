import math

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression with standard precedence and right-associative exponentiation.
    Supports unary minus (looser than ^), binary operators (+, -, *, /, %, ^), 
    parentheses, and variables. No eval/exec/ast used.
    """
    if variables is None:
        variables = {}

    class Lexer:
        def __init__(self, text):
            self.text = text
            self.pos = 0

        def get_tokens(self):
            tokens = []
            i = 0
            while i < len(self.text):
                char = self.text[i]
                if char.isspace():
                    i += 1
                elif char.isdigit() or char == '.':
                    num_str = ""
                    while i < len(self.text) and (self.text[i].isdigit() or self.text[i] == '.'):
                        num_str += self.text[i]
                        i += 1
                    if num_str == '.':
                        raise ValueError("Invalid number")
                    tokens.append(('NUMBER', float(num_str)))
                elif char.isalpha() or char == '_':
                    var_str = ""
                    while i < len(self.text) and (self.text[i].isalnum() or self.text[i] == '_'):
                        var_str += self.text[i]
                        i += 1
                    tokens.append(('VARIABLE', var_str))
                elif char in '+-*/%^()':
                    tokens.append((char, char))
                    i += 1
                else:
                    raise ValueError(f"Unknown character: {char}")
            return tokens

    class Parser:
        def __init__(self, tokens, variables):
            self.tokens = tokens
            self.pos = 0
            self.variables = variables

        @property
        def current_token(self):
            if self.pos < len(self.tokens):
                return self.tokens[self.pos]
            return ('EOF', None)

        def advance(self):
            self.pos += 1

        def expression(self):
            # Addition and Subtraction (Left-associative, lowest precedence)
            res = self.term()
            while self.current_token in ('+', '-'):
                op = self.current_token[0]
                self.advance()
                res = self.apply_binary(res, op, self.term())
            return res

        def term(self):
            # Multiplication, Division, Modulo (Left-associative)
            res = self.factor()
            while self.current_token in ('*', '/', '%'):
                op = self.current_token[0]
                self.advance()
                res = self.apply_binary(res, op, self.factor())
            return res

        def factor(self):
            # Unary minus is evaluated after power (looser than ^)
            return self.unary_minus()

        def unary_minus(self):
            if self.current_token == '-':
                self.advance()
                # Recursive call handles repeated unary minuses like --3
                return -self.unary_minus()
            else:
                return self.power()

        def power(self):
            # Exponentiation (Right-associative, higher precedence than unary minus)
            res = self.primary()
            if self.current_token == '^':
                self.advance()
                exponent = self.power()
                return res ** exponent
            return res

        def primary(self):
            # Parentheses, Variables, and Numbers (Highest precedence)
            token = self.current_token
            if token[0] == 'NUMBER':
                self.advance()
                return token[1]
            elif token[0] == 'VARIABLE':
                self.advance()
                if token[1] not in self.variables:
                    raise ValueError(f"Unknown variable: {token[1]}")
                return self.variables[token[1]]
            elif token[0] == '(':
                self.advance()
                res = self.expression()
                if self.current_token != ')':
                    raise ValueError("Unbalanced parentheses")
                self.advance()
                return res
            else:
                raise ValueError(f"Unexpected token: {token}")

        def apply_binary(self, left, op, right):
            if op == '+': return left + right
            if op == '-': return left - right
            if op == '*': return left * right
            if op == '/':
                if right == 0: raise ValueError("Division by zero")
                return left / right
            if op == '%':
                if right == 0: raise ValueError("Modulo by zero")
                return left % right

    tokens = Lexer(expr).get_tokens()
    parser = Parser(tokens, variables)
    result = parser.expression()
    
    # Ensure all tokens were consumed to detect malformed syntax like "1+2 3"
    if parser.pos < len(tokens):
        raise ValueError("Malformed syntax")
        
    return float(result)
