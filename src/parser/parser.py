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


# Parse Result (w dictionary that stores success (the node itself) or failure (the error message))

def create_parse_result(node = None, error = None):
    # dictionary
    result = {
        'error': error,
        'node': node # if success
    }
    return result

def is_error (result):
    return result['error'] is not None

# Create Nodes 

def create_program_node(hai_token, statements, kthxbye_token):
    """Program node now includes HAI and KTHXBYE tokens"""
    program_node = {
        'type': 'Program',
        'hai': hai_token,
        'statements': statements,
        'kthxbye': kthxbye_token,
        'children': statements,
        'pos_start': {'line': hai_token['line'], 'col': hai_token['col']},
        'pos_end': {'line': kthxbye_token['line'], 'col': kthxbye_token['col']}
    }
    return program_node

def create_var_declaration_node(varident, initial_value = None):
    children = []

    if initial_value:
        children.append(initial_value)

    var_declaration_node = {
        'type': 'Variable Declaration',
        'varident': varident['value'],
        'children': children,
        'pos_start': {'line': varident['line'], 'col': varident['col']},
        'pos_end': initial_value['pos_end'] if initial_value else {'line': varident['line'], 'col': varident['col']}
    }
    return var_declaration_node

def create_literal_node(token):
    literal_node = {
        'type': 'Literal',
        'value_type': token['type'].name,
        'value': token['value'],
        'children': [],
        'pos_start': {'line': token['line'], 'col': token['col']},
        'pos_end': {'line': token['line'], 'col': token['col']}
    }
    return literal_node

# Error Handling

## create a syntax error message
def create_syntax_error(token, expected):
    return {
        'type': 'SyntaxError',
        'message': f"Expected {expected}, got {token['type'].name}",
        'line': token['line'],
        'col': token['col'],
        'token': token['value']
    }

## format error for display
def format_error(error):
    if error:
        return f"Syntax Error at line {error['line']}, col {error['col']}: {error['message']}"
    return None

# Create parser state

## create a state dictionary
def create_parser_state(tokens):
    state = {
        'tokens': tokens,
        'current_index': 0,
        'current_token': tokens[0] if tokens else None
    }
    return state

## move to the next token
def advance(state):
    state['current_index'] += 1
    if state['current_index'] < len(state['tokens']):
        state['current_token'] = state['tokens'][state['current_index']]
    else:
        state['current_token'] = None
    return state['current_token']

## get next token w/o advance
def peek(state, offset = 1):
    index = state['current_index'] + offset
    if index < len(state['tokens']):
        return state['tokens'][index]
    return None

## validate if token is an existing type, if yes, advance
def expect(state, token_type):
    if state['current_token'] is None:
        return create_syntax_error({'type': TokenType.IDENTIFIER, 'line': 0, 'col': 0, 'value': 'EOF'}, token_type.name)
     
    if state['current_token']['type'] != token_type:
        return create_syntax_error(state['current_token'], token_type.name)
    
    token = state['current_token']
    advance(state)
    return token

# Create parser functions recursively

## <literal> ::= numbr | numbar | yarn | troof
def parse_literal(state):
    token = state['current_token']

    ### if success, return as success with node. does not use expect() kasi multiple types ang literal
    if token['type'] in [TokenType.WIN, TokenType.FAIL, TokenType.IDENTIFIER, TokenType.STRING, TokenType.INTEGER, TokenType.FLOAT]:
        advance(state)
        return create_parse_result(node=create_literal_node(token))
    
    ### else, returns an error
    return create_parse_result(error=create_syntax_error(token, "literal value"))


## <declaration> ::= I HAS A <varident> <initialization>
## <initialization> ::= ITZ <expression> | ε
def parse_declaration(state):
    token = state['current_token']

    ### expect I HAS A
    error = expect(state, TokenType.I_HAS_A)
    if isinstance(error, dict) and error['type'] == 'SyntaxError':
        return create_parse_result(error=error)
    
    ### expect varident
    varident = expect(state, TokenType.IDENTIFIER)
    if isinstance(varident, dict) and varident['type'] == 'SyntaxError':
        return create_parse_result(error=varident)
    
    ### I HAS A found
    initial_value = None

    ### optional check for ITZ
    if state['current_token'] and state['current_token']['type'] == TokenType.ITZ:
        advance(state)  # consume ITZ
        
        #### parse the initial value ***(LITERALS LANG MUNA)***
        value_result = parse_literal(state)
        if is_error(value_result):
            return value_result
        
        initial_value = value_result['node']
    
    ### else, returns an error
    return create_parse_result(node=create_var_declaration_node(varident, initial_value))

