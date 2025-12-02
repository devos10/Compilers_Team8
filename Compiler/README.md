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

## 3. Development

### 3.1 Design Considerations
- **Grammar:** Same as parser project (keywords, identifiers, operators, constants, literals, punctuation).
- **Compilation Flow:**
```
┌─────────────────┐
│  Código fuente  │  int main() { return 42; }
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  user_lexer.py  │  Tokenización
└────────┬────────┘
         │ [('keywords','int'), ('identifier','main'), ...]
         ▼
┌─────────────────┐
│adapter_lexer.py │  Conversión a Token objects
└────────┬────────┘
         │ [Token('INT','int'), Token('ID','main'), ...]
         ▼
┌─────────────────┐
│    parser.py    │  Parser + AST
└────────┬────────┘
         │ Program([FuncDecl('main', [], Return(Num(42)))])
         ▼
┌─────────────────┐
│    parser.py    │  Análisis Semántico
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ir_generator.py  │  Generación IR (TAC)
└────────┬────────┘
         │ [IRFuncBegin('main'), IRReturn('42'), IRFuncEnd('main')]
         ▼
┌─────────────────┐
│asm_generator.py │  Generación Ensamblador
└────────┬────────┘
         │ bits 64 / section .text / main: / push rbp / ...
         ▼
┌─────────────────┐
│  NASM → GCC     │  Ensamblado y Enlazado
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ejecutable.exe │
└─────────────────┘
```

### 3.2 Features
- ✅ **Lexical Analysis:** Complete tokenization (from previous project)
- ✅ **Syntax Analysis:** LL(1) recursive descent parser (from previous project)
- ✅ **Semantic Analysis:** Type checking, symbol validation (from previous project)
- ✅ **Intermediate Code Generation:** Three-Address Code with temporaries and labels
- ✅ **Assembly Code Generation:** x86-64 NASM with Windows x64 calling convention
- ✅ **Assembly & Linking:** NASM assembler + GCC linker to produce executables
- ✅ **Error Reporting:** Clear error messages at each compilation phase
- ✅ **CLI Options:** Inspect IR and assembly code, control compilation stages

### 3.3 Implementation 
- **Main files:**
  - `main.py` — Orchestrates all compilation phases, CLI interface
  - `ir_generator.py` — Converts AST to Three-Address Code 
  - `asm_generator.py` — Converts TAC to x86-64 NASM assembly 
  - `parser.py` — Syntax and semantic analysis (from previous project)
  - `lexer/adapter_lexer.py` — Lexical analysis adapter (from previous project)

### 3.4 IR Instruction Types
The IR generator constructs Three-Address Code using the following instruction types:
- `IRLabel` — Label definition for control flow
- `IRAssign` — Simple assignment
- `IRBinOp` — Binary operation (arithmetic, logical, relational)
- `IRUnaryOp` — Unary operation
- `IRGoto` — Unconditional jump
- `IRIfFalseGoto` — Conditional jump (if false)
- `IRCall` — Function call with arguments
- `IRParam` — Parameter passing marker
- `IRReturn` — Return statement
- `IRFuncBegin` — Function prologue marker
- `IRFuncEnd` — Function epilogue marker

### 3.5 Intermediate Code Generation

So, in this part of the project, we basically took the Abstract Syntax Tree (AST) we built earlier and turned it into something simpler called three-address code. Think of it as a middle step between understanding what the code means and actually running it on a computer.

The whole point of three-address code is pretty straightforward: no instruction can have more than three things in it. This might sound limiting, but it actually makes our lives way easier later on. Like, if you write something complicated like `x = a + b * c`, we just split it up: first do `t1 = b * c`, then `x = a + t1`. Nice and simple.

To make this work, we built a system that walks through the entire AST and spits out these intermediate instructions as it goes. We use temporary variables with boring names like `t0`, `t1`, `t2`, and so on to hold results while we're calculating stuff. We also create labels (`L0`, `L1`, `L2`, etc.) that basically act like bookmarks for when we need to jump around in control structures.

