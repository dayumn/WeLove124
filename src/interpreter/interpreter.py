from src.lexer.tokenizer import TokenType
from src.parser import *
from .runtime import *
from .values import *

# ═════════════════════════════════════════════════════════════════════════════════════════════════
# INTERPRETER
# ═════════════════════════════════════════════════════════════════════════════════════════════════
class Interpreter:
  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit(self, node, context):
    method_name = f'visit_{type(node).__name__}'
    method = getattr(self, method_name, self.no_visit_method)
    return method(node, context)
  
  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def no_visit_method(self, node, context):
    raise Exception(f'No visit_{type(node).__name__} method defined')
  
  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_IntegerNode(self, node, context):
    # print("Found integer node")
    return RTResult().success(
      Number(int(node.token['value']), node.token['line'])
    )
  
  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_FloatNode(self, node, context):
    # print("Found float node")
    return RTResult().success(
      Number(float(node.token['value']), node.token['line'])
    )
  
  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_BooleanNode(self, node, context):
    # print("Found boolean node")
    return RTResult().success(
      Boolean(node.token['value'], node.token['line'])
    )
  
  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_StringNode(self, node, context):
    # print("Found string node")
    # Quotes are already stripped by the tokenizer
    return RTResult().success(
      String(node.token['value'], node.token['line'])
    )
  
  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_NoobNode(self, node, context):
    return RTResult().success(
      Noob(node.line_number)
    )    
  
  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_ArithmeticBinaryOpNode(self, node, context):
    # print("Found ar bin op node")
    res = RTResult()
    left = res.register(self.visit(node.left_node, context))
    if res.error: return res
    right = res.register(self.visit(node.right_node, context))
    if res.error: return res

    if node.operation['type'] == TokenType.SUM_OF:
      result, error = left.added_by(right)

    elif node.operation['type'] == TokenType.DIFF_OF:
      result, error = left.subtracted_by(right)
    
    elif node.operation['type'] == TokenType.PRODUKT_OF:
      result, error = left.multiplied_by(right) 

    elif node.operation['type'] == TokenType.QUOSHUNT_OF:
      result, error = left.divided_by(right)

    elif node.operation['type'] == TokenType.MOD_OF:
      result, error = left.modulo(right)
    
    elif node.operation['type'] == TokenType.BIGGR_OF:
      result, error = left.maximum(right)
    
    elif node.operation['type'] == TokenType.SMALLR_OF:
      result, error = left.minimum(right)

    if (error):
      return res.failure(error)
    else:
      # context.symbol_table.set('IT', result)
      return res.success(result)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_BooleanBinaryOpNode(self, node, context):
    # print("Found bool bin op node")
    res = RTResult()
    left = res.register(self.visit(node.left_node, context))
    if res.error: return res
    right = res.register(self.visit(node.right_node, context))
    if res.error: return res

    if node.operation['type'] == TokenType.BOTH_OF:
      result, error = left.and_logic(right)

    elif node.operation['type'] == TokenType.EITHER_OF:
      result, error = left.or_logic(right)
    
    elif node.operation['type'] == TokenType.WON_OF:
      result, error = left.xor_logic(right) 

    if (error): return res.failure(error)
    else: return res.success(result)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_BooleanUnaryOpNode(self, node, context):
    res = RTResult()
    operand_ = res.register(self.visit(node.operand, context))
    if res.error: return res

    if (node.operation['type'] == TokenType.NOT):
      result, error = operand_.not_logic()

    if (error): return res.failure(error)
    else: return res.success(result)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_BooleanTernaryOpNode(self, node, context):
    res = RTResult()
    value = None
    boolean_results = []
    for boolean_statement in node.boolean_statements:
      boolean_result = res.register(self.visit(boolean_statement, context))
      if res.error: return res
      boolean_results.append(boolean_result)
    
    # Since the boolean values in the list are still expressed in the lolcode boolean system, we need to convert each of them first to its true boolean value so we can perform the desired operation on the entire list
    boolean_results = [boolean.value for boolean in boolean_results]

    if node.operation['type'] == TokenType.ALL_OF:
      value = Boolean(all(boolean_results))
    elif node.operation['type'] == TokenType.ANY_OF:
      value = Boolean(any(boolean_results))

    return res.success(value)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_ComparisonOpNode(self, node, context):
    # print("Found comparison op node")
    res = RTResult()
    left = res.register(self.visit(node.left_node, context))
    if res.error: return res
    right = res.register(self.visit(node.right_node, context))
    if res.error: return res

    if node.operation['type'] == TokenType.BOTH_SAEM:
      result, error = left.is_equal(right)

    elif node.operation['type'] == TokenType.DIFFRINT:
      result, error = left.is_not_equal(right)

    if (error): return res.failure(error)
    else: return res.success(result)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_StringConcatNode(self, node, context):
    res = RTResult()
    string_value = ""

    for operand in node.operands:
      operand_value = res.register(self.visit(operand, context))
      if res.error: return res

      # Perform typecasting
      # Old
      # operand_value, error = operand_value.typecast(String)
      # if error:
      #   res.error = error
      #   return res

      string_value += str(operand_value.value)
    
    return res.success(string_value)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_VarAccessNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_token['value']

    if not context.symbol_table.found(var_name):
      return res.failure(RuntimeError(node.var_name_token, f"'{var_name} is not defined!'"))
    
    value = context.symbol_table.get(var_name)
    return res.success(value)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_VarDeclarationNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_token['value']

    # If no value is provided, initialize with NOOB
    if node.value_node is None: 
      value = Noob()
      context.symbol_table.set(var_name, value)
      return res.success(value)

    value = res.register(self.visit(node.value_node, context))
    if res.error: return res

    context.symbol_table.set(var_name, value)
    return res.success(value)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_VarAssignmentNode(self, node, context):
    res = RTResult()
    
    var_to_access = node.var_to_access
    value_to_assign = res.register(self.visit(node.value_to_assign, context))

    if not context.symbol_table.found(var_to_access['value']):
      return res.failure(RuntimeError(var_to_access, f"'{var_to_access['value']} is not defined!'"))

    context.symbol_table.set(var_to_access['value'], value_to_assign)
    return res.success(value_to_assign)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_StatementListNode(self, node, context):
    res = RTResult()
    for statement in node.statements:
      implicit_value = res.register(self.visit(statement, context))
      if res.error: return res
      context.symbol_table.set('IT', implicit_value)  # update the IT variable
    return res.success(None)
  
  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_VarDecListNode(self, node, context):
    res = RTResult()
    for variable_declaration in node.variable_declarations:
        variable = res.register(self.visit(variable_declaration, context))
        if res.error: return res
    return res.success(None)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_PrintNode(self, node, context):
    res = RTResult()
    print_value = ""

    for operand in node.operands:
      operand_value = res.register(self.visit(operand, context))
      if res.error: return res
      print_value += str(operand_value)
    
    print(print_value)

    return res.success(print_value)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_TypecastNode(self, node, context):
    res = RTResult()

    source_value = res.register(self.visit(node.source_value, context))
    if res.error: return res

    desired_type = node.desired_type

    if desired_type == "NUMBR":       # Int
      converted_value, error = source_value.explicit_typecast(Number)
    elif desired_type == "NUMBAR":    # Float
      converted_value, error = source_value.explicit_typecast(Number, True)
    elif desired_type == "TROOF":    # Float
      converted_value, error = source_value.explicit_typecast(Boolean)  
    elif desired_type == "YARN":    # Float
      converted_value, error = source_value.explicit_typecast(Boolean)  

    if error: return res.failure(error)

    return res.success(converted_value)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_SwitchCaseNode(self, node, context):
    res = RTResult()
    is_there_a_true_case = False
    basis = context.symbol_table.get('IT')

    for i in range(len(node.cases)):
      case_value = res.register(self.visit(node.cases[i], context))
      if res.error: return res

      condition, error = basis.is_equal(case_value)
      if error: return res.failure(error)
      
      # print(condition, condition.value==True)

      if (condition.value):
        for statement in node.cases_statements[i]:
          statement_value = res.register(self.visit(statement, context))
          if res.error: return res

          if isinstance(statement_value, Break):
            is_there_a_true_case = True
            break

        # loop end
        is_there_a_true_case = True
        break
    
    if is_there_a_true_case == False:
      for statement in node.default_case_statements:
        statement_value = res.register(self.visit(statement, context))
        if res.error: return res

    return res.success(basis)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_IfNode(self, node, context):
    res = RTResult()
    basis = context.symbol_table.get('IT')

    basis_value, error = basis.typecast(Boolean)
    if error: return res.failure(error)

    if (basis_value.value):
      for statement in node.if_block_statements:
        statement_value = res.register(self.visit(statement, context))
        if res.error: return res
    else:
      for statement in node.else_block_statements:
        statement_value = res.register(self.visit(statement, context))
        if res.error: return res

    return res.success(basis)
  
  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_LoopNode(self, node, context):
    res = RTResult()

    label = node.label
    operation = node.operation
    variable = node.variable
    clause_type = node.clause_type
    til_wile_expression = node.til_wile_expression
    body_statements = node.body_statements
    
    # Get the variable name from the token
    var_name = variable['value']

    # Proceed to the loop
    is_running = True
    while is_running:
      # Check termination condition BEFORE executing the body
      if (clause_type and til_wile_expression != None):
        termination_condition = res.register(self.visit(til_wile_expression, context))
        if res.error: return res
        
        # Convert termination_condition to boolean if needed
        termination_condition_bool, error = termination_condition.typecast(Boolean)
        if error: return res.failure(error)

        # Distinguish TIL with WILE
        # The TIL <expression> clause will repeat the loop as long as <expression> is FAIL.
        if (
            clause_type == TokenType.TIL and
            termination_condition_bool.value == True
        ):
          break
        
        # The WILE <expression> clause will repeat the loop as long as <expression> returns WIN.
        if (
            clause_type == TokenType.WILE and
            termination_condition_bool.value == False
        ):
          break

      # Execute loop body
      for statement in body_statements:
        statement_value = res.register(self.visit(statement, context))
        if res.error: return res

        if isinstance(statement_value, Break):
          is_running = False
          break
      
      # If break was encountered, exit the loop
      if not is_running:
        break
      
      # Incrementor/Decrementor - directly update the value in the symbol table
      iterator = context.symbol_table.get(var_name)
      if iterator is None:
        return res.failure(RuntimeError(variable, f"Variable '{var_name}' is not defined"))
      
      # Typecast to Number if needed
      iterator, error = iterator.typecast(Number)
      if error: return res.failure(error)
      
      # Update the value based on operation
      if operation['type'] == TokenType.UPPIN:
        new_value = Number(iterator.value + 1)
      else:  # NERFIN
        new_value = Number(iterator.value - 1)
      
      # Set the new value in the symbol table
      context.symbol_table.set(var_name, new_value)

    return res.success(label)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_FuncDefNode(self, node, context):
    res = RTResult()
    return_value = None

    function_name = node.function_name['value']
    params = []

    # if there's any
    for param in node.parameters:
      param_name = param.var_name_token['value']
      params.append(param_name)

    body_statements = node.body_statements
    
    function_value = Function(function_name, params, body_statements).set_context(context)
    
    context.symbol_table.set(function_name, function_value)
    return res.success(function_value)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_FuncCallNode(self, node, context):
    res = RTResult()
    return_value = Noob()
    parameters_to_pass = []

    function_name = node.function_name
    parameters = node.parameters

    function_to_call = res.register(self.visit(function_name, context))
    if res.error: return res

    for param in parameters:
      par = res.register(self.visit(param, context))
      if res.error: return res

      parameters_to_pass.append(par)

    return_value = function_to_call.execute(parameters_to_pass)
    return res.success(return_value.value)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_InputNode(self, node, context):
    res = RTResult()
    variable = node.variable

    # Check if the variable is defined in the symbol table
    if context.symbol_table.found(variable.var_name_token['value']):
      # Get user input directly using input() function
      user_input_value = str(input())

      # Create a proper token dict for StringNode
      user_input_token = {
        'type': TokenType.STRING,
        'value': user_input_value,
        'line': variable.var_name_token['line'],
        'col': 0
      }
      user_input = StringNode(user_input_token)

      # Assign the user input to the variable in the symbol table
      value = res.register(self.visit(VarAssignmentNode(variable.var_name_token, user_input), context))
    else:
      # If the variable is not defined, return an error
      return res.failure(RuntimeError(
        ('Var Access Error', None, variable.var_name_token['line']), f"Can't find a variable named '{variable.var_name_token['value']}'"
      ))

    return res.success(value)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_BreakNode(self, node, context):
    res = RTResult()
    break_token = node.break_token
    return_value = Break(break_token['value']).set_context(context)
    return res.success(return_value)

  # ───────────────────────────────────────────────────────────────────────────────────────────────
  def visit_ProgramNode(self, node, context):
    res = RTResult()
    for section in node.sections:
        section_ = res.register(self.visit(section, context))
        if res.error: return res
    return res.success(None)