from src.lexer.token_types import MULTI_KEYWORDS, REGEX_KEYWORDS
import re

#############
# LEXER
#############

# # paano natin iimplement? line by line input or magreread siya ng .txt?
# def tokenizer():
#     tokens = [] # add the tokens here

#     # iterate line by line (identify first if multi-line or not)
#     # tokenize per match in the token types
#     # add to tokens
#     # return token

import re

def tokenize_lolcode(source_code):
    tokens = []
    in_multiline_comment = False

    # process line by line
    for line_num, line in enumerate(source_code.splitlines(), start=1):
        line = line.strip()

        # skip empty lines
        if not line:
            continue

        # handle multi-line comment / ignores it
        if in_multiline_comment:
            if "TLDR" in line:
                in_multiline_comment = False
            continue

        # detect start of multi-line comment
        if line.startswith("OBTW"):
            in_multiline_comment = True
            continue

        # handle single-line comment/ignores it
        if line.startswith("BTW"):
            continue

        # split lexemes by whitespace
        lexemes = line.split()

        # check each lexeme
        for lexeme in lexemes:
            token_type = None

            # check against regex keywords
            for pattern, t_type in REGEX_KEYWORDS:
                if re.match(pattern, lexeme):
                    token_type = t_type
                    break

            # if no regex match, check in MULTI_KEYWORDS
            if not token_type:
                for word, t_type in MULTI_KEYWORDS:
                    if lexeme == word:
                        token_type = t_type
                        break

            # default classification
            if not token_type:
                token_type = "Identifier or Unknown"

            tokens.append((lexeme, token_type, line_num))

    return tokens
