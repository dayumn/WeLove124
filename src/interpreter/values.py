import re
from .runtime import *
from src.parser.parser import *

class Value:
  def __init__(self, line_number=None):
    self.line_number = line_number
    self.set_context()

  def set_context(self, context=None):
    self.context = context
    return self

  # Typecasting method (to be implemented in subclasses)
  def typecast(self, target_class):
    raise NotImplementedError("Subclasses must implement this method")

  # Explicit Typecasting method (to be implemented in subclasses)
  def explicit_typecast(self, target_class, to_float=False): # To float is for typecasting Flot->Int or Int->FLoat
    raise NotImplementedError("Subclasses must implement this method")

  # ════════════════════════════════════════════════════════════════════════════════════════════════
  # Number Arithmetic operations (ensure result is always a Number)
  def added_by(self, other):
    # Typecast both operands to Number before performing the addition
    self, error = self.typecast(Number) 
    if error: return None, error

    other, error = other.typecast(Number)
    if error: return None, error

    result = self.value + other.value

    return Number(result).set_context(self.context), None

  def subtracted_by(self, other):
    # Typecast both operands to Number before performing the subtraction
    self, error = self.typecast(Number) 
    if error: return None, error

    other, error = other.typecast(Number)
    if error: return None, error

    result = self.value - other.value

    return Number(result).set_context(self.context), None

  def multiplied_by(self, other):
    # Typecast both operands to Number before performing the multiplication
    self, error = self.typecast(Number) 
    if error: return None, error

    other, error = other.typecast(Number)
    if error: return None, error

    result = self.value * other.value

    return Number(result).set_context(self.context), None

  def divided_by(self, other):
    # Typecast both operands to Number before performing the division
    self, error = self.typecast(Number) 
    if error: return None, error

    other, error = other.typecast(Number)
    if error: return None, error

    if other.value == 0:
      return None, RuntimeError(
        ('Division Error', None, other.line_number), 
        'Cannot divide by zero.\nThe divisor must be a non-zero number.'
      )
    
    result = self.value / other.value

    return Number(result).set_context(self.context), None
  
  def modulo(self, other):
    # Typecast both operands to Number before performing the modulo
    self, error = self.typecast(Number) 
    if error: return None, error

    other, error = other.typecast(Number)
    if error: return None, error

    result = self.value % other.value

    return Number(result).set_context(self.context), None

  def maximum(self, other):
    # Typecast both operands to Number before performing the division
    self, error = self.typecast(Number)
    if error: return None, error

    other, error = other.typecast(Number)
    if error: return None, error

    result = max(self.value, other.value)

    return Number(result).set_context(self.context) , None

  def minimum(self, other):
    # Typecast both operands to Number before performing the division
    self, error = self.typecast(Number)
    if error: return None, error

    other, error = other.typecast(Number)
    if error: return None, error

    result = min(self.value, other.value)

    return Number(result).set_context(self.context) , None
  
  
  # Boolean Logical Operations
  def and_logic(self, other):
    # Typecast both operands to Boolean before performing the and operation
    self, error = self.typecast(Boolean)
    if error: return None, error

    other, error = other.typecast(Boolean)
    if error: return None, error

    result = self.value and other.value

    return Boolean(result).set_context(self.context) , None

  def or_logic(self, other):
    # Typecast both operands to Boolean before performing the or operation
    self, error = self.typecast(Boolean)
    if error: return None, error

    other, error = other.typecast(Boolean)
    if error: return None, error

    result = self.value or other.value    

    return Boolean(result).set_context(self.context) , None

  def xor_logic(self, other):
    # Typecast both operands to Boolean before performing the xor operation
    self, error = self.typecast(Boolean) 
    if error: return None, error

    other, error = other.typecast(Boolean)
    if error: return None, error

    result = (self.value or other.value) and not (self.value and other.value) 

    return Boolean(result).set_context(self.context) , None

  def not_logic(self):
    # Typecast the operand to Boolean before performing the not operation
    self, error = self.typecast(Boolean) 
    if error: return None, error

    result = not self.value  

    return Boolean(result).set_context(self.context) , None

  
  # Comparison
  def is_equal(self, other, operation_token=None):
    # Only numeric comparisons are allowed
    if self.__class__ == Number and other.__class__ == Number:
      # Both are numeric types, compare values directly
      result = self.value == other.value
      return Boolean(result).set_context(self.context), None
    
    # Non-numeric types cannot be compared
    # Use operation token's line number if available, otherwise fall back to self.line_number
    return None, RuntimeError(
      ('Comparison Error', None, operation_token['line'] if operation_token else self.line_number, operation_token),
      f"Cannot compare non-numeric types. Only NUMBR and NUMBAR can be compared.\nConvert {self.__class__.__name__} and {other.__class__.__name__} to numbers first using explicit typecasting."
    )

  def is_not_equal(self, other, operation_token=None):
    # Only numeric comparisons are allowed
    if self.__class__ == Number and other.__class__ == Number:
      # Both are numeric types, compare values directly
      result = self.value != other.value
      return Boolean(result).set_context(self.context), None
    
    # Non-numeric types cannot be compared
    # Use operation token's line number if available, otherwise fall back to self.line_number
    return None, RuntimeError(
      ('Comparison Error', None, operation_token['line'] if operation_token else self.line_number, operation_token),
      f"Cannot compare non-numeric types. Only NUMBR and NUMBAR can be compared.\nConvert {self.__class__.__name__} and {other.__class__.__name__} to numbers first using explicit typecasting."
    )

  def __repr__(self):
    return str(self.value)  


