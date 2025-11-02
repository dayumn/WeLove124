import token_types
import re

#############
# LEXER
#############

# paano natin iimplement? line by line input or magreread siya ng .txt?
def tokenizer():
    tokens = [] # add the tokens here

    # iterate line by line (identify first if multi-line or not)
    # tokenize per match in the token types
    # add to tokens
    # return token