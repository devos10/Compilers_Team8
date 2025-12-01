"""
main.py - Punto de entrada del compilador completo

Este módulo coordina todas las fases del compilador:
1. Análisis léxico (tokenización)
2. Análisis sintáctico (parsing)
3. Análisis semántico (validación de tipos)
4. Generación de código intermedio (IR)
5. Generación de código ensamblador (ASM)
6. Ensamblado y enlazado (ejecutable)

Uso:
    python main.py archivo.c                    # Compila a ejecutable
    python main.py archivo.c --show-ir          # Muestra código intermedio
    python main.py archivo.c --show-asm         # Muestra código ensamblador
    python main.py archivo.c --asm-only         # Solo genera .asm (no ensambla)
    python main.py archivo.c -o salida          # Especifica nombre de salida
"""

import sys
import os
import subprocess
from pathlib import Path


def compile_file(input_file: str, output_name: str = None, show_ir: bool = False, 
                 show_asm: bool = False, asm_only: bool = False):

    # Leer archivo fuente
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no existe")
        return False
    
    # === FASE 1: Análisis Léxico ===
    print("=== FASE 1: Análisis Léxico ===")
    from lexer.adapter_lexer import tokenize_std as lex
    
    try:
        tokens = lex(source_code)
        print(f"✓ Tokens generados: {len(tokens)} tokens")
    except Exception as e:
        print(f"✗ Error léxico: {e}")
        return False
    
    # === FASE 2: Análisis Sintáctico ===
    print("\n=== FASE 2: Análisis Sintáctico ===")
    from parser import Parser, SyntaxError_
    
    parser = Parser(tokens)
    try:
        ast = parser.parse()
        print("✓ AST generado correctamente")
    except SyntaxError_ as e:
        print(f"✗ Error sintáctico: {e}")
        return False
    
    # === FASE 3: Análisis Semántico ===
    print("\n=== FASE 3: Análisis Semántico ===")

    # El análisis semántico ya se hace durante el parsing
    print("✓ Análisis semántico completado")
    
    # === FASE 4: Generación de Código Intermedio (IR) ===
    print("\n=== FASE 4: Generación de Código Intermedio ===")
    from ir_generator import generate_ir
    
    try:
        ir_instructions, string_literals = generate_ir(ast)
        print(f"✓ Código IR generado: {len(ir_instructions)} instrucciones")
        
        if show_ir:
            print("\n--- Código Intermedio (IR) ---")
            for instr in ir_instructions:
                print(f"  {instr}")
            print("--- Fin IR ---\n")
    except Exception as e:
        print(f"✗ Error generando IR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # === FASE 5: Generación de Código Ensamblador ===
    print("\n=== FASE 5: Generación de Código Ensamblador ===")
    from asm_generator import generate_asm
    
    try:
        asm_code = generate_asm(ir_instructions, string_literals)
        print("✓ Código ensamblador generado")
        
        if show_asm:
            print("\n--- Código Ensamblador (x86-64) ---")
            print(asm_code)
            print("--- Fin ASM ---\n")
    except Exception as e:
        print(f"✗ Error generando ensamblador: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Determinar nombre del archivo .asm
    if output_name:
        asm_file = f"{output_name}.asm"
    else:
        # Usar el nombre del archivo de entrada
        base_name = Path(input_file).stem
        asm_file = f"{base_name}.asm"
    
    # Guardar archivo .asm
    try:
        with open(asm_file, "w", encoding="utf-8") as f:
            f.write(asm_code)
        print(f"✓ Archivo ensamblador guardado: {asm_file}")
    except Exception as e:
        print(f"✗ Error guardando .asm: {e}")
        return False
    
    if asm_only:
        print("\n✓ Compilación completada (solo ASM)")
        return True
    
    # === FASE 6: Ensamblado y Enlazado ===
    print("\n=== FASE 6: Ensamblado y Enlazado ===")
    
    obj_file = asm_file.replace('.asm', '.obj')
    exe_file = asm_file.replace('.asm', '.exe')
    
    # Ensamblar con NASM
    print("Ensamblando con NASM...")
    nasm_cmd = ['nasm', '-f', 'win64', asm_file, '-o', obj_file]
    
    try:
        result = subprocess.run(nasm_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Error en NASM: {result.stderr}")
            print("\nNota: Asegúrate de tener NASM instalado:")
            print("  Descarga: https://www.nasm.us/")
            return False
        print(f"✓ Objeto generado: {obj_file}")
    except FileNotFoundError:
        print("✗ NASM no encontrado. Instala NASM:")
        print("  Descarga: https://www.nasm.us/")
        return False
    
    # Enlazar con GCC
    print("Enlazando con GCC...")
    gcc_cmd = ['gcc', obj_file, '-o', exe_file]
    
    try:
        result = subprocess.run(gcc_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Error en GCC: {result.stderr}")
            print("\nNota: Asegúrate de tener GCC/MinGW instalado:")
            print("  Descarga: https://winlibs.com/")
            return False
        print(f"✓ Ejecutable generado: {exe_file}")
    except FileNotFoundError:
        print("✗ GCC no encontrado. Instala MinGW-w64:")
        print("  Descarga: https://winlibs.com/")
        return False
    
    print("\n" + "="*50)
    print("✓ COMPILACIÓN COMPLETADA EXITOSAMENTE")
    print("="*50)
    print(f"\nEjecutable: {exe_file}")
    print(f"Para ejecutar: .\\{exe_file}")
    
    return True


def main():
    """Función principal del programa"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Compilador completo: C → ASM → Ejecutable',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py programa.c              # Compila a ejecutable
  python main.py programa.c -o salida    # Especifica nombre
  python main.py programa.c --show-ir    # Muestra código IR
  python main.py programa.c --show-asm   # Muestra código ASM
  python main.py programa.c --asm-only   # Solo genera .asm
        """
    )
    
    parser.add_argument('input', help='Archivo de código fuente (.c)')
    parser.add_argument('-o', '--output', help='Nombre del ejecutable de salida (sin extensión)')
    parser.add_argument('--show-ir', action='store_true', help='Mostrar código intermedio (IR)')
    parser.add_argument('--show-asm', action='store_true', help='Mostrar código ensamblador')
    parser.add_argument('--asm-only', action='store_true', help='Solo generar .asm (no ensamblar)')
    
    args = parser.parse_args()
    
    # Compilar archivo
    success = compile_file(
        args.input,
        args.output,
        args.show_ir,
        args.show_asm,
        args.asm_only
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
