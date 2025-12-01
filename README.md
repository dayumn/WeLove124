# WeLove124
WeLove124 is a custom LOLCODE IDE built with **Python** and **PyQt5**, providing a modern coding environment with syntax highlighting, line numbers, variable tracking, token visualization, and an integrated LOLCODE interpreter.

## **Requirements**
- **Python 3.8+**
- **PyQt5**
## **Installation**
1. Clone the repository:
```bash
git clone https://github.com/dayumn/WeLove124.git
cd WeLove124
```
2. Install the required dependencies:
```bash
pip install PyQt5
```

3. Run the application:
```bash
python gui.py
```
## Development Notes
- macOS may show UI differences due to native styling.
- The interpreter is fully built into this repository.
- The UI relies solely on PyQT5.

## Special Characters
Below are the following special characters implemented in this interpreter, along with their equivalent values. The mapping was sourced from this [Special Character Documentation](https://homepage.mi-ras.ru/~sk/lehre/fivt2013/Lolcode_spec1.2.html).

- **:)** -> Newline (\n)
- **:>** -> Tab (\t)
- **:o** -> Bell/Beep (\a)
- **:"** -> Literal Quote (")
- **::** -> Literal Colon (:)

## Line Continuation
Multiple lines can be combined into a single command by using an ellipsis at the end of a line:
- **...** (three periods)
- **…** (unicode ellipsis character U+2026)

Example:
```lolcode
I HAS A x ITZ ...
SUM OF 5 AN 10
```

## Soft Command Break
Multiple commands can be placed on a single line when separated by a comma:
```lolcode
I HAS A x ITZ 5, I HAS A y ITZ 10, VISIBLE x
```



