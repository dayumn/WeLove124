# WeLove124

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