class Break(Value):
  def __init__(self, value, line_number=None):
    self.value = value
    self.line_number = line_number
    self.set_context()
    super().__init__(line_number)

  def set_context(self, context=None):
    self.context = context
    return self

  # Typecasting method (to be implemented in subclasses)
  def typecast(self, target_class): pass

  # Explicit Typecasting method (to be implemented in subclasses)
  def explicit_typecast(self, target_class, to_float=False): pass


class Return(Value):
  def __init__(self, value, line_number=None):
    self.value = value
    self.line_number = line_number
    self.set_context()
    super().__init__(line_number)

  def set_context(self, context=None):
    self.context = context
    return self

  # Typecasting method (to be implemented in subclasses)
  def typecast(self, target_class): pass

  # Explicit Typecasting method (to be implemented in subclasses)
  def explicit_typecast(self, target_class, to_float=False): pass


class Noob(Value):
  def __init__(self, line_number=None):
    self.value = None
    self.line_number = line_number
    super().__init__(line_number)

  def typecast(self, target_class):
    # NOOBs can be implicitly typecast into TROOF
    if target_class == self.__class__:
      return self , None

    elif target_class == Boolean:
      return Boolean(False).set_context(self.context) , None
    
    # Implicit typecasting to any other type except TROOF will result in an error
    return None, RuntimeError(
        ('Typecast Error', None, self.line_number), 
        f"Cannot implicitly convert {self.__class__.__name__} ({self.value}) to {target_class.__name__}.\nUse explicit typecasting with MAEK or IS NOW A."
      )

  # Explicit typecasting of NOOBs is allowed and results to empty/zero values depending on the type.
  def explicit_typecast(self, target_class, to_float=False):
    # No need to typecast for Noob-to-Noob
    if target_class == self.__class__:
      return self , None

    elif target_class == Boolean:
      return Boolean(False).set_context(self.context) , None
    
    elif target_class == String:
      return String("").set_context(self.context) , None

    elif target_class == Number:
      if to_float:
        return Number(0.0).set_context(self.context) , None
      else:
        return Number(0).set_context(self.context) , None

    # Error
    return None, RuntimeError(
        ('Typecast Error', None, self.line_number), 
        f"Cannot convert {self.__class__.__name__} to {target_class.__name__}.\nThis type conversion is not supported."
      )

  def __repr__(self):
    return str('NOOB')   


