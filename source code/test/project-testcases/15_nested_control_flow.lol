BTW Test: Nested control flow structures

HAI
WAZZUP
I HAS A num
I HAS A i
I HAS A j
I HAS A result
I HAS A found
BUHBYE

VISIBLE "=== Testing Nested Control Flow ==="

BTW Test 1: Nested if-else
VISIBLE "Test 1: Nested if-else"
num R 7
BOTH SAEM BIGGR OF num AN 0 AN num, O RLY?
    YA RLY
        BOTH SAEM SMALLR OF num AN 10 AN num, O RLY?
            YA RLY
                VISIBLE "Between 0 and 10"
            NO WAI
                VISIBLE "Greater than 10"
        OIC
    NO WAI
        VISIBLE "Not positive"
OIC

BTW Test 2: Loop inside if-else
VISIBLE "Test 2: Loop in if-else"
num R 4
BOTH SAEM MOD OF num AN 2 AN 0, O RLY?
    YA RLY
        i R 0
        IM IN YR lp UPPIN YR i TIL BOTH SAEM i AN num
            VISIBLE i
        IM OUTTA YR lp
OIC

BTW Test 3: If-else inside loop
VISIBLE "Test 3: If-else in loop"
i R 1
IM IN YR lp2 UPPIN YR i TIL BOTH SAEM i AN 6
    BOTH SAEM MOD OF i AN 2 AN 0, O RLY?
        YA RLY
            VISIBLE "even"
        NO WAI
            VISIBLE "odd"
    OIC
IM OUTTA YR lp2

BTW Test 4: Nested loops
VISIBLE "Test 4: Nested loops"
i R 1
IM IN YR outer UPPIN YR i TIL BOTH SAEM i AN 4
    j R 1
    IM IN YR inner UPPIN YR j TIL BOTH SAEM j AN 4
        result R PRODUKT OF i AN j
        VISIBLE result
    IM OUTTA YR inner
IM OUTTA YR outer

BTW Test 5: Switch with nested if
VISIBLE "Test 5: Switch with nested if"
num R 2
num, WTF?
    OMG 1
        VISIBLE "Case 1"
        GTFO
    OMG 2
        num R 5
        result R 1
        i R 1
        IM IN YR fact UPPIN YR i TIL BOTH SAEM i AN SUM OF num AN 1
            result R PRODUKT OF result AN i
        IM OUTTA YR fact
        VISIBLE result
        GTFO
    OMGWTF
        VISIBLE "Default"
OIC

BTW Test 6: Break in nested loop
VISIBLE "Test 6: Break in loop"
i R 1
found R FAIL
IM IN YR search UPPIN YR i TIL BOTH SAEM i AN 20
    BOTH SAEM MOD OF i AN 15 AN 0, O RLY?
        YA RLY
            VISIBLE i
            found R WIN
            GTFO
    OIC
IM OUTTA YR search

KTHXBYE
