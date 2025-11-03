import re
from enum import Enum
try:
    from . import token_types as TOKEN_INFO  # when run as module
except Exception:
    import token_types as TOKEN_INFO  # when run as script

# Token types
class TokenType(Enum):
    # Keywords
    HAI = "HAI"
    KTHXBYE = "KTHXBYE"
    WAZZUP = "WAZZUP"
    BUHBYE = "BUHBYE"
    I_HAS_A = "I HAS A"
    ITZ = "ITZ"
    R = "R"
    SUM_OF = "SUM OF"
    DIFF_OF = "DIFF OF"
    PRODUKT_OF = "PRODUKT OF"
    QUOSHUNT_OF = "QUOSHUNT OF"
    MOD_OF = "MOD OF"
    BIGGR_OF = "BIGGR OF"
    SMALLR_OF = "SMALLR OF"
    BOTH_OF = "BOTH OF"
    EITHER_OF = "EITHER OF"
    WON_OF = "WON OF"
    NOT = "NOT"
    ANY_OF = "ANY OF"
    ALL_OF = "ALL OF"
    BOTH_SAEM = "BOTH SAEM"
    DIFFRINT = "DIFFRINT"
    SMOOSH = "SMOOSH"
    MAEK = "MAEK"
    A = "A"
    IS_NOW_A = "IS NOW A"
    VISIBLE = "VISIBLE"
    GIMMEH = "GIMMEH"
    O_RLY = "O RLY?"
    YA_RLY = "YA RLY"
    NO_WAI = "NO WAI"
    OIC = "OIC"
    WTF = "WTF?"
    OMG = "OMG"
    OMGWTF = "OMGWTF"
    IM_IN_YR = "IM IN YR"
    UPPIN = "UPPIN"
    NERFIN = "NERFIN"
    YR = "YR"
    TIL = "TIL"
    WILE = "WILE"
    IM_OUTTA_YR = "IM OUTTA YR"
    HOW_IZ_I = "HOW IZ I"
    IF_U_SAY_SO = "IF U SAY SO"
    GTFO = "GTFO"
    FOUND_YR = "FOUND YR"
    I_IZ = "I IZ"
    MKAY = "MKAY"
    AN = "AN"
    
    # Types
    NOOB = "NOOB"
    NUMBR = "NUMBR"
    NUMBAR = "NUMBAR"
    YARN = "YARN"
    TROOF = "TROOF"
    
    # Literals
    WIN = "WIN"
    FAIL = "FAIL"
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    
    # Special
    # NEWLINE = "NEWLINE"
    COMMENT = "COMMENT"
    ELLIPSIS = "ELLIPSIS"
    COMMA = "COMMA"
    EXCLAMATION = "EXCLAMATION"

# Token specification with patterns
TOKEN_SPEC = [
    # Comments (must come before other patterns)
    # Skip single-line and multi-line comments entirely for Milestone 1
    (None, r'BTW[^\n]*'),
    (None, r'OBTW.*?TLDR', re.DOTALL),
    
    # Skip multiline comments (neglect them entirely)
    (None, r'OBTW.*?TLDR', re.DOTALL),
    
    # Multi-word keywords (order matters - longest first)
    (TokenType.IM_OUTTA_YR, r'IM\s+OUTTA\s+YR'),
    (TokenType.IM_IN_YR, r'IM\s+IN\s+YR'),
    (TokenType.HOW_IZ_I, r'HOW\s+IZ\s+I'),
    (TokenType.IF_U_SAY_SO, r'IF\s+U\s+SAY\s+SO'),
    (TokenType.I_HAS_A, r'I\s+HAS\s+A'),
    (TokenType.IS_NOW_A, r'IS\s+NOW\s+A'),
    (TokenType.SUM_OF, r'SUM\s+OF'),
    (TokenType.DIFF_OF, r'DIFF\s+OF'),
    (TokenType.PRODUKT_OF, r'PRODUKT\s+OF'),
    (TokenType.QUOSHUNT_OF, r'QUOSHUNT\s+OF'),
    (TokenType.MOD_OF, r'MOD\s+OF'),
    (TokenType.BIGGR_OF, r'BIGGR\s+OF'),
    (TokenType.SMALLR_OF, r'SMALLR\s+OF'),
    (TokenType.BOTH_OF, r'BOTH\s+OF'),
    (TokenType.EITHER_OF, r'EITHER\s+OF'),
    (TokenType.WON_OF, r'WON\s+OF'),
    (TokenType.ANY_OF, r'ANY\s+OF'),
    (TokenType.ALL_OF, r'ALL\s+OF'),
    (TokenType.BOTH_SAEM, r'BOTH\s+SAEM'),
    (TokenType.FOUND_YR, r'FOUND\s+YR'),
    (TokenType.I_IZ, r'I\s+IZ'),
    
    # Single word keywords
    (TokenType.O_RLY, r'O\s+RLY\?'),
    (TokenType.YA_RLY, r'YA\s+RLY'),
    (TokenType.NO_WAI, r'NO\s+WAI'),
    (TokenType.WTF, r'WTF\?'),
    (TokenType.HAI, r'HAI'),
    (TokenType.KTHXBYE, r'KTHXBYE'),
    (TokenType.WAZZUP, r'WAZZUP'),
    (TokenType.BUHBYE, r'BUHBYE'),
    (TokenType.ITZ, r'ITZ'),
    (TokenType.R, r'R'),
    (TokenType.NOT, r'NOT'),
    (TokenType.DIFFRINT, r'DIFFRINT'),
    (TokenType.SMOOSH, r'SMOOSH'),
    (TokenType.MAEK, r'MAEK'),
    (TokenType.AN, r'AN'),
    (TokenType.A, r'A'),
    (TokenType.VISIBLE, r'VISIBLE'),
    (TokenType.GIMMEH, r'GIMMEH'),
    (TokenType.OIC, r'OIC'),
    (TokenType.OMG, r'OMG'),
    (TokenType.OMGWTF, r'OMGWTF'),
    (TokenType.UPPIN, r'UPPIN'),
    (TokenType.NERFIN, r'NERFIN'),
    (TokenType.YR, r'YR'),
    (TokenType.TIL, r'TIL'),
    (TokenType.WILE, r'WILE'),
    (TokenType.GTFO, r'GTFO'),
    (TokenType.MKAY, r'MKAY'),
    
    # Type keywords
    (TokenType.NOOB, r'NOOB'),
    (TokenType.NUMBR, r'NUMBR'),
    (TokenType.NUMBAR, r'NUMBAR'),
    (TokenType.YARN, r'YARN'),
    (TokenType.TROOF, r'TROOF'),
    
    # Boolean literals
    (TokenType.WIN, r'WIN'),
    (TokenType.FAIL, r'FAIL'),
    
    # Literals
    (TokenType.FLOAT, r'-?\d+\.\d+'),
    (TokenType.INTEGER, r'-?\d+'),
    (TokenType.STRING, r'"[^"]*"'),
    
    # Identifiers
    (TokenType.IDENTIFIER, r'[a-zA-Z_][a-zA-Z0-9_]*'),
    
    # Special characters
    (TokenType.ELLIPSIS, r'\.\.\.'),
    (TokenType.COMMA, r','),
    (TokenType.EXCLAMATION, r'!'),
    (None, r'\n'),
    
    # Skip whitespace
    (None, r'[ \t]+'),
]

