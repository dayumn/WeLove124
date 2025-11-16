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
    self.value = str(token['value'][1:-1])  # Remove quotes

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
  def __init__(self, operands):
    self.operands = operands

  def __repr__(self):
    return f"PrintNode({self.operands})"

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

class ProgramNode:
  def __init__(self, sections):
    self.sections = sections

  def __repr__(self):
    return f"ProgramNode({self.sections})"


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
    def __init__(self, token, details):
        super().__init__(token, details, error_name='Invalid Syntax')

    
#------------------------------------------------------------------------------------------------
# PARSER
#------------------------------------------------------------------------------------------------

class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.token_index = -1
    self.advance()

  def advance(self):
    self.token_index += 1
    if (self.token_index < len(self.tokens)):
      self.current_token = self.tokens[self.token_index]
    return self.current_token

  def parse(self):
    res = ParseResult()
    sections = []

    if (self.current_token['type'] != TokenType.HAI):
      return res.failure(InvalidSyntaxError(self.current_token, "Expected a 'HAI' Keyword!"))

    self.advance() # Eat HAI

    # Check if there's a variable section
    if self.current_token['type'] == TokenType.WAZZUP:
      self.advance() # Eat Wazzup

      variable_declaration_section =  res.register(self.variable_section())
      if variable_declaration_section is None: return res   # Check if there's an error
      sections.append(variable_declaration_section)         # No error

    # try to parse statements
    list_of_statements = res.register(self.statement_list())
    if list_of_statements is None: return res               # Check if there's an error
    sections.append(list_of_statements)                     # No error

    return res.success(ProgramNode(sections))

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def variable_section(self):
    res = ParseResult()
    variable_declarations = []

    while (self.current_token['type'] != TokenType.BUHBYE and self.current_token != self.tokens[-1]):
      variable_declaration = res.register(self.variable_declaration())

      # Has error
      if variable_declaration is None:
        return res

      variable_declarations.append(variable_declaration)

    # Error
    if (self.current_token['type'] != TokenType.BUHBYE):
      return res.failure(InvalidSyntaxError(self.current_token, "Expected a 'BUHBYE' or keyword!"))

    # No error
    self.advance() # Eat BUHBYE

    return res.success(VarDecListNode(variable_declarations))

  def variable_declaration(self):
    res = ParseResult()

    if self.current_token['type'] == TokenType.I_HAS_A:
      prev_token = self.current_token
      self.advance() # eats I has a

      if (self.current_token['type'] != TokenType.IDENTIFIER):
        return res.failure(InvalidSyntaxError(prev_token, "Expected Identifier!"))

      var_name_token = self.current_token
      self.advance() # eats var name

      if (self.current_token['type'] != TokenType.ITZ):
        return res.success(VarDeclarationNode(var_name_token, NoobNode()))

      itz_token = self.current_token
      self.advance() # eats ITZ

      expression = res.register(self.expression())
      if res.error: return res

      # Check if expression is None (ITZ without a value)
      if expression is None:
        return res.failure(InvalidSyntaxError(itz_token, "Expected a value after 'ITZ'!"))

      return res.success(VarDeclarationNode(var_name_token, expression))

    return res.failure(InvalidSyntaxError(self.current_token, "Expected an 'I HAS A' or 'BUHBYE' Keyword!"))

  def variable_literal(self):
    res = ParseResult()
    token = self.current_token

    if token['type'] == TokenType.IDENTIFIER:
      self.advance() # Eat

      return res.success(VarAccessNode(token))

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def statement_list(self):
    res = ParseResult()
    statements = []

    while (self.current_token['type'] != TokenType.KTHXBYE and self.current_token !=self.tokens[-1]):
      statement = res.register(self.statement())

      # Has error
      if statement is None:
        return res

      statements.append(statement)

    if (self.current_token['type'] != TokenType.KTHXBYE):
      return res.failure(InvalidSyntaxError(self.current_token, "Expected an 'KTHXBYE' keyword!"))

    return res.success(StatementListNode(statements))

  def statement(self):
    res = ParseResult()
    # Grammar: <statement> ::= <expression> | <conditional> | <loop> | <function_call> | <function_def> | <declaration> | <input> | <output>

    # Try declaration (I HAS A)
    if self.current_token['type'] == TokenType.I_HAS_A:
      res.node = res.register(self.variable_declaration())
      if res.error or res.node: return res

    # Try output (VISIBLE)
    res.node = res.register(self.print_statement())
    if res.error or res.node: return res

    # Try input (GIMMEH)
    res.node = res.register(self.input_statement())
    if res.error or res.node: return res

    # Try conditional (O RLY or WTF)
    res.node = res.register(self.if_statement())
    if res.error or res.node: return res

    res.node = res.register(self.switch_case_statement())
    if res.error or res.node: return res

    # Try loop (IM IN YR)
    res.node = res.register(self.loop_statement())
    if res.error or res.node: return res

    # Try function definition (HOW IZ I)
    res.node = res.register(self.function_definition())
    if res.error or res.node: return res

    # Try function call (I IZ)
    res.node = res.register(self.function_call())
    if res.error or res.node: return res

    # Try break statement (GTFO)
    res.node = res.register(self.break_statement())
    if res.error or res.node: return res

    # Try expression (includes assignment with R)
    res.node = res.register(self.expression())
    if res.error or res.node: return res

    # Can't parse
    return res.failure(InvalidSyntaxError(self.current_token, 'Unexpected Syntax'))

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
    # Grammar: <nestable_expr> ::= <arithmetic_expr> | <boolean_nest> | <comparison> | <function_call> | <typecasting> | <literal> | <relational> | varident

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

    # Try assignment (varident R or varident IS NOW A)
    if self.current_token['type'] == TokenType.IDENTIFIER:
      res.node = res.register(self.assignment_statement())
      return res

    # Try literal
    if self.current_token['type'] in (TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING, TokenType.WIN, TokenType.FAIL, TokenType.NOOB):
      res.node = res.register(self.literal())
      return res

    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def literal(self):
    res = ParseResult()

    if self.current_token['type'] in (TokenType.INTEGER, TokenType.FLOAT):
      res.node = res.register(self.arithmetic_literal())

    elif self.current_token['type'] == TokenType.STRING:
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
      if res.error: return res
      operands.extend(additional_operands)

      return res.success(StringConcatNode(operands))

    return res

  def string_literal(self):
    res = ParseResult()
    token = self.current_token

    if token['type'] == TokenType.STRING:
      self.advance() # Eat

      return res.success(StringNode(token))

    return res.failure(InvalidSyntaxError(token, 'Expected a string!'))

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def arithmetic_binary_operation(self):
    res = ParseResult()

    # if self.current_token[TOKEN_TAG] in (PRODUKT_OF, QUOSHUNT_OF, SUM_OF, DIFF_OF, BIGGR_OF, SMALLR_OF):
    operation = self.current_token

    self.advance() # Eath

    # Parse the left operand
    left = res.register(self.arithmetic_expression())  # Recursive call to handle the left side
    if res.error: return res

    # check for 'AN' keyword
    if self.current_token['type'] != TokenType.AN:
        # print(self.current_token['value'])
        return res.failure(InvalidSyntaxError(self.current_token, "Expected an 'AN' keyword!"))

    # Advance past the 'AN' keyword
    self.advance()

    # Parse the right operand which may also be an expression
    right = res.register(self.arithmetic_expression())  # Recursive call to handle right side
    if res.error: return res

    # Return an operation node with left and right operands
    return res.success(ArithmeticBinaryOpNode(left, operation, right))

  def arithmetic_expression(self):
    res = ParseResult()
    # Grammar: <arithmetic_op> ::= <arithmetic_expr> | <literal> | varident
    token = self.current_token

    if token['type'] in (TokenType.PRODUKT_OF, TokenType.QUOSHUNT_OF, TokenType.SUM_OF, TokenType.MOD_OF, TokenType.DIFF_OF, TokenType.BIGGR_OF, TokenType.SMALLR_OF):
      res.node = res.register(self.arithmetic_binary_operation())
    elif token['type'] == TokenType.IDENTIFIER:
      res.node = res.register(self.variable_literal())
    elif token['type'] in (TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING, TokenType.WIN, TokenType.FAIL, TokenType.NOOB):
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

    return res.failure(InvalidSyntaxError(token, 'Expected int or float!'))

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def boolean_nest(self):
    res = ParseResult()
    # Grammar: <boolean_nest> ::= BOTH OF <nestable_expr> AN <nestable_expr> | EITHER OF <nestable_expr> AN <nestable_expr> | WON OF <nestable_expr> AN <nestable_expr> | NOT <nestable_expr>

    if self.current_token['type'] in (TokenType.BOTH_OF, TokenType.EITHER_OF, TokenType.WON_OF):
      res.node = res.register(self.boolean_binary_operation())

    elif self.current_token['type'] == TokenType.NOT:
      res.node = res.register(self.boolean_unary_operation())

    return res

  def boolean_non_nest(self):
    res = ParseResult()
    # Grammar: <boolean_non_nest> ::= ALL OF <nestable_expr> AN <multi_expression_nestable> MKAY | ANY OF <nestable_expr> AN <multi_expression_nestable> MKAY
    boolean_statements = []

    if self.current_token['type'] in (TokenType.ALL_OF, TokenType.ANY_OF):
      operation = self.current_token
      self.advance() # Eat ALL OF or ANY OF

      # Parse the first nestable expression
      first_operand = res.register(self.nestable_expr())
      if res.error: return res
      boolean_statements.append(first_operand)

      # Expect AN
      if self.current_token['type'] != TokenType.AN:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected 'AN' keyword!"))

      # Don't eat AN yet - let multi_expression_nestable handle it

      # Parse multi_expression_nestable (which starts with AN)
      additional_operands = res.register(self.multi_expression_nestable())
      if res.error: return res
      boolean_statements.extend(additional_operands)

      # Expect MKAY
      if self.current_token['type'] != TokenType.MKAY:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected 'MKAY' keyword!"))

      self.advance() # Eat MKAY

      return res.success(BooleanTernaryOpNode(operation, boolean_statements))

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

      # Check for 'AN' keyword
      if self.current_token['type'] != TokenType.AN:
          return res.failure(InvalidSyntaxError(self.current_token, "Expected an 'AN' keyword!"))

      # Advance past the 'AN' keyword
      self.advance()

      # Parse the right operand (nestable_expr)
      right = res.register(self.nestable_expr())
      if res.error: return res

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

      return res.success(BooleanUnaryOpNode(operation, operand))

  def boolean_literal(self):
    res = ParseResult()
    token = self.current_token

    if token['type'] in (TokenType.WIN, TokenType.FAIL):
      self.advance() # Eat

      return res.success(BooleanNode(token))

    # Error
    return res.failure(InvalidSyntaxError(token, 'Expected boolean!'))

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def comparison_operation(self):
    res = ParseResult()
    # Grammar: <comparison> ::= BOTH SAEM <nestable_expr> AN <nestable_expr> | DIFFRINT <nestable_expr> AN <nestable_expr>
    # Grammar: <relational> ::= BOTH SAEM <nestable_expr> AN BIGGR OF <nestable_expr> AN <nestable_expr> | ...

    if self.current_token['type'] in (TokenType.BOTH_SAEM, TokenType.DIFFRINT):
      operation = self.current_token
      self.advance() # Eat BOTH SAEM or DIFFRINT

      # Parse the left operand (nestable_expr)
      left = res.register(self.nestable_expr())
      if res.error: return res

      # Check for 'AN' keyword
      if self.current_token['type'] != TokenType.AN:
          return res.failure(InvalidSyntaxError(self.current_token, "Expected 'AN' keyword!"))

      # Advance past the 'AN' keyword
      self.advance()

      # Parse the right operand
      # Check if there is BIGGR OF or SMALLR OF (relational operation)
      if self.current_token['type'] in (TokenType.BIGGR_OF, TokenType.SMALLR_OF):
        # This is a relational operation
        right = res.register(self.arithmetic_binary_operation())
        if res.error: return res
      else:
        # Regular comparison
        right = res.register(self.nestable_expr())
        if res.error: return res

      # Return an operation node with left and right operands
      return res.success(ComparisonOpNode(left, operation, right))

    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def print_statement(self):
    res = ParseResult()
    # Grammar: <output> ::= VISIBLE <print_args>
    # Grammar: <print_args> ::= <expression> | <expression> + <print_args>
    operands = []

    if self.current_token['type'] == TokenType.VISIBLE:
      self.advance() # Eat VISIBLE

      # Parse the first expression (required - VISIBLE cannot be empty)
      first_operand = res.register(self.expression())
      if res.error: return res

      # Check if expression returned None (empty VISIBLE statement)
      if first_operand is None:
        return res.failure(InvalidSyntaxError(self.current_token, "Empty VISIBLE Statement. To print a blank string use VISIBLE \"\""))

      operands.append(first_operand)

      # Continue while there's a + or AN separator
      while self.current_token['type'] in (TokenType.EXCLAMATION, TokenType.AN):
        self.advance() # Eat '+' or 'AN'

        additional_operand = res.register(self.expression())
        if res.error: return res
        operands.append(additional_operand)

      # Success
      return res.success(PrintNode(operands))

    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def typecast(self):
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
        if res.error: return res

        # Parse type literal (NOOB, TROOF, NUMBAR, NUMBR, YARN)
        if self.current_token['value'] in ("NUMBAR", "NUMBR", "YARN", "TROOF", "NOOB"):
          desired_type = self.current_token['value']
          self.advance() # Eat desired type
          return res.success(TypecastNode(source_value, desired_type))
        else:
          return res.failure(InvalidSyntaxError(self.current_token, "Expected a type literal (NOOB, TROOF, NUMBAR, NUMBR, YARN)!"))

      else:
        # MAEK <expr> A <type> syntax
        # Parse the nestable expression to typecast
        source_value = res.register(self.nestable_expr())
        if res.error: return res

        # Expect 'A' keyword
        if self.current_token['type'] != TokenType.A:
          return res.failure(InvalidSyntaxError(self.current_token, "Expected 'A' keyword after MAEK!"))

        self.advance() # Eat A

        # Parse type literal (NOOB, TROOF, NUMBAR, NUMBR, YARN)
        if self.current_token['value'] in ("NUMBAR", "NUMBR", "YARN", "TROOF", "NOOB"):
          desired_type = self.current_token['value']
          self.advance() # Eat desired type
          return res.success(TypecastNode(source_value, desired_type))
        else:
          return res.failure(InvalidSyntaxError(self.current_token, "Expected a type literal (NOOB, TROOF, NUMBAR, NUMBR, YARN)!"))

    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def assignment_statement(self):
    res = ParseResult()

    if self.current_token['type'] == TokenType.IDENTIFIER:
      var_to_access = self.current_token

      self.advance() # Eat Variable Identifier

      # Check for 'R' keyword
      if self.current_token['type'] not in (TokenType.R, TokenType.IS_NOW_A):
        # If there's no R or IS NOW A, then it might just be a variable access
        return res.success(VarAccessNode(var_to_access))


      # Else, continue
      if self.current_token['type'] == TokenType.R:
        self.advance() # Eat R

        value_to_assign = res.register(self.expression())

        # Check for errors
        if value_to_assign is None:
          return res.failure(InvalidSyntaxError(self.current_token, "Expected a value to assign!"))

        return res.success(VarAssignmentNode(var_to_access, value_to_assign))

      # Var assignment with TYPECASTING
      elif self.current_token['type'] == TokenType.IS_NOW_A:
        self.advance() # Eat IS NOW A

        if self.current_token['value'] not in ("NUMBAR", "NUMBR", "YARN", "TROOF"):
          return res.failure(InvalidSyntaxError(self.current_token, "Expected a type to cast the value!"))

        # Else, continue
        desired_type = self.current_token['value']

        self.advance() # Eat the desired type

        return res.success(VarAssignmentNode(var_to_access, TypecastNode(VarAccessNode(var_to_access), desired_type)))

    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def input_statement(self):
    res = ParseResult()

    if self.current_token['type'] == TokenType.GIMMEH:
      self.advance() # Eat Gimmeh

      # Error
      if self.current_token['type'] != TokenType.IDENTIFIER:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected a variable to store input!"))

      # Check if the variable name is valid
      variable_to_access = res.register(self.variable_literal())
      if variable_to_access is None: return res # Error

      # Proceed to the next step (getting user input and storing it in the variable stated)
      return res.success(InputNode(variable_to_access))

    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  # TODO: GTFO
  def break_statement(self):
    res = ParseResult()

    if self.current_token['type'] == TokenType.GTFO:
      break_token = self.current_token
      self.advance() # Eat GTFO

      return res.success(BreakNode(break_token))

    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def if_statement(self):
    res = ParseResult()
    # Grammar: <if_case> ::= <nestable_expr>, O RLY? <linebreak> <if_true> <if_false> OIC
    # Note: The nestable_expr should be parsed before calling this method
    # But for simplicity, we'll check if we're at O RLY

    if self.current_token['type'] == TokenType.O_RLY:
      # Optional: handle comma before O RLY (if it was parsed as separate token)
      self.advance() # Eat O RLY?

      # Parse if_true: YA RLY <linebreak> <statement_list> <linebreak>
      if self.current_token['type'] != TokenType.YA_RLY:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected 'YA RLY' keyword!"))

      self.advance() # Eat YA RLY

      # Parse statements for if_true block
      if_block_statements = []
      while self.current_token['type'] not in (TokenType.MEBBE, TokenType.NO_WAI, TokenType.OIC, TokenType.KTHXBYE):
        statement = res.register(self.statement())
        if res.error: return res
        if statement:
          if_block_statements.append(statement)

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
          statement = res.register(self.statement())
          if res.error: return res
          if statement:
            mebbe_statements.append(statement)

        mebbe_cases.append((mebbe_condition, mebbe_statements))

      # Handle NO WAI (else)
      if self.current_token['type'] == TokenType.NO_WAI:
        self.advance() # Eat NO WAI

        while self.current_token['type'] not in (TokenType.OIC, TokenType.KTHXBYE):
          statement = res.register(self.statement())
          if res.error: return res
          if statement:
            else_block_statements.append(statement)

      # Expect OIC
      if self.current_token['type'] != TokenType.OIC:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected 'OIC' keyword!"))

      self.advance() # Eat OIC

      # For now, convert MEBBE to nested if-else structure
      # Store mebbe_cases in a way the interpreter can handle
      return res.success(IfNode(if_block_statements, else_block_statements, mebbe_cases))

    return res



# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def switch_case_statement(self):
    res = ParseResult()
    cases = []
    cases_statements = []
    default_case_statements = []

    if self.current_token['type'] == TokenType.WTF:
      # Eat WTF
      self.advance()

      # Error
      if self.current_token['type'] != TokenType.OMG:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected an 'OMG' keyword!"))

      while self.current_token['type'] == TokenType.OMG:
        statements = []

        # Eat OMG
        self.advance()

        # Error
        if self.current_token['type'] not in (TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING, TokenType.WIN, TokenType.FAIL, TokenType.IDENTIFIER, TokenType.NOOB):
          return res.failure(InvalidSyntaxError(self.current_token, "Expected a literal for switch case!"))

        # Eat
        case_condition = res.register(self.literal())

        # Has error
        if case_condition is None:
          return res

        while self.current_token['type'] not in (TokenType.OMG, TokenType.OMGWTF, TokenType.OIC, TokenType.KTHXBYE):
          statement = res.register(self.statement())

          # Has error
          if statement is None:
            return res

          statements.append(statement)
        # Loop end

        cases.append(case_condition)
        cases_statements.append(statements)
      # Loop end

      if self.current_token['type'] != TokenType.OMGWTF:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected a default case for switch case!"))

      # Eat OMGWTF
      self.advance()

      # Add switch case
      while self.current_token['type'] not in (TokenType.OIC, TokenType.KTHXBYE):
        statement = res.register(self.statement())

        # Has error
        if statement is None:
          return res

        default_case_statements.append(statement)

      if self.current_token['type'] != TokenType.OIC:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected an 'OIC' keyword!"))

      # Eat OIC
      self.advance()

      return res.success(SwitchCaseNode(cases, cases_statements, default_case_statements))

    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def loop_statement(self):
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
        return res.failure(InvalidSyntaxError(self.current_token, "Expected a label for the loop!"))

      label = self.current_token['value']
      # Eat label
      self.advance()

      if self.current_token['type'] not in (TokenType.UPPIN, TokenType.NERFIN):
        return res.failure(InvalidSyntaxError(self.current_token, "Expected an operation for the loop condition!"))

      # Else, no error
      operation = self.current_token

      # Eat UPPIN or NERFIN
      self.advance()

      if self.current_token['type'] != TokenType.YR:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected a 'YR' keyword for the loop!"))

      # Else, no error
      # Eat YR
      self.advance()

      # Var
      if self.current_token['type'] != TokenType.IDENTIFIER:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected a variable for the loop!"))

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
        statement = res.register(self.statement())

        # Has error
        if statement is None:
          return res

        body_statements.append(statement)

      # Loop out
      if self.current_token['type'] != TokenType.IM_OUTTA_YR:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected an 'IM OUTTA YR' keyword!"))

      # Eat IM OUTTA YR
      self.advance()

      if self.current_token['type'] != TokenType.IDENTIFIER:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected a label to exit the loop!"))

      out_label = self.current_token['value']

      # Eat label
      self.advance()

      # print(label, out_label)
      if label != out_label:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected a similar label to exit the loop!"))


      return res.success(LoopNode(label, operation, variable, clause_type, til_wile_expression, body_statements))

    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def function_definition(self):
    res = ParseResult()
    function_name = None
    parameters = []
    body_statements = []

    if self.current_token['type'] == TokenType.HOW_IZ_I:
      # Eat HOW IZ I
      self.advance()

      # Identifier
      if self.current_token['type'] != TokenType.IDENTIFIER:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected a valid function name!"))

      function_name = self.current_token
      # Eat function name
      self.advance()

      # Check if there are parameters
      if self.current_token['type'] == TokenType.YR:
        # Eat YR
        self.advance()

        first_param = res.register(self.expression())
        if first_param is None: return res # Has error

        parameters.append(first_param)

        # Check for other params if there are any
        while self.current_token['type'] == TokenType.AN:
          # Eat AN
          self.advance()

          # Expect YR
          if self.current_token['type'] != TokenType.YR:
            return res.failure(InvalidSyntaxError(self.current_token, "Expected 'YR' after 'AN'!"))

          self.advance() # Eat YR

          additional_param = res.register(self.expression())
          if additional_param is None: return res # Has error

          parameters.append(additional_param)

      # function body
      while self.current_token['type'] not in (TokenType.FOUND_YR, TokenType.IF_U_SAY_SO, TokenType.KTHXBYE):
        statement = res.register(self.statement())
        if statement is None: return res # Has error

        body_statements.append(statement)

      if self.current_token['type'] == TokenType.FOUND_YR:
        # Eat FOUND YR
        self.advance()

        return_expression  = res.register(self.expression())
        if return_expression is None: return res # Has error

        body_statements.append(return_expression)

      if self.current_token['type'] != TokenType.IF_U_SAY_SO:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected an 'IF U SAY SO' keyword!"))

      # Eat IF U SAY SO
      self.advance()

      return res.success(FuncDefNode(function_name, parameters, body_statements))

    return res