When we hit arithmetic or logical expressions, we just turn them into a bunch of simple binary operations. Every operation from the AST gets its own instruction that saves the result in a fresh temporary variable. Then other instructions can grab that value when they need it.

Control structures needed some extra attention. For `if-else` statements, we create a sequence where we check the condition first, jump to wherever we need to go based on whether it's true or false, run that block of code, and then jump to the end. With `while` loops, we set up a starting point, check the condition there, bail out to the end if it's false, run the loop body, and jump back to the start.

`for` loops are kind of cool because we just break them down into their basic parts: run the initialization once, set up a label at the start, check the condition, execute the body, do the increment step, and loop back around.

Function calls turned into a series of instructions where we list out each argument, then call the function, and maybe save whatever it returns if we need it.

Oh, and string handling is kind of neat. Whenever we find a string literal in the code, we give it a unique ID like `str0`, `str1`, whatever. These IDs show up in our intermediate code and eventually become labels in the assembly code.

### 3.6 Assembly Code Generation

This is where things get real. We take those intermediate instructions and convert them into actual x86-64 assembly code that can run on Windows. We have to follow Windows' rules, manage the CPU registers properly, and make sure everything actually works.

We just go through each intermediate instruction one by one and write out the matching assembly code. We're using NASM with Intel syntax because it's pretty readable and works well for what we need.

#### Handling Variables and Memory

One thing we had to figure out was where to put all the variables. We keep track of where each variable lives on the stack by giving it an offset from the `RBP` register. As we find new variables, we just bump the offset and remember where everything is. This lets us write stuff like `QWORD [rbp-8]` or `QWORD [rbp-16]` and actually point to the right place.

#### Following the Rules

