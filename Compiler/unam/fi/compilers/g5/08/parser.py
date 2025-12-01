# main.py — Parser LL con validación de funciones y argumentos
# Extensión: validación de declaración previa, printf/scanf, y tipos de argumentos

from dataclasses import dataclass
from typing import List, Optional, Any, Tuple

# === Tokens estándar (desde adapter_lexer) ===
from lexer.adapter_lexer import tokenize_std as lex

# ======= Definición del AST extendido =======

@dataclass
class Program:
    """Nodo raíz del programa que contiene todas las funciones y sentencias globales"""
    items: list

@dataclass
class FuncDecl:
    """Declaración de función"""
    return_type: str
    name: str
    params: List[Tuple[str, str]]
    body: 'Block'

@dataclass
class Block:
    """Bloque de código (entre { })"""
    statements: list

@dataclass
class Return:
    """Statement de retorno"""
    expr: Optional[Any]

@dataclass
class FuncCall:
    """Llamada a función"""
    name: str
    args: list

@dataclass
class ExprStmt:
    """Statement que es solo una expresión"""
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

@dataclass
class IfStmt:
    """Statement condicional if-else"""
    condition: Any
    then_block: 'Block'
    else_block: Optional['Block']

@dataclass
class WhileStmt:
    """Statement de ciclo while"""
    condition: Any
    body: 'Block'

@dataclass
class ForStmt:
    """Statement de ciclo for"""
    init: Any
    condition: Any
    step: Any
    body: 'Block'

# ======= Excepciones =======
class SyntaxError_(Exception):
    pass

class SemanticError(Exception):
    pass

