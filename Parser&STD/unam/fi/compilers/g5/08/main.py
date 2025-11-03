# main.py — Parser LL con soporte para funciones, bloques y comentarios
# Extensión: declaración de funciones, llamadas a funciones, return, comentarios


from dataclasses import dataclass
from typing import List, Optional, Any, Tuple

# === Tokens estándar (desde adapter_lexer) ===
from lexer.adapter_lexer import tokenize_std as lex

# ======= Definición del AST extendido =======

@dataclass
class Program:
    """Nodo raíz del programa que contiene todas las funciones y sentencias globales"""
    items: list  # Puede contener FuncDecl, Decl, etc.

@dataclass
class FuncDecl:
    """Declaración de función
    Ejemplo: int main() { ... }
    """
    return_type: str  # 'int', 'void', 'float', etc.
    name: str
    params: List[Tuple[str, str]]  # [(tipo, nombre), ...]
    body: 'Block'

@dataclass
class Block:
    """Bloque de código (entre { })"""
    statements: list

@dataclass
class Return:
    """Statement de retorno
    Ejemplo: return x;
    """
    expr: Optional[Any]  # None para 'return;'

@dataclass
class FuncCall:
    """Llamada a función
    Ejemplo: printf("hola");
    """
    name: str
    args: list  # Lista de expresiones

@dataclass
class ExprStmt:
    """Statement que es solo una expresión (ej: llamada a función)"""
    expr: Any

@dataclass
class String:
    """Representa un literal de cadena de texto"""
    value: str

@dataclass
class Decl:
    """Declaración de variable con inicialización opcional"""
    name: str
    init: Optional[Any]

@dataclass
class Assign:
    """Asignación de valor a una variable"""
    name: str
    expr: Any

@dataclass
class BinOp:
    """Operación binaria"""
    left: Any
    op: str
    right: Any

@dataclass
class Num:
    """Representa un literal numérico"""
    value: int

@dataclass
class Var:
    """Referencia a una variable"""
    name: str

@dataclass
class UnaryOp:
    """Operación unaria"""
    op: str
    expr: Any

# ======= Excepciones =======
class SyntaxError_(Exception):
    pass

class SemanticError(Exception):
    pass

