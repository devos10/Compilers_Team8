<h1 align="center">
  <img src="https://github.com/user-attachments/assets/3abebde3-8ee0-40d0-ae38-82c52246b528" width="60" height="60" />
  Project: Parser & SDT
  <img src="https://github.com/user-attachments/assets/fe29e172-7262-4289-820a-1c08eecaa61b" width="60" height="60" />
</h1>

Repository corresponding to the Syntax Analysis project within the Compilers course.  
This project implements a **Recursive Descent Parser** and a **Lexer** in Python, supporting multiple data types, semantic checks, and function declarations/calls.

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
| Project      | Parser & SDT   |
| Semester     | 2026-1         |

---

## Introduction
Syntax analysis is the second phase in the construction of a compiler, following lexical analysis.  
The *Parser* receives a sequence of tokens from the lexer and builds an **Abstract Syntax Tree (AST)**, verifying the syntactic structure and performing semantic checks (such as type checking and variable declarations).

This project includes:
- A **Lexer** that tokenizes the input source code, including support for function declarations and calls.
- A **Recursive Descent Parser** that constructs the AST and performs semantic analysis (type checking, variable declaration, function analysis, etc.).
- **Two-pass function detection** that first collects all function declarations, then validates function calls and their arguments.

---

## Problem formulation
The objective of the project is to design and implement a parser that:
- Reads an input file or code from stdin.
- Tokenizes the input using the lexical analyzer.
- Analyzes the sequence of tokens, constructing an AST.
- Performs semantic checks (type compatibility, variable declaration, function usage, argument validation, etc.).
- Validates function declarations and calls with proper type checking.
- Reports errors with informative messages.

The main entry point is the function `run(src: str)` (see `main.py`), which processes the source code and prints parsing and semantic results, or error messages.

---

## Motivation
The parser and semantic analyzer are essential for ensuring that the source code is not only lexically correct, but also syntactically and semantically valid. This guarantees that only well-formed and meaningful programs are accepted for further compilation or interpretation.

Understanding function declarations and calls is crucial for:
- Validating function signatures and parameters
- Ensuring functions are declared before being called
- Type checking function arguments and return values
- Special handling of variadic functions like `printf()` and `scanf()`

---

## Objectives
- Correctly parse variable declarations, assignments, and expressions with support for multiple data types (`int`, `float`, `string`, `bool`).
- Parse and validate function declarations and function calls (including builtin functions like `printf()`, `scanf()`).
- Build an Abstract Syntax Tree (AST) representing the program structure.
- Perform semantic checks:
  - Type compatibility in assignments and expressions.
  - Variable declaration before use.
  - Function declaration before invocation (two-pass approach).
  - Detection of redeclarations and type errors.
  - Parameter count and type validation in function calls.
  - Return type validation.
- Provide clear and informative error messages for both syntax and semantic errors.

---

## Technologies
- **Language:** Python 3.8+
- **Libraries used and their use in the code:**
  - `dataclasses` → Definition of AST node classes and tokens.
  - `typing` → Type annotations for clarity and safety.
  - `re` → Regular expressions for token recognition in the lexer (in `adapter_lexer.py`).

---

## Theoretical Framework & Design used
- **Lexeme:** sequence of characters that corresponds to the pattern of a token (e.g. `123`, `if`, `"hola"`, `printf`).  
- **Token:** Minimal unit recognized by the lexer (e.g., `int`, `+`, `x`, function names).
- **Lexer:** Groups characters into tokens and passes them to the parser.
- **Parser:** Analyzes the sequence of tokens and builds the AST, enforcing the grammar rules.
- **AST (Abstract Syntax Tree):** Hierarchical representation of the program structure.
- **Semantic Analysis:** Checks for type compatibility, variable declarations, function usage, and other context-sensitive rules.

**Design in the current code:**
- The lexer is modular and can be replaced or adapted via `adapter_lexer.py`.
- The parser is implemented as a recursive-descent, **predictive LL(1)** parser (lookahead = 1).
- The grammar has been adapted so productions can be chosen with a single token of lookahead (left recursion removed and factoring applied where necessary).
- The AST is constructed using Python `@dataclass` definitions for clarity and easy extension.
- **Two-pass parsing:**
  1. **First pass:** Collects all function declarations before parsing function bodies.
  2. **Second pass:** Full parsing with function call validation and semantic checks.
- **Symbol table management:**
  - Global `functions` table: stores function signatures `(return_type, params, is_variadic)`.
  - Local `symbols` table: cleared for each function scope, stores local variables and parameters.
- **Special function handling:**
  - `printf()` and `scanf()` are treated as builtin variadic functions with custom validation rules.
  - `printf()` requires at least 1 argument; additional arguments must be declared variables.
  - `scanf()` requires at least 1 argument; all arguments must be declared variables.
