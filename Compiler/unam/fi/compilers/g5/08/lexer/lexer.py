from collections import defaultdict  # para agrupar
import re   # Para poder trabajar con expresiones regulares
import sys  # Argumentos de los archivos
import os   # Para trabajar con rutas y extensiones

# Lista de tokens con su nombre y expresión regular asociada
tokens = [
    ("keywords",    r'\b(?:int|bool|float|string|void|for|while|if|else|return)\b'),           # palabras reservadas
    ("identifier",  r'[A-Za-z_]\w*'),                                         # identificadores
    ("punctuacion", r'[,;(){}]'),                                            # símbolos de puntuación
    ("operator",    r'==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|%=|&&|\|\||[+\-*/%<>=!&|]'),  # operadores
    ("constant",    r'\d+(?:\.\d+)?'),                                        # números enteros o decimales
    ("literal",     r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\'')                    # literales de cadena
]

# Compilamos las expresiones regulares para mayor eficiencia (respetando el orden dado arriba)
compiled = [(typ, re.compile(pat)) for typ, pat in tokens]

# Espacios SIN salto de línea para poder contar líneas; el salto de línea se maneja aparte
_WS = re.compile(r'[ \t\r]+')

def lexer(code: str):
    """
    Analizador léxico.
    Devuelve:
        result: lista de tuplas (tipo, lexema)
        counts: dict con el número de tokens por tipo
    NOTA: Se mantienen los mismos nombres y la firma.
    """
    n = len(code)
    pos = 0
    line = 1
    col = 1

    # contador por tipo (usa las llaves de 'tokens' tal cual)
    counts = {typ: 0 for typ, _ in tokens}
    result = []

    def _advance(ch: str):
        nonlocal pos, line, col
        pos += 1
        if ch == '\n':
            line += 1
            col = 1
        else:
            col += 1

    def _advance_n(text: str):
        for ch in text:
            _advance(ch)
            
   

    while pos < n:
        ch = code[pos]

        # Comentario de una línea // ...\n  (se ignora)
        if code.startswith('//', pos):
            while pos < n and code[pos] != '\n':
                _advance(code[pos])
            continue

        # Comentario multi-línea /* ... */ (se ignora)
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

        # Salto de línea (para llevar línea/columna correctas)
        if ch == '\n':
            _advance('\n')
            continue

        # Espacios (sin \n)
        m = _WS.match(code, pos)
        if m:
            _advance_n(m.group(0))
            continue

        # Intentar match con algún token, en el orden dado
        matched = False
        for typ, rgx in compiled:
            m = rgx.match(code, pos)
            if m:
                lexeme = m.group(0)
                result.append((typ, lexeme))
                counts[typ] += 1
                _advance_n(lexeme)
                matched = True
                break
        if matched:
            continue

        # Verificar si es un literal sin cerraranza excepción si detecta error
            
        # Si no se reconoció nada, determinar el tipo de error más probable
        ch = code[pos]
        snippet = code[pos:pos+20].replace('\n', '\\n')
        error_msg = f"Carácter inesperado '{ch}' en L{line} C{col}"
        
        # Dar pistas sobre el error según el contexto
        if ch in '"\'':
            error_msg += " (¿literal de cadena mal formado?)"
        elif ch.isalpha():
            error_msg += " (¿identificador inválido?)"
        elif ch in '+-*/%<>=!&|':
            error_msg += " (¿operador inválido?)"
        
        error_msg += f"\nContexto: {snippet!r}"
        error_msg += "\nSímbolo más cercano encontrado: " + (
            result[-1][1] if result else "ninguno (inicio del archivo)"
        )
        
        raise SyntaxError(error_msg)

    return result, counts


if __name__ == "__main__":
    # Modo CLI sencillo para probar el lexer solo
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if not os.path.isfile(filename):
            print(f"Error: El archivo '{filename}' no existe")
            sys.exit(1)
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
    else:
        # Demo por defecto
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

    tokens_detectados, counts = lexer(code)

    # Agrupar tokens por tipo para mostrar
    groups = defaultdict(list)
    for typ, lexeme in tokens_detectados:
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

