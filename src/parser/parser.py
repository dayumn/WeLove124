from src.lexer import tokenizer

TokenType = tokenizer.TokenType

# PARSER NOTES

# Hierarchy:
# <program> → top level
# <statement_list> → multiple statements
# <statement> → individual statement types
# <expression> → various expression types
# <literal> → base values

# NEEDED:
# Parse Result
# Create Nodes
# Error Handling
# Parser State
# Parser Functions
# Main Parser

#------------------------------------------------------------------------------------------------
# PARSE RESULT
#------------------------------------------------------------------------------------------------

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        
    def register(self, res):
        if res.error: 
            self.error = res.error
        return res.node
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        if self.error is None:
            self.error = error
        return self

#------------------------------------------------------------------------------------------------
# NODES
#------------------------------------------------------------------------------------------------

class IntegerNode:
  def __init__(self, token):
    self.token = token

  def __repr__(self):
    return f'{self.token["value"]}'

class FloatNode:
  def __init__(self, token):
    self.token = token

  def __repr__(self):
    return f'{self.token["value"]}'

class BooleanNode:
  def __init__(self, token):
    self.token = token

  def __repr__(self):
    return f'{self.token["value"]}'

class StringNode:
  def __init__(self, token):
    self.token = token
    self.value = str(token['value'])  # Quotes already removed by tokenizer

  def __repr__(self):
    return f'"{self.value}"'

class NoobNode:
  def __init__(self, line_number=None):
    self.line_number = line_number

  def __repr__(self):
    return f"NOOB"

class StringConcatNode:
  def __init__(self, operands):
    self.operands = operands

  def __repr__(self):
    return f"StringConcatenation({self.operands})"

class ArithmeticBinaryOpNode:
  def __init__(self, left_node, operation, right_node):
    self.operation = operation
    self.left_node = left_node
    self.right_node = right_node

  def __repr__(self):
    return f'{self.operation["value"]}({self.left_node}, {self.right_node})'

class BooleanBinaryOpNode:
  def __init__(self, left_node, operation, right_node):
    self.operation = operation
    self.left_node = left_node
    self.right_node = right_node

  def __repr__(self):
    return f'{self.operation["value"]}({self.left_node}, {self.right_node})'

class BooleanUnaryOpNode:
  def __init__(self, operation, operand):
    self.operation = operation
    self.operand = operand

  def __repr__(self):
    return f'{self.operation["value"]}({self.operand})'

class BooleanTernaryOpNode:
  def __init__(self, operation, boolean_statements):
    self.operation = operation
    self.boolean_statements = boolean_statements

  def __repr__(self):
    return f"{self.operation}({self.boolean_statements})"

class ComparisonOpNode:
  def __init__(self, left_node, operation, right_node):
    self.operation = operation
    self.left_node = left_node
    self.right_node = right_node

  def __repr__(self):
    return f'{self.operation["value"]}({self.left_node}, {self.right_node})'

class VarAccessNode:
  def __init__(self, var_name_token):
    self.var_name_token = var_name_token

  def __repr__(self):
    return f"VarAccess({self.var_name_token['value']})"

class VarDeclarationNode:
  def __init__(self, var_name_token, value_node):
    self.var_name_token = var_name_token
    self.value_node = value_node

  def __repr__(self):
    return f"VarDeclare({self.var_name_token['value']}, {self.value_node})"

class VarAssignmentNode:
  def __init__(self, var_to_access, value_to_assign):
    self.var_to_access = var_to_access
    self.value_to_assign = value_to_assign

  def __repr__(self):
    return f"VarAssign({self.var_to_access['value']}, {self.value_to_assign})"

class StatementListNode:
  def __init__(self, statements):
    self.statements = statements

  def __repr__(self):
    return f"StatementList({self.statements})"

class VarDecListNode:
  def __init__(self, variable_declarations):
    self.variable_declarations = variable_declarations

  def __repr__(self):
    return f"VarDecListNode({self.variable_declarations})"

class PrintNode:
  def __init__(self, operands, suppress_newline=False):
    self.operands = operands
    self.suppress_newline = suppress_newline

  def __repr__(self):
    return f"PrintNode({self.operands}, suppress_newline={self.suppress_newline})"

class TypecastNode:
  def __init__(self, source_value, desired_type):
    self.source_value = source_value
    self.desired_type = desired_type

  def __repr__(self):
    return f"{self.desired_type}({self.source_value})"

class SwitchCaseNode:
  def __init__(self, cases, cases_statements, default_case_statements):
    self.cases = cases
    self.cases_statements = cases_statements
    self.default_case_statements = default_case_statements

  def __repr__(self):
    return f"SwitchCases({self.cases_statements})"

class IfNode: 
  def __init__(self, if_block_statements, else_block_statements, mebbe_cases=None):
    self.if_block_statements = if_block_statements
    self.else_block_statements = else_block_statements
    self.mebbe_cases = mebbe_cases if mebbe_cases else []  # List of (condition, statements) tuples

  def __repr__(self):
    if self.mebbe_cases:
      return f"IfElse({self.if_block_statements}, MEBBE{self.mebbe_cases}, {self.else_block_statements})"
    return f"IfElse({self.if_block_statements}, {self.else_block_statements})"

class LoopNode:
  def __init__(self, label, operation, variable, clause_type, til_wile_expression, body_statements):
    self.label = label
    self.operation = operation
    self.variable = variable
    self.clause_type = clause_type
    self.til_wile_expression = til_wile_expression
    self.body_statements = body_statements

  def __repr__(self):
    return f"Loop({self.label}, {self.operation['value']}, {self.variable}, {self.clause_type}, {self.til_wile_expression}, {self.body_statements})"

class FuncDefNode:
  def __init__(self, function_name, parameters, body_statements):
    self.function_name = function_name
    self.parameters = parameters
    self.body_statements = body_statements

  def __repr__(self):
    return f"FuncDef({self.function_name}, {self.parameters})"

class FuncCallNode:
  def __init__(self, function_name, parameters):
    self.function_name = function_name
    self.parameters = parameters

  def __repr__(self):
    return f"FuncCall({self.function_name}, {self.parameters})"

class InputNode:
  def __init__(self, variable):
    self.variable = variable

  def __repr__(self):
    return f"StoreTo({self.variable})"

class BreakNode:
  def __init__(self, break_token):
    self.break_token = break_token

  def __repr__(self):
    return f"BREAK"

class ReturnNode:
  def __init__(self, return_expression):
    self.return_expression = return_expression

  def __repr__(self):
    return f'RETURN({self.return_expression})'

class ProgramNode:
  def __init__(self, sections):
    self.sections = sections

  def __repr__(self):
    return f"ProgramNode({self.sections})"

# Array Implementation

class ArrayDeclarationNode:
  def __init__(self, array_name_token, element_type, size_expr):
    self.array_name_token = array_name_token
    self.element_type = element_type  # 'NUMBR', 'NUMBAR', 'YARN', 'TROOF'
    self.size_expr = size_expr

  def __repr__(self):
    return f"ArrayDecl({self.array_name_token['value']}, type={self.element_type}, size={self.size_expr})"

class ArrayAccessNode:
  def __init__(self, array_name_token, index_expr):
    self.array_name_token = array_name_token
    self.index_expr = index_expr

  def __repr__(self):
    return f"ArrayAccess({self.array_name_token['value']}[{self.index_expr}])"

class ArrayConfineNode:
  def __init__(self, value_expr, array_name_token, index_expr):
    self.value_expr = value_expr
    self.array_name_token = array_name_token
    self.index_expr = index_expr

  def __repr__(self):
    return f"CONFINE({self.value_expr} IN {self.array_name_token['value']} AT {self.index_expr})"

class ArrayDischargeNode:
  def __init__(self, array_name_token, index_expr):
    self.array_name_token = array_name_token
    self.index_expr = index_expr

  def __repr__(self):
    return f"DISCHARGE({self.array_name_token['value']} AT {self.index_expr})"

#------------------------------------------------------------------------------------------------
# ERRORS
#------------------------------------------------------------------------------------------------

class Error:
  def __init__(self, token, details, error_name):
      self.token = token
      self.details = details
      self.error_name = error_name
  
  def as_string(self):
      return f"{self.error_name}: '{self.token['value']}' at line {self.token['line']}\nDetails: {self.details}\n"

