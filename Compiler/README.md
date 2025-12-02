<h1 align="center">
  <img src="https://github.com/user-attachments/assets/3abebde3-8ee0-40d0-ae38-82c52246b528" width="60" height="60" />
  Project: Complete Compiler
  <img src="https://github.com/user-attachments/assets/fe29e172-7262-4289-820a-1c08eecaa61b" width="60" height="60" />
</h1>

Repository corresponding to the Complete Compiler project within the Compilers course.  
This project implements a **full-fledged compiler** in Python that transforms C-like source code into executable Windows programs through a six-phase compilation pipeline.

---

## Team Information
| Full name                            | Student ID      |
|----------------------------------    |-----------------|
| Araiza Valdés Diego Antonio          | 423032833       |
| Arroyo Solano Victor Julian          | 423529834       |
| Jaramillo Rodríguez Leslie Citlalli  | 320318931       |
| Salas Hernández Camila Alexandra     | 320332825       |
| Velazquez Caudillo Osbaldo           | 320341704       |

| Field        | Detail              |
|--------------|---------------------|
| Course       | Compilers           |
| Project      | Complete Compiler   |
| Semester     | 2026-1              |

---

## 1. Introduction
A compiler is a program that translates source code written in a high-level language into machine code that can be executed directly by the computer. This project implements a complete compilation pipeline consisting of six distinct phases: lexical analysis, syntax analysis, semantic analysis, intermediate code generation, assembly code generation, and assembly & linking.

This compiler accepts C-like source code and produces Windows x86-64 executables (.exe files) ready to run on modern Windows systems.
### 1.1 Problem Formulation
The objective of the project is to design and implement a complete compiler that:
- Reads C-like source code from an input file.
- Performs lexical, syntactic, and semantic analysis (phases already implemented in previous projects).
- Generates intermediate representation (IR) using Three-Address Code.
- Translates IR to x86-64 assembly language (NASM syntax).
- Assembles and links the code to produce a Windows executable.
- Provides options to inspect intermediate representations (IR and ASM) for debugging.
- Reports errors at each compilation stage with informative messages.

The main entry point is `main.py`, which orchestrates all compilation phases through the function `compile_file()`.

### 1.2 Motivation 
Understanding the complete compilation process from source code to executable is fundamental to computer science and software engineering. This project demonstrates:

- How high-level abstractions are progressively lowered to machine code.
- The role of intermediate representations in simplifying code generation.
- The relationship between compiler phases and their interdependencies.
- Practical aspects of code generation for a real-world architecture (x86-64).
- Integration with external tools (NASM assembler and GCC linker).

By implementing all six phases, we gain deep insight into how modern compilers work and the engineering challenges involved in translating human-readable code to machine instructions.

### 1.3 Objectives 
- Generate **Three-Address Code (TAC)** intermediate representation from the AST.
- Translate TAC instructions to **x86-64 assembly language** (NASM syntax, Intel format).
- Produce syntactically correct assembly code following **Windows x64 calling convention**.
- Support all language features: variable declarations, assignments, arithmetic/logical operations, function declarations/calls, control flow (if/else, while, for), and return statements.
- Generate proper **function prologues and epilogues** with stack frame management.
- Handle **string literals** and data section generation.
- Assemble the generated code into **object files (.obj)** using NASM.
- Link object files into **Windows executables (.exe)** using GCC.
- Provide CLI options to inspect IR and assembly code for debugging.
- Report errors at each compilation stage with clear messages.

## 2. Theoretical Framework

### 2.1 Preliminary compilation phases

* **Lexical Analysis**

Lexical analysis, or scanning, partitions the raw source code into tokens, the atomic syntactic units of a programming language. A lexeme is the concrete sequence of characters that matches the pattern of a token (e.g., 123, if, "hola", printf). A token is the abstract category to which a lexeme belongs (e.g., INT, IDENTIFIER).

The lexer is responsible for grouping characters into lexemes and producing tokens that encode their type and location in the input. This process relies on regular expressions and deterministic finite automata to recognize valid lexical structures efficiently.

* **Syntax Analysis**

The parser consumes the token stream and organizes it according to the grammar of the language. During this phase, the syntax analyzer constructs an Abstract Syntax Tree (AST), a hierarchical representation of the program’s structural composition free of syntactic noise such as punctuation [1]. The parser enforces grammar rules and rejects programs that violate the language’s context-free syntax.

* **Semantic Analysis**

Semantic analysis verifies context-sensitive properties such as type compatibility, variable declaration, function usage, and correct application of operators. This phase ensures that only semantically meaningful programs proceed to further compilation. The semantic analyzer typically annotates the AST with type information and prepares it for translation into an intermediate form.

### 2.2 Intermediate Representation (IR)
After semantic validation, the AST is lowered into an intermediate representation (IR) that abstracts away from the source language syntax while preserving execution semantics. A well-designed IR is machine-independent, compact, and suitable for further analysis and translation [1].

