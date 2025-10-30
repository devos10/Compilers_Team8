# adapter_lexer.py
# Adapta la salida de user_lexer.lexer(code) -> lista de (tipo, lexema [, line, col])
# a una lista de Token estándar que el parser entiende.

from dataclasses import dataclass
from typing import Any, List, Tuple
from . import user_lexer  # tu lexer (puedes reemplazar el archivo)

@dataclass
class Token:
    type: str
    lexeme: str
    literal: Any
    pos: Tuple[int, int]  # (line, column)

PUNCT_MAP = {
    ';': 'SEMI',
    '(': 'LPAREN',
    ')': 'RPAREN',
    '{': 'LBRACE',
    '}': 'RBRACE',
    ',': 'COMMA',
}

OP_MAP = {
    '==': 'EQ',
    '!=': 'NEQ',
    '<=': 'LE',
    '>=': 'GE',
    '&&': 'AND',
    '||': 'OR',
    '++': 'INC',
    '--': 'DEC',
    '+=': 'PLUSEQ',
    '-=': 'MINUSEQ',
    '*=': 'STAREQ',
    '/=': 'SLASHEQ',
    '=':  'ASSIGN',
    '+':  'PLUS',
    '-':  'MINUS',
    '*':  'STAR',
    '/':  'SLASH',
    '<':  'LT',
    '>':  'GT',
    '!':  'NOT',
}

def tokenize_std(source: str) -> List[Token]:
    raw_tokens, _counts = user_lexer.lexer(source)  # [(typ, lex[, line, col]), ...]
    out: List[Token] = []

    for item in raw_tokens:
        if len(item) == 2:
            typ, lex = item
            line, col = 1, 1
        else:
            typ, lex, line, col = item

        if typ == 'keywords':
            if lex == 'int':
                out.append(Token('INT', lex, None, (line, col)))
            else:
                # Otras keywords: por ahora como ID
                out.append(Token('ID', lex, None, (line, col)))

        elif typ == 'identifier':
            out.append(Token('ID', lex, None, (line, col)))

        elif typ == 'constant':
            # int o float (si contiene punto). El parser/SDT decidirá si es válido.
            try:
                val = float(lex) if '.' in lex else int(lex)
            except ValueError:
                val = None
            out.append(Token('NUM', lex, val, (line, col)))

        elif typ == 'punctuacion':
            t = PUNCT_MAP.get(lex)
            if not t:
                raise ValueError(f"Puntuación no mapeada: {lex} en L{line} C{col}")
            out.append(Token(t, lex, None, (line, col)))

        elif typ == 'operator':
            t = OP_MAP.get(lex)
            if not t:
                raise ValueError(f"Operador no soportado por la gramática base: {lex} en L{line} C{col}")
            out.append(Token(t, lex, None, (line, col)))

        elif typ == 'literal':
            # El parser base no soporta strings; lo marcamos como error temprano
            raise ValueError(f"Literal de cadena no soportado: {lex} en L{line} C{col}")

        else:
            raise ValueError(f"Tipo de token desconocido: {typ} en L{line} C{col}")

    # EOF final
    out.append(Token('EOF', '', None, (line if raw_tokens else 1, col if raw_tokens else 1)))
    return out
