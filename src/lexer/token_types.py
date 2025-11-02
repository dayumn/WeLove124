MULTI_KEYWORDS = [
    # variable declaration
    ("I HAS A", "Variable Declaration"),

    # arithmetic operators
    ("SUM OF", "Arithmetic Operator"),
    ("DIFF OF", "Arithmetic Operator"),
    ("PRODUKT OF", "Arithmetic Operator"),
    ("QUOSHUNT OF", "Arithmetic Operator"),
    ("MOD OF", "Arithmetic Operator"),

    # comparison operators
    ("BIGGR OF", "Comparison Operator"),
    ("SMALLR OF", "Comparison Operator"),
    ("BOTH SAEM", "Comparison Operator"),

    # boolean operators
    ("BOTH OF", "Boolean Operator"),
    ("EITHER OF", "Boolean Operator"),
    ("WON OF", "Boolean Operator"),
    ("NOT", "Boolean Operator"),
    ("ALL OF", "Boolean Operator"),
    ("ANY OF", "Boolean Operator"),
    ("ANY OF BOTH OF", "Boolean Operator"),
    ("ANY OF EITHER OF", "Boolean Operator"),
    ("ANY OF WON OF", "Boolean Operator"),
    ("ANY OF NOT", "Boolean Operator"),
    ("ANY OF ALL OF", "Boolean Operator"),

    # variable assignment
    ("IS NOW A", "Variable Assignment"),

    # loop delimiters
    ("IM IN YR", "Loop Delimiter"),
    ("IM OUTTA YR", "Loop Delimiter"),

    # function delimiters
    ("HOW IZ I", "Function Delimiter"),
    ("IF U SAY SO", "Function Delimiter"),

    # return statement
    ("FOUND YR", "Return Statement"),

    # conditional delimiters
    ("O RLY?", "Conditional Delimiter"),
    ("YA RLY", "Conditional Delimiter"),
    ("NO WAI", "Conditional Delimiter"),
]

REGEX_KEYWORDS = [
    # liteals
    (r"^\-?[0-9]+\.[0-9]+", "Float Literal"),
    (r"^\-?[0-9]+", "Integer Literal"),

    # troof
    (r"^WIN", "Boolean Value (True)"),
    (r"^FAIL", "Boolean Value (False)"),

    # CUT MUNA DITO MAGPAPARES MUNA KO
]