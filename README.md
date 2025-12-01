# WeLove124

A LOLCODE interpreter implemented in Python with bonus features including arrays, functions, and enhanced syntax support.

## Table of Contents
- [Installation](#installation)
- [Running the Interpreter](#running-the-interpreter)
- [LOLCODE Language Guide](#lolcode-language-guide)
- [Bonus Features](#bonus-features)

## Installation

### Prerequisites
- Python 3.x
- PyQt5 (for GUI)

### Install Dependencies
```bash
pip install PyQt5
```

## Running the Interpreter

### Command Line
```bash
# Run a LOLCODE file
python main.py <filename.lol>

# Examples:
python main.py test/project-testcases/01_variables.lol
```

### GUI Mode
```bash
python gui.py
```

The GUI provides:
- Syntax highlighting
- Token display with categories
- Symbol table visualization
- Interactive console output
- File loading and execution

---

## LOLCODE Language Guide

### Program Structure
Every LOLCODE program must start with `HAI` (no need to specify the version number) and end with `KTHXBYE`:

```lolcode
HAI
    BTW Your code here
KTHXBYE
```

### Comments
```lolcode
BTW This is a single-line comment

OBTW
    This is a
    multiline comment
TLDR
```

### Variables

#### Declaration
Variables are declared in the `WAZZUP...BUHBYE` section:

```lolcode
HAI
    WAZZUP
        I HAS A x
        I HAS A y ITZ 10
    BUHBYE
KTHXBYE
```

#### Assignment
```lolcode
x R 5                BTW Assign 5 to x
I HAS A name ITZ "Myko"   BTW Declare and initialize
```

### Data Types

- **NOOB** - Uninitialized (null)
- **NUMBR** - Integer
- **NUMBAR** - Float
- **YARN** - String
- **TROOF** - Boolean (WIN or FAIL)
- **UHS** - Array (bonus feature)

### Literals
```lolcode
I HAS A int ITZ 42
I HAS A float ITZ 3.14
I HAS A str ITZ "Hello"
I HAS A bool ITZ WIN
I HAS A nothing ITZ NOOB
```

### Input/Output

#### Output
```lolcode
VISIBLE "Hello World"         BTW Print with newline
VISIBLE "Hello" + "World"    BTW Print multiple values
VISIBLE "No newline"!         BTW Suppress newline with !
```

#### Input
```lolcode
GIMMEH name                   BTW Read input into variable
```

### Arithmetic Operations
```lolcode
SUM OF 5 AN 3                 BTW Addition (8)
DIFF OF 10 AN 4               BTW Subtraction (6)
PRODUKT OF 6 AN 7             BTW Multiplication (42)
QUOSHUNT OF 20 AN 4           BTW Division (5)
MOD OF 17 AN 5                BTW Modulo (2)
BIGGR OF 10 AN 20             BTW Maximum (20)
SMALLR OF 10 AN 20            BTW Minimum (10)
```

### Boolean Operations
```lolcode
BOTH OF WIN AN FAIL           BTW AND (FAIL)
EITHER OF WIN AN FAIL         BTW OR (WIN)
WON OF WIN AN FAIL            BTW XOR (WIN)
NOT WIN                       BTW NOT (FAIL)
ALL OF WIN AN WIN AN FAIL MKAY    BTW Infinite Arity AND
ANY OF FAIL AN FAIL AN WIN MKAY   BTW Infinite Arity OR
```

### Comparison Operations
```lolcode
BOTH SAEM x AN y              BTW Equal to
DIFFRINT x AN y               BTW Not equal to
```

### String Operations
```lolcode
SMOOSH "Hello" AN " " AN "World" MKAY   BTW Concatenation
```

### Typecasting

#### Explicit Casting
```lolcode
MAEK x A NUMBR                BTW Cast x to integer
MAEK y A YARN                 BTW Cast y to string
```

#### Recasting
```lolcode
x IS NOW A TROOF              BTW Change x's type to boolean
numbr R MAEK number YARN      BTW number reassigned to the YARN value of number (“17.0”)
```

### Conditional Statements

#### If-Else
```lolcode
x R 10
BOTH SAEM x AN 10
O RLY?
    YA RLY
        VISIBLE "x is 10"
    NO WAI
        VISIBLE "x is not 10"
OIC
```

#### If-Else If-Else
```lolcode
BOTH SAEM grade AN 90
O RLY?
    YA RLY
        VISIBLE "A"
    MEBBE BOTH SAEM grade AN 80
        VISIBLE "B"
    NO WAI
        VISIBLE "F"
OIC
```

### Switch-Case
```lolcode
WTF?
    OMG 1
        VISIBLE "Case 1"
        GTFO
    OMG 2
        VISIBLE "Case 2"
        GTFO
    OMGWTF
        VISIBLE "Default case"
OIC
```

### Loops

#### Basic Loop
```lolcode
IM IN YR loop UPPIN YR counter TIL BOTH SAEM counter AN 5
    VISIBLE counter
IM OUTTA YR loop
```

#### Loop with Condition
```lolcode
I HAS A x ITZ 0
IM IN YR loop UPPIN YR x WILE DIFFRINT x AN 10
    VISIBLE x
IM OUTTA YR loop
```

#### Breaking from Loop
```lolcode
IM IN YR loop UPPIN YR i TIL BOTH SAEM i AN 100
    BOTH SAEM i AN 5
    O RLY?
        YA RLY
            GTFO          BTW Break
    OIC
    VISIBLE i
IM OUTTA YR loop
```

### Functions

#### Declaration
```lolcode
HOW IZ I add YR a AN YR b
    I HAS A sum ITZ SUM OF a AN b
    FOUND YR sum
IF U SAY SO
```

#### Function Call
```lolcode
I HAS A result ITZ I IZ add YR 5 AN YR 3 MKAY
VISIBLE result                BTW Outputs: 8
```

---

## Bonus Features

# Special Characters
Below are the following special characters implemented in this interpreter, along with their equivalent values. The mapping was sourced from this [Special Character Documentation](https://homepage.mi-ras.ru/~sk/lehre/fivt2013/Lolcode_spec1.2.html).

- **:)** -> Newline (\n)
- **:>** -> Tab (\t)
- **:o** -> Bell/Beep (\a)
- **:"** -> Literal Quote (")
- **::** -> Literal Colon (:)

# Line Continuation
Multiple lines can be combined into a single command by using an ellipsis at the end of a line:
- **...** (three periods)
- **…** (unicode ellipsis character U+2026)

Example:
```lolcode
I HAS A x ITZ ...
SUM OF 5 AN 10
```

# Soft Command Break
Multiple commands can be placed on a single line when separated by a comma:
```lolcode
I HAS A x ITZ 5, I HAS A y ITZ 10, VISIBLE x
```

# Arrays (UHS Type)
Arrays allow you to store multiple values of the same type.

### Array Declaration
```lolcode
BTW Declare an array of 5 integers
I HAS A numbers ITZ A NUMBR UHS OF 5

BTW Declare an array of 3 strings
I HAS A names ITZ A YARN UHS OF 3
```

### Array Operations

#### CONFINE - Store a value at an index
```lolcode
CONFINE 100 IN numbers AT 0    BTW numbers[0] = 100
CONFINE 200 IN numbers AT 1    BTW numbers[1] = 200
```

#### Array Access - Use brackets
```lolcode
VISIBLE numbers[0]              BTW Display value at index 0
I HAS A val ITZ numbers[1]      BTW Assign array value to variable
```

#### DISCHARGE - Remove element at index
```lolcode
DISCHARGE numbers AT 0          BTW Remove element at index 0
```

### Complete Array Example
```lolcode
HAI
    WAZZUP
        BTW Create array of 3 numbers
        I HAS A nums ITZ A NUMBAR UHS OF 3
    BUHBYE
    
    BTW Store values
    CONFINE 10.5 IN nums AT 0
    CONFINE 20.3 IN nums AT 1
    CONFINE 30.7 IN nums AT 2
    
    BTW Display values
    VISIBLE nums[0]
    VISIBLE nums[1]
    VISIBLE nums[2]
    
    BTW Remove first element
    DISCHARGE nums AT 0
KTHXBYE
```

---

## Examples

### Example 1: Hello World
```lolcode
HAI
    VISIBLE "Hello World"
KTHXBYE
```

### Example 2: User Input
```lolcode
HAI
    VISIBLE "What is your name?"
    GIMMEH name
    VISIBLE "Hello " AN name AN "!"
KTHXBYE
```

### Example 3: Factorial
```lolcode
HAI
    I HAS A num ITZ 5
    I HAS A result ITZ 1
    
    IM IN YR loop UPPIN YR i TIL BOTH SAEM i AN num
        result R PRODUKT OF result AN SUM OF i AN 1
    IM OUTTA YR loop
    
    VISIBLE "Factorial: " AN result
KTHXBYE
```

### Example 4: Function with Arrays
```lolcode
HAI
    HOW IZ I sumArray YR arr AN YR size
        I HAS A total ITZ 0
        I HAS A i ITZ 0
        
        IM IN YR loop UPPIN YR i TIL BOTH SAEM i AN size
            total R SUM OF total AN arr[i]
        IM OUTTA YR loop
        
        FOUND YR total
    IF U SAY SO
    
    BTW Create and populate array
    I HAS A numbers ITZ A NUMBR UHS OF 3
    CONFINE 10 IN numbers AT 0
    CONFINE 20 IN numbers AT 1
    CONFINE 30 IN numbers AT 2
    
    BTW Call function
    I HAS A sum ITZ I IZ sumArray YR numbers AN YR 3 MKAY
    VISIBLE "Sum: " AN sum
KTHXBYE
```

---

## Testing

Run the test suite:
```bash
# Run individual test
python main.py test/project-testcases/01_variables.lol
python main.py test/project-testcases/17_arrays.lol

# Test all features
python main.py test/project-testcases/10_functions.lol
```

---

## Project Structure
```
WeLove124/
├── main.py                 # Command-line interpreter
├── gui.py                  # GUI application
├── src/
│   ├── lexer/
│   │   └── tokenizer.py    # Lexical analysis
│   ├── parser/
│   │   └── parser.py       # Syntax analysis
│   ├── interpreter/
│   │   ├── interpreter.py  # Code execution
│   │   ├── runtime.py      # Runtime environment
│   │   └── values.py       # Value types
│   └── utils/
│       └── file_reader.py  # File handling
└── test/
    └── project-testcases/  # Test files
```

---

## Contributors
- Team WeLove124

## License
Educational project for CMSC 124.

## Remarks
We love 124, but we hate LOLCode - Bry, Franz, Myko