class Parser:
    """Parser extendido con validación de funciones y argumentos"""
    
    def __init__(self, tokens: List):
        self.tokens = tokens
        self.i = 0
        self.current = self.tokens[self.i]
        self.symbols = {}
        self.functions = {}
        self.current_function_return_type = None
        self._init_builtin_functions()

    def _init_builtin_functions(self):
        """Inicializa funciones predefinidas como printf, scanf"""
        self.functions['printf'] = ('int', [], True)
        self.functions['scanf'] = ('int', [], True)

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

    def parse(self) -> Program:
        """program → (func_decl | stmt)* EOF"""
        items = []
        self._collect_function_declarations()
        self.i = 0
        self.current = self.tokens[self.i]
        
        while not self._check("EOF"):
            items.append(self.top_level())
        return Program(items)

    def _collect_function_declarations(self):
        """Primera pasada para registrar todas las funciones declaradas"""
        saved_i = self.i
        saved_current = self.current
        
        while not self._check("EOF"):
            if self._is_function_declaration():
                ret_type = self.current.lexeme if self._check('ID') else 'int'
                self._advance()
                
                name = self.current.lexeme
                self._advance()
                self._advance()  # LPAREN
                
                params = []
                if not self._check('RPAREN'):
                    params = self._collect_params()
                
                if name not in self.functions:
                    self.functions[name] = (ret_type, params, False)
                
                brace_count = 0
                while not self._check('EOF'):
                    if self._check('LBRACE'):
                        brace_count += 1
                        self._advance()
                        break
                    self._advance()
                
                while brace_count > 0 and not self._check('EOF'):
                    if self._check('LBRACE'):
                        brace_count += 1
                    elif self._check('RBRACE'):
                        brace_count -= 1
                    self._advance()
            else:
                while not self._check('SEMI') and not self._check('EOF'):
                    self._advance()
                if self._check('SEMI'):
                    self._advance()
        
        self.i = saved_i
        self.current = saved_current

    def _collect_params(self) -> List[Tuple[str, str]]:
        """Recolecta parámetros sin modificar tabla de símbolos"""
        params = []
        
        if self._check('INT'):
            ptype = 'int'
        elif self._check('ID'):
            ptype = self.current.lexeme
        else:
            return params
        self._advance()
        
        if self._check('ID'):
            pname = self.current.lexeme
            self._advance()
            params.append((ptype, pname))
        
        while self._check('COMMA'):
            self._advance()
            if self._check('INT'):
                ptype = 'int'
            elif self._check('ID'):
                ptype = self.current.lexeme
            else:
                break
            self._advance()
            
            if self._check('ID'):
                pname = self.current.lexeme
                self._advance()
                params.append((ptype, pname))
        
        return params

    def top_level(self):
        """Parsea declaraciones de nivel superior"""
        if self._is_function_declaration():
            return self.func_decl()
        else:
            return self.stmt()

    def _is_function_declaration(self) -> bool:
        """Verifica si lo siguiente es una declaración de función"""
        if self.i + 2 >= len(self.tokens):
            return False
        
        tok1 = self.tokens[self.i]
        tok2 = self.tokens[self.i + 1]
        tok3 = self.tokens[self.i + 2]
        
        is_type = tok1.type in ('INT', 'ID')
        is_name = tok2.type == 'ID'
        is_lparen = tok3.type == 'LPAREN'
        
        return is_type and is_name and is_lparen

    def func_decl(self) -> FuncDecl:
        """func_decl → type ID '(' params? ')' block"""
        if self._check('INT'):
            ret_type = 'int'
            self._advance()
        elif self._check('ID'):
            ret_type = self.current.lexeme
            self._advance()
        else:
            raise SyntaxError_("Se esperaba un tipo de retorno")

        name_tok = self._consume('ID', "Se esperaba nombre de función")
        name = name_tok.lexeme
        
        self.symbols = {}
        
        self._consume('LPAREN', "Se esperaba '(' después del nombre de función")
        params = self.params() if not self._check('RPAREN') else []
        self._consume('RPAREN', "Se esperaba ')'")

        prev_return_type = self.current_function_return_type
        self.current_function_return_type = ret_type

        body = self.block()

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
        """stmt → decl | assign | return_stmt | if_stmt | while_stmt | for_stmt | expr_stmt | block"""
        if self._check('RETURN') or (self._check('ID') and self.current.lexeme == 'return'):
            return self.return_stmt()
        
        if self._check('LBRACE'):
            return self.block()
        
        # Estructuras de control
        if self._check('ID'):
            if self.current.lexeme == 'if':
                return self.if_stmt()
            elif self.current.lexeme == 'while':
                return self.while_stmt()
            elif self.current.lexeme == 'for':
                return self.for_stmt()
        
        if self._check("INT"):
            return self.decl()
        
        if self._check("ID"):
            nxt = self.tokens[self.i+1] if self.i+1 < len(self.tokens) else None
            
            if nxt and nxt.type == 'ASSIGN':
                return self.assign()
            
            if nxt and nxt.type == 'ID':
                return self.decl_with_type()
            
            if nxt and nxt.type == 'LPAREN':
                expr = self.func_call()
                self._consume('SEMI', "Se esperaba ';' después de llamada a función")
                return ExprStmt(expr)
        
        raise SyntaxError_(f"Statement no reconocido: {self.current.type} '{self.current.lexeme}'")

    def return_stmt(self) -> Return:
        """return_stmt → 'return' expr? ';'"""
        if self._check('RETURN'):
            self._consume('RETURN', "Se esperaba 'return'")
        elif self._check('ID') and self.current.lexeme == 'return':
            self._advance()
        else:
            raise SyntaxError_("Se esperaba 'return'")
        
        expr = None
        if not self._check('SEMI'):
            expr = self.logical_or()
        
        self._consume('SEMI', "Se esperaba ';' después de return")
        
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

    def if_stmt(self):
        """if_stmt → 'if' '(' condition ')' '{' block '}' ('else' '{' block '}')?"""        
        if not (self._check('ID') and self.current.lexeme == 'if'):
            raise SyntaxError_("Se esperaba 'if'")
        self._advance()
        
        self._consume('LPAREN', "Se esperaba '(' después de 'if'")
        condition = self.logical_or()
        self._consume('RPAREN', "Se esperaba ')' después de la condición")
        
        # Validar que la condición sea válida (tipo booleano o numérico)
        cond_type = self.typeof(condition)
        if cond_type not in ('bool', 'int', 'float'):
            raise SemanticError(f"Condición de 'if' debe ser booleana o numérica, se obtuvo {cond_type}")
        
        then_block = self.block()
        
        else_block = None
        if self._check('ID') and self.current.lexeme == 'else':
            self._advance()
            else_block = self.block()
        
        return IfStmt(condition, then_block, else_block)

    def while_stmt(self):
        """while_stmt → 'while' '(' condition ')' '{' block '}'"""        
        if not (self._check('ID') and self.current.lexeme == 'while'):
            raise SyntaxError_("Se esperaba 'while'")
        self._advance()
        
        self._consume('LPAREN', "Se esperaba '(' después de 'while'")
        condition = self.logical_or()
        self._consume('RPAREN', "Se esperaba ')' después de la condición")
        
        # Validar que la condición sea válida
        cond_type = self.typeof(condition)
        if cond_type not in ('bool', 'int', 'float'):
            raise SemanticError(f"Condición de 'while' debe ser booleana o numérica, se obtuvo {cond_type}")
        
        body = self.block()
        
        return WhileStmt(condition, body)

    def for_stmt(self):
        """for_stmt → 'for' '(' init ';' condition ';' step ')' '{' block '}'"""        
        if not (self._check('ID') and self.current.lexeme == 'for'):
            raise SyntaxError_("Se esperaba 'for'")
        self._advance()
        
        self._consume('LPAREN', "Se esperaba '(' después de 'for'")
        
        # Inicialización (puede ser declaración o asignación)
        if self._check('INT'):
            init = self.decl_without_semi()
        elif self._check('ID'):
            # Verificar si es declaración con tipo o asignación
            nxt = self.tokens[self.i+1] if self.i+1 < len(self.tokens) else None
            if nxt and nxt.type == 'ID':
                init = self.decl_with_type_without_semi()
            elif nxt and nxt.type == 'ASSIGN':
                init = self.assign_without_semi()
            else:
                raise SyntaxError_("Se esperaba declaración o asignación en inicialización de for")
        else:
            raise SyntaxError_("Se esperaba declaración o asignación en inicialización de for")
        
        self._consume('SEMI', "Se esperaba ';' después de la inicialización")
        
        # Condición
        condition = self.logical_or()
        cond_type = self.typeof(condition)
        if cond_type not in ('bool', 'int', 'float'):
            raise SemanticError(f"Condición de 'for' debe ser booleana o numérica, se obtuvo {cond_type}")
        
        self._consume('SEMI', "Se esperaba ';' después de la condición")
        
        # Paso (incremento/decremento)
        step = self.assign_without_semi()
        
        self._consume('RPAREN', "Se esperaba ')' después del paso")
        
        body = self.block()
        
        return ForStmt(init, condition, step, body)

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

    def decl_without_semi(self):
        """decl → 'int' ID ('=' expr)? (sin punto y coma)"""        
        self._consume("INT", "Se esperaba 'int'")
        name_tok = self._consume("ID", "Se esperaba un identificador")
        name = name_tok.lexeme
        
        if name in self.symbols:
            raise SemanticError(f"Variable '{name}' ya declarada")
        
        init_expr = None
        if self._check("ASSIGN"):
            self._advance()
            init_expr = self.logical_or()

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

    def assign_without_semi(self):
        """assign → ID '=' expr (sin punto y coma)"""        
        name_tok = self._consume("ID", "Se esperaba un identificador")
        self._consume("ASSIGN", "Se esperaba '='")
        e = self.logical_or()

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

    def decl_with_type_without_semi(self):
        """decl_with_type → ID ID ('=' expr)? (sin punto y coma)"""        
        type_tok = self._consume('ID', "Se esperaba un tipo")
        name_tok = self._consume('ID', "Se esperaba un identificador")
        init_expr = None
        if self._check('ASSIGN'):
            self._advance()
            init_expr = self.logical_or()

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
        
        if name not in self.functions:
            raise SemanticError(f"Función '{name}' no declarada")
        
        self._consume('LPAREN', "Se esperaba '('")
        args = self.args() if not self._check('RPAREN') else []
        self._consume('RPAREN', "Se esperaba ')'")
        
        func_info = self.functions[name]
        expected_params = func_info[1]
        is_variadic = func_info[2] if len(func_info) > 2 else False
        
        if name == 'printf':
            if len(args) == 0:
                raise SemanticError("printf requiere al menos 1 argumento")
            
            if len(args) == 1:
                arg_type = self.typeof(args[0])
                if isinstance(args[0], Var) and args[0].name not in self.symbols:
                    raise SemanticError(f"printf: variable '{args[0].name}' no declarada")
            else:
                for i, arg in enumerate(args[1:], start=2):
                    if not isinstance(arg, Var):
                        raise SemanticError(f"printf: argumento {i} debe ser una variable")
                    if arg.name not in self.symbols:
                        raise SemanticError(f"printf: variable '{arg.name}' no declarada")
        
        elif name == 'scanf':
            if len(args) == 0:
                raise SemanticError("scanf requiere al menos 1 argumento")
            
            for i, arg in enumerate(args, start=1):
                if not isinstance(arg, Var):
                    raise SemanticError(f"scanf: argumento {i} debe ser una variable")
                if arg.name not in self.symbols:
                    raise SemanticError(f"scanf: variable '{arg.name}' no declarada")
        
        elif not is_variadic:
            if len(args) != len(expected_params):
                raise SemanticError(
                    f"Función '{name}' espera {len(expected_params)} argumento(s), "
                    f"se proporcionaron {len(args)}"
                )
            
            for i, (arg, (expected_type, param_name)) in enumerate(zip(args, expected_params)):
                arg_type = self.typeof(arg)
                
                if arg_type == expected_type:
                    continue
                elif arg_type == 'int' and expected_type == 'float':
                    continue
                else:
                    raise SemanticError(
                        f"Función '{name}', argumento {i+1} ('{param_name}'): "
                        f"se esperaba {expected_type}, se obtuvo {arg_type}"
                    )
        
        return FuncCall(name, args)

    def args(self) -> list:
        """args → expr (',' expr)*"""
        result = []
        result.append(self.logical_or())
        while self._check('COMMA'):
            self._advance()
            result.append(self.logical_or())
        return result

    def factor(self):
        """factor → ('+'|'-') factor | NUM | STRING | ID ('(' args? ')')? | '(' expr ')'"""
        if self._check("PLUS") or self._check("MINUS"):
            op = self.current.lexeme
            self._advance()
            return UnaryOp(op, self.factor())

        if self._check("NUM"):
            tok = self.current
            self._advance()
            if tok.literal is None:
                raise SyntaxError_("Número mal formado")
            return Num(tok.literal)

        if self._check("STRING"):
            tok = self.current
            self._advance()
            return String(tok.literal)

        if self._check("ID"):
            name = self.current.lexeme
            self._advance()
            
            if self._check('LPAREN'):
                self.i -= 1
                self.current = self.tokens[self.i]
                return self.func_call()
            
            return Var(name)

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
            if node.name in self.functions:
                return self.functions[node.name][0]
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