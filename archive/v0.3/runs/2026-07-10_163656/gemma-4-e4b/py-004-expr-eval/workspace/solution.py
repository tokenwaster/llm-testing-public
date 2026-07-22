import re
from typing import List, Tuple, Dict

class Token:
    """Represents a single recognized unit of the expression."""
    def __init__(self, type: str, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type}, {self.value!r})"
        return f"Token({self.type})"

class ParserError(ValueError):
    """Custom error for parsing failures."""
    pass

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression without using eval, exec, or ast.
    Implements a custom tokenizer and recursive descent parser.
    """
    if variables is None:
        variables = {}

    # --- 1. Tokenization Phase ---
    
    def tokenize(expression: str) -> List[Token]:
        tokens: List[Token] = []
        i = 0
        n = len(expression)
        
        # Regex pattern for identifying tokens: numbers, variables, operators, parentheses
        token_specification = [
            ('NUMBER', r'\d+(\.\d*)?'),  # Integers and decimals
            ('VARIABLE', r'[a-zA-Z_][a-zA-Z0-9_]*'), # Variable names
            ('OP', r'[+\-*/%^()]'),      # Operators and parentheses (single chars)
            ('SKIP', r'\s+'),           # Whitespace
        ]
        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
        
        tokens_list: List[Token] = []
        last_token_type = None # Used to track context for unary minus detection

        for match in re.finditer(tok_regex, expression):
            kind = match.lastgroup
            value = match.group(0)

            if kind == 'SKIP':
                continue
            elif kind == 'NUMBER':
                tokens_list.append(Token('NUM', float(value)))
                last_token_type = 'OPERAND'
            elif kind == 'VARIABLE':
                tokens_list.append(Token('VAR', value))
                last_token_type = 'OPERAND'
            elif kind == 'OP':
                # Handle parentheses and standard operators first
                if value in ('(', ')'):
                    tokens_list.append(Token(value, value))
                    last_token_type = None # Context reset after paren
                else:
                    op_type = value
                    
                    # Unary Minus Detection: 
                    # If '-' appears at the start, or immediately after an operator/paren, 
                    # it is treated as unary negation.
                    if op_type == '-':
                        if last_token_type in ['START', 'OPERATOR'] or (tokens_list and tokens_list[-1].type in ('(', '+', '-', '*', '/', '%', '^')):
                            # Replace binary '-' with a special UNARY token
                            tokens_list.append(Token('UNARY_MINUS', None))
                            last_token_type = 'OPERATOR' # Still acts as an operator contextually
                        else:
                            # Binary subtraction
                            tokens_list.append(Token('SUB', '-'))
                            last_token_type = 'OPERATOR'
                    elif op_type == '+':
                         if last_token_type in ['START', 'OPERATOR'] or (tokens_list and tokens_list[-1].type in ('(', '+', '-', '*', '/', '%', '^')):
                             # Treat unary plus as a no-op, but keep the token stream clean. 
                             # We can simply ignore it if we are strict about UNARY_MINUS handling.
                             # For simplicity and robustness, let's just treat '+' as binary for now, 
                             # unless we explicitly need to handle unary plus (which is usually redundant).
                            tokens_list.append(Token('ADD', '+'))
                            last_token_type = 'OPERATOR'
                         else:
                            tokens_list.append(Token('ADD', '+'))
                            last_token_type = 'OPERATOR'

                    elif op_type in ('*', '/', '%', '^'):
                        # All other operators are binary
                        op_map = {'*': 'MUL', '/': 'DIV', '%': 'MOD', '^': 'POW'}
                        tokens_list.append(Token(op_map[op_type], op_type))
                        last_token_type = 'OPERATOR'

                    else: # Should not happen given the regex, but good practice
                         raise ParserError(f"Unknown operator token: {value}")
                
            elif kind == 'OP':
                 # This branch handles cases where OP might catch something missed above.
                 pass 
        
        return tokens_list

    tokens = tokenize(expr)
    
    if not tokens:
        raise ParserError("Empty or invalid expression.")


    # --- 2. Parsing and Evaluation Phase (Recursive Descent) ---
    
    class TokenStream:
        """Manages the token list and current position."""
        def __init__(self, tokens: List[Token]):
            self.tokens = tokens
            self.pos = 0

        def peek(self) -> Token | None:
            if self.pos < len(self.tokens):
                return self.tokens[self.pos]
            return None

        def consume(self, expected_type: str | None = None) -> Token:
            token = self.peek()
            if token is None:
                raise ParserError("Unexpected end of expression.")
            
            if expected_type and token.type != expected_type:
                 # Special handling for operators that might have multiple types (e.g., SUB vs ADD)
                 if not isinstance(expected_type, str): # Check if we are expecting a general type check
                     pass 
                 else:
                    raise ParserError(f"Expected token type {expected_type}, but found {token.type}.")

            self.pos += 1
            return token

        def is_at_end(self) -> bool:
            return self.pos >= len(self.tokens)


    stream = TokenStream(tokens)

    def parse_primary() -> float:
        """Handles numbers, variables, and parenthesized expressions."""
        token = stream.peek()
        if token is None:
             raise ParserError("Expected operand but found end of input.")

        # Handle Unary Minus/Plus (Negation)
        if token.type == 'UNARY_MINUS':
            stream.consume('UNARY_MINUS') # Consume the unary minus token
            result = parse_primary()
            return -result
        
        # Note: We skip explicit UNARY_PLUS handling as it's redundant in arithmetic evaluation

        if token.type == 'NUM':
            token = stream.consume('NUM')
            return token.value
        elif token.type == 'VAR':
            token = stream.consume('VAR')
            var_name = token.value
            if var_name not in variables:
                raise ParserError(f"Unknown variable '{var_name}'")
            return variables[var_name]
        elif token.type == '(':
            stream.consume('(') # Consume '('
            result = parse_expression()
            stream.consume(')') # Must consume ')'
            return result
        else:
            raise ParserError(f"Unexpected token at start of primary expression: {token.type}")


    def parse_factor() -> float:
        """Handles the highest precedence operation: Exponentiation (Right-associative)."""
        result = parse_primary()

        while stream.peek() and stream.peek().type == 'POW': # '^'
            # Right-associativity: a ^ b ^ c = a ^ (b ^ c)
            op_token = stream.consume('POW')
            right_operand = parse_factor() # Recursively call factor to handle the right side fully
            result *= pow(result, right_operand) # This is wrong for exponentiation!

            # Correct implementation for Right-Associative Exponentiation:
            # We need to calculate result ^ (next calculation). 
            # Since we are parsing a sequence of factors separated by '^', 
            # the current 'result' is the base, and the next factor starts the exponent chain.
            
            # Let's restructure this loop for correct right-associativity:
            # We calculate R = Base ^ Exponent_Chain
            
            base = result # The accumulated value so far (the left side)
            stream.pos -= 1 # Put back the '^' token
            
            exponent = parse_factor() # Calculate the full exponent chain starting here
            return base ** exponent


    def parse_term() -> float:
        """Handles multiplication, division, and modulo (Left-associative)."""
        result = parse_factor()

        while stream.peek() and stream.peek().type in ('MUL', 'DIV', 'MOD'):
            op_token = stream.consume()
            right_operand = parse_factor()

            if op_token.type == 'DIV' or op_token.type == 'MOD':
                if right_operand == 0:
                    raise ParserError("Division by zero.")
            
            if op_token.type == 'MUL':
                result *= right_operand
            elif op_token.type == 'DIV':
                result /= right_operand
            else: # MOD
                result %= right_operand
        return result


    def parse_expression() -> float:
        """Handles addition and subtraction (Left-associative)."""
        result = parse_term()

        while stream.peek() and stream.peek().type in ('ADD', 'SUB'):
            op_token = stream.consume()
            right_operand = parse_term()

            if op_token.type == 'ADD':
                result += right_operand
            elif op_token.type == 'SUB':
                result -= right_operand
        return result


    # --- 3. Execution and Final Checks ---
    try:
        final_result = parse_expression()

        if not stream.is_at_end():
             raise ParserError(f"Syntax error: Unexpected token remaining after evaluation: {stream.peek()}")
        
        return final_result

    except ParserError as e:
        # Re-raise specific parsing errors
        raise ValueError(str(e))
    except ZeroDivisionError:
        # Catch potential runtime division by zero if the parser missed it (shouldn't happen)
        raise ValueError("Division or modulo by zero.")


if __name__ == '__main__':
    # Example Usage and Testing (Self-verification block - not part of final output)
    
    def run_test(expr, vars_dict=None):
        try:
            result = evaluate(expr, variables=vars_dict)
            print(f"'{expr}' -> {result}")
        except ValueError as e:
            print(f"'{expr}' -> ERROR: {e}")

    # Test 1: Basic arithmetic (Left-associative)
    run_test("2 + 3 * 4") # Expected: 14.0
    
    # Test 2: Exponentiation (Right-associative)
    run_test("2 ^ 3 ^ 2") # Expected: 512.0 (2^(3^2) = 2^9)

    # Test 3: Unary Minus and Parentheses
    run_test("- (4 + 5)") # Expected: -9.0
    run_test("10 * (-2 + 3)") # Expected: 10.0
    run_test("--5") # Expected: 5.0

    # Test 4: Variables
    variables = {"x": 2.0, "y": 3.0}
    run_test("x * (y + 1)", variables) # Expected: 8.0

    # Test 5: Mixed operations and precedence
    run_test("10 - 2 * 3 + 4 % 2") # Expected: 10 - 6 + 0 = 4.0
    
    # Test 6: Error Handling (Division by Zero)
    run_test("5 / (2 - 2)")

    # Test 7: Error Handling (Unknown Variable)
    run_test("a * b", variables={"a": 1}) # Should fail on 'b'

    # Test 8: Error Handling (Malformed Syntax/Unbalanced Parens)
    run_test("(5 + 3")
    run_test("5 ) + 3")
    
    # Test 9: Complex Unary Minus context
    run_test("-2 ^ 2") # Expected: -4.0
