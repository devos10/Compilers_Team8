// ERROR SINTÁCTICO Y SEMÁNTICO - Múltiples errores
// Este test debe fallar primero en sintaxis, luego en semántica
// Error esperado: Falta ')' en la línea 9
//
// Ejecución: py main.py Test_ER4.c
// (Debe fallar en FASE 2: Análisis Sintáctico)

int main() {
    int x = 10;
    if (x > 5 {  // Falta ')' después de la condición
        int y = x + w;  // 'w' no declarada (no se alcanza a validar)
    }
    return x;
}
