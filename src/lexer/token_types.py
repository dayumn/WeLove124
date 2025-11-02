##################
# TOKENS
#################


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
    # literals
    (r"^\-?[0-9]+\.[0-9]+", "Float Literal"),
    (r"^\-?[0-9]+", "Integer Literal"),
    (r'^".*"', "Yarn Literal"),

    # troof
    (r"^WIN", "Boolean Value (True)"),
    (r"^FAIL", "Boolean Value (False)"),

    # type literal
    (r"^(NUMBR|NUMBAR|YARN|TROOF)$", "Type Literal"),

    # other keywords (di ko alam if need tanggalin yung $ depende guro sa pag implement natin sa interpreter )
    (r"^HAI$", "HAI"),
    (r"^KTHXBYE$", "KTHXBYE"),
    (r"^WAZZUP$", "WAZZUP"),
    (r"^BUHBYE$", "BUHBYE"),
    (r"^BTW$", "BTW"),
    (r"^OBTW$", "OBTW"),
    (r"^TLDR$", "TLDR"),
    (r"^I HAS A$", "I_HAS_A"),
    (r"^ITZ$", "ITZ"),
    (r"^R$", "R"),
    (r"^SUM OF$", "SUM_OF"),
    (r"^DIFF OF$", "DIFF_OF"),
    (r"^PRODUKT OF$", "PRODUKT_OF"),
    (r"^QUOSHUNT OF$", "QUOSHUNT_OF"),
    (r"^MOD OF$", "MOD_OF"),
    (r"^BIGGR OF$", "BIGGR_OF"),
    (r"^SMALLR OF$", "SMALLR_OF"),
    (r"^BOTH OF$", "BOTH_OF"),
    (r"^EITHER OF$", "EITHER_OF"),
    (r"^WON OF$", "WON_OF"),
    (r"^NOT$", "NOT"),
    (r"^ANY OF$", "ANY_OF"),
    (r"^ALL OF$", "ALL_OF"),
    (r"^BOTH SAEM$", "BOTH_SAEM"),
    (r"^DIFFRINT$", "DIFFRINT"),
    (r"^SMOOSH$", "SMOOSH"),
    (r"^MAEK$", "MAEK"),
    (r"^A$", "A"),
    (r"^IS NOW A$", "IS_NOW_A"),
    (r"^VISIBLE$", "VISIBLE"),
    (r"^GIMMEH$", "GIMMEH"),
    (r"^O RLY\?$", "O_RLY"),
    (r"^YA RLY$", "YA_RLY"),
    (r"^MEBBE$", "MEBBE"),
    (r"^NO WAI$", "NO_WAI"),
    (r"^OIC$", "OIC"),
    (r"^WTF\?$", "WTF"),
    (r"^OMG$", "OMG"),
    (r"^OMGWTF$", "OMGWTF"),
    (r"^IM IN YR$", "IM_IN_YR"),
    (r"^UPPIN$", "UPPIN"),
    (r"^NERFIN$", "NERFIN"),
    (r"^YR$", "YR"),
    (r"^TIL$", "TIL"),
    (r"^WILE$", "WILE"),
    (r"^IM OUTTA YR$", "IM_OUTTA_YR"),
    (r"^HOW IZ I$", "HOW_IZ_I"),
    (r"^IF U SAY SO$", "IF_U_SAY_SO"),
    (r"^GTFO$", "GTFO"),
    (r"^FOUND YR$", "FOUND_YR"),
    (r"^I IZ$", "I_IZ"),
    (r"^MKAY$", "MKAY"),


]

