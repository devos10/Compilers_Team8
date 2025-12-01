"""
ir_generator.py - Generador de Código Intermedio (Three-Address Code)

Este módulo convierte el AST en representación intermedia (IR) usando
código de tres direcciones (Three-Address Code - TAC).

Cada instrucción tiene como máximo 3 operandos:
    t1 = a + b
    if a < b goto L1
    x = y
"""

from dataclasses import dataclass
from typing import Any, List, Optional
from parser import (
    Program, FuncDecl, Block, Return, FuncCall, ExprStmt,
    String, Decl, Assign, BinOp, Num, Var, UnaryOp,
    IfStmt, WhileStmt, ForStmt
)


# ======= Instrucciones IR =======

@dataclass
class IRInstr:
    """Clase base para instrucciones IR"""
    pass


@dataclass
class IRLabel(IRInstr):
    """Etiqueta: L1:"""
    name: str
    
    def __str__(self):
        return f"{self.name}:"


@dataclass
class IRAssign(IRInstr):
    """Asignación simple: dest = src"""
    dest: str
    src: str
    
    def __str__(self):
        return f"{self.dest} = {self.src}"


@dataclass
class IRBinOp(IRInstr):
    """Operación binaria: dest = left op right"""
    dest: str
    left: str
    op: str
    right: str
    
    def __str__(self):
        return f"{self.dest} = {self.left} {self.op} {self.right}"


@dataclass
class IRUnaryOp(IRInstr):
    """Operación unaria: dest = op expr"""
    dest: str
    op: str
    expr: str
    
    def __str__(self):
        return f"{self.dest} = {self.op}{self.expr}"


@dataclass
class IRGoto(IRInstr):
    """Salto incondicional: goto L1"""
    label: str
    
    def __str__(self):
        return f"goto {self.label}"


@dataclass
class IRIfFalseGoto(IRInstr):
    """Salto condicional: if not condition goto label"""
    condition: str
    label: str
    
    def __str__(self):
        return f"ifFalse {self.condition} goto {self.label}"


@dataclass
class IRCall(IRInstr):
    """Llamada a función: dest = call func(args)"""
    dest: Optional[str]
    func: str
    args: List[str]
    
    def __str__(self):
        args_str = ", ".join(self.args)
        if self.dest:
            return f"{self.dest} = call {self.func}({args_str})"
        return f"call {self.func}({args_str})"


@dataclass
class IRReturn(IRInstr):
    """Retorno: return value"""
    value: Optional[str]
    
    def __str__(self):
        if self.value:
            return f"return {self.value}"
        return "return"


@dataclass
class IRFuncBegin(IRInstr):
    """Inicio de función: func name(params)"""
    name: str
    params: List[str]
    
    def __str__(self):
        params_str = ", ".join(self.params)
        return f"func {self.name}({params_str})"


@dataclass
class IRFuncEnd(IRInstr):
    """Fin de función: endfunc"""
    name: str
    
    def __str__(self):
        return f"endfunc {self.name}"


@dataclass
class IRParam(IRInstr):
    """Parámetro para llamada: param value"""
    value: str
    
    def __str__(self):
        return f"param {self.value}"


# ======= Generador de IR =======

