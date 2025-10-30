# main.py — Parser LL sencillo + SDT (tipado int) con entrada desde user_lexer vía adapter_lexer
# Mejora: soporte de unario (+/-) SIN cambiar nombres ya usados en el parser

from dataclasses import dataclass
from typing import List, Optional, Any, Tuple

# === Tokens estándar (desde adapter_lexer) ===
from lexer.adapter_lexer import tokenize_std as lex  # devuelve List[Token(type, lexeme, literal, pos)]

# ======= AST =======
@dataclass
class Program:
    statements: list

@dataclass
class Decl:
    name: str
    init: Optional[Any]  # Expr | None

@dataclass
class Assign:
    name: str
    expr: Any  # Expr

@dataclass
class BinOp:
    left: Any
    op: str
    right: Any

@dataclass
class Num:
    value: int

@dataclass
class Var:
    name: str

# NUEVO: soporte unario
@dataclass
class UnaryOp:
    op: str
    expr: Any

class SyntaxError_(Exception):
    pass

class SemanticError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List):
        self.tokens = tokens
        self.i = 0
        self.current = self.tokens[self.i]
        self.symbols = {}  # nombre -> tipo ('int')

    # ------------- helpers -------------
    def _advance(self):
        if self.i < len(self.tokens)-1:
            self.i += 1
            self.current = self.tokens[self.i]

    def _check(self, ttype: str) -> bool:
        return self.current.type == ttype

    def _consume(self, ttype: str, msg: str):
        if self._check(ttype):
            tok = self.current
            self._advance()
            return tok
        raise SyntaxError_(f"{msg} (got {self.current.type})")

    # ------------- grammar -------------
    def parse(self) -> Program:
        stmts = []
        while not self._check("EOF"):
            stmts.append(self.stmt())
        return Program(stmts)

    def stmt(self):
        if self._check("INT"):
            return self.decl()
        elif self._check("ID"):
            return self.assign()
        else:
            raise SyntaxError_("Se esperaba 'int' o ID al inicio de una sentencia")

    # decl → 'int' ID ('=' expr)? ';'
    def decl(self):
        self._consume("INT", "Se esperaba 'int'")
        name_tok = self._consume("ID", "Se esperaba un identificador")
        init_expr = None
        if self._check("ASSIGN"):
            self._advance()
            init_expr = self.expr()
        self._consume("SEMI", "Falta ';' al final de la declaración")

        name = name_tok.lexeme
        if name in self.symbols:
            raise SemanticError(f"Variable '{name}' ya declarada")
        self.symbols[name] = 'int'

        if init_expr is not None:
            t = self.typeof(init_expr)
            if t != 'int':
                raise SemanticError(f"Tipo incompatible en inicialización de '{name}': {t}")

        return Decl(name, init_expr)

    # assign → ID '=' expr ';'
    def assign(self):
        name_tok = self._consume("ID", "Se esperaba un identificador")
        self._consume("ASSIGN", "Se esperaba '='")
        e = self.expr()
        self._consume("SEMI", "Falta ';' al final de la asignación")

        name = name_tok.lexeme
        if name not in self.symbols:
            raise SemanticError(f"Variable '{name}' no declarada")
        t = self.typeof(e)
        if t != 'int':
            raise SemanticError(f"Tipo incompatible en asignación a '{name}': {t}")
        return Assign(name, e)

    # expr → term (('+'|'-') term)*
    def expr(self):
        left = self.term()
        while self._check("PLUS") or self._check("MINUS"):
            op = self.current.lexeme
            self._advance()
            right = self.term()
            left = BinOp(left, op, right)
        return left

    # term → factor (('*'|'/') factor)*
    def term(self):
        left = self.factor()
        while self._check("STAR") or self._check("SLASH"):
            op = self.current.lexeme
            self._advance()
            right = self.factor()
            left = BinOp(left, op, right)
        return left

    # factor → ('+'|'-') factor | NUM | ID | '(' expr ')'
    def factor(self):
        # soporte unario
        if self._check("PLUS") or self._check("MINUS"):
            op = self.current.lexeme
            self._advance()
            return UnaryOp(op, self.factor())

        if self._check("NUM"):
            tok = self.current
            self._advance()
            # Rechaza float aquí como SDT error para lenguaje de 'int'
            if isinstance(tok.literal, float):
                raise SemanticError(f"Constante float '{tok.lexeme}' no permitida para tipo int")
            if tok.literal is None:
                raise SyntaxError_("Número mal formado")
            return Num(int(tok.literal))

        if self._check("ID"):
            tok = self.current
            self._advance()
            return Var(tok.lexeme)

        if self._check("LPAREN"):
            self._advance()
            e = self.expr()
            self._consume("RPAREN", "Se esperaba ')'")
            return e

        raise SyntaxError_("Factor inválido")

    # ===== SDT tipo simple =====
    def typeof(self, node) -> str:
        if isinstance(node, Num):
            return 'int'
        if isinstance(node, Var):
            if node.name not in self.symbols:
                raise SemanticError(f"Uso de variable no declarada '{node.name}'")
            return self.symbols[node.name]
        if isinstance(node, UnaryOp):
            t = self.typeof(node.expr)
            if t != 'int':
                raise SemanticError(f"Unario '{node.op}' espera int, obtuvo {t}")
            return 'int'
        if isinstance(node, BinOp):
            tl = self.typeof(node.left)
            tr = self.typeof(node.right)
            if tl == 'int' and tr == 'int':
                return 'int'
            raise SemanticError(f"Operación '{node.op}' incompatible: {tl} y {tr}")
        raise SemanticError(f"No sé inferir tipo de {type(node).__name__}")

def run(src: str):
    # Lexing (vía adaptador a partir de user_lexer)
    try:
        tokens = lex(src)
    except Exception as e:
        print("Parsing error...")
        print(str(e))
        return

    p = Parser(tokens)

    # Parsing
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

    # Validación SDT adicional
    try:
        for st in ast.statements:
            if isinstance(st, Decl) and st.init is not None:
                _ = p.typeof(st.init)
            elif isinstance(st, Assign):
                _ = p.typeof(st.expr)
    except SemanticError as e:
        print("Parsing Success!")
        print("SDT error...")
        print(str(e))
        return

    print("Parsing Success!")
    print("SDT Verified!")