The IR consists of node structures representing arithmetic operations, logical comparisons, variable references, assignments, function constructs, and control-flow structures. These nodes express program semantics in a uniform format that simplifies subsequent lowering into TAC.

### 2.3 Three-Address Code (TAC)
Three-Address Code (TAC) is a linear, low-level intermediate representation in which each instruction contains at most one operator and up to three operands. TAC breaks down complex expressions into simple steps, typically of the form:

```text
t1 = x + y
if t1 < 10 goto L1
```

This representation is favored in compiler design because it is easy to analyze, optimize, and translate to machine instructions.

TAC includes explicit temporaries, arithmetic operations, assignments, control-flow jumps, and labels. Structured constructs such as if-else and while loops are lowered into explicit branching instructions, following classical translation schemes described in compiler literature [1].

### 2.4 Control Flow and Labeling
High-level control structures are translated into explicit control-flow sequences composed of labels and jumps. For example, loops rely on labels marking entry and continuation points, conditional expressions resolve into comparison operations followed by conditional jumps, and blocks translate into linear instruction sequences. 

### 2.5 Code Generation
The code generation phase translates the intermediate representation —typically TAC or an equivalent IR—into the assembly language of the target architecture. Classical compilers produce low-level instructions such as x86-64 NASM, ARM, or RISC-V assembly, mapping abstract operations to concrete machine instructions while preserving the program’s semantics [1], [2]. This step requires selecting appropriate instruction sequences, managing temporary values, allocating registers or stack locations, and emitting explicit control-flow constructs.

During this phase, symbolic labels produced by earlier IR transformations are resolved, control-flow graphs are linearized, and the program is lowered into a sequential form suitable for assembly and later transformation by assemblers and linkers. Code generation thus serves as the bridge between machine-independent representations and executable machine code, completing the compiler’s backend pipeline.

### 2.6 Assembly and Linking
Finally, the generated assembly-like instructions are aggregated into a single output. In classical systems, assembly and linking resolve symbol addresses, merge code sections, and produce a binary executable. 

## **Design in the current code:** ##
- The lexer and parser are modular (implemented in previous projects).
- The IR generator uses *Visitor pattern* to traverse the AST with match-case dispatch.
- Three-Address Code uses *temporaries* (t0, t1, t2, ...) for intermediate results and *labels* (L0, L1, L2, ...) for control flow.
- The assembly generator translates IR instructions to x86-64 using *Visitor pattern* with match-case.
- Variables and temporaries stored in *stack frame* (RBP-relative addressing).
- *Windows x64 calling convention:* First 4 arguments in RCX, RDX, R8, R9; return value in RAX.
- *NASM* assembles .asm files to .obj object files (PE/COFF format).
- *GCC* links object files with C runtime library to produce .exe executables.
- Error handling at each phase with informative messages and installation instructions for external tools.

## 3. Desarrollo

## 4. Resultados

### 4.1 Test 1
The input code has no lexical, syntactic, or semantic errors, which allows the compiler to correctly generate the parse tree and produce the intermediate code. This intermediate code is then translated into assembly language and finally assembled and linked to obtain the executable.
<img width="1400" height="631" alt="image" src="https://github.com/user-attachments/assets/794062a9-e775-474a-9442-3713c8fe6014"/>

### 4.2 Test 2
The input code has no lexical, syntactic, or semantic errors, which allows the compiler to correctly generate the parse tree and produce the intermediate code. This intermediate code is then translated into assembly language and finally assembled and linked to obtain the executable.
<img width="500" height="782" alt="image" src="https://github.com/user-attachments/assets/d60be885-05e4-4b69-9a91-21f2c8850221"/>

### 4.3 Test 3
The input code has no lexical, syntactic, or semantic errors, which allows the compiler to correctly generate the parse tree and produce the intermediate code. This intermediate code is then translated into assembly language and finally assembled and linked to obtain the executable.
<img width="500" height="595" alt="image" src="https://github.com/user-attachments/assets/6dd2689a-f0d4-44fc-a441-718944af52c1" />

### 4.4 Test 4
The input code has no lexical, syntactic, or semantic errors, which allows the compiler to correctly generate the parse tree and produce the intermediate code. This intermediate code is then translated into assembly language and finally assembled and linked to obtain the executable.
<img width="500" height="757" alt="image" src="https://github.com/user-attachments/assets/2966920b-a369-4757-80b6-7bae9a922c7f" />

### 4.5 Test 5
The input code has no lexical, syntactic, or semantic errors, which allows the compiler to correctly generate the parse tree and produce the intermediate code. This intermediate code is then translated into assembly language and finally assembled and linked to obtain the executable.
<img width="500" height="749" alt="image" src="https://github.com/user-attachments/assets/51f5f0cb-9aac-48d4-a3a3-7c45a0fdc98c" />

### 4.6 Test 6
The submitted code encountered a lexical analysis error because it contains an unexpected '@' character; therefore it cannot proceed to the subsequent phases.