class InvalidSyntaxError(Error):
  def __init__(self, token, details, expected=None, found=None, category=None, context_kind=None, start_token=None, failing_token=None, parse_stack=None):
    # token retained for backward compatibility (primary pointer)
    super().__init__(token, details, error_name='Invalid Syntax')
    self.expected = expected
    self.found = found
    self.category = category
    self.context_kind = context_kind
    self.start_token = start_token or token
    self.failing_token = failing_token or token
    self.parse_stack = parse_stack or []

  def as_string(self):
    base_cat = self.category or (self.start_token.get('category') if isinstance(self.start_token, dict) else None) or (self.start_token.get('type').value if isinstance(self.start_token, dict) else 'UNKNOWN')
    lexeme = self.start_token['value'] if isinstance(self.start_token, dict) else '<UNKNOWN>'
    line = self.start_token['line'] if isinstance(self.start_token, dict) else 0
    col = self.start_token.get('col', 0) if isinstance(self.start_token, dict) else 0
    
    # Format: Line X:Y, SyntaxError: message (consistent with lexer/runtime errors)
    msg = f'Line {line}:{col}\n'
    msg += f'SyntaxError: '
    
    # Build error message
    if self.expected and self.found:
      if isinstance(self.expected, (list, tuple)):
        msg += f"expected {' or '.join(repr(e) for e in self.expected)}, got '{self.found}'"
      else:
        msg += f"expected '{self.expected}', got '{self.found}'"
    elif self.expected:
      if isinstance(self.expected, (list, tuple)):
        msg += f"expected {' or '.join(repr(e) for e in self.expected)}"
      else:
        msg += f"expected '{self.expected}'"
    elif self.details:
      msg += self.details
    else:
      msg += f"invalid syntax near '{lexeme}'"
    
    # Add parsing context as traceback
    if self.parse_stack:
      traceback = "Traceback (most recent call last):\n"
      for ctx in self.parse_stack:
        ctx_filename = ctx.get('filename', '<stdin>')
        ctx_line = ctx.get('line', 0)
        ctx_col = ctx['token'].get('col', 0) if isinstance(ctx.get('token'), dict) else 0
        traceback += f'  File "{ctx_filename}", line {ctx_line}:{ctx_col}, in {ctx["function"]}\n'
      msg = traceback + msg
    
    return msg + "\n"

class RuntimeError(Error):
  def __init__(self, token, details, filename='<stdin>'):
    super().__init__(token, details, error_name='Runtime Error')
    self.filename = filename
  
  def as_string(self):
    # Handle different token formats
    if isinstance(self.token, dict):
      line = self.token.get('line', 'unknown')
      col = self.token.get('col', 0)
      value = self.token.get('value', '<unknown>')
      # Simplified format: just line number
      msg = f'Line {line}:{col}\n'
      msg += f'RuntimeError: {self.details}\n'
      if value and value != '<unknown>':
        msg += f'  at: {repr(value)}\n'
      return msg
    elif isinstance(self.token, tuple):
      # Handle tuple format: (category, subcategory, line_number, token)
      category = self.token[0] if len(self.token) > 0 else 'Unknown'
      line = self.token[2] if len(self.token) > 2 else 'unknown'
      token = self.token[3] if len(self.token) > 3 else None
      col = token.get('col', 0) if isinstance(token, dict) else 0
      # Simplified format: just line number
      msg = f'Line {line}:{col}\n'
      msg += f'RuntimeError: {self.details}\n'
      if category and category != 'Unknown':
        msg += f'  Category: {category}\n'
      return msg
    else:
      # Fallback format
      msg = f'RuntimeError: {self.details}\n'
      return msg

    
#------------------------------------------------------------------------------------------------
# PARSER
#------------------------------------------------------------------------------------------------

