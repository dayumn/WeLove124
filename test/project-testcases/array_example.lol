BTW Array Implementation Example for WeLove124

HAI 1.2

BTW Declare variables
WAZZUP
    I HAS A myuhs ITZ A UHS OF 5
    I HAS A arraysize ITZ 10
    I HAS A patients ITZ A UHS OF arraysize
    I HAS A index
    I HAS A value
BUHBYE

BTW Store values in array using CONFINE
CONFINE 42 IN myuhs AT 0
CONFINE 100 IN myuhs AT 1
CONFINE "John Doe" IN myuhs AT 2
CONFINE WIN IN myuhs AT 3

BTW Access array elements directly in expressions
VISIBLE myuhs[0]
BTW Output: 42

BTW Use array values in arithmetic
I HAS A result ITZ SUM OF myuhs[0] AN myuhs[1]
VISIBLE result
BTW Output: 142

BTW Use variable as index
index R 2
VISIBLE myuhs[index]
BTW Output: John Doe

BTW Use expression as index
VISIBLE myuhs[SUM OF 1 AN 2]
BTW Output: WIN

BTW Set array element to NOOB using DISCHARGE
DISCHARGE myuhs AT 3
VISIBLE myuhs[3]
BTW Output: NOOB

BTW Confine again after discharge
CONFINE "New Value" IN myuhs AT 3
VISIBLE myuhs[3]
BTW Output: New Value

KTHXBYE
