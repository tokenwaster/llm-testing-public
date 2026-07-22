def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
  if variables is None:
    variables = {}
  
  # Tokenize
  tokens = []
  i = 0
  while i < len(expr):
    if expr[i].isspace():
      i += 1
    elif expr[i] in '+-*/%^()':
      tokens.append(expr[i])
      i += 1
    elif expr[i].isdigit() or expr[i] == '.':
      j = i
      while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
        j += 1
      tokens.append(expr[i:j])
      i = j
    elif expr[i].isalpha() or expr[i] == '_':
      j = i
      while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
        j += 1
      tokens.append(expr[i:j])
      i = j
    else:
      raise ValueError(f"Unexpected character: '{expr[i]}'")
  
  # Parser
  pos = 0
  
  def current():
    return tokens[pos] if pos < len(tokens) else None
  
  def advance():
    nonlocal pos
    pos += 1
  
  def is_number(token):
    if not token:
      return False
    try:
      float(token)
      return True
    except ValueError:
      return False
  
  def is_variable_name(token):
    if not token:
      return False
    if not (token[0].isalpha() or token[0] == '_'):
      return False
    return all(c.isalnum() or c == '_' for c in token)
  
  def parse_additive():
    left = parse_multiplicative()
    while current() in ['+', '-']:
      op = current()
      advance()
      right = parse_multiplicative()
      if op == '+':
        left = left + right
      else:
        left = left - right
    return left
  
  def parse_multiplicative():
    left = parse_unary()
    while current() in ['*', '/', '%']:
      op = current()
      advance()
      right = parse_unary()
      if op == '*':
        left = left * right
      elif op == '/':
        if right == 0:
          raise ValueError("Division by zero")
        left = left / right
      else:  # op == '%'
        if right == 0:
          raise ValueError("Modulo by zero")
        left = left % right
    return left
  
  def parse_unary():
    if current() in ['+', '-']:
      op = current()
      advance()
      right = parse_unary()
      if op == '-':
        return -right
      else:
        return right
    else:
      return parse_exponentiation()
  
  def parse_exponentiation():
    left = parse_primary()
    if current() == '^':
      advance()
      right = parse_exponentiation()
      return left ** right
    return left
  
  def parse_primary():
    token = current()
    if token == '(':
      advance()
      result = parse_additive()
      if current() != ')':
        raise ValueError("Unbalanced parentheses")
      advance()
      return result
    elif is_number(token):
      advance()
      return float(token)
    elif is_variable_name(token):
      advance()
      if token not in variables:
        raise ValueError(f"Unknown variable: '{token}'")
      return variables[token]
    else:
      raise ValueError(f"Unexpected token: '{token}'")
  
  result = parse_additive()
  
  if pos < len(tokens):
    raise ValueError(f"Unexpected token after expression: '{current()}'")
  
  return float(result)
