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
### 1.1 Problem Statement
A compiler is a program that translates source code written in a high-level language into machine-executable instructions. The problem addressed in this project is the design and implementation of a complete compiler capable of processing C-like source code and generating Windows x86-64 executable files. This requires building a full compilation pipeline that includes lexical analysis, syntax analysis, semantic analysis, intermediate code generation, assembly code generation, and finally assembly and linking to produce a runnable program.

### 1.2 Motivation 
Developing a compiler provides a practical way to apply the theoretical concepts studied in the course, such as formal languages, parsing techniques, and program translation. Implementing each phase of the compilation process makes it possible to understand how source code is transformed from a human-readable form into machine code. This project strengthens the understanding of programming language design, improves problem-solving and software engineering skills, and offers direct experience with the internal workings of compilers and modern computing systems.

### 1.3 Objectives 
- To implement a functional compiler capable of translating C-like source code into Windows x86-64 executable files (.exe).

- To develop all required phases of the compilation process: lexical analysis, syntax analysis, semantic analysis, intermediate code generation, assembly code generation, and assembly/linking.

- To apply theoretical concepts from the course through the construction of a complete, well-structured compilation system.

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
<img width="1444" height="631" alt="image" src="https://github.com/user-attachments/assets/794062a9-e775-474a-9442-3713c8fe6014" />

### 4.2 Test 2
<img width="631" height="782" alt="image" src="https://github.com/user-attachments/assets/d60be885-05e4-4b69-9a91-21f2c8850221" />

### 4.3 Test 3
<img width="636" height="595" alt="image" src="https://github.com/user-attachments/assets/6dd2689a-f0d4-44fc-a441-718944af52c1" />

### 4.4 Test 4
<img width="603" height="757" alt="image" src="https://github.com/user-attachments/assets/2966920b-a369-4757-80b6-7bae9a922c7f" />

### 4.5 Test 5
<img width="564" height="749" alt="image" src="https://github.com/user-attachments/assets/51f5f0cb-9aac-48d4-a3a3-7c45a0fdc98c" />

### 4.6 Test 6
<img width="896" height="118" alt="image" src="https://github.com/user-attachments/assets/92b883e5-de55-4b7b-8596-bad26ca52ff3" />

### 4.7 Test 7
<img width="789" height="184" alt="image" src="https://github.com/user-attachments/assets/f46466b9-6fda-49c0-9445-6457e7473f59" />

### 4.8 Test 8
<img width="637" height="188" alt="image" src="https://github.com/user-attachments/assets/51089bcf-c771-4c90-bca7-3fb8d6006f29" />

### 4.9 Test 9
<img width="826" height="169" alt="image" src="https://github.com/user-attachments/assets/8496bd80-058b-4ff2-aaa8-b278916bbe50" />










## 5. Conclusion 

The development of the compiler demonstrates how theoretical principles in programming language processing integrate to systematically address the problem of translating high-level code into an executable representation. The interaction among the phases —lexical recognition, syntactic parsing, semantic analysis, intermediate code generation, and subsequent lowering into assembly— highlights the necessity of formal structures and well-defined models to ensure correctness and consistency throughout the compilation pipeline.

Additionally, the implementation confirms the relevance of using intermediate representations such as three-address code to simplify translation and maintain a clear flow of information across stages. Proper symbol management, semantic verification, and control-flow organization illustrate how theoretical concepts ensure that each transformation preserves the integrity of the original program.

Overall, the project reinforces that compiler theory not only provides the conceptual foundations for each phase, but also establishes a methodological framework that guarantees coherent transitions between abstraction levels. This demonstrates that a deep understanding of formal models, internal data structures, and translation strategies is essential for building reliable and efficient compilation systems, underscoring the significance of the studied concepts within the field of compilers.

## 6. References 
1. [1] A. V. Aho, M. S. Lam, R. Sethi, and J. D. Ullman, *Compilers: Principles, Techniques, and Tools*, 2nd ed. Boston, MA, USA: Addison-Wesley, 2006.
2. [2] S. S. Muchnick, *Advanced Compiler Design and Implementation*. San Francisco, CA, USA: Morgan Kaufmann, 1997.
