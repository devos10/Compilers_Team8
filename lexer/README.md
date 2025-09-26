<h1 align="center">
  <img src="https://github.com/user-attachments/assets/3abebde3-8ee0-40d0-ae38-82c52246b528" width="60" height="60" />
  Project: Lexical Analyzer (Lexer)
  <img src="https://github.com/user-attachments/assets/fe29e172-7262-4289-820a-1c08eecaa61b" width="60" height="60" />
</h1>

Repository corresponding to the Lexical Analysis project within the Compilers course.  
This project implements a **Lexer** in Python.

---

## Team Information
| Full name                            | Student ID      |
|----------------------------------    |-----------------|
| Araiza Valdés Diego Antonio          | 423032833       |
| Arroyo Solano Victor Julian          | 423529834       |
| Jaramillo Rodríguez Leslie Citlalli  | 320318931       |
| Salas Hernández Camila Alexandra     | 320332825       |
| Velazquez Caudillo Osbaldo           | 320341704       |

| Field        | Detail         |
|--------------|----------------|
| Course       | Compilers      |
| Project      | Lexer (Lexical Analysis) |
| Semester     | 2026-1         |

---

## Introduction
Lexical analysis is the first phase in the construction of a compiler.  
The *Lexer* receives the source code as input and converts it into a sequence of **tokens**.  
Each token is classified into categories (keywords, identifiers, operators, constants, literals, and punctuation) to be consumed by later stages of the compiler.

---

## Problem Formulation
The objective of the project is to design and implement a lexical analyzer that:
- Reads an input file.
- Identifies and classifies lexemes as tokens.
- Displays the list of tokens grouped by category, the count per category, and the total count.  


In this repository the main function is `lexer(code: str)` (see `src/lexer.py`), which processes the string `code` and returns two values: `result` (list of tuples `(type, lexeme)`) and `counts` (dictionary with counts per type).

---

## Motivation
The tokens produced by the lexer are the building blocks of the compiler: the parser and subsequent phases depend on the tokens being correct and complete. 

---

## Objectives
- Classify tokens into the categories defined by the project (see *Design Considerations*).
- Display:
  - Complete listing of tokens with their classification.
  - Number of tokens found per category.
  - Total number of tokens.

---

## Technologies
- **Language:** Python
- **Libraries used and their use in the code:**
  - `re` → Definition and use of regular expressions to recognize each token type. 
  - `collections.defaultdict` → Used to group tokens by type when printing results.
  - `sys` → Reading command-line arguments (`sys.argv`) to obtain the name of the file to process.
  - `os` → Verification of the existence and correct extension of the file and simple path handling.

---

## Theoretical Framework & Design used
- **Lexeme:** sequence of characters that corresponds to the pattern of a token (e.g. `123`, `if`, `"hola"`).  
- **Token:** minimal unit recognized by the compiler (example: if, +, x). 
- **Lexer:** program that groups characters into tokens and passes them to the parser.  

**Design in the current code:**
- A list `tokens` is defined with pairs `(type_name, regex_pattern)`; for example:
  - `("keywords", r'\b(?:int|float|for|while|if|else|return)\b')`
  - `("identifier", r'[a-zA-Z_]\w*')`, etc.
- The **order** of patterns is important: the lexer tries each pattern in the order of the compiled list (`compiled`). Therefore, more specific patterns must come before more general ones.
- Processing is by **positions**:
  1. `pos` is maintained as the current index in the string.
  2. Whitespace is ignored with `_WS` (regex for `\s+`).
  3. For each `pos`, `rgx.match(code, pos)` is attempted for each pattern until one matches from `pos`.
  4. If there is a match, `lexeme = m.group(0)` is extracted, `(type, lexeme)` is appended to the `result` list, `counts[type]` is incremented, and `pos = m.end()` advances.
  5. If no pattern matches at `pos`, a `SyntaxError` is raised with the position of the unexpected character.
- The flow ensures that each character is consumed exactly once and that there are no uncontrolled overlaps.

> **Important note:** in the current code there is no pattern for comments (for example `//...`) — if support for comments is needed, it should be added explicitly to the `tokens` list (before `identifier`).

---

## Development

### Design Considerations
- **Types (names as they appear in the code):**
  - Keywords: `int | float | for | while | if | else | return  `
  - Identifier: `[a-zA-Z_]\w*  `
  - Punctuation: `(, ), {, }, ;, ,  `
  - Operator: `== | != | <= | >= | ++ | -- | += | -= | ... | [+\-*/%<>=!&|]  `
  - Constant: `\d+(?:\.\d+)?  ` (integers and floats)
  - Literal: `"..."` or `'...'  ` (strings with escapes)

### Implementation 
- **File:** `src/lexer.py`
- **Main function:** `lexer(code: str) -> (result, counts)`
  - `result` is a list of tuples `(type, lexeme)`.
  - `counts` is a dictionary with the number of occurrences per type (`{ "keywords": 3, "identifier": 5, ... }`).
- **CLI (current script behavior):**
  - Verify if we pass a file as an argument; if it is =1 no file is passed and it works with the default code; if it is 0 then it did receive a file.
  - If an argument is provided, the script treats `sys.argv[1]` as `filename`, validates that the file exists and that the extension is `.txt`. If any validation fails, the script prints an error and exits.
  - After reading the file, it calls `lexer(code)` and obtains `tokens, counts`.
  - Then it groups tokens by type with `defaultdict(list)` and presents:
    - `Grouped TOKENS:` → unique values per type (duplicates removed while preserving order).
    - `COUNTS:` → shows `counts` for each type.
    - `Total` → total number of tokens (length of the `tokens` list).

---

## Results
The lexical analyzer, with the current implementation, returns:
- The complete list of tokens `(type, lexeme)` in order of appearance.  
- A `counts` dictionary that indicates how many tokens of each type were found.  

The console output (CLI) shows grouped tokens (unique values per type), the count per type, and the total number of tokens.

---

## How to run
### Run without a file as argument (default)
 - If the file is in the same folder where you run the command, it is enough to indicate only the name and its extension. 
 - If the file is in another folder, you must pass the relative or absolute path.
 Use the following command
 ```
 $ python lexer.py <input_file>
 ```
### Run with a file as argument
 - If <input_file> is not provided, the script executes an embedded code snippet included for tests.
 ```bash
 $ python lexer.py
 ```
