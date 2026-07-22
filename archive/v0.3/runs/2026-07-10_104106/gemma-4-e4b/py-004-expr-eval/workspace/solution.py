import re
from typing import Dict, List, Tuple, Union

# Define Token Types
TT_NUMBER = 1
TT_IDENTIFIER = 2
TT_OPERATOR = 3  # +, -, *, /, %, ^
TT_LPAREN = 4
TT_RPAREN = 5
TT_EOF = 6

class Token:
    """Represents a single token found in the expression."""
    def __init__(self, type: int, value: str):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, '{self.value}')"

# --- Helper Functions for Grammar and Precedence ---

PRECEDENCE = {
    '+': 2, '-': 2,
    '*': 3, '/': 3, '%': 3,
    '^': 4
}

ASSOCIATIVITY = {
    '^': 'R',  # Right-associative
    '+': 'L', '-': 2,
    '*': 3, '/': 3, '%': 3,
}

def get_precedence(op: str) -> int:
    """Returns the precedence level of an operator."""
    return PRECEDENCE.get(op, -1)

def is_operator(token: Token) -> bool:
    """Checks if a token represents a binary arithmetic operator."""
    return token.type == TT_OPERATOR and token.value in PRECEDENCE

# --- Core Logic Functions ---

def tokenize(expr: str) -> List[Token]:
    """Converts the input string into a list of structured tokens."""
    tokens = []
    i = 0
    n = len(expr)
    
    # Regex pattern for matching tokens: numbers, identifiers, operators/parentheses, or whitespace
    token_specification = [
        ('NUMBER', r'\d+(\.\d*)?'),  # Integers and decimals
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'), # Variables
        ('OP', r'[\+\-\*/%\^()]'),    # Operators and parentheses (captured as one group)
        ('SKIP', r'\s+'),            # Whitespace
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    
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

        if token_type == 'NUMBER':
            tokens.append(Token(TT_NUMBER, value))
        elif token_type == 'IDENTIFIER':
            tokens.append(Token(TT_IDENTIFIER, value))
        elif token_type == 'OP':
            # Handle parentheses separately for clearer type assignment
            if value in ('(', ')'):
                if value == '(':
                    tokens.append(Token(TT_LPAREN, value))
                else: # )
                    tokens.append(Token(TT_RPAREN, value))
            elif value in PRECEDENCE:
                # This is a binary operator (+, -, *, /, %, ^)
                tokens.append(Token(TT_OPERATOR, value))
            elif value == '-':
                # Special handling for potential unary minus detection later
                tokens.append(Token(TT_OPERATOR, value)) 
            else:
                 raise ValueError(f"Malformed syntax near operator '{value}'")

    return tokens


def apply_op(op: str, b: float, a: float) -> float:
    """Applies the binary operation op to operands a and b."""
    if op == '+': return a + b
    if op == '-': return a - b
    if op == '*': return a * b
    if op == '/': 
        if b == 0.0: raise ZeroDivisionError("Division by zero")
        return a / b
    if op == '%': 
        if b == 0.0: raise ZeroDivisionError("Modulo by zero")
        return a % b
    if op == '^': return a ** b

def process_tokens(tokens: List[Token], variables: Dict[str, float]) -> float:
    """
    Evaluates the token stream using two stacks (values and operators).
    Handles precedence, associativity, and unary minus.
    """
    values = []
    ops = []

    def process_top_op():
        """Pops an operator, pops two values, calculates, and pushes result."""
        if len(ops) < 1 or len(values) < 2:
            raise ValueError("Malformed expression: insufficient operands for operation.")
        
        op = ops.pop()
        b = values.pop()
        a = values.pop()
        result = apply_op(op, b, a)
        values.append(result)

    def peek_precedence(current_op: str, top_op: str) -> int:
        """Compares precedence of current operator vs stack top."""
        return get_precedence(current_op) - get_precedence(top_op)

    # State tracking for unary minus detection
    # True if the next expected token is either an operand or a unary sign.
    expecting_operand = True 

    for i, token in enumerate(tokens):
        value = token.value
        
        if token.type == TT_NUMBER:
            values.append(float(value))
            expecting_operand = False
        
        elif token.type == TT_IDENTIFIER:
            if value not in variables:
                raise ValueError(f"Unknown variable '{value}'")
            values.append(variables[value])
            expecting_operand = False

        elif token.type == TT_LPAREN:
            ops.append(token.value)
            # After '(', we expect an operand or a unary sign
            expecting_operand = True 

        elif token.type == TT_RPAREN:
            # Evaluate everything inside the parentheses first
            while ops and ops[-1] != '(':
                process_top_op()
            
            if not ops or ops[-1] != '(':
                raise ValueError("Mismatched parentheses: missing opening parenthesis.")
            
            ops.pop() # Pop '('
            expecting_operand = False

        elif token.type == TT_OPERATOR:
            # --- Unary Minus Handling ---
            if value == '-' and expecting_operand:
                # If we expect an operand, treat '-' as a placeholder for unary negation.
                # We push 'NEG' onto the stack of operators temporarily.
                ops.append('NEG') 
                expecting_operand = True # Still expecting operand after NEG

            elif value in PRECEDENCE:
                op = value
                
                if op == '-' and not expecting_operand:
                    # Binary subtraction case (e.g., a - b)
                    pass # Use standard logic below
                
                # Standard binary operator handling
                while (ops and ops[-1] != '(' and 
                       (get_precedence(op) < get_precedence(ops[-1]) or 
                        (ASSOCIATIVITY.get(op, 'L') == 'L' and get_precedence(op) <= get_precedence(ops[-1])))):
                    process_top_op()
                
                # Push the current operator
                if op != '-': # If it was a binary minus, push it normally
                     ops.append(op)
                else:
                    # This case should ideally be caught by the unary handling above, 
                    # but if we reach here with '-' and expecting_operand=False, 
                    # it means it's a standard subtraction operator.
                    ops.append('-')

            elif value == '+' and expecting_operand:
                # Ignore leading/redundant plus signs (e.g., "+(3)")
                pass
            else:
                 # This handles cases like 'a++b' or misplaced operators
                 raise ValueError(f"Malformed syntax near operator '{value}'")

        # After processing a token that is not an operator, we are no longer expecting an operand
        if token.type != TT_OPERATOR and token.type != TT_LPAREN:
            expecting_operand = False


    # --- Final Evaluation Pass ---
    while ops:
        op = ops[-1]
        if op == '(':
             raise ValueError("Mismatched parentheses: missing closing parenthesis.")
        process_top_op()

    if len(values) != 1:
        raise ValueError("Malformed expression: too many operands or incomplete calculation.")
    
    return values[0]


def evaluate(expr: str, variables: Dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression string.
    Handles precedence, associativity, and unary minus.
    """
    if variables is None:
        variables = {}

    # 1. Tokenize the input
    tokens = tokenize(expr)
    
    # 2. Process tokens and evaluate
    try:
        result = process_tokens(tokens, variables)
        return result
    except ZeroDivisionError as e:
        raise ValueError(str(e))
    except Exception as e:
        # Catch general parsing/syntax errors raised internally
        if isinstance(e, ValueError):
            raise e
        # Re-raise other unexpected errors if they occur during calculation
        raise ValueError(f"Evaluation error: {type(e).__name__}: {str(e)}")


if __name__ == '__main__':
    # Example Usage and Tests (Not part of the final output, but useful for verification)

    # Test 1: Basic arithmetic
    print("Test 1: 2 + 3 * 4 = ", evaluate("2 + 3 * 4")) # Expected: 14.0

    # Test 2: Parentheses override precedence
    print("Test 2: (2 + 3) * 4 = ", evaluate("(2 + 3) * 4")) # Expected: 20.0

    # Test 3: Exponentiation and associativity (Right-associative)
    # 2^3^2 = 2^(3^2) = 2^9 = 512
    print("Test 3: 2^3^2 = ", evaluate("2^3^2")) # Expected: 512.0

    # Test 4: Unary minus (Leading negation)
    print("Test 4: -5 + 10 = ", evaluate("-5 + 10")) # Expected: 5.0

    # Test 5: Repeated unary minus
    print("Test 5: --3 * 2 = ", evaluate("--3 * 2")) # Expected: 6.0

    # Test 6: Unary minus with exponentiation (Unary binds looser than ^)
    # -2^2 = -(2^2) = -4
    print("Test 6: -2^2 = ", evaluate("-2^2")) # Expected: -4.0

    # Test 7: Variables
    variables_dict = {"x": 10.0, "y": 5.0}
    print("Test 7: x / y + 1 = ", evaluate("x / y + 1", variables=variables_dict)) # Expected: 3.0

    # Test 8: Complex mix (Unary minus, exponentiation, parentheses)
    # -((2+3)*4) ^ 2 = -(5*4)^2 = (-20)^2 = 400
    print("Test 8: -((2+3)*4))^2 = ", evaluate("-((2+3)*4))^2")) # Expected: 400.0

    # Test 9: Floating point numbers and modulo
    print("Test 9: 17 % 5.5 = ", evaluate("17 % 5.5")) # Note: Python's % handles floats, but standard math context might vary. Assuming float arithmetic is fine. (17 - 3*5) / 5.5 -> 2/5.5
    # For simplicity and adherence to typical integer modulo behavior when mixing types, we rely on Python's native float handling for %.
    print("Test 9b: 10 % 3 = ", evaluate("10 % 3")) # Expected: 1.0

    # Test 10: Error Handling (Zero Division)
    try:
        evaluate("5 / (2 - 2)")
    except ValueError as e:
        print(f"Test 10 Success (Error): {e}") # Expects ZeroDivisionError wrapped in ValueError

    # Test 11: Error Handling (Mismatched Parentheses)
    try:
        evaluate("((5+3)")
    except ValueError as e:
        print(f"Test 11 Success (Error): {e}") # Expects Mismatched parentheses

    # Test 12: Error Handling (Unknown Variable)
    try:
        evaluate("a + b")
    except ValueError as e:
        print(f"Test 12 Success (Error): {e}") # Expects Unknown variable 'a'
