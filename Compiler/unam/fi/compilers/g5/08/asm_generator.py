"""
asm_generator.py - Generador de Código Ensamblador x86-64 (NASM)

Este módulo convierte las instrucciones IR (Three-Address Code) 
en código ensamblador x86-64 para arquitectura Windows.

Convenciones:
- Sintaxis: NASM (Intel)
- Arquitectura: x86-64 (64 bits)
- Sistema: Windows x64 calling convention
- Registros de parámetros: RCX, RDX, R8, R9 (primeros 4 args)
"""

from typing import List, Dict, Optional
from ir_generator import (
    IRInstr, IRLabel, IRAssign, IRBinOp, IRUnaryOp,
    IRGoto, IRIfGoto, IRIfFalseGoto, IRCall, IRReturn,
    IRFuncBegin, IRFuncEnd, IRParam
)


class AsmGenerator:
    """Genera código ensamblador x86-64 desde IR"""
    
    def __init__(self, instructions: List[IRInstr], string_literals: Dict[str, str]):
        self.instructions = instructions
        self.string_literals = string_literals
        self.output: List[str] = []
        self.var_offset: Dict[str, int] = {}  # Variable -> offset desde RBP
        self.current_offset = 0
        self.param_regs = ['rcx', 'rdx', 'r8', 'r9']  # Windows x64 calling convention
        self.in_function = False
        self.function_name = ""
    
    def emit(self, line: str):
        """Emite una línea de código ensamblador"""
        self.output.append(line)
    
    def generate(self) -> str:
        """Genera el código ensamblador completo"""
        self.emit_header()
        self.emit_data_section()
        self.emit_code_section()
        return "\n".join(self.output)
    
    def emit_header(self):
        """Emite el encabezado del archivo ASM"""
        self.emit("; Generado por el compilador")
        self.emit("; Arquitectura: x86-64 (64 bits)")
        self.emit("; Sintaxis: NASM (Intel)")
        self.emit("")
        self.emit("bits 64")
        self.emit("default rel")
        self.emit("")
    
    def emit_data_section(self):
        """Emite la sección de datos (literales de cadena)"""
        if not self.string_literals:
            return
        
        self.emit("section .data")
        for value, name in self.string_literals.items():
            # Escapar caracteres especiales
            escaped = value.replace('\\n', '", 10, "').replace('\\t', '", 9, "')
            self.emit(f"    {name}: db \"{escaped}\", 0")
        self.emit("")
    
    def emit_code_section(self):
        """Emite la sección de código"""
        self.emit("section .text")
        
        # Declarar funciones externas comunes
        self.emit("    extern printf")
        self.emit("    extern scanf")
        self.emit("    extern exit")
        self.emit("")
        
        # Exportar main si existe
        has_main = any(isinstance(instr, IRFuncBegin) and instr.name == 'main' 
                       for instr in self.instructions)
        if has_main:
            self.emit("    global main")
            self.emit("")
        
        # Generar código para cada instrucción
        for instr in self.instructions:
            self.visit(instr)
    
    def visit(self, instr: IRInstr):
        """Visita una instrucción IR y genera código ASM"""
        match instr:
            case IRFuncBegin():
                self.visit_func_begin(instr)
            case IRFuncEnd():
                self.visit_func_end(instr)
            case IRLabel():
                self.visit_label(instr)
            case IRAssign():
                self.visit_assign(instr)
            case IRBinOp():
                self.visit_binop(instr)
            case IRUnaryOp():
                self.visit_unaryop(instr)
            case IRGoto():
                self.visit_goto(instr)
            case IRIfGoto():
                self.visit_if_goto(instr)
            case IRIfFalseGoto():
                self.visit_if_false_goto(instr)
            case IRParam():
                pass  # Los parámetros se manejan en IRCall
            case IRCall():
                self.visit_call(instr)
            case IRReturn():
                self.visit_return(instr)
    
    def get_var_location(self, var: str) -> str:
        """Retorna la ubicación de una variable (registro o memoria)"""
        # Si es un número literal
        if var.isdigit() or (var.startswith('-') and var[1:].isdigit()):
            return var
        
        # Si es una variable/temporal
        if var not in self.var_offset:
            self.current_offset += 8
            self.var_offset[var] = self.current_offset
        
        return f"QWORD [rbp-{self.var_offset[var]}]"    

    def visit_func_begin(self, instr: IRFuncBegin):
        """Genera prólogo de función"""
        self.in_function = True
        self.function_name = instr.name
        self.var_offset = {}
        self.current_offset = 0
        
        self.emit(f"{instr.name}:")
        self.emit("    push rbp")
        self.emit("    mov rbp, rsp")
        
        # Reservar espacio para variables locales (ajustaremos al final)
        self.emit("    sub rsp, 64  ; Espacio para variables locales")
        self.emit("")
        
        # Guardar parámetros en el stack
        for i, param in enumerate(instr.params):
            self.current_offset += 8
            self.var_offset[param] = self.current_offset
            if i < len(self.param_regs):
                self.emit(f"    mov QWORD [rbp-{self.current_offset}], {self.param_regs[i]}")
    
    def visit_func_end(self, instr: IRFuncEnd):
        """Genera epílogo de función"""
        self.emit(f".end_{instr.name}:")
        self.emit("    mov rsp, rbp")
        self.emit("    pop rbp")
        self.emit("    ret")
        self.emit("")
        self.in_function = False
    
    def visit_label(self, instr: IRLabel):
        """Emite una etiqueta"""
        self.emit(f".{instr.name}:")
    
    def visit_assign(self, instr: IRAssign):
        """dest = src"""
        dest_loc = self.get_var_location(instr.dest)
        
        # Si src es literal numérico
        if instr.src.isdigit() or (instr.src.startswith('-') and instr.src[1:].isdigit()):
            self.emit(f"    mov {dest_loc}, {instr.src}")
        # Si src es string literal
        elif instr.src.startswith('str'):
            self.emit(f"    lea rax, [{instr.src}]")
            self.emit(f"    mov {dest_loc}, rax")
        # Si src es variable
        else:
            src_loc = self.get_var_location(instr.src)
            self.emit(f"    mov rax, {src_loc}")
            self.emit(f"    mov {dest_loc}, rax")
    
    def visit_binop(self, instr: IRBinOp):
        """dest = left op right"""
        dest_loc = self.get_var_location(instr.dest)
        left_loc = self.get_var_location(instr.left)
        right_loc = self.get_var_location(instr.right)
        
        # Cargar operandos en registros
        if instr.left.isdigit():
            self.emit(f"    mov rax, {instr.left}")
        else:
            self.emit(f"    mov rax, {left_loc}")
        
        if instr.right.isdigit():
            self.emit(f"    mov rbx, {instr.right}")
        else:
            self.emit(f"    mov rbx, {right_loc}")
        
        # Realizar operación
        match instr.op:
            case '+':
                self.emit(f"    add rax, rbx")
            case '-':
                self.emit(f"    sub rax, rbx")
            case '*':
                self.emit(f"    imul rax, rbx")
            case '/':
                self.emit(f"    xor rdx, rdx")
                self.emit(f"    idiv rbx")
            case '%':
                self.emit(f"    xor rdx, rdx")
                self.emit(f"    idiv rbx")
                self.emit(f"    mov rax, rdx")
            case '<' | '>' | '<=' | '>=' | '==' | '!=':
                self.emit(f"    cmp rax, rbx")
                match instr.op:
                    case '<':
                        self.emit(f"    setl al")
                    case '>':
                        self.emit(f"    setg al")
                    case '<=':
                        self.emit(f"    setle al")
                    case '>=':
                        self.emit(f"    setge al")
                    case '==':
                        self.emit(f"    sete al")
                    case '!=':
                        self.emit(f"    setne al")
                self.emit(f"    movzx rax, al")
        
        # Guardar resultado
        self.emit(f"    mov {dest_loc}, rax")
    
    def visit_unaryop(self, instr: IRUnaryOp):
        """dest = op expr"""
        dest_loc = self.get_var_location(instr.dest)
        expr_loc = self.get_var_location(instr.expr)
        
        self.emit(f"    mov rax, {expr_loc}")
        
        if instr.op == '-':
            self.emit(f"    neg rax")
        elif instr.op == '!':
            self.emit(f"    test rax, rax")
            self.emit(f"    setz al")
            self.emit(f"    movzx rax, al")
        
        self.emit(f"    mov {dest_loc}, rax")
    
    def visit_goto(self, instr: IRGoto):
        """goto label"""
        self.emit(f"    jmp .{instr.label}")
    
    def visit_if_goto(self, instr: IRIfGoto):
        """if condition goto label"""
        cond_loc = self.get_var_location(instr.condition)
        self.emit(f"    mov rax, {cond_loc}")
        self.emit(f"    test rax, rax")
        self.emit(f"    jnz .{instr.label}")
    
    def visit_if_false_goto(self, instr: IRIfFalseGoto):
        """ifFalse condition goto label"""
        cond_loc = self.get_var_location(instr.condition)
        self.emit(f"    mov rax, {cond_loc}")
        self.emit(f"    test rax, rax")
        self.emit(f"    jz .{instr.label}")
    
    def visit_call(self, instr: IRCall):
        """dest = call func(args)"""
        # Alinear el stack a 16 bytes (requerido por Windows x64)
        self.emit(f"    sub rsp, 32  ; Shadow space para Windows x64")
        
        # Pasar argumentos en registros (Windows x64: RCX, RDX, R8, R9)
        for i, arg in enumerate(instr.args):
            if i < len(self.param_regs):
                arg_loc = self.get_var_location(arg)
                if arg.isdigit():
                    self.emit(f"    mov {self.param_regs[i]}, {arg}")
                elif arg.startswith('str'):
                    self.emit(f"    lea {self.param_regs[i]}, [{arg}]")
                else:
                    self.emit(f"    mov {self.param_regs[i]}, {arg_loc}")
        
        # Llamar a la función
        self.emit(f"    call {instr.func}")
        self.emit(f"    add rsp, 32")
        
        # Guardar valor de retorno si es necesario
        if instr.dest:
            dest_loc = self.get_var_location(instr.dest)
            self.emit(f"    mov {dest_loc}, rax")
    
    def visit_return(self, instr: IRReturn):
        """return value"""
        if instr.value:
            value_loc = self.get_var_location(instr.value)
            if instr.value.isdigit():
                self.emit(f"    mov rax, {instr.value}")
            else:
                self.emit(f"    mov rax, {value_loc}")
        else:
            self.emit(f"    xor rax, rax  ; return 0")
        
        self.emit(f"    jmp .end_{self.function_name}")


def generate_asm(instructions: List[IRInstr], string_literals: Dict[str, str]) -> str:
    """Función auxiliar para generar código ensamblador desde IR
    
    Args:
        instructions: Lista de instrucciones IR
        string_literals: Diccionario de literales de cadena
    
    Returns:
        Código ensamblador como string
    """
    gen = AsmGenerator(instructions, string_literals)
    return gen.generate()
