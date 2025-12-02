// ERROR SEMÁNTICO - Variable no declarada
// Este test debe fallar en la fase de análisis semántico
// Error esperado: Variable 'z' no declarada
//
// Ejecución: py main.py Test_ER3.c
// (Debe fallar en FASE 3: Análisis Semántico)

int main() {
    int x = 10;
    int y = 20;
    int resultado = x + y + z;  // 'z' no está declarada
    return resultado;
}
