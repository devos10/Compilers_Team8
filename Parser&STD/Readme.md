<h1 align="center">
  <img src="https://github.com/user-attachments/assets/3abebde3-8ee0-40d0-ae38-82c52246b528" width="60" height="60" />
  Project: Parser & SDT
  <img src="https://github.com/user-attachments/assets/fe29e172-7262-4289-820a-1c08eecaa61b" width="60" height="60" />
</h1>

Repository corresponding to the Syntax Analysis project within the Compilers course.  
This project implements a **Recursive Descent Parser** and a **Lexer** in Python, supporting multiple data types and semantic checks.

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
- A **Lexer** that tokenizes the input source code.
- A **Recursive Descent Parser** that constructs the AST and performs semantic analysis (type checking, variable declaration, etc.).

---

## Problem formulation
The objective of the project is to design and implement a parser that:
- Reads an input file or code from stdin.
- Tokenizes the input using the lexical analyzer created previously.
- Analyzes the sequence of tokens, constructing an AST.
- Performs semantic checks (type compatibility, variable declaration, etc.).
- Reports errors with informative messages.

The main entry point is the function `run(src: str)` (see `main.py`), which processes the source code, prints parsing and semantic results, or error messages.

---

## Motivation
The parser and semantic analyzer are essential for ensuring that the source code is not only lexically correct, but also syntactically and semantically valid. This guarantees that only well-formed and meaningful programs are accepted for further compilation or interpretation.

---

## Objectives
- Correctly parse variable declarations, assignments, and expressions with support for multiple data types (`int`, `float`, `string`, `bool`).
- Build an Abstract Syntax Tree (AST) representing the program structure.
- Perform semantic checks:
  - Type compatibility in assignments and expressions.
  - Variable declaration before use.
  - Detection of redeclarations and type errors.
- Provide clear and informative error messages for both syntax and semantic errors.

---

## Technologies
- **Language:** Python
- **Libraries used and their use in the code:**
  - `re` → Regular expressions for token recognition in the lexer.
  - `dataclasses` → Definition of AST node classes and tokens.
  - `collections.defaultdict` → Grouping tokens by type for reporting.
  - `sys` → Reading command-line arguments and input files.
  - `os` → File existence and path handling.
  - `typing` → Type annotations for clarity and safety.

---

## Theoretical Framework & Design used
- **Lexeme:** sequence of characters that corresponds to the pattern of a token (e.g. `123`, `if`, `"hola"`).  
- **Token:** Minimal unit recognized by the lexer (e.g., `int`, `+`, `x`).
- **Lexer:** Groups characters into tokens and passes them to the parser.
- **Parser:** Analyzes the sequence of tokens and builds the AST, enforcing the grammar rules.
- **AST (Abstract Syntax Tree):** Hierarchical representation of the program structure.
- **Semantic Analysis:** Checks for type compatibility, variable declarations, and other context-sensitive rules.

**Design in the current code:**
The lexer is modular and can be replaced or adapted via `adapter_lexer.py`.
- The parser is implemented as a recursive-descent, **predictive LL(1)** parser (lookahead = 1); the grammar has been adapted so productions can be chosen with a single token of lookahead (left recursion removed and factoring applied where necessary).
- Predictive decisions rely on FIRST/FOLLOW reasoning (implemented implicitly in parsing routines via lookahead checks). Consider adding explicit FIRST/FOLLOW documentation for maintainability.
- The AST is constructed using Python `@dataclass` definitions for clarity, easy extension, and straightforward serialization/transformation.
- Semantic actions run during parsing when immediate information is available (e.g., simple type checks and basic declaration/use checks).
- A final validation pass traverses the AST and symbol tables to perform global semantic checks (full type checking, symbol resolution, return/break validation, scope integrity, and warnings).
- Error reporting uses token objects that carry position `(line, column)`. **Note:** currently parser/semantic exceptions do not always include position in their messages — recommended fix included in the repository.
- Basic panic-mode recovery is recommended to avoid cascading errors; currently parse stops on the first syntax error — recommended snippet included.
- The current symbol table is flat (single dict). For block/function scopes, convert to a scope stack (`enter_scope`/`exit_scope`) to support correct identifier resolution and attributes (type, mutability, parameters).
- The architecture is modular (lexer ↔ parser ↔ AST ↔ semantic passes ↔ optimizer/generator) so each stage can be replaced or extended independently.
- `adapter_lexer.py` allows feeding different token sources (files, REPL, generated input) without changing parser/semantic code.
- The design favors extensibility: adding new language constructs requires adding grammar rules and corresponding `@dataclass` AST nodes with minimal cross-cutting changes.
- Testing is recommended: add unit tests for the lexer tokens, parser productions (valid/invalid cases), AST shape, and semantic checks (error and success cases), plus regression tests when grammar changes.
- Performance notes: as an LL(1) recursive-descent parser with no backtracking, parsing is linear in input size; additional cost depends on semantic-pass complexity and symbol-table operations.
- Known limitations & future work:
  - Constructs needing >1 token of lookahead or inherently ambiguous grammar require grammar refactoring or using a different parser strategy (LL(k), LR, or GLR).
  - Improve recovery beyond simple panic-mode (more precise resynchronization and friendlier messages).
  - Add AST/table visualization tools and richer error suggestions for developers and users.

---

## Development

### Design Considerations
- **Grammar:**
  - Keywords: `int | float | for | while | if | else | return  `
  - Identifier: `[A-Za-z_]\w*  `
  - Punctuation: `., (, ), {, }, ;, ,  `
  - Operator: `== | != | <= | >= | \+\+ | -- | \+= | -= | \*= | /= | %= | && | \|\| | [+\-*/%<>=!&|]  `
  - Constant: `\d+(?:\.\d+)?  ` (integers and floats)
  - Literal: `"([^"\\]|\\.)*" | \'([^\'\\]|\\.)*\' ` (strings with escapes)

- **Statements:**
  - Variable declaration (with or without initialization)
  - Assignment
  - Expressions (arithmetic, logical, relational, etc.)


### Implementation 
- **Main files:**
  - `main.py` — Core implementation of the parser, AST construction, and semantic analyzer.
  - `parser.py` — Runner / CLI wrapper that invokes `run(src: str)` from `main.py` (entry point for scripts or command-line use).
  - `Lexer/lexer.py` — Main lexer implementation responsible for token generation.
  - `Lexer/adapter_lexer.py` — Adapter that normalizes tokens from the customizable lexer to the parser’s expected format.
  - `Lexer/user_lexer.py` — Customizable lexer implementation that can be modified or replaced according to user needs.

---

## Results
The parser and semantic analyzer, with the current implementation, return:
- Informative messages for successful parsing and semantic validation.
- Error messages for syntax or semantic errors (type mismatches, undeclared variables, etc.).

---

## How to run
### Run with a file as argument (default)
 - If the file is in the same folder where you run the command, it is enough to indicate only the name and its extension. 
 - If the file is in another folder, you must pass the relative or absolute path.
 Use the following command
 ```bash
 $ python parser.py <input_file>
 ```
### Run without a file as argument
 - If <input_file> is not provided, you must enter the text on the command line.
 ```bash
 $ parse parser.py
 ```
