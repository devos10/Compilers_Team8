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
- **Function detection** that identifies both function declarations/definitions and function calls.

---

## Problem formulation
The objective of the project is to design and implement a parser that:
- Reads an input file or code from stdin.
- Tokenizes the input using the lexical analyzer created previously.
- Analyzes the sequence of tokens, constructing an AST.
- Performs semantic checks (type compatibility, variable declaration, function usage, etc.).
- Detects and reports function declarations and calls.
- Reports errors with informative messages including line and column numbers.

The main entry point is the function `run(src: str)` (see `main.py`), which processes the source code, prints parsing and semantic results, or error messages.

---

## Motivation
The parser and semantic analyzer are essential for ensuring that the source code is not only lexically correct, but also syntactically and semantically valid. This guarantees that only well-formed and meaningful programs are accepted for further compilation or interpretation.

Understanding function declarations and calls is crucial for:
- Validating function signatures and parameters
- Ensuring functions are declared before being called
- Type checking function arguments and return values

---

## Objectives
- Correctly parse variable declarations, assignments, and expressions with support for multiple data types (`int`, `float`, `string`, `bool`, `char`, `double`, `void`).
- Parse and validate function declarations and function calls (e.g., `printf()`, `scanf()`, custom functions).
- Build an Abstract Syntax Tree (AST) representing the program structure.
- Perform semantic checks:
  - Type compatibility in assignments and expressions.
  - Variable declaration before use.
  - Function declaration before invocation.
  - Detection of redeclarations and type errors.
  - Parameter validation in function calls.
- Provide clear and informative error messages for both syntax and semantic errors with line and column information.

---

## Technologies
- **Language:** Python 3.8+
- **Libraries used and their use in the code:**
  - `re` → Regular expressions for token recognition in the lexer.
  - `dataclasses` → Definition of AST node classes and tokens.
  - `collections.defaultdict` → Grouping tokens by type for reporting.
  - `sys` → Reading command-line arguments and input files.
  - `os` → File existence and path handling.
  - `typing` → Type annotations for clarity and safety.

---

## Theoretical Framework & Design used
- **Lexeme:** sequence of characters that corresponds to the pattern of a token (e.g. `123`, `if`, `"hola"`, `printf`).  
- **Token:** Minimal unit recognized by the lexer (e.g., `int`, `+`, `x`, function names).
- **Lexer:** Groups characters into tokens and passes them to the parser. Now includes function detection.
- **Parser:** Analyzes the sequence of tokens and builds the AST, enforcing the grammar rules.
- **AST (Abstract Syntax Tree):** Hierarchical representation of the program structure.
- **Semantic Analysis:** Checks for type compatibility, variable declarations, function usage, and other context-sensitive rules.

**Design in the current code:**
The lexer is modular and can be replaced or adapted via `adapter_lexer.py`.
- The parser is implemented as a recursive-descent, **predictive LL(1)** parser (lookahead = 1); the grammar has been adapted so productions can be chosen with a single token of lookahead (left recursion removed and factoring applied where necessary).
- Predictive decisions rely on FIRST/FOLLOW reasoning (implemented implicitly in parsing routines via lookahead checks). Consider adding explicit FIRST/FOLLOW documentation for maintainability.
- The AST is constructed using Python `@dataclass` definitions for clarity, easy extension, and straightforward serialization/transformation.
- **Function analysis:** The lexer performs post-processing to identify function declarations (pattern: `type identifier (`) and function calls (pattern: `identifier (` not preceded by type keyword).
- Semantic actions run during parsing when immediate information is available (e.g., simple type checks and basic declaration/use checks).
- A final validation pass traverses the AST and symbol tables to perform global semantic checks (full type checking, symbol resolution, return/break validation, scope integrity, and warnings).
- Error reporting uses token objects that carry position `(line, column)` for precise error location.
- The current symbol table supports function tracking (declarations and calls) and can be extended to a scope stack for nested blocks.
- The architecture is modular (lexer ↔ parser ↔ AST ↔ semantic passes ↔ optimizer/generator) so each stage can be replaced or extended independently.
- `adapter_lexer.py` allows feeding different token sources (files, REPL, generated input) without changing parser/semantic code.
- The design favors extensibility: adding new language constructs requires adding grammar rules and corresponding `@dataclass` AST nodes with minimal cross-cutting changes.

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
  - Variable declaration (with or without initialization)
  - Function declaration/definition
  - Function calls (with arguments)
  - Assignment
  - Expressions (arithmetic, logical, relational, etc.)
  - Control structures (if, while, for)

### Features
- ✅ **Lexical Analysis:** Complete tokenization with error detection
- ✅ **Function Detection:** Automatic identification of function declarations and calls
- ✅ **Syntax Analysis:** LL(1) recursive descent parser
- ✅ **Semantic Analysis:** Type checking and symbol validation
- ✅ **Error Reporting:** Detailed error messages with line/column information
- ✅ **Comment Support:** Single-line (`//`) and multi-line (`/* */`) comments
- ✅ **String Literals:** Support for escaped characters in strings

### Implementation 
- **Main files:**
  - `main.py` — Core implementation of the parser, AST construction, and semantic analyzer.
  - `parser.py` — Runner / CLI wrapper that invokes `run(src: str)` from `main.py` (entry point for scripts or command-line use).
  - `Lexer/lexer.py` — Main lexer implementation responsible for token generation and function detection.
  - `Lexer/adapter_lexer.py` — Adapter that normalizes tokens from the customizable lexer to the parser's expected format.
  - `Lexer/user_lexer.py` — Customizable lexer implementation that can be modified or replaced according to user needs.

---

## Results
The parser and semantic analyzer, with the current implementation, return:
- Informative messages for successful parsing and semantic validation.
- Detailed function analysis showing declarations and calls.
- Error messages for syntax or semantic errors (type mismatches, undeclared variables, undefined functions, etc.).
- Token statistics and grouping for debugging purposes.

---

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

### Run lexer standalone
 - To test only the lexical analyzer:

```bash
python Lexer/lexer.py <input_file>
```

---

## Known Limitations & Future Work
- Constructs needing >1 token of lookahead or inherently ambiguous grammar require grammar refactoring or using a different parser strategy (LL(k), LR, or GLR).
- Improve recovery beyond simple panic-mode (more precise resynchronization and friendlier messages).
- Add AST/table visualization tools and richer error suggestions for developers and users.
