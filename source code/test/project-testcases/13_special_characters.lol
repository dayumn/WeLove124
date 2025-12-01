BTW Test: Special character escape sequences
BTW :) = newline, :> = tab, :o = bell, :" = quote, :: = colon
BTW Simplified version for testing basic functionality

HAI
    WAZZUP
        I HAS A name ITZ "John"
        I HAS A age ITZ 25
        I HAS A city ITZ "Manila"
    BUHBYE
    
    VISIBLE "=== Testing Special Character Escapes ==="
    VISIBLE ""
    
    BTW Test 1: Basic newline test
    VISIBLE "Test 1: Newline character :)"
    VISIBLE "Line 1"
    VISIBLE "Line 2"
    VISIBLE "Line 3"
    VISIBLE ""
    
    BTW Test 2: Tab simulation with spaces
    VISIBLE "Test 2: Tab formatting"
    VISIBLE "Name: :>John"
    VISIBLE "Age: :>25"
    VISIBLE "City: :>Manila"
    VISIBLE ""
    
    BTW Test 3: Quote handling
    VISIBLE "Test 3: Quotes in strings"
    VISIBLE ":"He said Hello World:""
    VISIBLE ""
    
    BTW Test 4: Colon in strings
    VISIBLE "Test 4: Colon character"
    VISIBLE "Time:: 12::30::45:)"

    
KTHXBYE