class IRGenerator:
    """Genera código intermedio (Three-Address Code) desde el AST"""
    
    def __init__(self):
        self.instructions: List[IRInstr] = []
        self.temp_count = 0
        self.label_count = 0
        self.string_literals = {}  # Mapeo de strings a nombres
        self.string_count = 0
    
    def new_temp(self) -> str:
        """Genera un nuevo temporal: t0, t1, t2, ..."""
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp
    
    def new_label(self) -> str:
        """Genera una nueva etiqueta: L0, L1, L2, ..."""
        label = f"L{self.label_count}"
        self.label_count += 1
        return label
    
    def new_string(self, value: str) -> str:
        """Registra un literal de cadena y retorna su nombre"""
        if value not in self.string_literals:
            name = f"str{self.string_count}"
            self.string_literals[value] = name
            self.string_count += 1
        return self.string_literals[value]
    
    def emit(self, instr: IRInstr):
        """Emite una instrucción IR"""
        self.instructions.append(instr)
    
    def generate(self, ast: Program) -> List[IRInstr]:
        """Genera IR desde el AST"""
        self.visit(ast)
        return self.instructions
    
    def visit(self, node: Any) -> Optional[str]:
        """Visita un nodo del AST y retorna el temporal que contiene su resultado"""
        match node:
            case Program():
                return self.visit_program(node)
            case FuncDecl():
                return self.visit_func_decl(node)
            case Block():
                return self.visit_block(node)
            case Decl():
                return self.visit_decl(node)
            case Assign():
                return self.visit_assign(node)
            case Return():
                return self.visit_return(node)
            case IfStmt():
                return self.visit_if(node)
            case WhileStmt():
                return self.visit_while(node)
            case ForStmt():
                return self.visit_for(node)
            case ExprStmt():
                return self.visit(node.expr)
            case BinOp():
                return self.visit_binop(node)
            case UnaryOp():
                return self.visit_unaryop(node)
            case FuncCall():
                return self.visit_call(node)
            case Num():
                return str(node.value)
            case String():
                return self.new_string(node.value)
            case Var():
                return node.name
            case _:
                return None
    
    def visit_program(self, node: Program):
        """Visita el nodo Program"""
        for item in node.items:
            self.visit(item)
    
    def visit_func_decl(self, node: FuncDecl):
        """Visita declaración de función"""
        param_names = [name for _, name in node.params]
        self.emit(IRFuncBegin(node.name, param_names))
        self.visit(node.body)
        self.emit(IRFuncEnd(node.name))
    
    def visit_block(self, node: Block):
        """Visita bloque de código"""
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_decl(self, node: Decl):
        """Visita declaración de variable"""
        if node.init is not None:
            src = self.visit(node.init)
            self.emit(IRAssign(node.name, src))
    
    def visit_assign(self, node: Assign):
        """Visita asignación"""
        src = self.visit(node.expr)
        self.emit(IRAssign(node.name, src))
    
    def visit_return(self, node: Return):
        """Visita return"""
        if node.expr is not None:
            value = self.visit(node.expr)
            self.emit(IRReturn(value))
        else:
            self.emit(IRReturn(None))
    
    def visit_binop(self, node: BinOp) -> str:
        """Visita operación binaria"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        temp = self.new_temp()
        self.emit(IRBinOp(temp, left, node.op, right))
        return temp
    
    def visit_unaryop(self, node: UnaryOp) -> str:
        """Visita operación unaria"""
        expr = self.visit(node.expr)
        temp = self.new_temp()
        self.emit(IRUnaryOp(temp, node.op, expr))
        return temp
    
    def visit_call(self, node: FuncCall) -> str:
        """Visita llamada a función"""
        # Emitir parámetros
        arg_temps = []
        for arg in node.args:
            arg_temp = self.visit(arg)
            arg_temps.append(arg_temp)
            self.emit(IRParam(arg_temp))
        
        # Llamada
        temp = self.new_temp()
        self.emit(IRCall(temp, node.name, arg_temps))
        return temp
    
    def visit_if(self, node: IfStmt):
        """Visita if statement"""
        cond = self.visit(node.condition)
        
        label_then = self.new_label()
        label_end = self.new_label()
        label_else = self.new_label() if node.else_block else label_end
        
        # if not cond goto else/end
        self.emit(IRIfFalseGoto(cond, label_else))
        
        # Then block
        self.emit(IRLabel(label_then))
        self.visit(node.then_block)
        
        if node.else_block:
            self.emit(IRGoto(label_end))
            # Else block
            self.emit(IRLabel(label_else))
            self.visit(node.else_block)
        
        self.emit(IRLabel(label_end))
    
    def visit_while(self, node: WhileStmt):
        """Visita while loop"""
        label_start = self.new_label()
        label_body = self.new_label()
        label_end = self.new_label()
        
        # Start: evaluar condición
        self.emit(IRLabel(label_start))
        cond = self.visit(node.condition)
        self.emit(IRIfFalseGoto(cond, label_end))
        
        # Body
        self.emit(IRLabel(label_body))
        self.visit(node.body)
        self.emit(IRGoto(label_start))
        
        # End
        self.emit(IRLabel(label_end))
    
    def visit_for(self, node: ForStmt):
        """Visita for loop"""
        # Init
        self.visit(node.init)
        
        label_start = self.new_label()
        label_body = self.new_label()
        label_end = self.new_label()
        
        # Start: evaluar condición
        self.emit(IRLabel(label_start))
        cond = self.visit(node.condition)
        self.emit(IRIfFalseGoto(cond, label_end))
        
        # Body
        self.emit(IRLabel(label_body))
        self.visit(node.body)
        
        # Step
        self.visit(node.step)
        self.emit(IRGoto(label_start))
        
        # End
        self.emit(IRLabel(label_end))


def generate_ir(ast: Program) -> tuple[List[IRInstr], dict]:
    """Función auxiliar para generar IR desde AST
    
    Returns:
        (instrucciones, string_literals)
    """
    gen = IRGenerator()
    instructions = gen.generate(ast)
    return instructions, gen.string_literals
