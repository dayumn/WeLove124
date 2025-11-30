import re
from enum import Enum

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
    QUOTE = "QUOTE"
    PLUS = "PLUS"
    MEBBE = "MEBBE"

# Token specification with patterns
TOKEN_SPEC = [
    # Comments (must come before other patterns)
    # Skip single-line and multi-line comments entirely for Milestone 1
    (None, r'\bBTW\b[^\n]*'),
    (None, r'\bOBTW\b.*?\bTLDR\b', re.DOTALL),
    
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
    (TokenType.OMGWTF, r'OMGWTF'),
    (TokenType.OMG, r'OMG'),
    (TokenType.UPPIN, r'UPPIN'),
    (TokenType.NERFIN, r'NERFIN'),
    (TokenType.YR, r'YR'),
    (TokenType.TIL, r'TIL'),
    (TokenType.WILE, r'WILE'),
    (TokenType.GTFO, r'GTFO'),
    (TokenType.MKAY, r'MKAY'),
    (TokenType.MEBBE, r'MEBBE'),
    
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
    (TokenType.QUOTE, r'\"'),
    
    # Identifiers
    (TokenType.IDENTIFIER, r'[a-zA-Z_][a-zA-Z0-9_]*'),
    
    # Special characters
    (TokenType.ELLIPSIS, r'\.\.\.'),
    (TokenType.COMMA, r','),
    (TokenType.EXCLAMATION, r'!'),
    (TokenType.PLUS, r'\+'),
    (None, r'\n'),
    
    # Skip whitespace
    (None, r'[ \t]+'),
]

def create_token(token_type, value, line, col):
    
    return {
        'type': token_type,
        'value': value,
        'line': line,
        'col': col,
        'category': None,
}

CATEGORY_MAP = {

    # --- Boolean Values ---
    TokenType.WIN: "Boolean Value (True)",
    TokenType.FAIL: "Boolean Value (False)",

    # --- Code Delimiters ---
    TokenType.HAI: "Code Delimiter",
    TokenType.KTHXBYE: "Code Delimiter",

    # --- Comments ---
    TokenType.COMMENT: "Comment",

    # --- Comparison Operators ---
    TokenType.BIGGR_OF: "Comparison Operator",
    TokenType.BOTH_SAEM: "Comparison Operator",
    TokenType.DIFFRINT: "Comparison Operator",
    TokenType.SMALLR_OF: "Comparison Operator",

    # --- Data Types ---
    TokenType.NOOB: "Type Literal",
    TokenType.NUMBR: "Type Literal",
    TokenType.NUMBAR: "Type Literal",
    TokenType.YARN: "Type Literal",
    TokenType.TROOF: "Type Literal",

    # --- Flow Control ---
    TokenType.GTFO: "Flow Control (Break)",

    # --- Function Keywords ---
    TokenType.HOW_IZ_I: "Function Declaration Keyword",
    TokenType.IF_U_SAY_SO: "Function End Keyword",
    TokenType.FOUND_YR: "Function Return Keyword",
    TokenType.I_IZ: "Function Call Keyword",
    TokenType.MKAY: "Function Call Terminator",

    # --- Identifiers ---
    TokenType.IDENTIFIER: "Variable Identifier",

    # --- Input/Output ---
    TokenType.VISIBLE: "Output Keyword",
    TokenType.GIMMEH: "Input Keyword",

    # --- Literals ---
    TokenType.STRING: "Yarn Literal",
    TokenType.INTEGER: "Integer Literal",
    TokenType.FLOAT: "Float Literal",

    # --- Loop Keywords ---
    TokenType.IM_IN_YR: "Loop Start Keyword",
    TokenType.IM_OUTTA_YR: "Loop End Keyword",
    TokenType.UPPIN: "Loop Increment Keyword",
    TokenType.NERFIN: "Loop Decrement Keyword",
    TokenType.YR: "Loop Iterator Keyword",
    TokenType.TIL: "Loop Until Condition",
    TokenType.WILE: "Loop While Condition",

    # --- Misc / Symbols ---
    TokenType.ELLIPSIS: "Ellipsis Operator",
    TokenType.COMMA: "Comma Separator",
    TokenType.EXCLAMATION: "Exclamation Symbol",
    TokenType.PLUS: "Plus Symbol",
    TokenType.QUOTE: "String Delimiter",
    TokenType.A: "Typecast Helper Keyword",

    # --- Operations: Arithmetic ---
    TokenType.SUM_OF: "Arithmetic Operator",
    TokenType.DIFF_OF: "Arithmetic Operator",
    TokenType.PRODUKT_OF: "Arithmetic Operator",
    TokenType.QUOSHUNT_OF: "Arithmetic Operator",
    TokenType.MOD_OF: "Arithmetic Operator",

    # --- Operations: Boolean ---
    TokenType.BOTH_OF: "Boolean Operator",
    TokenType.EITHER_OF: "Boolean Operator",
    TokenType.WON_OF: "Boolean Operator",
    TokenType.NOT: "Boolean Operator",
    TokenType.ANY_OF: "Boolean Variadic Operator",
    TokenType.ALL_OF: "Boolean Variadic Operator",

    # --- Operations: String ---
    TokenType.SMOOSH: "String Concatenation Operator",

    # --- Operations: Typecasting ---
    TokenType.MAEK: "Typecast Operator",
    TokenType.IS_NOW_A: "Explicit Typecast Keyword",

    # --- Switch / Case ---
    TokenType.WTF: "Switch Keyword",
    TokenType.OMG: "Switch Case Keyword",
    TokenType.OMGWTF: "Switch Default Keyword",

    # --- Variable Declaration & Assignment ---
    TokenType.I_HAS_A: "Variable Declaration",
    TokenType.ITZ: "Variable Assignment",
    TokenType.R: "Assignment Operator",

    # --- Variable List Delimiters ---
    TokenType.WAZZUP: "Variable List Delimiter",
    TokenType.BUHBYE: "Variable List Delimiter",

    # --- If/Else Branching ---
    TokenType.O_RLY: "If-Else Keyword",
    TokenType.YA_RLY: "If Branch Keyword",
    TokenType.NO_WAI: "Else Branch Keyword",
    TokenType.MEBBE: "Else-If Keyword",
    TokenType.OIC: "Conditional/Switch End Keyword",

    # --- Misc operators / helpers ---
    TokenType.AN: "Multiple Parameter Separator",

}