class Parser:
  def __init__(self, tokens, filename='<stdin>'):
    self.tokens = tokens
    self.token_index = -1
    self.parse_stack = []  # Stack to track parsing context
    self.control_flow_stack = []  # Stack to track control flow contexts (switch/loop/function) for GTFO validation
    self.filename = filename
    self.advance()
  
  def push_context(self, function_name, expected=None):
    """Push a parsing context onto the stack"""
    ctx = {
      'function': function_name,
      'line': self.current_token['line'] if self.current_token else 0,
      'token': self.current_token,
      'expected': expected,
      'filename': self.filename
    }
    self.parse_stack.append(ctx)
  
  def pop_context(self):
    """Pop the most recent parsing context"""
    if self.parse_stack:
      self.parse_stack.pop()

  def push_control_flow(self, context_type):
    """Push a control flow context (switch/loop/function) for GTFO validation"""
    self.control_flow_stack.append(context_type)
  
  def pop_control_flow(self):
    """Pop the most recent control flow context"""
    if self.control_flow_stack:
      self.control_flow_stack.pop()
  
  def is_in_valid_gtfo_context(self):
    """Check if GTFO can be used in current context (must be inside switch/loop/function)"""
    return len(self.control_flow_stack) > 0
  
  def get_current_control_flow_context(self):
    """Get the current control flow context name for error messages"""
    if self.control_flow_stack:
      return self.control_flow_stack[-1]
    return None

  # Standardized error factory
  def syntax_error(self, start_token, expected, found=None, category=None, context_kind=None, failing_token=None):
    # Normalize expected and found
    if found is None:
      if self.current_token is None:
        found = 'end of input'
      else:
        found = self.current_token['value']
    
    # If parse_stack is empty, create a minimal stack with filename from parser
    parse_stack = list(self.parse_stack) if self.parse_stack else [{'filename': self.filename, 'line': start_token.get('line', 0) if isinstance(start_token, dict) else 0, 'token': start_token, 'function': 'parse', 'expected': None}]
    
    return InvalidSyntaxError(
      start_token,
      details='',
      expected=expected,
      found=found,
      category=category or (start_token.get('category') if isinstance(start_token, dict) else None),
      context_kind=context_kind,
      start_token=start_token,
      failing_token=failing_token or self.current_token,
      parse_stack=parse_stack
    )

  def peek(self, offset=1):
    index = self.token_index + offset
    if 0 <= index < len(self.tokens):
      return self.tokens[index]
    return None

  def advance(self):
    self.token_index += 1
    if (self.token_index < len(self.tokens)):
      self.current_token = self.tokens[self.token_index]
    return self.current_token

  def parse(self):
    self.push_context('program', 'HAI ... KTHXBYE')
    res = ParseResult()
    sections = []
    
    # Skip any leading newlines at the start of the file
    while self.current_token and self.current_token['type'] == TokenType.NEWLINE:
      self.advance()
    
    # Parse function definitions before HAI
    while self.current_token and self.current_token['type'] == TokenType.HOW_IZ_I:
      func_def = res.register(self.function_definition())
      if func_def is None:
        self.pop_context()
        return res  # Has error
      sections.append(func_def)
      
      # Skip newlines after function definition
      while self.current_token and self.current_token['type'] == TokenType.NEWLINE:
        self.advance()
    
    start = self.current_token if self.current_token else {'value':'<START>','line':1,'type':'<START>','category':'Start'}
    if (self.current_token['type'] != TokenType.HAI):
      self.pop_context()
      return res.failure(self.syntax_error(start, 'HAI', (self.current_token['value'] if self.current_token else 'end of input'), category='Program Delimiter', context_kind='program'))

    self.advance() # Eat HAI

    # Optionally eat version number (e.g., 1.2)
    if self.current_token['type'] in (TokenType.FLOAT, TokenType.INTEGER):
      self.advance()

    # Skip newlines after HAI
    while self.current_token['type'] == TokenType.NEWLINE:
      self.advance()

    # Check if there's a variable section
    if self.current_token['type'] == TokenType.WAZZUP:
      self.advance() # Eat Wazzup
      variable_declaration_section =  res.register(self.variable_section())
      if variable_declaration_section is None:
        self.pop_context()
        return res   # Check if there's an error
      sections.append(variable_declaration_section)         # No error
    # If we see a variable declaration outside of WAZZUP
    elif self.current_token['type'] == TokenType.I_HAS_A:
      self.pop_context()
      return res.failure(self.syntax_error(self.current_token, ['WAZZUP','statement'], 'I HAS A', category='Variable Declaration', context_kind='program'))

    # try to parse statements
    list_of_statements = res.register(self.statement_list())
    if list_of_statements is None:
      self.pop_context()
      return res               # Check if there's an error
    sections.append(list_of_statements)                     # No error

    # Parse function definitions after KTHXBYE
    # Skip newlines after KTHXBYE
    while (self.token_index < len(self.tokens) and 
           self.current_token and 
           self.current_token['type'] == TokenType.NEWLINE):
      self.advance()
    
    # Collect functions defined after KTHXBYE
    functions_after = []
    while (self.token_index < len(self.tokens) and
           self.current_token and 
           self.current_token['type'] == TokenType.HOW_IZ_I):
      func_def = res.register(self.function_definition())
      if func_def is None:
        self.pop_context()
        return res  # Has error
      functions_after.append(func_def)
      
      # Skip newlines after function definition
      while (self.token_index < len(self.tokens) and
             self.current_token and 
             self.current_token['type'] == TokenType.NEWLINE):
        self.advance()
    
    # Add functions defined after KTHXBYE to the beginning (after functions before HAI)
    # so they're defined before the main code executes
    # Count how many function definitions are at the start
    func_count_before = 0
    for section in sections:
      if isinstance(section, FuncDefNode):
        func_count_before += 1
      else:
        break
    
    # Insert functions after KTHXBYE right after functions before HAI
    for i, func in enumerate(functions_after):
      sections.insert(func_count_before + i, func)

    self.pop_context()
    return res.success(ProgramNode(sections))

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def variable_section(self):
    self.push_context('variable_section', 'WAZZUP ... BUHBYE')
    res = ParseResult()
    variable_declarations = []

    while (self.current_token['type'] != TokenType.BUHBYE and self.token_index < len(self.tokens) - 1):
      # Skip leading newlines
      while self.current_token['type'] == TokenType.NEWLINE:
        self.advance()
      if self.current_token['type'] == TokenType.BUHBYE or self.token_index >= len(self.tokens) - 1:
        break
      
      variable_declaration = res.register(self.variable_declaration())

      # Has error
      if variable_declaration is None:
        return res

      variable_declarations.append(variable_declaration)
      
      # Skip newlines after variable declaration
      while self.current_token['type'] == TokenType.NEWLINE:
        self.advance()

    # Error
    if (self.current_token['type'] != TokenType.BUHBYE):
      self.pop_context()
      return res.failure(self.syntax_error(self.current_token, 'BUHBYE', self.current_token['value'], category='Variable List Delimiter', context_kind='variable_section'))

    # No error
    self.advance() # Eat BUHBYE
    
    # Skip newlines after BUHBYE
    while self.current_token['type'] == TokenType.NEWLINE:
      self.advance()

    self.pop_context()
    return res.success(VarDecListNode(variable_declarations))

  def variable_declaration(self):
    res = ParseResult()

    if self.current_token['type'] == TokenType.I_HAS_A:
      prev_token = self.current_token
      self.advance() # eats I has a

      if (self.current_token['type'] != TokenType.IDENTIFIER):
        return res.failure(self.syntax_error(prev_token, 'IDENTIFIER', self.current_token['value'], category='Variable Declaration', context_kind='var_decl'))

      var_name_token = self.current_token
      self.advance() # eats var name

      if (self.current_token['type'] != TokenType.ITZ):
        return res.success(VarDeclarationNode(var_name_token, NoobNode()))

      itz_token = self.current_token
      self.advance() # eats ITZ

      # Check for array declaration: ITZ A <TYPE> UHS OF <size_expr>
      if self.current_token['type'] == TokenType.A:
        next_token = self.peek()
        # Check if this is a typed array declaration
        if next_token and next_token['type'] in (TokenType.NUMBR, TokenType.NUMBAR, TokenType.YARN, TokenType.TROOF):
          self.advance() # Eat A
          
          # Get the element type
          if self.current_token['type'] not in (TokenType.NUMBR, TokenType.NUMBAR, TokenType.YARN, TokenType.TROOF):
            return res.failure(self.syntax_error(self.current_token, 'type (NUMBR, NUMBAR, YARN, or TROOF)', self.current_token['value'], category='Array Declaration', context_kind='array_decl'))
          
          element_type = self.current_token['value']  # Store the type as string
          self.advance() # Eat type
          
          # Expect UHS
          if self.current_token['type'] != TokenType.UHS:
            return res.failure(self.syntax_error(self.current_token, 'UHS', self.current_token['value'], category='Array Declaration', context_kind='array_decl'))
          
          self.advance() # Eat UHS
          
          # Expect OF
          if self.current_token['type'] != TokenType.OF:
            return res.failure(self.syntax_error(self.current_token, 'OF', self.current_token['value'], category='Array Declaration', context_kind='array_decl'))
          
          self.advance() # Eat OF
          
          # Parse size expression (can be integer literal, variable, or arithmetic expression)
          size_expr = res.register(self.arithmetic_expression())
          if res.error: return res
          if size_expr is None:
            return res.failure(self.syntax_error(self.current_token, 'size expression', self.current_token['value'], category='Array Size', context_kind='array_decl'))
          
          return res.success(ArrayDeclarationNode(var_name_token, element_type, size_expr))

      # Regular variable declaration
      expression = res.register(self.expression())
      if res.error: return res

      # Check if expression is None (ITZ without a value)
      if expression is None:
        return res.failure(self.syntax_error(itz_token, 'expression', self.current_token['value'], category='Variable Assignment', context_kind='var_decl'))

      return res.success(VarDeclarationNode(var_name_token, expression))

    return res.failure(self.syntax_error(self.current_token, ['I HAS A','BUHBYE'], self.current_token['value'], category='Variable Section', context_kind='var_section'))

  def variable_literal(self):
    res = ParseResult()
    token = self.current_token

    if token['type'] == TokenType.IDENTIFIER:
      self.advance() # Eat

      return res.success(VarAccessNode(token))

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def statement_list(self):
    self.push_context('statement_list', 'list of statements')
    res = ParseResult()
    statements = []

    while (self.current_token['type'] != TokenType.KTHXBYE and self.token_index < len(self.tokens) - 1):
      # Skip leading newlines
      while self.current_token['type'] == TokenType.NEWLINE:
        self.advance()
      
      # Check again after skipping newlines
      if self.current_token['type'] == TokenType.KTHXBYE or self.token_index >= len(self.tokens) - 1:
        break
      
      prev_token_index = self.token_index  # Track position before parsing
      statement = res.register(self.statement())

      # Has error
      if statement is None:
        return res

      # Safety check: ensure we advanced at least one token
      if self.token_index == prev_token_index:
        return res.failure(self.syntax_error(self.current_token, 'valid statement', self.current_token['value'], category='Statement', context_kind='statement_list'))

      statements.append(statement)
      
      # Check for statement separators (newline or comma)
      if self.current_token['type'] == TokenType.COMMA:
        self.advance()  # Eat the comma and continue to next statement
      elif self.current_token['type'] == TokenType.NEWLINE:
        self.advance()  # Eat the newline and continue to next statement
      # If neither comma nor newline, continue (for cases like after OIC, etc.)

    if (self.current_token['type'] != TokenType.KTHXBYE):
      return res.failure(self.syntax_error(self.current_token, 'KTHXBYE', self.current_token['value'], category='Code Delimiter', context_kind='program_body'))

    self.advance()  # Eat KTHXBYE
    return res.success(StatementListNode(statements))

  def statement(self):
    self.push_context('statement', 'any valid statement')
    res = ParseResult()
    # Grammar: <statement> ::= <expression> | <conditional> | <loop> | <function_call> | <function_def> | <declaration> | <input> | <output> | <array_operation>

    # Try declaration (I HAS A)
    if self.current_token['type'] == TokenType.I_HAS_A:
      res.node = res.register(self.variable_declaration())
      if res.error or res.node:
        self.pop_context()
        return res

    # Try array operations (CONFINE, DISCHARGE)
    if self.current_token['type'] in (TokenType.CONFINE, TokenType.DISCHARGE):
      res.node = res.register(self.array_operation())
      if res.error or res.node:
        self.pop_context()
        return res

    # Try output (VISIBLE)
    res.node = res.register(self.print_statement())
    if res.error or res.node:
      self.pop_context()
      return res

    # Try input (GIMMEH)
    res.node = res.register(self.input_statement())
    if res.error or res.node:
      self.pop_context()
      return res

    # Try conditional (O RLY or WTF)
    res.node = res.register(self.if_statement())
    if res.error or res.node:
      self.pop_context()
      return res

    res.node = res.register(self.switch_case_statement())
    if res.error or res.node:
      self.pop_context()
      return res

    # Try loop (IM IN YR)
    res.node = res.register(self.loop_statement())
    if res.error or res.node:
      self.pop_context()
      return res

    # Try function definition (HOW IZ I)
    res.node = res.register(self.function_definition())
    if res.error or res.node:
      self.pop_context()
      return res

    # Try function call (I IZ)
    res.node = res.register(self.function_call())
    if res.error or res.node:
      self.pop_context()
      return res

    # Try break statement (GTFO)
    res.node = res.register(self.break_statement())
    if res.error or res.node:
      self.pop_context()
      return res

    # Try return statement (FOUND YR)
    res.node = res.register(self.return_statement())
    if res.error or res.node:
      self.pop_context()
      return res

    # Try expression-statements (operations and assignments (?), not literals)
    if self.current_token['type'] == TokenType.IDENTIFIER:
        identifier_token = self.current_token
        self.advance()
        
        if self.current_token['type'] in (TokenType.R, TokenType.IS_NOW_A):
            # if assignment, backtrack
            self.token_index -= 1
            self.current_token = self.tokens[self.token_index]
            res.node = res.register(self.assignment_statement())
            if res.error or res.node:
              self.pop_context()
              return res
        else:
            # if identifier looks like existing tokens
            suspicious_tokens = {
                TokenType.QUOTE, TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING,
                TokenType.IDENTIFIER, TokenType.WIN, TokenType.FAIL
            }
            if self.current_token['type'] in suspicious_tokens:
                error = self.syntax_error(
                    identifier_token, 
                    'valid statement keyword or assignment operator',
                    identifier_token['value'],
                    category='Statement',
                    context_kind='statement'
                )
                self.pop_context()
                return res.failure(error)
            else:
                # Return VarAccessNode - we've already advanced past the identifier
                self.pop_context()
                return res.success(VarAccessNode(identifier_token))
    elif self.current_token['type'] in (
        # Arithmetic operations
        TokenType.PRODUKT_OF, TokenType.QUOSHUNT_OF, TokenType.SUM_OF, 
        TokenType.DIFF_OF, TokenType.MOD_OF, TokenType.BIGGR_OF, TokenType.SMALLR_OF,
        # Boolean operations
        TokenType.BOTH_OF, TokenType.EITHER_OF, TokenType.WON_OF, TokenType.NOT,
        TokenType.ALL_OF, TokenType.ANY_OF,
        # Comparison operations
        TokenType.BOTH_SAEM, TokenType.DIFFRINT,
        # String operations
        TokenType.SMOOSH,
        # Typecasting
        TokenType.MAEK
    ):
        res.node = res.register(self.expression())
        if res.error or res.node:
          self.pop_context()
          return res

    # Can't parse
    error = self.syntax_error(self.current_token, 'valid statement', self.current_token['value'], category='Statement', context_kind='statement')
    self.pop_context()
    return res.failure(error)

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def expression(self):
    res = ParseResult()
    # Grammar: <expression> ::= <nestable_expr> | <non_nestable_expr>

    # Try non-nestable expressions first (SMOOSH, ALL OF, ANY OF)
    if self.current_token['type'] == TokenType.SMOOSH:
      res.node = res.register(self.string_concatenation())
      return res

    if self.current_token['type'] in (TokenType.ALL_OF, TokenType.ANY_OF):
      res.node = res.register(self.boolean_non_nest())
      return res

    # Try nestable expressions
    res.node = res.register(self.nestable_expr())
    return res

  def nestable_expr(self):
    res = ParseResult()
    # Grammar: <nestable_expr> ::= <arithmetic_expr> | <boolean_nest> | <comparison> | <function_call> | <typecasting> | <literal> | <relational> | varident | <array_access>

    # Check for invalid infinite arity operators
    if self.current_token['type'] in (TokenType.ALL_OF, TokenType.ANY_OF):
      return res.failure(InvalidSyntaxError(
        self.current_token,
        f"Nesting infinite arity boolean operators (ALL OF/ANY OF) is not allowed",
        category='Boolean Multi-Operand'
      ))

    # Try arithmetic expressions
    if self.current_token['type'] in (TokenType.PRODUKT_OF, TokenType.QUOSHUNT_OF, TokenType.SUM_OF, TokenType.DIFF_OF, TokenType.MOD_OF, TokenType.BIGGR_OF, TokenType.SMALLR_OF):
      res.node = res.register(self.arithmetic_binary_operation())
      return res

    # Try boolean nest (BOTH OF, EITHER OF, WON OF, NOT)
    if self.current_token['type'] in (TokenType.BOTH_OF, TokenType.EITHER_OF, TokenType.WON_OF, TokenType.NOT):
      res.node = res.register(self.boolean_nest())
      return res

    # Try comparison and relational
    if self.current_token['type'] in (TokenType.BOTH_SAEM, TokenType.DIFFRINT):
      res.node = res.register(self.comparison_operation())
      return res

    # Try function call (I IZ)
    if self.current_token['type'] == TokenType.I_IZ:
      res.node = res.register(self.function_call())
      return res

    # Try typecasting (MAEK)
    if self.current_token['type'] == TokenType.MAEK:
      res.node = res.register(self.typecast())
      return res

    # Try array access or variable literal
    if self.current_token['type'] == TokenType.IDENTIFIER:
      # Check if next token is LBRACKET for array access
      next_token = self.peek()
      if next_token and next_token['type'] == TokenType.LBRACKET:
        res.node = res.register(self.array_access())
      else:
        # Just a variable reference, not an assignment
        res.node = res.register(self.variable_literal())
      return res

    # Try literal
    if self.current_token['type'] in (TokenType.INTEGER, TokenType.FLOAT, TokenType.QUOTE, TokenType.WIN, TokenType.FAIL, TokenType.NOOB):
      res.node = res.register(self.literal())
      return res

    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def literal(self):
    res = ParseResult()

    if self.current_token['type'] in (TokenType.INTEGER, TokenType.FLOAT):
      res.node = res.register(self.arithmetic_literal())

    elif self.current_token['type'] == TokenType.QUOTE:
      res.node = res.register(self.string_literal())

    elif self.current_token['type'] in (TokenType.WIN, TokenType.FAIL):
      res.node = res.register(self.boolean_literal())

    elif self.current_token['type'] == TokenType.IDENTIFIER:
      res.node = res.register(self.variable_literal())

    elif self.current_token['type'] == TokenType.NOOB:
      res.node = res.register(self.noob())

    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def noob(self):
    res = ParseResult()
    token = self.current_token

    if token['type'] == TokenType.NOOB:
      self.advance() # Eat NOOB

      return res.success(NoobNode(token['line']))

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def string_concatenation(self):
    self.push_context('string_concatenation', 'SMOOSH <expr> [AN <expr>]... [MKAY]')
    res = ParseResult()
    # Grammar: <concatenation> ::= SMOOSH <nestable_expr> <multi_expression_nestable>
    operands = []

    if self.current_token['type'] == TokenType.SMOOSH:
      self.advance() # Eat SMOOSH

      # Parse the first nestable expression
      first_operand = res.register(self.nestable_expr())
      if res.error: return res
      operands.append(first_operand)

      # Parse multi_expression_nestable (handles AN <nestable_expr> recursively)
      additional_operands = res.register(self.multi_expression_nestable())
      if res.error:
        self.pop_context()
        return res
      operands.extend(additional_operands)

      self.pop_context()
      return res.success(StringConcatNode(operands))

    self.pop_context()
    return res

  def string_literal(self):
    res = ParseResult()
    
    # Expect opening quote
    if self.current_token['type'] != TokenType.QUOTE:
      return res.failure(self.syntax_error(self.current_token, 'QUOTE (")', self.current_token['value'], category='String Delimiter', context_kind='string_literal'))
    
    opening_quote = self.current_token
    self.advance() # Eat opening quote

    # Check for string content or immediate closing quote (empty string)
    if self.current_token['type'] == TokenType.STRING:
      string_token = self.current_token
      self.advance() # Eat string content
    else:
      # Empty string case - create a token with empty value
      string_token = {'type': TokenType.STRING, 'value': '', 'line': opening_quote['line']}

    # Expect closing quote
    if self.current_token['type'] != TokenType.QUOTE:
      return res.failure(self.syntax_error(self.current_token, 'QUOTE (")', self.current_token['value'], category='String Delimiter', context_kind='string_literal'))
    
    self.advance() # Eat closing quote

    return res.success(StringNode(string_token))

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def arithmetic_binary_operation(self):
    self.push_context('arithmetic_binary_operation', '<operation> <expr> AN <expr>')
    res = ParseResult()

    # if self.current_token[TOKEN_TAG] in (PRODUKT_OF, QUOSHUNT_OF, SUM_OF, DIFF_OF, BIGGR_OF, SMALLR_OF):
    operation = self.current_token

    self.advance() # Eath

    # Parse the left operand
    left = res.register(self.arithmetic_expression())
    if res.error:
      self.pop_context()
      return res
    if left is None:
      self.pop_context()
      return res.failure(self.syntax_error(operation, 'left operand expression', category='Arithmetic Operation', context_kind='arithmetic'))

    # check for 'AN' keyword
    if self.current_token['type'] != TokenType.AN:
      self.pop_context()
      return res.failure(self.syntax_error(operation, 'AN', self.current_token['value'], category='Arithmetic Operation', context_kind='arithmetic'))

    # Advance past the 'AN' keyword
    self.advance()

    # Parse the right operand which may also be an expression
    right = res.register(self.arithmetic_expression())
    if res.error:
      self.pop_context()
      return res
    if right is None:
      self.pop_context()
      return res.failure(self.syntax_error(operation, 'right operand expression', category='Arithmetic Operation', context_kind='arithmetic'))

    # Return an operation node with left and right operands
    self.pop_context()
    return res.success(ArithmeticBinaryOpNode(left, operation, right))

  def arithmetic_expression(self):
    res = ParseResult()
    # Grammar: <arithmetic_op> ::= <arithmetic_expr> | <literal> | varident | <array_access>
    token = self.current_token

    if token['type'] in (TokenType.PRODUKT_OF, TokenType.QUOSHUNT_OF, TokenType.SUM_OF, TokenType.MOD_OF, TokenType.DIFF_OF, TokenType.BIGGR_OF, TokenType.SMALLR_OF):
      res.node = res.register(self.arithmetic_binary_operation())
    elif token['type'] == TokenType.IDENTIFIER:
      # Check if this is array access
      next_token = self.peek()
      if next_token and next_token['type'] == TokenType.LBRACKET:
        res.node = res.register(self.array_access())
      else:
        res.node = res.register(self.variable_literal())
    elif token['type'] in (TokenType.INTEGER, TokenType.FLOAT, TokenType.QUOTE, TokenType.WIN, TokenType.FAIL, TokenType.NOOB):
      # Any literal can be used in arithmetic (will be implicitly typecast by interpreter)
      res.node = res.register(self.literal())

    return res

  def arithmetic_literal(self):
    res = ParseResult()
    token = self.current_token

    if token['type'] in (TokenType.INTEGER, TokenType.FLOAT):
      self.advance()

      if token['type'] == TokenType.INTEGER:
        return res.success(IntegerNode(token))
      else:
        return res.success(FloatNode(token))

    return res.failure(self.syntax_error(token, 'int or float', token['value'] if token else 'end of input'))

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def boolean_nest(self):
    self.push_context('boolean_nest', 'boolean operation')
    res = ParseResult()
    # Grammar: <boolean_nest> ::= BOTH OF <nestable_expr> AN <nestable_expr> | EITHER OF <nestable_expr> AN <nestable_expr> | WON OF <nestable_expr> AN <nestable_expr> | NOT <nestable_expr>

    if self.current_token['type'] in (TokenType.BOTH_OF, TokenType.EITHER_OF, TokenType.WON_OF):
      res.node = res.register(self.boolean_binary_operation())

    elif self.current_token['type'] == TokenType.NOT:
      res.node = res.register(self.boolean_unary_operation())

    self.pop_context()
    return res

  def boolean_non_nest(self):
    self.push_context('boolean_non_nest', 'ALL OF / ANY OF ... MKAY')
    res = ParseResult()
    # Grammar: <boolean_non_nest> ::= ALL OF <nestable_expr> AN <multi_expression_nestable> MKAY | ANY OF <nestable_expr> AN <multi_expression_nestable> MKAY
    boolean_statements = []

    if self.current_token['type'] in (TokenType.ALL_OF, TokenType.ANY_OF):
      operation = self.current_token
      self.advance() # Eat ALL OF or ANY OF

      # Parse the first nestable expression
      first_operand = res.register(self.nestable_expr())
      if res.error:
        self.pop_context()
        return res
      
      boolean_statements.append(first_operand)

      # Expect AN
      if self.current_token['type'] != TokenType.AN:
        self.pop_context()
        return res.failure(self.syntax_error(operation, 'AN', self.current_token['value'], category='Boolean Multi-Operand', context_kind='boolean_any_all'))

      # Don't eat AN yet - let multi_expression_nestable handle it

      # Parse multi_expression_nestable (which starts with AN)
      additional_operands = res.register(self.multi_expression_nestable())
      if res.error:
        self.pop_context()
        return res
      boolean_statements.extend(additional_operands)

      # Expect MKAY
      if self.current_token['type'] != TokenType.MKAY:
        self.pop_context()
        return res.failure(self.syntax_error(operation, 'MKAY', self.current_token['value'], category='Boolean Multi-Operand', context_kind='boolean_any_all'))

      self.advance() # Eat MKAY

      self.pop_context()
      return res.success(BooleanTernaryOpNode(operation, boolean_statements))

    self.pop_context()
    return res

  def multi_expression_nestable(self):
    res = ParseResult()
    # Grammar: <multi_expression_nestable> ::= AN <nestable_expr> <multi_expression_nestable> | ε
    expressions = []

    # Continue while there are AN keywords
    while self.current_token['type'] == TokenType.AN:
      self.advance() # Eat AN

      expr = res.register(self.nestable_expr())
      if res.error: return res
      
      expressions.append(expr)

    return res.success(expressions)

  def boolean_binary_operation(self):
    res = ParseResult()

    if self.current_token['type'] in (TokenType.BOTH_OF, TokenType.EITHER_OF, TokenType.WON_OF):
      operation = self.current_token
      self.advance()  # Eat

      # Parse the left operand (nestable_expr)
      left = res.register(self.nestable_expr())
      if res.error: return res
      if left is None:
        return res.failure(self.syntax_error(operation, 'left operand expression', category='Boolean Operation', context_kind='boolean_binary'))

      # Check for 'AN' keyword
      if self.current_token['type'] != TokenType.AN:
        return res.failure(self.syntax_error(operation, 'AN', self.current_token['value'], category='Boolean Operation', context_kind='boolean_binary'))

      # Advance past the 'AN' keyword
      self.advance()

      # Parse the right operand (nestable_expr)
      right = res.register(self.nestable_expr())
      if res.error: return res
      if right is None:
        return res.failure(self.syntax_error(operation, 'right operand expression', category='Boolean Operation', context_kind='boolean_binary'))

      # Return an operation node with left and right operands
      return res.success(BooleanBinaryOpNode(left, operation, right))

  def boolean_unary_operation(self):
    res = ParseResult()

    if self.current_token['type'] == TokenType.NOT:
      operation = self.current_token
      self.advance() # Eat NOT

      # Parse the operand (nestable_expr)
      operand = res.register(self.nestable_expr())
      if res.error: return res
      if operand is None:
        return res.failure(self.syntax_error(operation, 'operand expression', category='Boolean Operation', context_kind='boolean_unary'))

      return res.success(BooleanUnaryOpNode(operation, operand))

  def boolean_literal(self):
    res = ParseResult()
    token = self.current_token

    if token['type'] in (TokenType.WIN, TokenType.FAIL):
      self.advance() # Eat

      return res.success(BooleanNode(token))

    # Error
    return res.failure(self.syntax_error(token, 'WIN or FAIL', token['value'], category='Boolean Value', context_kind='boolean_literal'))

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def comparison_operation(self):
    self.push_context('comparison_operation', 'BOTH SAEM / DIFFRINT')
    res = ParseResult()
    # Grammar: <comparison> ::= BOTH SAEM <nestable_expr> AN <nestable_expr> | DIFFRINT <nestable_expr> AN <nestable_expr>
    # Grammar: <relational> ::= BOTH SAEM <nestable_expr> AN BIGGR OF <nestable_expr> AN <nestable_expr> | ...

    if self.current_token['type'] in (TokenType.BOTH_SAEM, TokenType.DIFFRINT):
      operation = self.current_token
      self.advance() # Eat BOTH SAEM or DIFFRINT

      # Parse the left operand (nestable_expr)
      left = res.register(self.nestable_expr())
      if res.error:
        self.pop_context()
        return res
      if left is None:
        self.pop_context()
        return res.failure(self.syntax_error(operation, 'left operand expression', category='Comparison', context_kind='comparison'))

      # Check for 'AN' keyword
      if self.current_token['type'] != TokenType.AN:
        self.pop_context()
        return res.failure(self.syntax_error(operation, 'AN', self.current_token['value'], category='Comparison', context_kind='comparison'))

      # Advance past the 'AN' keyword
      self.advance()

      # Parse the right operand
      # Check if there is BIGGR OF or SMALLR OF (relational operation)
      if self.current_token['type'] in (TokenType.BIGGR_OF, TokenType.SMALLR_OF):
        # This is a relational operation
        right = res.register(self.arithmetic_binary_operation())
        if res.error:
          self.pop_context()
          return res
        if right is None:
          self.pop_context()
          return res.failure(self.syntax_error(operation, 'right operand expression', category='Comparison', context_kind='comparison'))
      else:
        # Regular comparison
        right = res.register(self.nestable_expr())
        if res.error:
          self.pop_context()
          return res
        if right is None:
          self.pop_context()
          return res.failure(self.syntax_error(operation, 'right operand expression', category='Comparison', context_kind='comparison'))

      # Return an operation node with left and right operands
      self.pop_context()
      return res.success(ComparisonOpNode(left, operation, right))

    self.pop_context()
    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def print_statement(self):
    self.push_context('print_statement', 'VISIBLE <expr> [<expr>]...')
    res = ParseResult()
    # Grammar: <output> ::= VISIBLE <print_args>
    # Grammar: <print_args> ::= <expression> | <expression> + <print_args>
    operands = []

    if self.current_token['type'] == TokenType.VISIBLE:
      self.advance() # Eat VISIBLE

      # Parse the first expression (required - VISIBLE cannot be empty)
      first_operand = res.register(self.expression())
      if res.error:
        self.pop_context()
        return res

      # Check if expression returned None (empty VISIBLE statement)
      if first_operand is None:
        visible_tok = self.peek(-1) or self.current_token
        self.pop_context()
        return res.failure(self.syntax_error(visible_tok, 'expression operand', visible_tok['value'], category='Output Keyword', context_kind='print'))

      operands.append(first_operand)

      # Continue while there's a + or AN separator
      suppress_newline = False
      while self.current_token['type'] in (TokenType.EXCLAMATION, TokenType.AN, TokenType.PLUS):
        # Check if it's an exclamation mark (suppress newline)
        if self.current_token['type'] == TokenType.EXCLAMATION:
          suppress_newline = True
          self.advance() # Eat '!'
          break  # ! should be at the end, no more operands after it
        
        self.advance() # Eat 'AN' or '+'

        additional_operand = res.register(self.expression())
        if res.error:
          self.pop_context()
          return res
        operands.append(additional_operand)

      # Success
      self.pop_context()
      return res.success(PrintNode(operands, suppress_newline))

    self.pop_context()
    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def typecast(self):
    self.push_context('typecast', 'MAEK <expr> A <type>')
    res = ParseResult()
    # Supports two syntaxes:
    # 1. MAEK A <var> <type_literal> - alternative syntax
    # 2. MAEK <nestable_expr> A <type_literal> - grammar syntax
    # Note: varident IS NOW A is handled in assignment_statement

    if self.current_token['type'] == TokenType.MAEK:
      self.advance() # Eat MAEK

      # Check if next token is 'A' (syntax: MAEK A <var> <type>)
      if self.current_token['type'] == TokenType.A:
        self.advance() # Eat A

        # Parse the variable/expression to typecast
        source_value = res.register(self.nestable_expr())
        if res.error:
          self.pop_context()
          return res

        # Parse type literal (NOOB, TROOF, NUMBAR, NUMBR, YARN)
        if self.current_token['value'] in ("NUMBAR", "NUMBR", "YARN", "TROOF", "NOOB"):
          desired_type = self.current_token['value']
          self.advance() # Eat desired type
          self.pop_context()
          return res.success(TypecastNode(source_value, desired_type))
        else:
          self.pop_context()
          return res.failure(self.syntax_error(self.current_token, ['NOOB','TROOF','NUMBAR','NUMBR','YARN'], self.current_token['value'], category='Type Literal', context_kind='typecast'))

      else:
        # MAEK <expr> A <type> syntax
        # Parse the nestable expression to typecast
        source_value = res.register(self.nestable_expr())
        if res.error:
          self.pop_context()
          return res

        # Expect 'A' keyword
        if self.current_token['type'] != TokenType.A:
          self.pop_context()
          return res.failure(self.syntax_error(self.peek(-1) or self.current_token, 'A', self.current_token['value'], category='Typecast', context_kind='typecast'))

        self.advance() # Eat A

        # Parse type literal (NOOB, TROOF, NUMBAR, NUMBR, YARN)
        if self.current_token['value'] in ("NUMBAR", "NUMBR", "YARN", "TROOF", "NOOB"):
          desired_type = self.current_token['value']
          self.advance() # Eat desired type
          self.pop_context()
          return res.success(TypecastNode(source_value, desired_type))
        else:
          self.pop_context()
          return res.failure(self.syntax_error(self.current_token, ['NOOB','TROOF','NUMBAR','NUMBR','YARN'], self.current_token['value'], category='Type Literal', context_kind='typecast'))

    self.pop_context()
    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def assignment_statement(self):
    self.push_context('assignment_statement', '<var> R <expr> | <var> IS NOW A <type>')
    res = ParseResult()

    if self.current_token['type'] == TokenType.IDENTIFIER:
      var_to_access = self.current_token

      self.advance() # Eat Variable Identifier

      # Check for 'R' keyword
      if self.current_token['type'] not in (TokenType.R, TokenType.IS_NOW_A):
        # If next token looks like start of an expression, treat as missing assignment operator
        # Note: I_IZ is NOT included because it starts a new statement, not an expression
        expr_start_types = {
          TokenType.PRODUKT_OF, TokenType.QUOSHUNT_OF, TokenType.SUM_OF, TokenType.DIFF_OF,
          TokenType.MOD_OF, TokenType.BIGGR_OF, TokenType.SMALLR_OF, TokenType.BOTH_OF,
          TokenType.EITHER_OF, TokenType.WON_OF, TokenType.NOT, TokenType.BOTH_SAEM,
          TokenType.DIFFRINT, TokenType.MAEK, TokenType.INTEGER,
          TokenType.FLOAT, TokenType.STRING, TokenType.WIN, TokenType.FAIL, TokenType.NOOB,
          TokenType.SMOOSH, TokenType.ALL_OF, TokenType.ANY_OF
        }
        if self.current_token['type'] in expr_start_types:
          self.pop_context()
          return res.failure(self.syntax_error(var_to_access, ['R','IS NOW A'], self.current_token['value'], category='Assignment', context_kind='assignment'))
        # Otherwise treat as simple variable access (standalone)
        self.pop_context()
        return res.success(VarAccessNode(var_to_access))


      # Else, continue
      if self.current_token['type'] == TokenType.R:
        self.advance() # Eat R

        value_to_assign = res.register(self.expression())

        # Check for errors
        if value_to_assign is None:
          r_token = self.peek(-1) or var_to_access
          self.pop_context()
          return res.failure(self.syntax_error(r_token, 'expression', (self.current_token['value'] if self.current_token else 'end of input'), category='Assignment Operator', context_kind='assignment'))

        self.pop_context()
        return res.success(VarAssignmentNode(var_to_access, value_to_assign))

      # Var assignment with TYPECASTING
      elif self.current_token['type'] == TokenType.IS_NOW_A:
        self.advance() # Eat IS NOW A

        if self.current_token['value'] not in ("NUMBAR", "NUMBR", "YARN", "TROOF"):
          self.pop_context()
          return res.failure(self.syntax_error(self.current_token, ['NUMBAR','NUMBR','YARN','TROOF'], self.current_token['value'], category='Type Literal', context_kind='assignment_typecast'))

        # Else, continue
        desired_type = self.current_token['value']

        self.advance() # Eat the desired type

        self.pop_context()
        return res.success(VarAssignmentNode(var_to_access, TypecastNode(VarAccessNode(var_to_access), desired_type)))

    self.pop_context()
    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def array_operation(self):
    self.push_context('array_operation', 'CONFINE / DISCHARGE')
    res = ParseResult()
    # Grammar: <array_operation> ::= CONFINE <nestable_expr> IN uhsident AT <index_expr> | DISCHARGE uhsident AT <index_expr>

    if self.current_token['type'] == TokenType.CONFINE:
      self.advance() # Eat CONFINE

      # Parse value expression
      value_expr = res.register(self.nestable_expr())
      if res.error:
        self.pop_context()
        return res
      if value_expr is None:
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'value expression', self.current_token['value'], category='Array Operation', context_kind='confine'))

      # Expect IN
      if self.current_token['type'] != TokenType.IN:
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'IN', self.current_token['value'], category='Array Operation', context_kind='confine'))
      self.advance() # Eat IN

      # Expect array identifier
      if self.current_token['type'] != TokenType.IDENTIFIER:
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'array identifier', self.current_token['value'], category='Array Operation', context_kind='confine'))
      array_name_token = self.current_token
      self.advance() # Eat identifier

      # Expect AT
      if self.current_token['type'] != TokenType.AT:
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'AT', self.current_token['value'], category='Array Operation', context_kind='confine'))
      self.advance() # Eat AT

      # Parse index expression
      index_expr = res.register(self.index_expression())
      if res.error:
        self.pop_context()
        return res
      if index_expr is None:
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'index expression', self.current_token['value'], category='Array Operation', context_kind='confine'))

      self.pop_context()
      return res.success(ArrayConfineNode(value_expr, array_name_token, index_expr))

    elif self.current_token['type'] == TokenType.DISCHARGE:
      self.advance() # Eat DISCHARGE

      # Expect array identifier
      if self.current_token['type'] != TokenType.IDENTIFIER:
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'array identifier', self.current_token['value'], category='Array Operation', context_kind='discharge'))
      array_name_token = self.current_token
      self.advance() # Eat identifier

      # Expect AT
      if self.current_token['type'] != TokenType.AT:
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'AT', self.current_token['value'], category='Array Operation', context_kind='discharge'))
      self.advance() # Eat AT

      # Parse index expression
      index_expr = res.register(self.index_expression())
      if res.error:
        self.pop_context()
        return res
      if index_expr is None:
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'index expression', self.current_token['value'], category='Array Operation', context_kind='discharge'))

      self.pop_context()
      return res.success(ArrayDischargeNode(array_name_token, index_expr))

    self.pop_context()
    return res

  def array_access(self):
    self.push_context('array_access', 'array[index]')
    res = ParseResult()
    # Grammar: <array_access> ::= uhsident [ <index_expr> ]

    if self.current_token['type'] != TokenType.IDENTIFIER:
      self.pop_context()
      return res.failure(self.syntax_error(self.current_token, 'array identifier', self.current_token['value'], category='Array Access', context_kind='array_access'))
    
    array_name_token = self.current_token
    self.advance() # Eat identifier

    # Expect LBRACKET
    if self.current_token['type'] != TokenType.LBRACKET:
      self.pop_context()
      return res.failure(self.syntax_error(self.current_token, '[', self.current_token['value'], category='Array Access', context_kind='array_access'))
    self.advance() # Eat [

    # Parse index expression
    index_expr = res.register(self.index_expression())
    if res.error:
      self.pop_context()
      return res
    if index_expr is None:
      self.pop_context()
      return res.failure(self.syntax_error(self.current_token, 'index expression', self.current_token['value'], category='Array Access', context_kind='array_access'))

    # Expect RBRACKET
    if self.current_token['type'] != TokenType.RBRACKET:
      self.pop_context()
      return res.failure(self.syntax_error(self.current_token, ']', self.current_token['value'], category='Array Access', context_kind='array_access'))
    self.advance() # Eat ]

    self.pop_context()
    return res.success(ArrayAccessNode(array_name_token, index_expr))

  def index_expression(self):
    res = ParseResult()
    # Grammar: <index_expr> ::= numbr | varident | <arithmetic_expr> | <array_access>

    if self.current_token['type'] == TokenType.INTEGER:
      res.node = res.register(self.arithmetic_literal())
    elif self.current_token['type'] == TokenType.IDENTIFIER:
      # Check if this is array access
      next_token = self.peek()
      if next_token and next_token['type'] == TokenType.LBRACKET:
        res.node = res.register(self.array_access())
      else:
        res.node = res.register(self.variable_literal())
    elif self.current_token['type'] in (TokenType.SUM_OF, TokenType.DIFF_OF, TokenType.PRODUKT_OF, TokenType.QUOSHUNT_OF, TokenType.MOD_OF):
      res.node = res.register(self.arithmetic_binary_operation())
    else:
      return res.failure(self.syntax_error(self.current_token, 'integer, variable, array access, or arithmetic expression', self.current_token['value'], category='Array Index', context_kind='index_expr'))

    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def input_statement(self):
    self.push_context('input_statement', 'GIMMEH <var>')
    res = ParseResult()

    if self.current_token['type'] == TokenType.GIMMEH:
      self.advance() # Eat Gimmeh

      # Error
      if self.current_token['type'] != TokenType.IDENTIFIER:
        self.pop_context()
        return res.failure(self.syntax_error(self.peek(-1) or self.current_token, 'IDENTIFIER', self.current_token['value'], category='Input Keyword', context_kind='input'))

      # Check if the variable name is valid
      variable_to_access = res.register(self.variable_literal())
      if variable_to_access is None:
        self.pop_context()
        return res # Error

      # Proceed to the next step (getting user input and storing it in the variable stated)
      self.pop_context()
      return res.success(InputNode(variable_to_access))

    self.pop_context()
    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def break_statement(self):
    self.push_context('break_statement', 'GTFO')
    res = ParseResult()

    if self.current_token['type'] == TokenType.GTFO:
      # Validate that GTFO is used in valid context (switch/loop/function)
      if not self.is_in_valid_gtfo_context():
        self.pop_context()
        return res.failure(self.syntax_error(
          self.current_token,
          'GTFO inside switch (WTF), loop (IM IN YR), or function (HOW IZ I)',
          'GTFO outside valid context',
          category='Break Statement',
          context_kind='break'
        ))
      
      break_token = self.current_token
      self.advance() # Eat GTFO

      self.pop_context()
      return res.success(BreakNode(break_token))

    self.pop_context()
    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def return_statement(self):
    self.push_context('return_statement', 'FOUND YR <expr>')
    res = ParseResult()

    if self.current_token['type'] == TokenType.FOUND_YR:
      self.advance() # Eat FOUND YR

      return_expression = res.register(self.expression())
      if return_expression is None:
        self.pop_context()
        return res  # Has error

      self.pop_context()
      return res.success(ReturnNode(return_expression))

    self.pop_context()
    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def if_statement(self):
    self.push_context('if_statement', 'O RLY? ... OIC')
    res = ParseResult()
    # Grammar: <if_case> ::= <nestable_expr>, O RLY? <linebreak> <if_true> <if_false> OIC
    # Note: The nestable_expr should be parsed before calling this method
    # But for simplicity, we'll check if we're at O RLY

    if self.current_token['type'] == TokenType.O_RLY:
      # Optional: handle comma before O RLY (if it was parsed as separate token)
      self.advance() # Eat O RLY?

      # Skip newlines after O RLY?
      while self.current_token['type'] == TokenType.NEWLINE:
        self.advance()

      # Parse if_true: YA RLY <linebreak> <statement_list> <linebreak>
      if self.current_token['type'] != TokenType.YA_RLY:
        self.pop_context()
        return res.failure(self.syntax_error(self.peek(-1) or self.current_token, 'YA RLY', self.current_token['value'], category='Conditional', context_kind='if'))

      self.advance() # Eat YA RLY

      # Parse statements for if_true block
      if_block_statements = []
      while self.current_token['type'] not in (TokenType.MEBBE, TokenType.NO_WAI, TokenType.OIC, TokenType.KTHXBYE):
        # Skip leading newlines
        while self.current_token['type'] == TokenType.NEWLINE:
          self.advance()
        if self.current_token['type'] in (TokenType.MEBBE, TokenType.NO_WAI, TokenType.OIC, TokenType.KTHXBYE):
          break
        
        statement = res.register(self.statement())
        if res.error: return res
        if statement:
          if_block_statements.append(statement)
        # Check for statement separators
        if self.current_token['type'] == TokenType.COMMA:
          self.advance()
        elif self.current_token['type'] == TokenType.NEWLINE:
          self.advance()

      # Parse if_false: MEBBE <expression> <linebreak> <statement_list> <linebreak> <if_false> | NO WAI <linebreak> <statement_list> <linebreak> | ε
      mebbe_cases = []  # List of (condition, statements) tuples
      else_block_statements = []

      # Handle MEBBE clauses
      while self.current_token['type'] == TokenType.MEBBE:
        self.advance() # Eat MEBBE

        # Parse condition expression
        mebbe_condition = res.register(self.expression())
        if res.error: return res

        # Parse statements for this MEBBE block
        mebbe_statements = []
        while self.current_token['type'] not in (TokenType.MEBBE, TokenType.NO_WAI, TokenType.OIC, TokenType.KTHXBYE):
          # Skip leading newlines
          while self.current_token['type'] == TokenType.NEWLINE:
            self.advance()
          if self.current_token['type'] in (TokenType.MEBBE, TokenType.NO_WAI, TokenType.OIC, TokenType.KTHXBYE):
            break
          
          statement = res.register(self.statement())
          if res.error: return res
          if statement:
            mebbe_statements.append(statement)
          # Check for statement separators
          if self.current_token['type'] == TokenType.COMMA:
            self.advance()
          elif self.current_token['type'] == TokenType.NEWLINE:
            self.advance()

        mebbe_cases.append((mebbe_condition, mebbe_statements))

      # Handle NO WAI (else)
      if self.current_token['type'] == TokenType.NO_WAI:
        self.advance() # Eat NO WAI

        while self.current_token['type'] not in (TokenType.OIC, TokenType.KTHXBYE):
          # Skip leading newlines
          while self.current_token['type'] == TokenType.NEWLINE:
            self.advance()
          if self.current_token['type'] in (TokenType.OIC, TokenType.KTHXBYE):
            break
          
          statement = res.register(self.statement())
          if res.error: return res
          if statement:
            else_block_statements.append(statement)
          # Check for statement separators
          if self.current_token['type'] == TokenType.COMMA:
            self.advance()
          elif self.current_token['type'] == TokenType.NEWLINE:
            self.advance()

      # Expect OIC
      if self.current_token['type'] != TokenType.OIC:
        self.pop_context()
        return res.failure(self.syntax_error(self.peek(-1) or self.current_token, 'OIC', self.current_token['value'], category='Conditional', context_kind='if'))

      self.advance() # Eat OIC

      # For now, convert MEBBE to nested if-else structure
      # Store mebbe_cases in a way the interpreter can handle
      self.pop_context()
      return res.success(IfNode(if_block_statements, else_block_statements, mebbe_cases))

    self.pop_context()
    return res



# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def switch_case_statement(self):
    self.push_context('switch_case_statement', 'WTF? ... OIC')
    self.push_control_flow('switch')  # Track that we're inside a switch for GTFO validation
    res = ParseResult()
    cases = []
    cases_statements = []
    default_case_statements = []

    if self.current_token['type'] == TokenType.WTF:
      # Eat WTF
      self.advance()

      # Skip newlines after WTF?
      while self.current_token['type'] == TokenType.NEWLINE:
        self.advance()

      # Error
      if self.current_token['type'] != TokenType.OMG:
        self.pop_control_flow()  # Exit switch context on error
        self.pop_context()
        return res.failure(self.syntax_error(self.peek(-1) or self.current_token, 'OMG', self.current_token['value'], category='Switch Start', context_kind='switch'))

      while self.current_token['type'] == TokenType.OMG:
        statements = []

        # Eat OMG
        self.advance()

        # Error - OMG must be followed by a literal value only (not expressions)
        if self.current_token['type'] not in (TokenType.INTEGER, TokenType.FLOAT, TokenType.QUOTE, TokenType.WIN, TokenType.FAIL, TokenType.NOOB):
          self.pop_control_flow()  # Exit switch context on error
          self.pop_context()
          return res.failure(self.syntax_error(self.current_token, 'literal (INTEGER, FLOAT, STRING, WIN, FAIL, or NOOB)', self.current_token['value'], category='Switch Case', context_kind='switch'))

        # Eat
        case_condition = res.register(self.literal())

        # Has error
        if case_condition is None:
          return res

        while self.current_token['type'] not in (TokenType.OMG, TokenType.OMGWTF, TokenType.OIC, TokenType.KTHXBYE):
          # Skip leading newlines
          while self.current_token['type'] == TokenType.NEWLINE:
            self.advance()
          if self.current_token['type'] in (TokenType.OMG, TokenType.OMGWTF, TokenType.OIC, TokenType.KTHXBYE):
            break
          
          statement = res.register(self.statement())

          # Has error
          if statement is None:
            return res

          statements.append(statement)
          # Check for statement separators
          if self.current_token['type'] == TokenType.COMMA:
            self.advance()
          elif self.current_token['type'] == TokenType.NEWLINE:
            self.advance()
        # Loop end

        cases.append(case_condition)
        cases_statements.append(statements)
      # Loop end

      if self.current_token['type'] != TokenType.OMGWTF:
        self.pop_control_flow()  # Exit switch context on error
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'OMGWTF', self.current_token['value'], category='Switch Default', context_kind='switch'))

      # Eat OMGWTF
      self.advance()

      # Add switch case
      while self.current_token['type'] not in (TokenType.OIC, TokenType.KTHXBYE):
        # Skip leading newlines
        while self.current_token['type'] == TokenType.NEWLINE:
          self.advance()
        if self.current_token['type'] in (TokenType.OIC, TokenType.KTHXBYE):
          break
        
        statement = res.register(self.statement())

        # Has error
        if statement is None:
          self.pop_control_flow()  # Exit switch context on error
          self.pop_context()
          return res

        default_case_statements.append(statement)
        # Check for statement separators
        if self.current_token['type'] == TokenType.COMMA:
          self.advance()
        elif self.current_token['type'] == TokenType.NEWLINE:
          self.advance()

      if self.current_token['type'] != TokenType.OIC:
        self.pop_control_flow()  # Exit switch context on error
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'OIC', self.current_token['value'], category='Switch Terminator', context_kind='switch'))

      # Eat OIC
      self.advance()

      self.pop_control_flow()  # Exit switch context
      self.pop_context()
      return res.success(SwitchCaseNode(cases, cases_statements, default_case_statements))

    self.pop_control_flow()  # Exit switch context on early return
    self.pop_context()
    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def loop_statement(self):
    self.push_context('loop_statement', 'IM IN YR ... IM OUTTA YR')
    self.push_control_flow('loop')  # Track that we're inside a loop for GTFO validation
    res = ParseResult()
    label = None
    operation = None
    variable = None
    til_wile_expression = None
    body_statements = []

    if self.current_token['type'] == TokenType.IM_IN_YR:
      # Eat IM IN YR
      self.advance()

      if self.current_token['type'] != TokenType.IDENTIFIER:
        self.pop_control_flow()  # Exit loop context on error
        self.pop_context()
        return res.failure(self.syntax_error(self.peek(-1) or self.current_token, 'loop label IDENTIFIER', self.current_token['value'], category='Loop Start', context_kind='loop'))

      label = self.current_token['value']
      # Eat label
      self.advance()

      if self.current_token['type'] not in (TokenType.UPPIN, TokenType.NERFIN):
        self.pop_control_flow()  # Exit loop context on error
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, ['UPPIN','NERFIN'], self.current_token['value'], category='Loop Operation', context_kind='loop'))

      # Else, no error
      operation = self.current_token

      # Eat UPPIN or NERFIN
      self.advance()

      if self.current_token['type'] != TokenType.YR:
        self.pop_control_flow()  # Exit loop context on error
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'YR', self.current_token['value'], category='Loop Clause', context_kind='loop'))

      # Else, no error
      # Eat YR
      self.advance()

      # Var
      if self.current_token['type'] != TokenType.IDENTIFIER:
        self.pop_control_flow()  # Exit loop context on error
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'loop variable IDENTIFIER', self.current_token['value'], category='Loop Variable', context_kind='loop'))

      # Get the desired variable to access (same with assignment statement)
      variable = self.current_token

      # Eat variable
      self.advance()

      # TIL/WILE
      clause_type = None
      if self.current_token['type'] in (TokenType.TIL, TokenType.WILE):
        # Eat TIL or WILE
        clause_type = self.current_token['type']
        self.advance()

        til_wile_expression = res.register(self.expression())

        # Has error
        if til_wile_expression is None:
          return res

      # Loop body
      while self.current_token['type'] not in (TokenType.IM_OUTTA_YR, TokenType.KTHXBYE):
        # Skip leading newlines
        while self.current_token['type'] == TokenType.NEWLINE:
          self.advance()
        if self.current_token['type'] in (TokenType.IM_OUTTA_YR, TokenType.KTHXBYE):
          break
        
        statement = res.register(self.statement())

        # Has error
        if statement is None:
          return res

        body_statements.append(statement)
        # Check for statement separators
        if self.current_token['type'] == TokenType.COMMA:
          self.advance()
        elif self.current_token['type'] == TokenType.NEWLINE:
          self.advance()

      # Loop out
      if self.current_token['type'] != TokenType.IM_OUTTA_YR:
        self.pop_control_flow()  # Exit loop context on error
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'IM OUTTA YR', self.current_token['value'], category='Loop Terminator', context_kind='loop'))

      # Eat IM OUTTA YR
      self.advance()

      if self.current_token['type'] != TokenType.IDENTIFIER:
        self.pop_control_flow()  # Exit loop context on error
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'loop exit label IDENTIFIER', self.current_token['value'], category='Loop Terminator', context_kind='loop'))

      out_label = self.current_token['value']

      # Eat label
      self.advance()

      # print(label, out_label)
      if label != out_label:
        self.pop_control_flow()  # Exit loop context on error
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, label, out_label, category='Loop Terminator', context_kind='loop'))


      self.pop_control_flow()  # Exit loop context
      self.pop_context()
      return res.success(LoopNode(label, operation, variable, clause_type, til_wile_expression, body_statements))

    self.pop_control_flow()  # Exit loop context on early return
    self.pop_context()
    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def function_definition(self):
    self.push_context('function_definition', 'HOW IZ I ... IF U SAY SO')
    self.push_control_flow('function')  # Track that we're inside a function for GTFO validation
    res = ParseResult()
    function_name = None
    parameters = []
    body_statements = []

    if self.current_token['type'] == TokenType.HOW_IZ_I:
      # Eat HOW IZ I
      self.advance()

      # Identifier
      if self.current_token['type'] != TokenType.IDENTIFIER:
        self.pop_control_flow()  # Exit function context on error
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'function name IDENTIFIER', self.current_token['value'], category='Function Definition', context_kind='function_def'))

      function_name = self.current_token
      # Eat function name
      self.advance()

      # Check if there are parameters
      if self.current_token['type'] == TokenType.YR:
        # Eat YR
        self.advance()

        first_param = res.register(self.expression())
        if first_param is None:
          self.pop_control_flow()  # Exit function context on error
          return res # Has error

        parameters.append(first_param)

        # Check for other params if there are any
        while self.current_token['type'] == TokenType.AN:
          # Eat AN
          self.advance()

          # Expect YR
          if self.current_token['type'] != TokenType.YR:
            self.pop_control_flow()  # Exit function context on error
            self.pop_context()
            return res.failure(self.syntax_error(self.current_token, 'YR', self.current_token['value'], category='Function Parameters', context_kind='function_def'))

          self.advance() # Eat YR

          additional_param = res.register(self.expression())
          if additional_param is None:
            self.pop_control_flow()  # Exit function context on error
            self.pop_context()
            return res # Has error

          parameters.append(additional_param)

      # function body
      while self.current_token['type'] not in (TokenType.FOUND_YR, TokenType.IF_U_SAY_SO, TokenType.KTHXBYE):
        # Skip leading newlines
        while self.current_token['type'] == TokenType.NEWLINE:
          self.advance()
        if self.current_token['type'] in (TokenType.FOUND_YR, TokenType.IF_U_SAY_SO, TokenType.KTHXBYE):
          break
        
        statement = res.register(self.statement())
        if statement is None:
          self.pop_control_flow()  # Exit function context on error
          self.pop_context()
          return res # Has error

        body_statements.append(statement)
        # Check for statement separators
        if self.current_token['type'] == TokenType.COMMA:
          self.advance()
        elif self.current_token['type'] == TokenType.NEWLINE:
          self.advance()

      if self.current_token['type'] == TokenType.FOUND_YR:
        # Eat FOUND YR
        self.advance()

        return_expression  = res.register(self.expression())
        if return_expression is None:
          self.pop_control_flow()  # Exit function context on error
          self.pop_context()
          return res # Has error

        body_statements.append(ReturnNode(return_expression))

      # Skip newlines before IF U SAY SO
      while self.current_token['type'] == TokenType.NEWLINE:
        self.advance()

      if self.current_token['type'] != TokenType.IF_U_SAY_SO:
        self.pop_control_flow()  # Exit function context on error
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'IF U SAY SO', self.current_token['value'], category='Function Terminator', context_kind='function_def'))

      # Eat IF U SAY SO
      self.advance()

      self.pop_control_flow()  # Exit function context
      self.pop_context()
      return res.success(FuncDefNode(function_name, parameters, body_statements))

    self.pop_control_flow()  # Exit function context on early return
    self.pop_context()
    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def function_call(self):
    self.push_context('function_call', 'I IZ <func> [YR <param>]... [MKAY]')
    res = ParseResult()
    function_name = None
    parameters = []

    if self.current_token['type'] == TokenType.I_IZ:
      # Eat I IZ
      self.advance()

      # Identifier
      if self.current_token['type'] != TokenType.IDENTIFIER:
        self.pop_context()
        return res.failure(self.syntax_error(self.current_token, 'function name IDENTIFIER', self.current_token['value'], category='Function Call', context_kind='function_call'))

      function_name = res.register(self.expression())
      if function_name is None:
        self.pop_context()
        return res

      # Check if there are parameters
      if self.current_token['type'] == TokenType.YR:
        # Eat YR
        self.advance()

        first_param = res.register(self.expression())
        if first_param is None:
          self.pop_context()
          return res # Has error

        parameters.append(first_param)

        # Check for other params if there are any
        while self.current_token['type'] == TokenType.AN:
          # Eat AN
          self.advance()

          # Expect YR
          if self.current_token['type'] != TokenType.YR:
            self.pop_context()
            return res.failure(self.syntax_error(self.current_token, 'YR', self.current_token['value'], category='Function Call Parameters', context_kind='function_call'))

          self.advance() # Eat YR

          additional_param = res.register(self.expression())
          if additional_param is None:
            self.pop_context()
            return res # Has error

          parameters.append(additional_param)

      # MKAY is optional for function calls - only consume it if present
      if self.current_token['type'] == TokenType.MKAY:
        self.advance() # Eat MKAY

      self.pop_context()
      return res.success(FuncCallNode(function_name, parameters))

    self.pop_context()
    return res