BTW Test: Arrays (Bukkit) feature
BTW Testing array declaration, access, and manipulation

HAI
    WAZZUP
        I HAS A numbers ITZ A NUMBAR UHS OF 5
        I HAS A names ITZ A YARN UHS OF 3
        I HAS A index
    BUHBYE
    
    VISIBLE "=== Testing Arrays (Bukkit) ==="
    VISIBLE ""
    
    BTW Test 1: Array initialization with CONFINE
    VISIBLE "Test 1: Array initialization"
    CONFINE 10 IN numbers AT 0
    CONFINE 20 IN numbers AT 1
    CONFINE 30 IN numbers AT 2
    CONFINE 40 IN numbers AT 3
    CONFINE 50 IN numbers AT 4
    VISIBLE "Array initialized with 5 elements"
    VISIBLE ""
    
    BTW Test 2: Array element access
    VISIBLE "Test 2: Array access"
    VISIBLE "numbers[0] = " + numbers[0]
    VISIBLE "numbers[1] = " + numbers[1]
    VISIBLE "numbers[2] = " + numbers[2]
    VISIBLE "numbers[3] = " + numbers[3]
    VISIBLE "numbers[4] = " + numbers[4]
    VISIBLE ""
    
    BTW Test 3: Array with strings
    VISIBLE "Test 3: String array"
    CONFINE "Alice" IN names AT 0
    CONFINE "Bob" IN names AT 1
    CONFINE "Charlie" IN names AT 2
    VISIBLE "Name 0: " + names[0]
    VISIBLE "Name 1: " + names[1]
    VISIBLE "Name 2: " + names[2]
    VISIBLE ""
    
    BTW Test 4: Array operations with expressions
    VISIBLE "Test 4: Array with expressions"
    CONFINE SUM OF 5 AN 5 IN numbers AT 0
    CONFINE PRODUKT OF 3 AN 7 IN numbers AT 1
    CONFINE DIFF OF 100 AN 25 IN numbers AT 2
    VISIBLE "numbers[0] = 5 + 5 = " + numbers[0]
    VISIBLE "numbers[1] = 3 * 7 = " + numbers[1]
    VISIBLE "numbers[2] = 100 - 25 = " + numbers[2]
    VISIBLE ""
    
    BTW Test 5: Array sum calculation
    VISIBLE "Test 5: Calculate array sum"
    I HAS A sum ITZ 0
    index R 0
    IM IN YR loop UPPIN YR index TIL BOTH SAEM index AN 5
        sum R SUM OF sum AN numbers[index]
    IM OUTTA YR loop
    VISIBLE "Sum of array elements: " + sum
    VISIBLE ""
    
    BTW Test 6: DISCHARGE operation
    VISIBLE "Test 6: DISCHARGE operation"
    VISIBLE "Before discharge: " + numbers[0]
    DISCHARGE numbers AT 0
    VISIBLE "After discharge: " + numbers[0]
    
KTHXBYE
