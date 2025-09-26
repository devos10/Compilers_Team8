from collections import defaultdict #para agrupar
import re # Para poder trabajar con las expresiones regulares
import sys # Argumentos de los archivos
import os # Para trabajar con rutas y extensiones 

# Lista de tokens con su nombre y expresión regular asociada
tokens = [
    ("keywords",    r'\b(?:int|float|for|while|if|else|return)\b'),   # palabras reservadas
    ("identifier",  r'[a-zA-Z_]\w*'),                                # identificadores
    ("punctuacion", r'[,;(){}]'),                                    # símbolos de puntuación
    ("operator",    r'==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|%=|&&|\|\||[+\-*/%<>=!&|]'), # operadores
    ("constant",    r'\d+(?:\.\d+)?'),                               # números enteros o decimales
    ("literal",     r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\'')           # literales de cadena
]

# Compilamos las expresiones regulares para mayor eficiencia
compiled = [(typ, re.compile(pat)) for typ, pat in tokens]

# Expresión regular para detectar espacios en blanco
_WS = re.compile(r'\s+')  # evita que los espacios cuenten como tokens

def lexer(code: str):
    pos = 0
    n = len(code)

    # Diccionario con la cuenta de cada tipo de token inicializada en 0
    counts = {typ: 0 for typ, _ in tokens}  # Ejemplo: {"keywords":0, "identifier":0, ...}

    result = []  # Aquí se guardarán todos los tokens encontrados como tuplas (tipo, lexema)

    # Recorremos el código carácter por carácter
    while pos < n:
        # Ignorar espacios en blanco
        m = _WS.match(code, pos)
        if m:
            pos = m.end()
            continue

        # Probar si el fragmento actual del código coincide con algún token
        for typ, rgx in compiled:
            m = rgx.match(code, pos)
            if m:  
                lexeme = m.group(0)  # obtenemos el valor exacto del token
                result.append((typ, lexeme))   # agregamos el token encontrado a la lista
                counts[typ] += 1               # incrementamos el contador de su tipo
                pos = m.end()                  # avanzamos la posición en el código
                break
        else:
            # Si no coincidió con ningún token, lanzamos error de sintaxis
            raise SyntaxError(f"Carácter inesperado: {code[pos]!r} en posición {pos}")

    return result, counts   # regresamos lista de tokens y sus totales

if __name__ == "__main__":
    
    Piv = 0   # verificar si le pasamos un archivo como argumento si es =1 no se pasa archivo y trabajr con el codigo por default si es 0 entonces si recibio archivo
    
    # Si no se pasa archivo como argumento, usamos código por defecto
    if len(sys.argv) < 2:
        Piv = 1
        code = '''
        int main() {
            int x = 10;
            print("Hola mundo", x);
            return 0;
        }
        '''
    
    # Si se pasa archivo como argumento
    if (Piv==0):    
        filename = sys.argv[1]

        # Verificar que el archivo existe
        if not os.path.isfile(filename):
            print(f"Error: El archivo '{filename}' no existe")
            sys.exit(1)
        
        # Verificar que tenga extensión .txt
        if not filename.endswith((".txt")):
            print("Error: El archivo debe tener extensión .txt")
            sys.exit(1)
        
        print("El archivo a utilizar es:", sys.argv[1])
        
        # Leemos el contenido del archivo
        with open(filename, "r") as f:
            code = f.read()
    
    # Ejecutamos el lexer
    tokens, counts = lexer(code)

    # Agrupamos los tokens por tipo usando defaultdict
    groups = defaultdict(list)
    for tipo, valor in tokens:
        groups[tipo].append(valor)
    
    # Mostramos tokens encontrados
    print("\nTOKENS agrupados:")
    for tipo, valores in groups.items():
        # dict.fromkeys elimina duplicados pero conserva el orden
        valores_unicos = list(dict.fromkeys(valores))
        print(f"{tipo}: {', '.join(repr(v) for v in valores_unicos)}")

    # Mostramos las cantidades por tipo
    print("\nCANTIDADES:")
    for tipo, cantidad in counts.items():
        print(f"{tipo}: {cantidad}")

    # Mostramos el total de tokens detectados
    print(f"\nTotal= {len(tokens)}")
