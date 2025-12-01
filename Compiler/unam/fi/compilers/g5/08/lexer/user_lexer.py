"""
user_lexer.py - Analizador léxico (lexer) personalizado

Este módulo implementa un analizador léxico completo que:
- Reconoce tokens mediante expresiones regulares
- Maneja comentarios de una línea (//) y multi-línea (/* */)
- Rastrea números de línea y columna para mensajes de error
- Soporta literales de cadena con caracteres de escape
- Proporciona manejo de errores detallado

El lexer es la primera fase del compilador: convierte el código fuente
en una secuencia de tokens que el parser puede procesar.
"""

from collections import defaultdict  # para agrupar
import re   # Para poder trabajar con expresiones regulares
import sys  # Argumentos de los archivos
import os   # Para trabajar con rutas y extensiones

# Lista de tokens con su nombre y expresión regular asociada
# El orden importa: se intenta coincidir en el orden especificado
tokens = [
    ("keywords",    r'\b(?:int|bool|float|string|void|for|while|if|else|return)\b'),    # palabras reservadas
    ("identifier",  r'[A-Za-z_]\w*'),                                                   # identificadores
    ("punctuacion", r'[,;(){}]'),                                                      # símbolos de puntuación
    ("operator",    r'==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|%=|&&|\|\||[+\-*/%<>=!&|]'),    # operadores
    ("constant",    r'\d+(?:\.\d+)?'),                                                  # números enteros o decimales
    ("literal",     r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\'')                              # literales de cadena
]

# Compilamos las expresiones regulares para mayor eficiencia (respetando el orden dado arriba)
compiled = [(typ, re.compile(pat)) for typ, pat in tokens]

# Espacios SIN salto de línea para poder contar líneas; el salto de línea se maneja aparte
_WS = re.compile(r'[ \t\r]+')

def lexer(code: str):
    """Analizador léxico principal
    
    Procesa el código fuente caracter por caracter, identificando tokens
    y manteniendo seguimiento de líneas y columnas para mensajes de error.
    
    Args:
        code: Código fuente a analizar
        
    Returns:
        Tupla (result, counts) donde:
        - result: lista de tuplas (tipo, lexema, línea, columna)
        - counts: diccionario con el conteo de tokens por tipo
        
    Raises:
        SyntaxError: Si se encuentra un carácter inesperado o token mal formado
    """
    n = len(code)
    pos = 0       # Posición actual en el código
    line = 1      # Línea actual
    col = 1       # Columna actual

    # Contador por tipo (usa las llaves de 'tokens' tal cual)
    counts = {typ: 0 for typ, _ in tokens}
    result = []

    def _advance(ch: str):
        """Avanza una posición en el código, actualizando línea y columna"""
        nonlocal pos, line, col
        pos += 1
        if ch == '\n':
            line += 1
            col = 1
        else:
            col += 1

    def _advance_n(text: str):
        """Avanza múltiples posiciones procesando un string completo"""
        for ch in text:
            _advance(ch)

    while pos < n:
        ch = code[pos]

        # ===== Manejo de comentarios =====
        # Comentario de una línea: // hasta el final de la línea (se ignora)
        if code.startswith('//', pos):
            while pos < n and code[pos] != '\n':
                _advance(code[pos])
            continue

        # Comentario multi-línea: /* ... */ (se ignora)
        if code.startswith('/*', pos):
            _advance('/') ; _advance('*')
            cerrado = False
            while pos < n:
                if code.startswith('*/', pos):
                    _advance('*'); _advance('/')
                    cerrado = True
                    break
                _advance(code[pos])
            if not cerrado:
                raise SyntaxError(f"Comentario /* sin cierre en L{line} C{col}")
            continue

        # ===== Manejo de espacios en blanco =====
        # Salto de línea (se cuenta pero no se tokeniza)
        if ch == '\n':
            _advance('\n')
            continue

        # Espacios horizontales (tab, espacio) - se ignoran
        m = _WS.match(code, pos)
        if m:
            _advance_n(m.group(0))
            continue

        # ===== Reconocimiento de tokens =====
        # Intentar match con algún token, en el orden dado
        matched = False
        for typ, rgx in compiled:
            m = rgx.match(code, pos)
            if m:
                lexeme = m.group(0)
                start_line, start_col = line, col
                result.append((typ, lexeme, start_line, start_col))
                counts[typ] += 1
                _advance_n(lexeme)
                matched = True
                break
        if matched:
            continue

        # ===== Manejo de errores =====
        # Si no se reconoció nada, reportar carácter inesperado (con línea y columna)
        snippet = code[pos:pos+20].replace('\n', '\\n')
        raise SyntaxError(f"Carácter inesperado '{code[pos]}' en L{line} C{col} cerca de: {snippet!r}")

    return result, counts


if __name__ == "__main__":
    """Modo de prueba standalone del lexer
    
    Permite probar el lexer de forma independiente, ya sea:
    - Pasando un archivo como argumento: python user_lexer.py archivo.txt
    - Usando el código de demostración por defecto
    """
    # Modo CLI sencillo para probar el lexer solo
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if not os.path.isfile(filename):
            print(f"Error: El archivo '{filename}' no existe")
            sys.exit(1)
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
    else:
        # Demo por defecto: código de prueba
        code = """\
// Demo por defecto
int main() {
    int x = 10;
    // comentario de línea
    /* comentario
       multi-línea */
    x = x + 2*(3+4);
    return x;
}
"""

    # Ejecutar el lexer
    tokens_detectados, counts = lexer(code)

    # Agrupar tokens por tipo para mostrar
    groups = defaultdict(list)
    for typ, lexeme, _, _ in tokens_detectados:
        groups[typ].append(lexeme)

    print("\nTOKENS agrupados:")
    for tipo, valores in groups.items():
        valores_unicos = list(dict.fromkeys(valores))  # elimina duplicados manteniendo orden
        print(f"{tipo}: {', '.join(repr(v) for v in valores_unicos)}")

    print("\nCANTIDADES:")
    for tipo, cantidad in counts.items():
        print(f"{tipo}: {cantidad}")

    # Total de tokens detectados (de la entrada)
    print(f"\nTotal= {len(tokens_detectados)}")
