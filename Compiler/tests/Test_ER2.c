// ERROR SINTÁCTICO - Falta punto y coma
// Este test debe fallar en la fase de análisis sintáctico
// Error esperado: Se esperaba ';' pero se encontró 'int'
//
// Ejecución: py main.py Test_ER2.c
// (Debe fallar en FASE 2: Análisis Sintáctico)

int main() {
    int x = 10  // Falta punto y coma
    int y = 20;
    return x + y;
}
