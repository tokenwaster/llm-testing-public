import re
from typing import List, Tuple, Dict

class Token:
    """Represents a single token."""
    def __init__(self, type: str, value: any = None):
        self.type = type  # e.g., 'NUMBER', 'VARIABLE', 'OP', 'LPAREN', 'RPAREN'
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"

class ParserError(ValueError):
    """Custom error for parsing failures."""
    pass

def tokenize(expr: str) -> List[Token]:
    """Converts the input string into a list of tokens."""
    # Regex pattern to match numbers, variables, operators, and parentheses.
    # It handles whitespace implicitly by ignoring it during matching.
    token_specification = [
        ('NUMBER', r'\d+(\.\d*)?'),  # Integers or decimals
        ('VARIABLE', r'[a-zA-Z_][a-zA-Z0-9_]*'), # Variable names
        ('OP', r'[\+\-\*/%^]'),      # Operators (+, -, *, /, %, ^)
        ('LPAREN', r'\('),          # Left parenthesis
        ('RPAREN', r'\)'),          # Right parenthesis
        ('SKIP', r'[ \t]+')         # Whitespace (to be ignored)
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    
    tokens: List[Token] = []
    for match in re.finditer(tok_regex, expr):
        token_type = None
        value = None
        
        # Determine the type and value based on which group matched
        for name, pattern in token_specification:
            if name == 'SKIP':
                continue
            elif match.group(name) is not None:
                token_type = name
                value = match.group(name)
                break

        if token_type:
            tokens.append(Token(token_type, value))
    
    return tokens

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression without using eval, exec, or ast.
    Uses a recursive descent parser structure based on operator precedence.
    """
    if not expr.strip():
        raise ParserError("Empty expression")

    tokens = tokenize(expr)
    current_token_index = 0

    def peek() -> Token | None:
        """Returns the current token without advancing."""
        nonlocal current_token_index
        if current_token_index < len(tokens):
            return tokens[current_token_index]
        return None

    def consume(expected_type: str = None, expected_value: str = None) -> Token:
        """Advances the token pointer and returns the consumed token."""
        nonlocal current_token_index
        if current_token_index >= len(tokens):
            raise ParserError("Unexpected end of expression")
        
        token = tokens[current_token_index]
        current_token_index += 1

        if expected_type and token.type != expected_type:
            raise ParserError(f"Expected {expected_type}, got {token.type}")
        if expected_value and token.value != expected_value:
             raise ParserError(f"Expected '{expected_value}', got '{token.value}'")

        return token

    def is_operator(t: Token) -> bool:
        """Checks if a token is an arithmetic operator."""
        return t.type == 'OP' and t.value in ['+', '-', '*', '/', '%', '^']

    # --- Parsing Functions (Precedence Hierarchy) ---

    def parse_primary() -> float:
        """Handles numbers, variables, parentheses, and unary minus/plus."""
        token = peek()
        if not token:
            raise ParserError("Unexpected end of expression while expecting primary operand.")

        # 1. Handle Unary Sign (Must be at the start or after an opening parenthesis)
        is_unary_context = (
            (peek().type == 'OP' and peek().value in ['-', '+']) and 
            (current_token_index == 0 or tokens[current_token_index - 1].type == 'LPAREN' or not is_operator(tokens[current_token_index - 1]))
        )

        if is_unary_context:
            op_token = consume() # Consume the sign (+ or -)
            sign = op_token.value
            
            # Recursively parse what follows (which must be a factor/primary expression)
            result = parse_primary() 
            
            if sign == '-':
                return -result
            elif sign == '+':
                return result # Effectively no change

        # 2. Handle Parentheses
        if token.type == 'LPAREN':
            consume('LPAREN')
            result = parse_expression()
            consume('RPAREN')
            return result
        
        # 3. Handle Numbers
        elif token.type == 'NUMBER':
            value = float(consume().value)
            return value

        # 4. Handle Variables
        elif token.type == 'VARIABLE':
            var_name = consume().value
            if variables is None or var_name not in variables:
                raise ParserError(f"Unknown variable '{var_name}'")
            return variables[var_name]

        # 5. Error Case
        else:
            raise ParserError(f"Unexpected token at start of primary expression: {token}")


    def parse_power() -> float:
        """Handles exponentiation (^) - Right Associative."""
        left = parse_primary()
        
        while peek() and peek().type == 'OP' and peek().value == '^':
            # Consume the operator
            consume('OP', '^') 
            
            # Due to right-associativity, we recursively call parse_power 
            # for the right operand (B ^ C) when evaluating A ^ B ^ C.
            right = parse_power() 
            left *= float(pow(left, right)) # Use math.pow logic: left ** right
        return left

    def parse_term() -> float:
        """Handles multiplication (*), division (/), and modulo (%). Left Associative."""
        result = parse_power()
        
        while peek() and peek().type == 'OP' and peek().value in ['*', '/', '%']:
            op_token = consume('OP')
            right = parse_power()

            if op_token.value == '*':
                result *= right
            elif op_token.value == '/':
                if right == 0:
                    raise ParserError("Division by zero")
                result /= right
            elif op_token.value == '%':
                if right == 0:
                    raise ParserError("Modulo by zero")
                # Python's % operator handles floats correctly for modulo arithmetic
                result = result % right
        return result

    def parse_expression() -> float:
        """Handles addition (+) and subtraction (-). Left Associative."""
        result = parse_term()
        
        while peek() and peek().type == 'OP' and peek().value in ['+', '-']:
            op_token = consume('OP')
            right = parse_term()

            if op_token.value == '+':
                result += right
            elif op_token.value == '-':
                result -= right
        return result

    # Start parsing from the highest level (addition/subtraction)
    try:
        final_result = parse_expression()
        
        # Check for remaining tokens after successful evaluation
        if current_token_index < len(tokens):
            raise ParserError(f"Unexpected trailing tokens starting with '{tokens[current_token_index].value}'")

        return final_result

    except ParserError as e:
        # Re-raise specific parsing errors
        raise e
    except Exception as e:
        # Catch unexpected runtime errors during evaluation (e.g., type conversion)
        raise ParserError(f"Evaluation failed due to internal error: {str(e)}")

if __name__ == '__main__':
    # Example usage and testing structure (not part of the final output, but useful for verification)
    pass
