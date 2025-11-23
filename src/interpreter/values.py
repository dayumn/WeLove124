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
        ('Result is Zero', None, other.line_number), 'Division by Zero'
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
  def is_equal(self, other):
    # If both are same type, compare directly
    if self.__class__ == other.__class__:
      result = self.value == other.value
      return Boolean(result).set_context(self.context), None
    
    # Try to typecast the second operand to the data type of the first operand
    other_converted, error = other.typecast(self.__class__)
    if error:
      # If typecast fails, they're not equal
      return Boolean(False).set_context(self.context), None

    result = self.value == other_converted.value
    return Boolean(result).set_context(self.context), None

  def is_not_equal(self, other):
    # If both are same type, compare directly
    if self.__class__ == other.__class__:
      result = self.value != other.value
      return Boolean(result).set_context(self.context), None
    
    # Try to typecast the second operand to the data type of the first operand
    other_converted, error = other.typecast(self.__class__)
    if error:
      # If typecast fails, they're not equal
      return Boolean(True).set_context(self.context), None

    result = self.value != other_converted.value
    return Boolean(result).set_context(self.context), None

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
    # No need to typecast for Noob-to-Noob
    if target_class == self.__class__:
      return self , None

    elif target_class == Boolean:
      return Boolean(self.value).set_context(self.context) , None
    
    # Error
    return None, RuntimeError(
        ('Typecast error', None, self.line_number), f"Can't Typecast {self.__class__.__name__}: {self.value}  to {target_class.__name__}"
      )

  # Explicit typecasting of NOOBs is allowed and results to empty/zero values depending on the type.
  def explicit_typecast(self, target_class, to_float=False):
    # No need to typecast for Noob-to-Noob
    if target_class == self.__class__:
      return self , None

    elif target_class == Boolean:
      return Boolean(self.value).set_context(self.context) , None
    
    elif target_class == String:
      return String("").set_context(self.context) , None

    elif target_class == Number:
      return Number(0).set_context(self.context) , None

    # Error
    return None, RuntimeError(
        ('Typecast error', None, self.line_number), f"Can't Typecast {self.__class__.__name__}: {self.value}  to {target_class.__name__}"
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

    elif target_class == Boolean:
      return Boolean(self.value).set_context(self.context) , None
    
    elif target_class == Number:
      if Number.is_integer(self.value):
        return Number(int(self.value)).set_context(self.context) , None
      elif Number.is_float(self.value):
        # Truncate up to 2 decimal places
        return Number(float(self.value)).set_context(self.context) , None
      # else:
      #   # 0 if empty, 1 if not (delete this, was not mentioned in project specs)
      #   return Number(int(bool(self.value))).set_context(self.context) , None

    # Error
    return None, RuntimeError(
        ('Typecast error', None, self.line_number), f"Can't Typecast {self.__class__.__name__}: {self.value}  to {target_class.__name__}"
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

    elif target_class == Boolean:
      return Boolean(self.value != 0).set_context(self.context) , None
    
    elif target_class == String:
      if Number.is_integer(self.value):
        return String(str(self.value)).set_context(self.context) , None
      elif Number.is_float(self.value):
        return String(str(int(self.value * 100) / 100)).set_context(self.context) , None  # if Float, Truncate up to two decimal places
    
    # Error
    return None, RuntimeError(
        ('Typecast error', None, self.line_number), f"Can't Typecast {self.__class__.__name__}: {self.value}  to {target_class.__name__}"
      )
  
  def explicit_typecast(self, target_class, to_float=False):
    # Casting NUMBARs to NUMBR will truncate the decimal portion of the NUMBAR.
    # Casting NUMBRs to NUMBAR will just convert the value into a floating point.The value should be retained.
    if target_class == self.__class__:
      if Number.is_integer(self.value) and to_float == False:
        return self , None # No need to change anything if Int already
      
      # Integer -> Float
      elif Number.is_integer(self.value) and to_float == True:
        return Number(float(self.value)).set_context(self.context) , None
      
      # Float -> Integer
      elif Number.is_float(self.value) and to_float == True:
        return Number(int(self.value)).set_context(self.context) , None

    elif target_class == Boolean:
      return Boolean(self.value != 0).set_context(self.context) , None
    
    elif target_class == String:
      if Number.is_integer(self.value):
        return String(str(self.value)).set_context(self.context) , None
      elif Number.is_float(self.value):
        return String(str(int(self.value * 100) / 100)).set_context(self.context) , None  # if Float, Truncate up to two decimal places
    
    # Error
    return None, RuntimeError(
        ('Typecast error', None, self.line_number), f"Can't Typecast {self.__class__.__name__}: {self.value}  to {target_class.__name__}"
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

    elif target_class == Number:
      return Number(1 if self.value else 0).set_context(self.context) , None

    elif target_class == String:
      return String(self.get_value_representation()), None

    # Error
    return None, RuntimeError(
        ('Typecast error', None, self.line_number), f"Can't Typecast {self.__class__.__name__}: {self.value}  to {target_class.__name__}"
      )

  # Casting WIN to a numerical type results in 1 or 1.0.
  def explicit_typecast(self, target_class, to_float=False):
    # No need to typecast for Boolean-to-Boolean
    if target_class == self.__class__:
      return self , None

    elif target_class == Number:
      if to_float == False:
        return Number(1 if self.value else 0).set_context(self.context) , None
      else:
        return Number(1.0 if self.value else 0).set_context(self.context) , None

    elif target_class == String:
      return String(self.get_value_representation()), None

    # Error
    return None, RuntimeError(
        ('Typecast error', None, self.line_number), f"Can't Typecast {self.__class__.__name__}: {self.value}  to {target_class.__name__}"
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
        ("Function", "Function", None),
        f"{len(passed_parameters) - len(self.parameters)} too many parameters passed into {self}"
      ))
    
    if len(passed_parameters) < len(self.parameters):
      return res.failure(RuntimeError(
        self.pos_start, self.pos_end,
        f"{len(self.parameters) - len(passed_parameters)} too few parameters passed into {self}"
      ))
    
    for i in range(len(passed_parameters)):
      param_name = self.parameters[i]
      param_name
      param_value = passed_parameters[i]

      param_value.set_context(new_context)
      new_context.symbol_table.set(param_name, param_value)
      
    value = None
    for statement in self.body_statements:
      value = res.register(interpreter.visit(statement, new_context))
      if res.error: return res

      # Check for early return (FOUND YR)
      if isinstance(value, Return):
        return res.success(value.value)
      
      # Check for GTFO (break)
      if isinstance(value, Break):
        value = Noob()
        break

    return res.success(value if value is not None else Noob())

#   def typecast(self, target_class): return True
#   def explicit_typecast(self, target_class, to_float=False): return True

  def __repr__(self):
    return f"<function {self.function_name}>"
  