Windows x64 has specific rules about how functions should work, and we had to follow them exactly. The first four arguments go in registers `RCX`, `RDX`, `R8`, and `R9`. If you had more than four (which our compiler doesn't really worry about), they'd go on the stack. There's also this weird "shadow space" thing where you have to reserve 32 bytes on the stack before calling a function, even if the function doesn't use it.

#### How the Code Looks

The assembly code we generate has a few sections. There's a data section (`.data`) where we put all the strings we found, each with its own label. Then there's the text section (`.text`) with all the actual code, including references to external functions like `printf` and `scanf`, plus all the functions from the program.

Every function starts the same way: save the old `RBP` value, set `RBP` to point to the current stack position, and make room for local variables. At the end, we clean everything up by restoring the stack and returning.

#### Turning Instructions into Assembly

Simple assignments just become `mov` instructions that shuffle values around between registers and memory. Numbers get loaded straight in, but strings need `lea` (Load Effective Address) to grab their address from the label we created earlier.

For binary operations, we load both operands into `RAX` and `RBX`, do the operation (`add`, `sub`, `imul`, `idiv`, whatever), and save the result. Comparisons are slightly more involved - we use `cmp` to compare things, then `setcc` to set a byte to 0 or 1 depending on the result, and extend that to 64 bits with `movzx`.

Jumps are pretty straightforward. Conditional jumps use `test` to check if something is zero, then `jnz` or `jz` to jump based on that. Unconditional jumps are just `jmp`.

Function calls are a bit of a production. Reserve the shadow space, load arguments into registers, do the `call`, clean up the shadow space, and grab the return value from `RAX` if we need it.

#### Making It Better

We threw in a few basic optimizations. Like, if we see a literal number, we just load it directly instead of doing something fancy. We also try to reuse `RAX` when we can to avoid moving stuff around in memory unnecessarily.

We're pretty conservative with registers - mostly sticking to `RAX`, `RBX`, `RCX`, `RDX`, `R8`, and `R9`. This keeps things simple and leaves room for improvements later.

### 3.7 Putting It All Together

The main module is basically the conductor of the whole orchestra. It runs everything from start to finish and gives you a command-line interface to control what happens.

It starts by reading your source code file, then runs through each phase: lexical analysis to break it into tokens, parsing to build and check the AST, intermediate code generation, assembly translation, and finally assembling and linking to create the executable.

Each step tells you what's happening. If something goes wrong, everything stops right there and you get an error message explaining what broke. This way you catch problems early instead of having them pile up.

We added some flags so you can peek at what's happening inside. Use `--show-ir` to see the intermediate code, `--show-asm` to check out the assembly, or `--asm-only` if you just want the assembly file without going all the way to an executable.

For the assembly step, we automatically call NASM to turn the assembly into object code. If you don't have NASM installed, the compiler will tell you where to get it. Same deal with GCC for linking - it glues everything together with the system libraries to make the final executable.

We tried to handle errors well. Whether it's a missing file, bad characters, syntax mistakes, type errors, or problems during assembly or linking, you'll get a message that actually helps you figure out what went wrong.

The nice thing about how we built this is that it's easy to add new stuff later. Want to add optimization or support for different architectures? Just slot in a new phase and you're good to go.

### 3.8 Usage
```bash
python main.py <source_file> [options]
```

#### Options

- `--show-ir` - Display the generated intermediate code
- `--show-asm` - Display the generated assembly code
- `--asm-only` - Generate only the assembly file without assembling

#### Requirements

- Python 3.x
- NASM (Netwide Assembler)
- GCC (for linking)

### 3.9 Example
```bash
# Compile and run a program
python main.py program.txt

# View intermediate code
python main.py program.txt --show-ir

# View assembly code
python main.py program.txt --show-asm

# Generate assembly only
python main.py program.txt --asm-only
```


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

## 6. Known Limitations & Future Work

**6.1 Current limitations:**
- **No optimizations:** Generated code is not optimized (no dead code elimination, constant folding, register allocation, etc.).
- **Simple register usage:** Only RAX and RBX used for operations; no sophisticated register allocation.
- **Fixed stack allocation:** Functions reserve 64 bytes regardless of actual variable count.
- **No array support:** Arrays and pointers not yet implemented.
- **Limited control flow:** While `if`, `while`, `for` are supported in IR, complex nested structures may need testing.
- **No error recovery:** Compilation stops at first error in any phase.
- **Windows-only:** Currently targets Windows x64; Linux/Mac support would require different calling convention and linker.

**6.2 Future improvements:**
- **Code optimization:** Constant propagation, dead code elimination, common subexpression elimination.
- **Register allocation:** Use more registers to reduce memory accesses.
- **Dynamic stack allocation:** Calculate exact stack space needed per function.
- **Cross-platform support:** Generate assembly for Linux (System V ABI) and macOS.
- **Advanced features:** Arrays, pointers, structs, global variables.
- **Better error recovery:** Continue compilation after errors to report multiple issues.
- **Debugging support:** Generate debug symbols for GDB/LLDB.

## 7. How to run
### 7.1 Prerequisites
- **Python 3.10 or higher** (for match-case syntax)
- **NASM** (Netwide Assembler)
  - Download: https://www.nasm.us/
  - Add to PATH after installation
- **GCC (MinGW-w64)** for Windows
  - Download: https://winlibs.com/
  - Install and add to PATH

### 7.2 Verify installations:
```bash
python --version    # Should be 3.10+
nasm -v             # Should show NASM version
gcc --version       # Should show GCC version
```

### 7.3 Run with a file as argument (default)
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
## 8. References 
1. [1] A. V. Aho, M. S. Lam, R. Sethi, and J. D. Ullman, *Compilers: Principles, Techniques, and Tools*, 2nd ed. Boston, MA, USA: Addison-Wesley, 2006.
2. [2] S. S. Muchnick, *Advanced Compiler Design and Implementation*. San Francisco, CA, USA: Morgan Kaufmann, 1997.
