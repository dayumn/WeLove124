BTW Test: Soft command break (comma separator)
BTW Multiple statements on a single line

HAI
    WAZZUP
        I HAS A a
        I HAS A b
        I HAS A c
        I HAS A sum
        I HAS A product
    BUHBYE
    
    VISIBLE "=== Testing Soft Command Break (Comma) ==="
    VISIBLE ""
    
    BTW Test 1: Multiple declarations on one line (already in WAZZUP)
    VISIBLE "Test 1: Variables declared with commas"
    a R 5, b R 10, c R 15
    VISIBLE "a = " + a + ", b = " + b + ", c = " + c
    VISIBLE ""
    
    BTW Test 2: Multiple operations on one line
    VISIBLE "Test 2: Multiple operations on one line"
    sum R SUM OF a AN b, product R PRODUKT OF a AN b
    VISIBLE "Sum: " + sum + ", Product: " + product
    VISIBLE ""
    
    BTW Test 3: Chained operations
    VISIBLE "Test 3: Chained calculations"
    a R 1, b R 2, c R 3
    sum R SUM OF a AN b, c R SUM OF sum AN c, VISIBLE "Running sum: " + c
    VISIBLE ""
    
    BTW Test 4: Multiple VISIBLE statements
    VISIBLE "Test 4: Multiple outputs on one line"
    VISIBLE "First", VISIBLE "Second", VISIBLE "Third"
    VISIBLE ""
    
    BTW Test 5: Complex mixed statements
    VISIBLE "Test 5: Mixed statement types"
    a R 100, b R 200, sum R SUM OF a AN b, VISIBLE "a=" + a, VISIBLE "b=" + b, VISIBLE "sum=" + sum
    VISIBLE ""
    
    BTW Test 6: Conditional with comma
    VISIBLE "Test 6: Conditional statements"
    a R 10, b R 10
    BOTH SAEM a AN b, O RLY?
        YA RLY
            VISIBLE "a equals b", a R 20, VISIBLE "a is now " + a
        NO WAI
            VISIBLE "a not equal to b"
    OIC
    
KTHXBYE
