# main.py — Parser LL sencillo + SDT (tipado int) con entrada desde user_lexer vía adapter_lexer
# Mejora: soporte de unario (+/-) SIN cambiar nombres ya usados en el parser
#
# Este archivo implementa un parser descendente recursivo (LL) con análisis semántico
# dirigido por sintaxis (SDT) que verifica tipos en tiempo de compilación.
# Soporta múltiples tipos de datos (int, float, string, bool) y sus operaciones.

from dataclasses import dataclass
from typing import List, Optional, Any, Tuple

# === Tokens estándar (desde adapter_lexer) ===
from lexer.adapter_lexer import tokenize_std as lex  # devuelve List[Token(type, lexeme, literal, pos)]

# ======= Definición del AST (Abstract Syntax Tree) =======
# Cada clase representa un nodo diferente en el árbol de sintaxis abstracta

@dataclass
class Program:
    """Nodo raíz del programa que contiene todas las sentencias"""
    statements: list

@dataclass
class String:
    """Representa un literal de cadena de texto"""
    value: str

@dataclass
class Decl:
    """Declaración de variable con inicialización opcional
    Ejemplo: int x = 5; o string s = "hola";
    """
    name: str
    init: Optional[Any]  # Expr | None

@dataclass
class Assign:
    """Asignación de valor a una variable ya declarada
    Ejemplo: x = 10;
    """
    name: str
    expr: Any  # Expr

@dataclass
class BinOp:
    """Operación binaria (dos operandos)
    Soporta: +, -, *, /, %, ==, !=, <, >, <=, >=, &&, ||
    """
    left: Any
    op: str
    right: Any

@dataclass
class Num:
    """Representa un literal numérico (int o float)"""
    value: int

@dataclass
class Var:
    """Referencia a una variable por su nombre"""
    name: str

@dataclass
class UnaryOp:
    """Operación unaria (un solo operando)
    Soporta: + (positivo), - (negativo)
    Ejemplo: -5, +x
    """
    op: str
    expr: Any

# ======= Excepciones personalizadas =======
class SyntaxError_(Exception):
    """Error de sintaxis durante el parsing"""
    pass

class SemanticError(Exception):
    """Error semántico (tipos incompatibles, variables no declaradas, etc.)"""
    pass