class String(Value):
  def __init__(self, value, line_number=None):
    self.value = value
    self.line_number = line_number
    super().__init__(line_number)

  def typecast(self, target_class):
    # No need to typecast for String-to-String
    if target_class == self.__class__:
      return self , None

    # The empty string ("") is cast to FAIL, all other values are cast to WIN
    elif target_class == Boolean:
      return Boolean(self.value != "").set_context(self.context) , None
    
    # A YARN can be successfully cast into a NUMBAR or NUMBR if the YARN does not contain 
    # any non-numerical, non-hyphen, non-period characters
    elif target_class == Number:
      # Check if string contains only valid numeric characters: digits, hyphen (at start), and period
      if re.match(r'^-?\d+$', self.value):  # Integer format
        return Number(int(self.value)).set_context(self.context) , None
      elif re.match(r'^-?\d*\.\d+$', self.value):  # Float format
        return Number(float(self.value)).set_context(self.context) , None
      else:
        # String contains non-numeric characters
        return None, RuntimeError(
            ('Typecast Error', None, self.line_number), 
            f"Cannot convert String '{self.value}' to {target_class.__name__}.\nThe string contains non-numerical characters."
          )

    # Error
    return None, RuntimeError(
        ('Typecast Error', None, self.line_number), 
        f"Cannot implicitly convert String '{self.value}' to {target_class.__name__}.\nThe string format is incompatible with the target type."
      )

  # No change with implicit typecasting
  def explicit_typecast(self, target_class, to_float=False):
    return self.typecast(target_class)

  # Override maximum for string comparison (lexicographic or numeric if possible)
  def maximum(self, other):
    # Try to convert both to numbers first
    self_num, err1 = self.typecast(Number)
    other_num, err2 = other.typecast(Number)
    
    if err1 is None and err2 is None:
      # Both can be converted to numbers, use numeric comparison
      result = max(self_num.value, other_num.value)
      return Number(result).set_context(self.context), None
    
    # If can't convert to numbers, use lexicographic comparison
    other_str, error = other.typecast(String)
    if error: return None, error
    
    result = max(self.value, other_str.value)
    return String(result).set_context(self.context), None

  # Override minimum for string comparison (lexicographic or numeric if possible)
  def minimum(self, other):
    # Try to convert both to numbers first
    self_num, err1 = self.typecast(Number)
    other_num, err2 = other.typecast(Number)
    
    if err1 is None and err2 is None:
      # Both can be converted to numbers, use numeric comparison
      result = min(self_num.value, other_num.value)
      return Number(result).set_context(self.context), None
    
    # If can't convert to numbers, use lexicographic comparison
    other_str, error = other.typecast(String)
    if error: return None, error
    
    result = min(self.value, other_str.value)
    return String(result).set_context(self.context), None

  def __repr__(self):
    return str(self.value) 


class Number(Value):
  def __init__(self, value, line_number=None):
    self.value = value
    self.line_number = line_number
    super().__init__(line_number)

  def typecast(self, target_class):
    # No need to typecast for Number-to-Number
    if target_class == self.__class__:
      return self , None

    # Numerical zero values are cast to FAIL, all other values are cast to WIN
    elif target_class == Boolean:
      return Boolean(self.value != 0 and self.value != 0.0).set_context(self.context) , None
    
    elif target_class == String:
      if Number.is_integer(self.value):
        # Casting NUMBRs to YARN will just convert the value into a string of characters
        return String(str(int(self.value))).set_context(self.context) , None
      elif Number.is_float(self.value):
        # Casting NUMBARs to YARN will truncate the decimal portion up to two decimal places
        return String(f"{self.value:.2f}").set_context(self.context) , None
    
    # Error
    return None, RuntimeError(
        ('Typecast Error', None, self.line_number), 
        f"Cannot implicitly convert Number ({self.value}) to {target_class.__name__}.\nThis type conversion is not supported."
      )
  
  def explicit_typecast(self, target_class, to_float=False):
    # Casting NUMBARs to NUMBR will truncate the decimal portion of the NUMBAR.
    # Casting NUMBRs to NUMBAR will just convert the value into a floating point. The value should be retained.
    if target_class == self.__class__:
      if Number.is_integer(self.value) and to_float == False:
        return self , None # No need to change anything if Int already
      
      # Casting NUMBRs to NUMBAR (Integer -> Float)
      elif Number.is_integer(self.value) and to_float == True:
        return Number(float(self.value)).set_context(self.context) , None
      
      # Casting NUMBARs to NUMBR (Float -> Integer) - truncate decimal portion
      elif Number.is_float(self.value) and to_float == False:
        return Number(int(self.value)).set_context(self.context) , None
      
      # Float to Float - no change
      elif Number.is_float(self.value) and to_float == True:
        return self , None

    # Numerical zero values are cast to FAIL, all other values are cast to WIN
    elif target_class == Boolean:
      return Boolean(self.value != 0 and self.value != 0.0).set_context(self.context) , None
    
    elif target_class == String:
      if Number.is_integer(self.value):
        # Casting NUMBRs to YARN will just convert the value into a string of characters
        return String(str(int(self.value))).set_context(self.context) , None
      elif Number.is_float(self.value):
        # Casting NUMBARs to YARN will truncate the decimal portion up to two decimal places
        return String(f"{self.value:.2f}").set_context(self.context) , None
    
    # Error
    return None, RuntimeError(
        ('Typecast Error', None, self.line_number), 
        f"Cannot convert Number ({self.value}) to {target_class.__name__}.\nThis type conversion is not supported."
      )

  def is_integer(value_to_check):
    return bool(re.match(r'^-?\d+$', str(value_to_check)))  

  def is_float(value_to_check):
    return bool(re.match(r'^-?\d*\.\d*$', str(value_to_check)))

  #Implement Implicit Typecase here
  def __repr__(self):
    return str(self.value)


