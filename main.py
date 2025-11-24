from src.lexer import tokenizer
from src.parser.parser import Parser
from src.interpreter.runtime import SymbolTable, Context
from src.interpreter.interpreter import Interpreter



def print_tokens(tokens):
    """Print tokens in a readable format."""
    for token in tokens:
        cat = token['category'] or token['type'].name
        print(f"{cat:28} {token['value']} Line {token['line']}")


def main():
    base = "test/project-testcases"
    files = [
        "test/project-testcases/10_functions.lol",
    ]

    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
        except FileNotFoundError:
            print(f"Skipping missing file: {path}")
            continue

        print(f"\n=== TEST for: {path} ===")
        try:
            tokens = tokenizer.tokenize(source)
            print(f"Total tokens: {len(tokens)}\n")
            print_tokens(tokens)

            parser = Parser(tokens)
            AST = parser.parse()
            print("\nPARSE TREE")

            if AST.error:
                print(AST.error.as_string())
            else:
                print(AST.node)

            #If no errors run interpreter
            print("\nINTERPRETER OUTPUT:")
            lolcode_interpreter = Interpreter()
            context = Context('<program>')
            context.symbol_table = SymbolTable()
            result = lolcode_interpreter.visit(AST.node, context)
            
            # Print symbol table for debugging
            print("\n=== SYMBOL TABLE ===")
            for name, value in context.symbol_table.symbols.items():
                # Map Python type names to LOLCODE type names
                type_map = {
                    'Number': 'NUMBR/NUMBAR',
                    'String': 'YARN',
                    'Boolean': 'TROOF',
                    'Noob': 'NOOB',
                    'Function': 'FUNCTION'
                }
                lolcode_type = type_map.get(type(value).__name__, type(value).__name__)
                print(f"{name}: {value} ({lolcode_type})")

            if result.error:
                print(result.error.as_string())
            # else:
            #     print(f"\nProgram executed successfully")
            
        except SyntaxError as e:
            print(f"ERROR {e}")
main()