class Parser:
    """Parser descendente recursivo (LL) con análisis semántico integrado
    
    Implementa un analizador sintáctico que construye un AST (Árbol de Sintaxis Abstracta)
    y verifica tipos en tiempo de compilación mediante SDT (Syntax-Directed Translation).
    """
    def __init__(self, tokens: List):
        """Inicializa el parser con la lista de tokens
        
        Args:
            tokens: Lista de tokens obtenida del lexer
        """
        self.tokens = tokens
        self.i = 0  # Índice del token actual
        self.current = self.tokens[self.i]
        self.symbols = {}  # Tabla de símbolos: nombre -> tipo ('int', 'float', 'string', 'bool')

    # ------------- Métodos auxiliares -------------
    def _advance(self):
        """Avanza al siguiente token si no estamos al final"""
        if self.i < len(self.tokens)-1:
            self.i += 1
            self.current = self.tokens[self.i]

    def _check(self, ttype: str) -> bool:
        """Verifica si el token actual es del tipo especificado
        
        Args:
            ttype: Tipo de token a verificar (ej: 'INT', 'ID', 'SEMI')
            
        Returns:
            True si el token actual coincide con el tipo, False en caso contrario
        """
        return self.current.type == ttype

    def _consume(self, ttype: str, msg: str):
        """Consume un token del tipo esperado o lanza error
        
        Args:
            ttype: Tipo de token esperado
            msg: Mensaje de error si el token no coincide
            
        Returns:
            El token consumido
            
        Raises:
            SyntaxError_: Si el token actual no es del tipo esperado
        """
        if self._check(ttype):
            tok = self.current
            self._advance()
            return tok
        raise SyntaxError_(f"{msg} (got {self.current.type})")

    # ------------- Reglas gramaticales -------------
    def parse(self) -> Program:
        """Punto de entrada del parser. Analiza el programa completo.
        
        Gramática: program → stmt* EOF
        
        Returns:
            Program: Nodo raíz del AST con todas las sentencias
        """
        stmts = []
        while not self._check("EOF"):
            stmts.append(self.stmt())
        return Program(stmts)

    def stmt(self):
        """Analiza una sentencia (declaración o asignación)
        
        Gramática: stmt → decl | assign
        
        Returns:
            Decl | Assign: Nodo del AST correspondiente a la sentencia
            
        Raises:
            SyntaxError_: Si no se reconoce el inicio de una sentencia válida
        """
        if self._check("INT"):
            return self.decl()
        elif self._check("ID"):
            # Lookahead: si el siguiente token también es ID, lo interpretamos como
            # 'TYPE ID ...' (declaración con nombre de tipo como identificador)
            nxt = self.tokens[self.i+1] if self.i+1 < len(self.tokens) else None
            if nxt and nxt.type == 'ID':
                return self.decl_with_type()
            return self.assign()
        else:
            raise SyntaxError_("Se esperaba 'int' o ID al inicio de una sentencia")

    # decl → 'int' ID ('=' expr)? ';'
    def decl(self):
        """Analiza una declaración de variable de tipo int
        
        Gramática: decl → 'int' ID ('=' expr)? ';'
        
        Returns:
            Decl: Nodo de declaración con el nombre y expresión de inicialización
            
        Raises:
            SemanticError: Si la variable ya está declarada o el tipo de inicialización no coincide
        """
        self._consume("INT", "Se esperaba 'int'")
        name_tok = self._consume("ID", "Se esperaba un identificador")
        init_expr = None
        if self._check("ASSIGN"):
            self._advance()
            init_expr = self.logical_or()
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
        """Analiza una asignación a una variable existente
        
        Gramática: assign → ID '=' expr ';'
        
        Returns:
            Assign: Nodo de asignación con el nombre de la variable y la expresión
            
        Raises:
            SemanticError: Si la variable no está declarada o hay incompatibilidad de tipos
        """
        name_tok = self._consume("ID", "Se esperaba un identificador")
        self._consume("ASSIGN", "Se esperaba '='")
        e = self.logical_or()
        self._consume("SEMI", "Falta ';' al final de la asignación")

        name = name_tok.lexeme
        if name not in self.symbols:
            raise SemanticError(f"Variable '{name}' no declarada")
        t = self.typeof(e)
        if t != 'int':
            raise SemanticError(f"Tipo incompatible en asignación a '{name}': {t}")
        return Assign(name, e)

    # decl_with_type → ID ID ('=' expr)? ';'
    # Soporta declaraciones donde el primer ID es el nombre del tipo (por ejemplo 'string s = "a";')
    def decl_with_type(self):
        """Analiza una declaración de variable con tipo personalizado
        
        Gramática: decl_with_type → ID ID ('=' expr)? ';'
        Soporta tipos como: string, float, bool
        
        Returns:
            Decl: Nodo de declaración con el nombre y expresión de inicialización
            
        Raises:
            SemanticError: Si la variable ya está declarada o hay incompatibilidad de tipos
        """
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
        # Guardamos el tipo tal cual (p. ej. 'string', 'float', 'int', 'bool')
        self.symbols[name] = type_name

        if init_expr is not None:
            t = self.typeof(init_expr)
            # Compatibilidad simple: mismo tipo, o int -> float permitido
            if t != type_name:
                if not (t == 'int' and type_name == 'float'):
                    raise SemanticError(f"Tipo incompatible en inicialización de '{name}': {t}")

        return Decl(name, init_expr)

    # factor → ('+'|'-') factor | NUM | STRING | ID | '(' expr ')'
    def factor(self):
        """Analiza un factor (unidad básica de expresión)
        
        Gramática: factor → ('+'|'-') factor | NUM | STRING | ID | '(' expr ')'
        
        Returns:
            UnaryOp | Num | String | Var | Expr: Nodo del AST correspondiente al factor
            
        Raises:
            SyntaxError_: Si no se reconoce un factor válido
        """
        # Soporte para operadores unarios (+/-)
        if self._check("PLUS") or self._check("MINUS"):
            op = self.current.lexeme
            self._advance()
            return UnaryOp(op, self.factor())

        # Números literales (int o float)
        if self._check("NUM"):
            tok = self.current
            self._advance()
            if tok.literal is None:
                raise SyntaxError_("Número mal formado")
            return Num(tok.literal)

        # Literales de cadena
        if self._check("STRING"):
            tok = self.current
            self._advance()
            return String(tok.literal)

        # Identificadores (variables)
        if self._check("ID"):
            tok = self.current
            self._advance()
            return Var(tok.lexeme)

        # Expresiones entre paréntesis
        if self._check("LPAREN"):
            self._advance()
            e = self.logical_or()
            self._consume("RPAREN", "Se esperaba ')'")
            return e

        raise SyntaxError_("Factor inválido")

    # term → factor (('*'|'/') factor)*
    def term(self):
        """Analiza un término (multiplicación, división, módulo)
        
        Gramática: term → factor (('*'|'/'|'%') factor)*
        
        Returns:
            BinOp | Factor: Nodo del AST correspondiente al término
        """
        left = self.factor()
        while self._check("STAR") or self._check("SLASH") or self._check("PERC"):
            op = self.current.lexeme
            self._advance()
            right = self.factor()
            left = BinOp(left, op, right)
        return left

    # additive → term (('+'|'-') term)*
    def additive(self):
        """Analiza expresiones aditivas (suma y resta)
        
        Gramática: additive → term (('+'|'-') term)*
        
        Returns:
            BinOp | Term: Nodo del AST correspondiente a la expresión aditiva
        """
        left = self.term()
        while self._check("PLUS") or self._check("MINUS"):
            op = self.current.lexeme
            self._advance()
            right = self.term()
            left = BinOp(left, op, right)
        return left

    # relational → additive (('<'|'>'|'LE'|'GE') additive)?
    def relational(self):
        """Analiza expresiones relacionales (comparaciones)
        
        Gramática: relational → additive (('<'|'>'|'<='|'>=') additive)?
        
        Returns:
            BinOp | Additive: Nodo del AST correspondiente a la comparación
        """
        left = self.additive()
        while self._check('LT') or self._check('GT') or self._check('LE') or self._check('GE'):
            op = self.current.lexeme
            self._advance()
            right = self.additive()
            left = BinOp(left, op, right)
        return left

    # equality → relational (('=='|'!=' ) relational)*
    def equality(self):
        """Analiza expresiones de igualdad/desigualdad
        
        Gramática: equality → relational (('=='|'!=') relational)*
        
        Returns:
            BinOp | Relational: Nodo del AST correspondiente a la igualdad
        """
        left = self.relational()
        while self._check('EQ') or self._check('NEQ'):
            op = self.current.lexeme
            self._advance()
            right = self.relational()
            left = BinOp(left, op, right)
        return left

    # logical_and → equality ( 'AND' equality )*
    def logical_and(self):
        """Analiza expresiones lógicas AND (&&)
        
        Gramática: logical_and → equality ('&&' equality)*
        
        Returns:
            BinOp | Equality: Nodo del AST correspondiente a la operación AND
        """
        left = self.equality()
        while self._check('AND'):
            op = self.current.lexeme
            self._advance()
            right = self.equality()
            left = BinOp(left, op, right)
        return left

    # logical_or → logical_and ( 'OR' logical_and )*
    def logical_or(self):
        """Analiza expresiones lógicas OR (||)
        
        Gramática: logical_or → logical_and ('||' logical_and)*
        
        Returns:
            BinOp | LogicalAnd: Nodo del AST correspondiente a la operación OR
        """
        left = self.logical_and()
        while self._check('OR'):
            op = self.current.lexeme
            self._advance()
            right = self.logical_and()
            left = BinOp(left, op, right)
        return left

    # ===== SDT tipo simple =====
    def typeof(self, node) -> str:
        """Determina el tipo de una expresión del AST (SDT - Syntax-Directed Translation)
        
        Args:
            node: Nodo del AST a evaluar
            
        Returns:
            str: El tipo del nodo ('int', 'float', 'string', 'bool')
            
        Raises:
            SemanticError: Si hay errores de tipos o incompatibilidades
        """
        if isinstance(node, Num):
            # Determinamos el tipo basado en el valor
            return 'float' if isinstance(node.value, float) else 'int'
        
        if isinstance(node, String):
            return 'string'
        
        if isinstance(node, Var):
            # Verifica que la variable esté declarada
            if node.name not in self.symbols:
                raise SemanticError(f"Uso de variable no declarada '{node.name}'")
            return self.symbols[node.name]
        
        if isinstance(node, UnaryOp):
            # Los operadores unarios solo se aplican a números
            t = self.typeof(node.expr)
            if t not in ('int', 'float'):
                raise SemanticError(f"Unario '{node.op}' espera número, obtuvo {t}")
            return t
        
        if isinstance(node, BinOp):
            tl = self.typeof(node.left)
            tr = self.typeof(node.right)

            # Caso especial: '+' puede ser concatenación de strings o suma numérica
            if node.op == '+':
                # Si ambos son strings -> concatenación
                if tl == 'string' and tr == 'string':
                    return 'string'
                # Si ambos son numéricos -> suma (con promoción a float)
                if tl in ('int', 'float') and tr in ('int', 'float'):
                    return 'float' if 'float' in (tl, tr) else 'int'
                raise SemanticError(f"Operación '+' incompatible entre {tl} y {tr}")

            # Operaciones aritméticas (-, *, /, %)
            if node.op in ('-', '*', '/', '%'):
                if tl in ('int', 'float') and tr in ('int', 'float'):
                    # Promoción de tipo: si alguno es float, el resultado es float
                    return 'float' if 'float' in (tl, tr) else 'int'
                raise SemanticError(f"Operación '{node.op}' espera números, obtuvo {tl} y {tr}")

            # Operaciones de comparación (retornan bool)
            if node.op in ('==', '!=', '<', '>', '<=', '>='):
                # Comparación entre números o entre strings
                if (tl in ('int', 'float') and tr in ('int', 'float')) or (tl == tr == 'string'):
                    return 'bool'
                raise SemanticError(f"Comparación '{node.op}' incompatible entre {tl} y {tr}")

            # Operaciones lógicas (&&, ||) - requieren booleanos
            if node.op in ('&&', '||'):
                if tl == tr == 'bool':
                    return 'bool'
                raise SemanticError(f"Operación lógica '{node.op}' espera booleanos, obtuvo {tl} y {tr}")

        raise SemanticError(f"No sé inferir tipo de {type(node).__name__}")

def run(src: str):
    """Función principal para ejecutar el parser y análisis semántico
    
    Args:
        src: Código fuente a analizar
        
    Imprime:
        - "Parsing Success!" si el análisis sintáctico es correcto
        - "SDT Verified!" si el análisis semántico es correcto
        - Mensajes de error en caso de fallo
    """
    # Fase 1: Análisis léxico (tokenización)
    try:
        tokens = lex(src)
    except Exception as e:
        print("Lexical error...")
        print(str(e))
        return

    p = Parser(tokens)

    # Fase 2: Análisis sintáctico (parsing)
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

    # Fase 3: Validación semántica adicional (SDT)
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