class Boolean(Value):
  def __init__(self, value_representation, line_number=None):
    self.line_number = line_number
    self.value = None
    
    if value_representation == 'WIN':
      self.value = True
    elif value_representation == 'FAIL':
      self.value = False
    else:
      # TYPECAST if needed
      self.value = bool(value_representation)

    super().__init__(line_number)

  def typecast(self, target_class):
    # No need to typecast for Boolean-to-Boolean
    if target_class == self.__class__:
      return self , None

    # Casting WIN to a numerical type results in 1, Casting FAIL results in a numerical zero
    elif target_class == Number:
      return Number(1 if self.value else 0).set_context(self.context) , None

    elif target_class == String:
      return String(self.get_value_representation()).set_context(self.context), None

    # Error
    return None, RuntimeError(
        ('Typecast Error', None, self.line_number), 
        f"Cannot implicitly convert Boolean ({self.get_value_representation()}) to {target_class.__name__}.\nThis type conversion is not supported."
      )

  # Casting WIN to a numerical type results in 1 or 1.0. Casting FAIL results in a numerical zero.
  def explicit_typecast(self, target_class, to_float=False):
    # No need to typecast for Boolean-to-Boolean
    if target_class == self.__class__:
      return self , None

    elif target_class == Number:
      if to_float:
        return Number(1.0 if self.value else 0.0).set_context(self.context) , None
      else:
        return Number(1 if self.value else 0).set_context(self.context) , None

    elif target_class == String:
      return String(self.get_value_representation()).set_context(self.context), None

    # Error
    return None, RuntimeError(
        ('Typecast Error', None, self.line_number), 
        f"Cannot convert Boolean ({self.get_value_representation()}) to {target_class.__name__}.\nThis type conversion is not supported."
      ) 
  
  def get_value_representation(self):
    return 'WIN' if self.value else 'FAIL'

  def __repr__(self):
    return str(self.get_value_representation())


class Function(Value):
  def __init__(self, function_name, parameters, body_statements):
    self.function_name = function_name
    self.parameters = parameters
    self.body_statements = body_statements
    super().__init__()

  def execute(self, passed_parameters):
    from src.interpreter.interpreter import Interpreter

    res = RTResult()
    interpreter = Interpreter()
    new_context = Context(self.function_name, parent=self.context)
    new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

    if len(passed_parameters) > len(self.parameters):
      return res.failure(RuntimeError(
        ("Function Call", "Function", None),
        f"Too many arguments for function '{self.function_name}'.\nExpected {len(self.parameters)} parameter(s), but got {len(passed_parameters)}.\nExtra arguments: {len(passed_parameters) - len(self.parameters)}"
      ))
    
    if len(passed_parameters) < len(self.parameters):
      return res.failure(RuntimeError(
        ("Function Call", "Function", None),
        f"Not enough arguments for function '{self.function_name}'.\nExpected {len(self.parameters)} parameter(s), but got {len(passed_parameters)}.\nMissing arguments: {len(self.parameters) - len(passed_parameters)}"
      ))
    
    for i in range(len(passed_parameters)):
      param_name = self.parameters[i]
      param_value = passed_parameters[i]

      param_value.set_context(new_context)
      new_context.symbol_table.set(param_name, param_value)
      
    return_value = Noob()  # Default return value
    
    for statement in self.body_statements:
      value = res.register(interpreter.visit(statement, new_context))
      if res.error: return res

      # Check for early return (FOUND YR)
      if isinstance(value, Return):
        return res.success(value.value)
      
      # Check for GTFO (break) - in a function, acts like return with NOOB
      if isinstance(value, Break):
        return res.success(Noob())
      
      # Update return_value to the last expression result (ignoring None)
      if value is not None and not isinstance(value, (Break, Return)):
        return_value = value

    return res.success(return_value)

#   def typecast(self, target_class): return True
#   def explicit_typecast(self, target_class, to_float=False): return True

  def __repr__(self):
    return f"<function {self.function_name}>"
  