- **Type checking:**
  - Performed during parsing via the `typeof()` method.
  - Supports implicit `int` to `float` conversion.
  - Validates binary operations, unary operations, and comparisons.
- **Error handling:**
  - `SyntaxError_` for parsing errors (unexpected tokens, missing delimiters, etc.).
  - `SemanticError` for semantic errors (undeclared variables/functions, type mismatches, etc.).
- The architecture is modular (lexer ↔ parser ↔ AST ↔ semantic checks) so each stage can be extended independently.

---

## Development

### Design Considerations
- **Grammar:**
  - **Keywords:** `int | float | for | while | if | else | return | void | char | double | long | short | unsigned | signed | struct | typedef`
  - **Identifier:** `[A-Za-z_]\w*` (includes variable names and function names)
  - **Punctuation:** `., (, ), {, }, ;, ,`
  - **Operator:** `== | != | <= | >= | \+\+ | -- | \+= | -= | \*= | /= | %= | && | \|\| | [+\-*/%<>=!&|]`
  - **Constant:** `\d+(?:\.\d+)?` (integers and floats)
  - **Literal:** `"([^"\\]|\\.)*" | \'([^\'\\]|\\.)*\'` (strings with escapes)

- **Statements:**
  - Variable declaration (with or without initialization): `int x;` or `int x = 5;`
  - Function declaration/definition: `int add(int a, int b) { ... }`
  - Function calls (with arguments): `printf("Hello");` or `add(3, 5);`
  - Assignment: `x = 10;`
  - Expressions (arithmetic, logical, relational): `x + y`, `a && b`, `x < 5`
  - Return statements: `return x;`
  - Code blocks: `{ ... }`

### Features
- ✅ **Lexical Analysis:** Complete tokenization via `adapter_lexer.py`
- ✅ **Two-pass Function Analysis:** First pass collects declarations, second pass validates calls
- ✅ **Syntax Analysis:** LL(1) recursive descent parser
- ✅ **Semantic Analysis:** Type checking, symbol validation, and function argument validation
- ✅ **Error Reporting:** Clear error messages indicating the type of error
- ✅ **Builtin Functions:** Special handling for `printf()` and `scanf()`
- ✅ **Type System:** Support for `int`, `float`, `string`, `bool` with implicit conversions
- ✅ **Scope Management:** Proper function-local scopes with parameter handling

### Implementation 
- **Main files:**
  - `main.py` — Core implementation of the parser, AST construction, and semantic analyzer.
  - `parser.py` — Runner / CLI wrapper that invokes `run(src: str)` from `main.py` (entry point for scripts or command-line use).
  - `lexer/adapter_lexer.py` — Adapter that normalizes tokens to the parser's expected format, using `tokenize_std` as the main interface.

### AST Node Types
The parser constructs an AST using the following node types:
- `Program` — Root node containing all top-level items
- `FuncDecl` — Function declaration with return type, name, parameters, and body
- `Block` — Code block containing statements
- `Return` — Return statement with optional expression
- `FuncCall` — Function call with name and arguments
- `ExprStmt` — Expression as a statement
- `Decl` — Variable declaration with optional initialization
- `Assign` — Variable assignment
- `BinOp` — Binary operation (arithmetic, logical, relational)
- `UnaryOp` — Unary operation (+, -)
- `Var` — Variable reference
- `Num` — Numeric literal
- `String` — String literal

---

## Results
The parser and semantic analyzer, with the current implementation, return:
- **Successful parsing:**
  ```
  Parsing Success!
  SDT Verified!
  ```
- **Syntax errors:**
  ```
  Parsing error...
  <error message with token information>
  ```
- **Semantic errors:**
  ```
  Parsing Success!
  SDT error...
  <error message describing the semantic issue>
  ```
## How to run

### Prerequisites
- Python 3.8 or higher

### Run with a file as argument
 - If the file is in the same folder where you run the command, it is enough to indicate only the name and its extension. 
 - If the file is in another folder, you must pass the relative or absolute path.

```bash
python parser.py <input_file>
```

### Run without a file as argument (Interactive mode)
 - If `<input_file>` is not provided, you can enter the code directly in the terminal (finish with Ctrl+D on Unix/Mac or Ctrl+Z on Windows):

```bash
python parser.py
```
---

## Known Limitations & Future Work
- **No nested scopes:** Currently only supports function-level scopes, not block-level scopes within functions.
- **Limited control flow:** `if`, `while`, `for` structures are not yet fully implemented in the parser.
- **No arrays or pointers:** Complex data types not yet supported.
- **Return validation:** Not all code paths are checked for return statements.
- **Error recovery:** Basic error handling without sophisticated recovery strategies.
