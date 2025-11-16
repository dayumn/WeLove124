from src.lexer import tokenizer

def print_tokens(tokens):
    """Print tokens in a readable format."""
    for token in tokens:
        cat = token.get('category') or token['type'].name
        print(f"{cat:28} {token['value']} Line {token['line']}")


def main():
    base = "test/project-testcases"
    files = [
        # f"{base}/01_variables.lol",
        f"{base}/02_gimmeh.lol",
        # f"{base}/03_arith.lol",
        # f"{base}/04_smoosh_assign.lol",
        # f"{base}/05_bool.lol",
        # f"{base}/06_comparison.lol",
        # f"{base}/07_ifelse.lol",
        # f"{base}/08_switch.lol",
        # f"{base}/09_loops.lol",
        # f"{base}/10_functions.lol",
    ]

    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
        except FileNotFoundError:
            print(f"Skipping missing file: {path}")
            continue

        print(f"\n=== Tokens for: {path} ===")
        try:
            tokens = tokenizer.tokenize(source)
            print_tokens(tokens)
            print(f"Total tokens: {len(tokens)}\n")
        except SyntaxError as e:
            print(f"Lexer error in {path}: {e}")
main()