"""
__main__.py - Punto de entrada del programa

Este módulo permite ejecutar el parser desde la línea de comandos.
Puede recibir un archivo como argumento o leer desde la entrada estándar.

Uso:
    python -m 08 archivo.txt       # Lee código desde un archivo
    python -m 08                   # Lee código desde stdin
"""

def main():
    """Función principal del programa
    
    Lee el código fuente desde un archivo (si se proporciona como argumento)
    o desde la entrada estándar, y ejecuta el análisis léxico, sintáctico y semántico.
    """
    import sys
    from main import run
    
    # Verificar si se proporcionó un archivo como argumento
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, "r", encoding="utf-8") as f:
                src = f.read()
        except FileNotFoundError:
            print(f"Error: El archivo '{filename}' no existe")
            return
    else:
        # Si no hay archivo, leer desde stdin
        print("Introduce el código fuente (finaliza con Ctrl+Z y Enter en Windows, Ctrl+D en Unix):")
        src = sys.stdin.read()

    # Ejecutar el parser
    run(src)

if __name__ == "__main__":
    main()