def tokenize(code):
    """
    Tokenize LOLCODE source code.
    Returns a list of tokens.
    """
    tokens = []
    line = 1
    col = 1
    pos = 0
    in_string = False
    
    while pos < len(code):
        match_found = False
        
        # Special handling for string content when inside quotes
        if in_string and code[pos] != '"':
            # Capture all content until the next quote or newline
            string_start = pos
            string_col = col
            while pos < len(code) and code[pos] != '"' and code[pos] != '\n':
                pos += 1

            if pos < len(code) and code[pos] == '\n':
                raise SyntaxError(f"Unclosed string literal at line {line}, col {string_col}")
            
            if pos > string_start:
                value = code[string_start:pos]
                tok = create_token(TokenType.STRING, value, line, string_col)
                tok['category'] = CATEGORY_MAP.get(TokenType.STRING, TokenType.STRING)
                tokens.append(tok)
                col += len(value)
            match_found = True
        else:
            # Try each token pattern
            for token_type, pattern, *flags in TOKEN_SPEC:
                regex_flags = flags[0] if flags else 0
                regex = re.compile(pattern, regex_flags)
                match = regex.match(code, pos)
                
                if match:
                    value = match.group()
                    
                    # Skip whitespace (token_type is None)
                    if token_type is not None:
                        # Check for malformed comment keywords that got matched as identifiers
                        if token_type == TokenType.IDENTIFIER and value.startswith(('BTW', 'OBTW', 'TLDR')):
                            raise SyntaxError(f"Invalid comment keyword '{value}' at line {line}, col {col}.")
                        
                        # Track when we enter/exit string mode
                        if token_type == TokenType.QUOTE:
                            in_string = not in_string
                        
                        tok = create_token(token_type, value, line, col)
                        if tok['type'] in CATEGORY_MAP:
                            tok['category'] = CATEGORY_MAP[tok['type']]
                        else:
                            tok['category'] = tok['type']
                        tokens.append(tok)
                    
                    # Update pos tracking
                    newline_count = value.count('\n')
                    if newline_count == 0:
                        col += len(value)
                    else:
                        line += newline_count
                        col = len(value) - value.rfind('\n')
                        
                    pos = match.end()
                    match_found = True
                    break
        
        if not match_found:
            # Handle unexpected character
            char = code[pos]
            raise SyntaxError(f"Unexpected character '{char}' at line {line}, col {col}")
    
    return tokens


