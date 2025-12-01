BTW Test: Line continuation feature
BTW Using ... to continue expressions across multiple lines

HAI
    WAZZUP
        I HAS A x ITZ 10
        I HAS A y ITZ 20
        I HAS A z ITZ 30
        I HAS A result
    BUHBYE
    
    VISIBLE "=== Testing Line Continuation ==="
    VISIBLE ""
    
    BTW Test 1: Simple arithmetic with line continuation
    VISIBLE "Test 1: Multi-line arithmetic"
    result R SUM OF x AN ...
              SUM OF y AN z
    VISIBLE "x + y + z = " + result
    VISIBLE ""
    
    BTW Test 2: Complex expression
    VISIBLE "Test 2: Complex expression"
    result R PRODUKT OF ...
             SUM OF x AN y ...
             AN ...
             DIFF OF z AN 5
    VISIBLE "(x + y) * (z - 5) = " + result
    VISIBLE ""
    
    BTW Test 3: String concatenation with line continuation
    VISIBLE "Test 3: Multi-line string concatenation"
    I HAS A greeting ITZ SMOOSH "Hello, " ...
                                AN "this is " ...
                                AN "a multi-line " ...
                                AN "string!"
    VISIBLE greeting
    VISIBLE ""
    
    BTW Test 4: Variable declaration with line continuation
    VISIBLE "Test 4: Variable initialization"
    I HAS A calculation ITZ ...
        PRODUKT OF ...
        SUM OF 5 AN 3 ...
        AN ...
        DIFF OF 10 AN 2
    VISIBLE "Calculation result: " + calculation
    VISIBLE ""
    
    BTW Test 5: Nested operations
    VISIBLE "Test 5: Deeply nested operations"
    result R SUM OF ...
             PRODUKT OF 2 AN 3 ...
             AN ...
             SUM OF ...
             QUOSHUNT OF 20 AN 4 ...
             AN ...
             MOD OF 17 AN 5
    VISIBLE "Complex nested result: " + result
    
KTHXBYE