## parse each statement (<expression> | <conditional> | <loop> | <function_call> | <function_def> | <declaration> | <input> | <output>)
def parse_statement(state):
    token = state['current_token']

    ### for declaration 
    if token['type'] == TokenType.I_HAS_A:
        return parse_declaration(state)

    ### if all fails
    return create_parse_result(error=create_syntax_error(token, "a valid statement"))

## parse <statement_list> ::= <statement> <linebreak> <statement_list> | ε
def parse_statement_list(state):
    statements = []

    while state['current_token'] and state['current_token']['type'] != TokenType.KTHXBYE:
        statement_result = parse_statement(state)

        if is_error(statement_result):
            return statement_result
        
        #### statement_list > statement > .. > .. is success if node is returned, then, append it to list
        statements.append(statement_result['node'])

    ### return the successful result 
    return create_parse_result(node=statements)

## parse <program> ::= HAI <linebreak> <statement_list> <linebreak> KTHXBYE
def parse_program(state):
    
    ### expect HAI
    hai_token = expect(state, TokenType.HAI)
    if isinstance(hai_token, dict) and hai_token.get('type') == 'SyntaxError':
        return create_parse_result(error=hai_token)
    
    ### parse stataments
    statement_result = parse_statement_list(state)
    if is_error(statement_result):
        return statement_result
    
    ### if statement list success, pass node
    statements = statement_result['node']
    
    ### expect KTHXBYE
    kthxbye_token = expect(state, TokenType.KTHXBYE)
    if isinstance(kthxbye_token, dict) and kthxbye_token.get('type') == 'SyntaxError':
        return create_parse_result(error=kthxbye_token)
    
    ### if success, pass both delimiter tokens
    return create_parse_result(node=create_program_node(hai_token, statements, kthxbye_token))

# Main Parser, returns (ast_node, error)
def parse(tokens):

    ## fall back if no tokens found
    if not tokens:
        return None, {'type': 'SyntaxError', 'message': 'No tokens to parse', 'line': 0, 'col': 0}
    
    state = create_parser_state(tokens)
    result = parse_program(state)

    ## if error
    if is_error(result):
        return None, result['error']

    ## if success
    return result['node'], None

# UTILITY: PRINT AST
def print_ast(node, indent=0):
    """Pretty print the AST"""
    if node is None:
        return
    
    prefix = "  " * indent
    
    if isinstance(node, list):
        for item in node:
            print_ast(item, indent)
        return
    
    # Get position info
    line = node['pos_start']['line']
    col = node['pos_start']['col']
    pos_str = f"[Line {line}, Col {col}]"
    
    if node['type'] == 'Program':
        print(f"{prefix}Program: {pos_str}")
        print(f"{prefix}  HAI [Line {node['hai']['line']}, Col {node['hai']['col']}]")
        print(f"{prefix}  Body:")
        print_ast(node['statements'], indent + 2)
        print(f"{prefix}  KTHXBYE [Line {node['kthxbye']['line']}, Col {node['kthxbye']['col']}]")
    
    elif node['type'] == 'Variable Declaration':
        print(f"{prefix}Variable Declaration: {node['varident']} {pos_str}")
        if node['children']:
            print(f"{prefix}  Initial value:")
            for child in node['children']:
                print_ast(child, indent + 2)
    
    elif node['type'] == 'Literal':
        print(f"{prefix}Literal({node['value_type']}): {node['value']} {pos_str}")


# Test
def main():
    test_cases = [
        # Test 1: Simple variable declaration
        """HAI\nI HAS A x\nKTHXBYE""",
        
        # Test 2: Variable with initialization
        """HAI\nI HAS A x ITZ 42\nKTHXBYE""",
        
        # Test 3: Multiple variables (has error - missing variable name)
        """HAI\nI HAS A ITZ 42\nI HAS A y ITZ "hello"\nI HAS A z\nKTHXBYE""",
    ]

    for i, code in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"Test Case {i}:")
        print(code)
        print(f"\n{'─'*50}")

        try:
            tokens = tokenizer.tokenize(code)
            ast, error = parse(tokens)

            if error: 
                print("\nParse Error:")
                print(f"Syntax Error at line {error['line']}, col {error['col']}: {error['message']}")

            else:
                print("\nParse Success!")
                print("\nAST:")
                print_ast(ast)
            
        except Exception as e:
            print(f"Error: {e}")


main()