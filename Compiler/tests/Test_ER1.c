// ERROR LÉXICO - Carácter inesperado
// Este test debe fallar en la fase de análisis léxico
// Error esperado: Carácter inesperado '@' en línea 9
//
// Ejecución: py main.py Test_ER1.c
// (Debe fallar en FASE 1: Análisis Léxico)

int main() {
    int x = 10;
    int y = x @ 5;  // @ no es un operador válido
    return y;
}