class Parser:
    """Parser extendido con soporte para funciones y bloques"""
    
    def __init__(self, tokens: List):
        self.tokens = tokens
        self.i = 0
        self.current = self.tokens[self.i]
        self.symbols = {}  # Tabla de símbolos: nombre -> tipo
        self.functions = {}  # Tabla de funciones: nombre -> (return_type, params)
        self.current_function_return_type = None  # Para validar returns
        self.scope_stack = []  # Pila de scopes para manejo correcto

    def _advance(self):
        """Avanza al siguiente token"""
        if self.i < len(self.tokens)-1:
            self.i += 1
            self.current = self.tokens[self.i]

    def _check(self, ttype: str) -> bool:
        """Verifica si el token actual es del tipo especificado"""
        return self.current.type == ttype

    def _consume(self, ttype: str, msg: str):
        """Consume un token del tipo esperado o lanza error"""
        if self._check(ttype):
            tok = self.current
            self._advance()
            return tok
        raise SyntaxError_(f"{msg} (got {self.current.type} '{self.current.lexeme}')")

    # ============= GRAMÁTICA EXTENDIDA =============
    
    def parse(self) -> Program:
        """program → (func_decl | stmt)* EOF"""
        items = []
        while not self._check("EOF"):
            # Intentar parsear función o statement
            items.append(self.top_level())
        return Program(items)

    def top_level(self):
        """Parsea declaraciones de nivel superior (funciones o variables globales)"""
        # Detectar si es una función: tipo + ID + '('
        if self._is_function_declaration():
            return self.func_decl()
        else:
            return self.stmt()

    def _is_function_declaration(self) -> bool:
        """Verifica si lo siguiente es una declaración de función"""
        # Necesitamos lookahead para ver: tipo ID (
        # Ejemplo: int main ( ...
        if self.i + 2 >= len(self.tokens):
            return False
        
        # Buscar patrón: (INT|ID) ID LPAREN
        tok1 = self.tokens[self.i]
        tok2 = self.tokens[self.i + 1]
        tok3 = self.tokens[self.i + 2]
        
        is_type = tok1.type in ('INT', 'ID')  # tipo
        is_name = tok2.type == 'ID'  # nombre función
        is_lparen = tok3.type == 'LPAREN'  # paréntesis
        
        return is_type and is_name and is_lparen

    def func_decl(self) -> FuncDecl:
        """func_decl → type ID '(' params? ')' block"""
        # Tipo de retorno
        if self._check('INT'):
            ret_type = 'int'
            self._advance()
        elif self._check('ID'):
            ret_type = self.current.lexeme  # void, float, etc.
            self._advance()
        else:
            raise SyntaxError_("Se esperaba un tipo de retorno")

        # Nombre de función
        name_tok = self._consume('ID', "Se esperaba nombre de función")
        name = name_tok.lexeme

        # Guardar función en tabla de símbolos
        if name in self.functions:
            raise SemanticError(f"Función '{name}' ya declarada")
        
        # CREAR NUEVO SCOPE LIMPIO para la función
        self.symbols = {}  # Resetear completamente la tabla de símbolos
        
        # Parámetros (se agregan al nuevo scope limpio)
        self._consume('LPAREN', "Se esperaba '(' después del nombre de función")
        params = self.params() if not self._check('RPAREN') else []
        self._consume('RPAREN', "Se esperaba ')'")
        
        self.functions[name] = (ret_type, params)

        # Guardar tipo de retorno actual para validar returns
        prev_return_type = self.current_function_return_type
        self.current_function_return_type = ret_type

        # Cuerpo
        body = self.block()

        # Limpiar scope de la función (no restaurar, simplemente limpiar)
        self.symbols = {}
        self.current_function_return_type = prev_return_type

        return FuncDecl(ret_type, name, params, body)

    def params(self) -> List[Tuple[str, str]]:
        """params → param (',' param)*"""
        result = []
        result.append(self.param())
        while self._check('COMMA'):
            self._advance()
            result.append(self.param())
        return result

    def param(self) -> Tuple[str, str]:
        """param → type ID"""
        if self._check('INT'):
            ptype = 'int'
            self._advance()
        elif self._check('ID'):
            ptype = self.current.lexeme
            self._advance()
        else:
            raise SyntaxError_("Se esperaba un tipo en parámetro")
        
        name_tok = self._consume('ID', "Se esperaba nombre de parámetro")
        pname = name_tok.lexeme
        
        # Agregar parámetro a tabla de símbolos local
        self.symbols[pname] = ptype
        
        return (ptype, pname)

    def block(self) -> Block:
        """block → '{' stmt* '}'"""
        self._consume('LBRACE', "Se esperaba '{'")
        
        stmts = []
        while not self._check('RBRACE'):
            if self._check('EOF'):
                raise SyntaxError_("Se esperaba '}' pero se alcanzó EOF")
            stmts.append(self.stmt())
        
        self._consume('RBRACE', "Se esperaba '}'")
        
        return Block(stmts)

    def stmt(self):
        """stmt → decl | assign | return_stmt | expr_stmt | block"""
        # Return statement (puede venir como RETURN o como ID 'return')
        if self._check('RETURN') or (self._check('ID') and self.current.lexeme == 'return'):
            return self.return_stmt()
        
        # Bloque anidado
        if self._check('LBRACE'):
            return self.block()
        
        # Declaración de variable (int x = ...)
        if self._check("INT"):
            return self.decl()
        
        # ID puede ser: declaración con tipo personalizado, asignación, o llamada a función
        if self._check("ID"):
            # Lookahead
            nxt = self.tokens[self.i+1] if self.i+1 < len(self.tokens) else None
            
            # Caso 1: ID = ... (asignación) - DEBE IR PRIMERO
            if nxt and nxt.type == 'ASSIGN':
                return self.assign()
            
            # Caso 2: tipo ID ... (declaración)
            if nxt and nxt.type == 'ID':
                return self.decl_with_type()
            
            # Caso 3: ID ( ... (llamada a función como statement)
            if nxt and nxt.type == 'LPAREN':
                expr = self.func_call()
                self._consume('SEMI', "Se esperaba ';' después de llamada a función")
                return ExprStmt(expr)
        
        raise SyntaxError_(f"Statement no reconocido: {self.current.type} '{self.current.lexeme}'")

    def return_stmt(self) -> Return:
        """return_stmt → 'return' expr? ';'"""
        # Consumir 'return' (puede ser RETURN o ID 'return')
        if self._check('RETURN'):
            self._consume('RETURN', "Se esperaba 'return'")
        elif self._check('ID') and self.current.lexeme == 'return':
            self._advance()  # consumir el ID 'return'
        else:
            raise SyntaxError_("Se esperaba 'return'")
        
        expr = None
        if not self._check('SEMI'):
            expr = self.logical_or()
        
        self._consume('SEMI', "Se esperaba ';' después de return")
        
        # Validar tipo de retorno
        if self.current_function_return_type is not None:
            if expr is None:
                if self.current_function_return_type != 'void':
                    raise SemanticError(f"Return sin valor en función que retorna {self.current_function_return_type}")
            else:
                expr_type = self.typeof(expr)
                if expr_type != self.current_function_return_type:
                    if not (expr_type == 'int' and self.current_function_return_type == 'float'):
                        raise SemanticError(f"Tipo de return incompatible: se esperaba {self.current_function_return_type}, se obtuvo {expr_type}")
        
        return Return(expr)

    def decl(self):
        """decl → 'int' ID ('=' expr)? ';'"""
        self._consume("INT", "Se esperaba 'int'")
        name_tok = self._consume("ID", "Se esperaba un identificador")
        name = name_tok.lexeme
        
        if name in self.symbols:
            raise SemanticError(f"Variable '{name}' ya declarada")
        
        init_expr = None
        if self._check("ASSIGN"):
            self._advance()
            init_expr = self.logical_or()
        self._consume("SEMI", "Falta ';' al final de la declaración")

        self.symbols[name] = 'int'

        if init_expr is not None:
            t = self.typeof(init_expr)
            if t != 'int':
                raise SemanticError(f"Tipo incompatible en inicialización de '{name}': {t}")

        return Decl(name, init_expr)

    def assign(self):
        """assign → ID '=' expr ';'"""
        name_tok = self._consume("ID", "Se esperaba un identificador")
        self._consume("ASSIGN", "Se esperaba '='")
        e = self.logical_or()
        self._consume("SEMI", "Falta ';' al final de la asignación")

        name = name_tok.lexeme
        if name not in self.symbols:
            raise SemanticError(f"Variable '{name}' no declarada")
        t = self.typeof(e)
        expected_type = self.symbols[name]
        if t != expected_type:
            if not (t == 'int' and expected_type == 'float'):
                raise SemanticError(f"Tipo incompatible en asignación a '{name}': se esperaba {expected_type}, se obtuvo {t}")
        return Assign(name, e)

    def decl_with_type(self):
        """decl_with_type → ID ID ('=' expr)? ';'"""
        type_tok = self._consume('ID', "Se esperaba un tipo")
        name_tok = self._consume('ID', "Se esperaba un identificador")
        init_expr = None
        if self._check('ASSIGN'):
            self._advance()
            init_expr = self.logical_or()
        self._consume('SEMI', "Falta ';' al final de la declaración")

        type_name = type_tok.lexeme
        name = name_tok.lexeme
        if name in self.symbols:
            raise SemanticError(f"Variable '{name}' ya declarada")
        self.symbols[name] = type_name

        if init_expr is not None:
            t = self.typeof(init_expr)
            if t != type_name:
                if not (t == 'int' and type_name == 'float'):
                    raise SemanticError(f"Tipo incompatible en inicialización de '{name}': {t}")

        return Decl(name, init_expr)

    def func_call(self) -> FuncCall:
        """func_call → ID '(' args? ')'"""
        name_tok = self._consume('ID', "Se esperaba nombre de función")
        name = name_tok.lexeme
        
        self._consume('LPAREN', "Se esperaba '('")
        args = self.args() if not self._check('RPAREN') else []
        self._consume('RPAREN', "Se esperaba ')'")
        
        return FuncCall(name, args)

    def args(self) -> list:
        """args → expr (',' expr)*"""
        result = []
        result.append(self.logical_or())
        while self._check('COMMA'):
            self._advance()
            result.append(self.logical_or())
        return result

    # ============= EXPRESIONES =============

    def factor(self):
        """factor → ('+'|'-') factor | NUM | STRING | ID ('(' args? ')')? | '(' expr ')'"""
        # Operadores unarios
        if self._check("PLUS") or self._check("MINUS"):
            op = self.current.lexeme
            self._advance()
            return UnaryOp(op, self.factor())

        # Números
        if self._check("NUM"):
            tok = self.current
            self._advance()
            if tok.literal is None:
                raise SyntaxError_("Número mal formado")
            return Num(tok.literal)

        # Strings
        if self._check("STRING"):
            tok = self.current
            self._advance()
            return String(tok.literal)

        # ID (variable o función)
        if self._check("ID"):
            name = self.current.lexeme
            self._advance()
            
            # Si sigue '(', es llamada a función
            if self._check('LPAREN'):
                self.i -= 1  # Retroceder para que func_call procese desde ID
                self.current = self.tokens[self.i]
                return self.func_call()
            
            # Es una variable
            return Var(name)

        # Paréntesis
        if self._check("LPAREN"):
            self._advance()
            e = self.logical_or()
            self._consume("RPAREN", "Se esperaba ')'")
            return e

        raise SyntaxError_("Factor inválido")

    def term(self):
        """term → factor (('*'|'/'|'%') factor)*"""
        left = self.factor()
        while self._check("STAR") or self._check("SLASH") or self._check("PERC"):
            op = self.current.lexeme
            self._advance()
            right = self.factor()
            left = BinOp(left, op, right)
        return left

    def additive(self):
        """additive → term (('+'|'-') term)*"""
        left = self.term()
        while self._check("PLUS") or self._check("MINUS"):
            op = self.current.lexeme
            self._advance()
            right = self.term()
            left = BinOp(left, op, right)
        return left

    def relational(self):
        """relational → additive (('<'|'>'|'<='|'>=') additive)?"""
        left = self.additive()
        while self._check('LT') or self._check('GT') or self._check('LE') or self._check('GE'):
            op = self.current.lexeme
            self._advance()
            right = self.additive()
            left = BinOp(left, op, right)
        return left

    def equality(self):
        """equality → relational (('=='|'!=') relational)*"""
        left = self.relational()
        while self._check('EQ') or self._check('NEQ'):
            op = self.current.lexeme
            self._advance()
            right = self.relational()
            left = BinOp(left, op, right)
        return left

    def logical_and(self):
        """logical_and → equality ('&&' equality)*"""
        left = self.equality()
        while self._check('AND'):
            op = self.current.lexeme
            self._advance()
            right = self.equality()
            left = BinOp(left, op, right)
        return left

    def logical_or(self):
        """logical_or → logical_and ('||' logical_and)*"""
        left = self.logical_and()
        while self._check('OR'):
            op = self.current.lexeme
            self._advance()
            right = self.logical_and()
            left = BinOp(left, op, right)
        return left

    # ============= ANÁLISIS SEMÁNTICO =============

    def typeof(self, node) -> str:
        """Determina el tipo de una expresión del AST"""
        if isinstance(node, Num):
            return 'float' if isinstance(node.value, float) else 'int'
        
        if isinstance(node, String):
            return 'string'
        
        if isinstance(node, Var):
            if node.name not in self.symbols:
                raise SemanticError(f"Uso de variable no declarada '{node.name}'")
            return self.symbols[node.name]
        
        if isinstance(node, FuncCall):
            # Para llamadas a función, necesitamos saber su tipo de retorno
            if node.name in self.functions:
                return self.functions[node.name][0]  # return_type
            # Función desconocida - asumir que es válida (ej: printf)
            return 'void'
        
        if isinstance(node, UnaryOp):
            t = self.typeof(node.expr)
            if t not in ('int', 'float'):
                raise SemanticError(f"Unario '{node.op}' espera número, obtuvo {t}")
            return t
        
        if isinstance(node, BinOp):
            tl = self.typeof(node.left)
            tr = self.typeof(node.right)

            if node.op == '+':
                if tl == 'string' and tr == 'string':
                    return 'string'
                if tl in ('int', 'float') and tr in ('int', 'float'):
                    return 'float' if 'float' in (tl, tr) else 'int'
                raise SemanticError(f"Operación '+' incompatible entre {tl} y {tr}")

            if node.op in ('-', '*', '/', '%'):
                if tl in ('int', 'float') and tr in ('int', 'float'):
                    return 'float' if 'float' in (tl, tr) else 'int'
                raise SemanticError(f"Operación '{node.op}' espera números, obtuvo {tl} y {tr}")

            if node.op in ('==', '!=', '<', '>', '<=', '>='):
                if (tl in ('int', 'float') and tr in ('int', 'float')) or (tl == tr == 'string'):
                    return 'bool'
                raise SemanticError(f"Comparación '{node.op}' incompatible entre {tl} y {tr}")

            if node.op in ('&&', '||'):
                if tl == tr == 'bool':
                    return 'bool'
                raise SemanticError(f"Operación lógica '{node.op}' espera booleanos, obtuvo {tl} y {tr}")

        raise SemanticError(f"No sé inferir tipo de {type(node).__name__}")

def run(src: str):
    """Función principal para ejecutar el parser"""
    try:
        tokens = lex(src)
    except Exception as e:
        print("Lexical error...")
        print(str(e))
        return

    p = Parser(tokens)

    try:
        ast = p.parse()
    except SyntaxError_ as e:
        print("Parsing error...")
        print(str(e))
        return
    except SemanticError as e:
        print("Parsing Success!")
        print("SDT error...")
        print(str(e))
        return

    print("Parsing Success!")
    print("SDT Verified!")

# Método auxiliar para validar bloques recursivamente
def _validate_block(self, block: Block):
    """Valida tipos en un bloque de código"""
    for st in block.statements:
        if isinstance(st, Block):
            self._validate_block(st)
        elif isinstance(st, Decl) and st.init is not None:
            _ = self.typeof(st.init)
        elif isinstance(st, Assign):
            _ = self.typeof(st.expr)
        elif isinstance(st, Return) and st.expr is not None:
            _ = self.typeof(st.expr)
        elif isinstance(st, ExprStmt):
            _ = self.typeof(st.expr)

Parser._validate_block = _validate_block