# ═════════════════════════════════════════════════════════════════════════════════════════════════
  def function_call(self):
    res = ParseResult()
    function_name = None
    parameters = []

    if self.current_token['type'] == TokenType.I_IZ:
      # Eat I IZ
      self.advance()

      # Identifier
      if self.current_token['type'] != TokenType.IDENTIFIER:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected a valid function name!"))

      function_name = res.register(self.expression())
      if function_name is None: return res

      # Check if there are parameters
      if self.current_token['type'] == TokenType.YR:
        # Eat YR
        self.advance()

        first_param = res.register(self.expression())
        if first_param is None: return res # Has error

        parameters.append(first_param)

        # Check for other params if there are any
        while self.current_token['type'] == TokenType.AN:
          # Eat AN
          self.advance()

          # Expect YR
          if self.current_token['type'] != TokenType.YR:
            return res.failure(InvalidSyntaxError(self.current_token, "Expected 'YR' after 'AN'!"))

          self.advance() # Eat YR

          additional_param = res.register(self.expression())
          if additional_param is None: return res # Has error

          parameters.append(additional_param)

      # function body
      if self.current_token['type'] != TokenType.MKAY:
        return res.failure(InvalidSyntaxError(self.current_token, "Expected an 'MKAY' keyword!"))

      # Eat MKAY
      self.advance()

      return res.success(FuncCallNode(function_name, parameters))

    return res