def create_token(token_type, value, line, column):
    
    return {
        'type': token_type,
        'value': value,
        'line': line,
        'column': column,
        'category': None,
    }

_SIMPLE_CATEGORY_MAP = {
    TokenType.HAI: "Code Delimiter",
    TokenType.KTHXBYE: "Code Delimiter",
    TokenType.WAZZUP: "Variable List Delimiter",
    TokenType.BUHBYE: "Variable List Delimiter",
    TokenType.I_HAS_A: "Variable Declaration",
    TokenType.ITZ: "Variable Assignment",
    TokenType.R: "Assignment Operator",
    TokenType.VISIBLE: "Output Keyword",
    TokenType.AN: "Multiple Parameter Separator",
    TokenType.NOOB: "Type Literal",
    TokenType.NUMBR: "Type Literal",
    TokenType.NUMBAR: "Type Literal",
    TokenType.YARN: "Type Literal",
    TokenType.TROOF: "Type Literal",
}

def categorize_token(token):
    value = token['value']
    ttype = token['type']

    if ttype in _SIMPLE_CATEGORY_MAP:
        return _SIMPLE_CATEGORY_MAP[ttype]

    if ttype == TokenType.INTEGER:
        return "Integer Literal"
    if ttype == TokenType.FLOAT:
        return "Float Literal"
    if ttype == TokenType.STRING:
        return "Yarn Literal"
    if ttype == TokenType.WIN:
        return "Boolean Value (True)"
    if ttype == TokenType.FAIL:
        return "Boolean Value (False)"
    if ttype == TokenType.IDENTIFIER:
        return "Variable Identifier"

    for kw, label in TOKEN_INFO.MULTI_KEYWORDS:
        if value == kw:
            return label

    for pattern, label in TOKEN_INFO.REGEX_KEYWORDS:
        if re.match(pattern, value):
            return label

    return ttype.name if isinstance(ttype, TokenType) else str(ttype)

def tokenize(code):
    """
    Tokenize LOLCODE source code.
    Returns a list of tokens.
    """
    tokens = []
    line = 1
    column = 1
    position = 0
    
    while position < len(code):
        match_found = False
        
        # Try each token pattern
        for token_type, pattern, *flags in TOKEN_SPEC:
            regex_flags = flags[0] if flags else 0
            regex = re.compile(pattern, regex_flags)
            match = regex.match(code, position)
            
            if match:
                value = match.group(0)
                
                # Skip whitespace (token_type is None)
                if token_type is not None:
                    tok = create_token(token_type, value, line, column)
                    tok['category'] = categorize_token(tok)
                    tokens.append(tok)
                
                # Update position tracking
                newline_count = value.count('\n')
                if newline_count > 0:
                    line += newline_count
                    column = len(value) - value.rfind('\n')
                else:
                    column += len(value)
                
                position = match.end()
                match_found = True
                break
        
        if not match_found:
            # Handle unexpected character
            char = code[position]
            raise SyntaxError(f"Unexpected character '{char}' at line {line}, column {column}")
    
    return tokens

def print_tokens(tokens):
    """Print tokens in a readable format."""
    for token in tokens:
        cat = token.get('category') or token['type'].name
        print(f"{cat:28} {token['value']}")

def main():
    base = "/Users/bry/Desktop/bry/college/third year/CMSC 124/final-project/WeLove124/test/project-testcases"
    files = [
        f"{base}/01_variables.lol",
        # f"{base}/02_gimmeh.lol",
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
            tokens = tokenize(source)
            print_tokens(tokens)
            print(f"Total tokens: {len(tokens)}\n")
        except SyntaxError as e:
            print(f"Lexer error in {path}: {e}")

main()