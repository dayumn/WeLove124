from src.lexer.tokenizer import tokenize_lolcode

def print_tokens(tokens):
    for token in tokens:
        print(f"lexeme: {token[0]}, type: {token[1]}, line num: {token[2]}")
        print("\n")

while True:
    tokens = []
    text = input('====TOKENIZING====')

    try:
        with open("./test/project-testcases/01_variables.lol", "r") as file: # run test codes here
            source_code = file.read()
    except:
        print("Error: File not found! \n")

    tokens = tokenize_lolcode(source_code) # call tokenizer
    print_tokens(tokens)


    