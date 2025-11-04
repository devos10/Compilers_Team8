"""
adapter_lexer.py - Adaptador entre user_lexer y el parser

Este módulo convierte la salida del lexer personalizado (user_lexer) a un formato
estándar que el parser puede entender. Actúa como una capa de abstracción que
permite cambiar el lexer sin modificar el parser.

Funcionalidad principal:
- Transforma tuplas (tipo, lexema, line, col) en objetos Token
- Mapea tokens de puntuación y operadores a nombres estándar
- Maneja literales numéricos y de cadena
- Añade token EOF al final
"""

from dataclasses import dataclass
from typing import Any, List, Tuple
from . import user_lexer  # tu lexer (puedes reemplazar el archivo)

@dataclass
class Token:
    """Representa un token con información completa
    
    Attributes:
        type: Tipo del token (ej: 'INT', 'ID', 'SEMI')
        lexeme: Texto original del token
        literal: Valor literal (para números y strings)
        pos: Tupla (línea, columna) donde aparece el token
    """
    type: str
    lexeme: str
    literal: Any
    pos: Tuple[int, int]  # (line, column)

# Mapeo de símbolos de puntuación a nombres de tokens
PUNCT_MAP = {
    ';': 'SEMI',       # punto y coma
    '(': 'LPAREN',     # paréntesis izquierdo
    ')': 'RPAREN',     # paréntesis derecho
    '{': 'LBRACE',     # llave izquierda
    '}': 'RBRACE',     # llave derecha
    ',': 'COMMA',      # coma
}

# Mapeo de operadores a nombres de tokens
OP_MAP = {
    '==': 'EQ',        # igualdad
    '!=': 'NEQ',       # desigualdad
    '<=': 'LE',        # menor o igual
    '>=': 'GE',        # mayor o igual
    '&&': 'AND',       # AND lógico
    '||': 'OR',        # OR lógico
    '++': 'INC',       # incremento
    '--': 'DEC',       # decremento
    '+=': 'PLUSEQ',    # suma y asignación
    '-=': 'MINUSEQ',   # resta y asignación
    '*=': 'STAREQ',    # multiplicación y asignación
    '/=': 'SLASHEQ',   # división y asignación
    '=':  'ASSIGN',    # asignación
    '+':  'PLUS',      # suma
    '-':  'MINUS',     # resta
    '*':  'STAR',      # multiplicación
    '/':  'SLASH',     # división
    '<':  'LT',        # menor que
    '>':  'GT',        # mayor que
    '!':  'NOT',       # negación lógica
    '%':  'PERC',      # módulo
}

def tokenize_std(source: str) -> List[Token]:
    """Convierte código fuente a lista de tokens estándar
    
    Este es el punto de entrada principal del adaptador. Toma el código fuente,
    lo pasa por el lexer personalizado, y convierte su salida al formato esperado
    por el parser.
    
    Args:
        source: Código fuente a tokenizar
        
    Returns:
        Lista de objetos Token, incluyendo un token EOF al final
        
    Raises:
        ValueError: Si se encuentra un token no reconocido o no mapeado
    """
    # Llamar al lexer personalizado
    raw_tokens, _counts = user_lexer.lexer(source)  # [(typ, lex[, line, col]), ...]
    out: List[Token] = []

    for item in raw_tokens:
        # Manejar tokens sin información de posición (retrocompatibilidad)
        if len(item) == 2:
            typ, lex = item
            line, col = 1, 1
        else:
            typ, lex, line, col = item

        # Procesamiento según el tipo de token
        if typ == 'keywords':
            # Palabras reservadas
            if lex == 'int':
                out.append(Token('INT', lex, None, (line, col)))
            else:
                # Otras keywords por ahora se tratan como identificadores
                out.append(Token('ID', lex, None, (line, col)))

        elif typ == 'identifier':
            # Identificadores (nombres de variables, funciones, etc.)
            out.append(Token('ID', lex, None, (line, col)))

        elif typ == 'constant':
            # Literales numéricos (int o float)
            # El parser/SDT decidirá si el valor es válido en su contexto
            try:
                val = float(lex) if '.' in lex else int(lex)
            except ValueError:
                val = None
            out.append(Token('NUM', lex, val, (line, col)))

        elif typ == 'punctuacion':
            # Símbolos de puntuación
            t = PUNCT_MAP.get(lex)
            if not t:
                raise ValueError(f"Puntuación no mapeada: {lex} en L{line} C{col}")
            out.append(Token(t, lex, None, (line, col)))

        elif typ == 'operator':
            # Operadores
            t = OP_MAP.get(lex)
            if not t:
                raise ValueError(f"Operador no soportado por la gramática base: {lex} en L{line} C{col}")
            out.append(Token(t, lex, None, (line, col)))

        elif typ == 'literal':
            # Literales de cadena (con comillas simples o dobles)
            # Removemos las comillas del valor literal
            val = lex[1:-1]  # quitamos las comillas
            out.append(Token('STRING', lex, val, (line, col)))

        else:
            raise ValueError(f"Tipo de token desconocido: {typ} en L{line} C{col}")

    # Añadir token EOF (End Of File) al final
    out.append(Token('EOF', '', None, (line if raw_tokens else 1, col if raw_tokens else 1)))
    return out