<img width="500" height="118" alt="image" src="https://github.com/user-attachments/assets/92b883e5-de55-4b7b-8596-bad26ca52ff3" />

### 4.7 Test 7
The input code successfully passed the lexical analysis stage but had a syntax error because a ‘;’ is missing at the end of a declaration.
<img width="500" height="184" alt="image" src="https://github.com/user-attachments/assets/f46466b9-6fda-49c0-9445-6457e7473f59" />

### 4.8 Test 8
The input code passed the first stage correctly, but in the second phase it has a semantic error because an undeclared variable is being used.
<img width="500" height="188" alt="image" src="https://github.com/user-attachments/assets/51089bcf-c771-4c90-bca7-3fb8d6006f29" />

### 4.9 Test 9
The input code passed the first stage correctly, but in the next phase a syntax error was detected because a ')' is missing at the end of the condition.

<img width="500" height="169" alt="image" src="https://github.com/user-attachments/assets/8496bd80-058b-4ff2-aaa8-b278916bbe50" />

## 5. Conclusion 

The development of the compiler demonstrates how theoretical principles in programming language processing integrate to systematically address the problem of translating high-level code into an executable representation. The interaction among the phases —lexical recognition, syntactic parsing, semantic analysis, intermediate code generation, and subsequent lowering into assembly— highlights the necessity of formal structures and well-defined models to ensure correctness and consistency throughout the compilation pipeline.

Additionally, the implementation confirms the relevance of using intermediate representations such as three-address code to simplify translation and maintain a clear flow of information across stages. Proper symbol management, semantic verification, and control-flow organization illustrate how theoretical concepts ensure that each transformation preserves the integrity of the original program.

Overall, the project reinforces that compiler theory not only provides the conceptual foundations for each phase, but also establishes a methodological framework that guarantees coherent transitions between abstraction levels. This demonstrates that a deep understanding of formal models, internal data structures, and translation strategies is essential for building reliable and efficient compilation systems, underscoring the significance of the studied concepts within the field of compilers.

## How to run

### Prerequisites
- **Python 3.10 or higher** (for match-case syntax)
- **NASM** (Netwide Assembler)
  - Download: https://www.nasm.us/
  - Add to PATH after installation
- **GCC (MinGW-w64)** for Windows
  - Download: https://winlibs.com/
  - Install and add to PATH

### Verify installations:
```bash
python --version    # Should be 3.10+
nasm -v             # Should show NASM version
gcc --version       # Should show GCC version
```

### Run with a file as argument (default)
If the file is in the same folder where you run the command, it is enough to indicate only the name and its extension.  
If the file is in another folder, you must pass the relative or absolute path.

**Basic compilation:**
```bash
python main.py programa.c
```
This produces `programa.exe`.

**Specify output name:**
```bash
python main.py programa.c -o salida
```
This produces `salida.exe`.

**Show intermediate representation (IR):**
```bash
python main.py programa.c --show-ir
```

**Show assembly code:**
```bash
python main.py programa.c --show-asm
```

**Generate assembly only (no linking):**
```bash
python main.py programa.c --asm-only
```
This produces `programa.asm` and stops before assembly/linking.

**Combine options:**
```bash
python main.py programa.c --show-ir --show-asm -o resultado
```

### Run the compiled executable:
After successful compilation:
```bash
.\programa.exe
```

---

## Known Limitations & Future Work

**Current limitations:**
- **No optimizations:** Generated code is not optimized (no dead code elimination, constant folding, register allocation, etc.).
- **Simple register usage:** Only RAX and RBX used for operations; no sophisticated register allocation.
- **Fixed stack allocation:** Functions reserve 64 bytes regardless of actual variable count.
- **No array support:** Arrays and pointers not yet implemented.
- **Limited control flow:** While `if`, `while`, `for` are supported in IR, complex nested structures may need testing.
- **No error recovery:** Compilation stops at first error in any phase.
- **Windows-only:** Currently targets Windows x64; Linux/Mac support would require different calling convention and linker.

**Future improvements:**
- **Code optimization:** Constant propagation, dead code elimination, common subexpression elimination.
- **Register allocation:** Use more registers to reduce memory accesses.
- **Dynamic stack allocation:** Calculate exact stack space needed per function.
- **Cross-platform support:** Generate assembly for Linux (System V ABI) and macOS.
- **Advanced features:** Arrays, pointers, structs, global variables.
- **Better error recovery:** Continue compilation after errors to report multiple issues.
- **Debugging support:** Generate debug symbols for GDB/LLDB.



## 6. References 
1. [1] A. V. Aho, M. S. Lam, R. Sethi, and J. D. Ullman, *Compilers: Principles, Techniques, and Tools*, 2nd ed. Boston, MA, USA: Addison-Wesley, 2006.
2. [2] S. S. Muchnick, *Advanced Compiler Design and Implementation*. San Francisco, CA, USA: Morgan Kaufmann, 1997.
