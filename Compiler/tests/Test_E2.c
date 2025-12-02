// OPERACIONES RELACIONALES, CONDICIONALES IF-ELSE
// Este test verifica: comparaciones, operadores relacionales, control flow con if-else
//
// Ejecución: py main.py Test_E2.c
// (Sin banderas)

int main() {
    int x = 15;
    int y = 10;
    int resultado = 0;
    
    // Comparaciones relacionales
    if (x > y) {
        resultado = 1;
    } else {
        resultado = 0;
    }
    
    int mayor = 0;
    if (x >= 20) {
        mayor = 20;
    } else {
        mayor = x;
    }
    
    int igual = 0;
    if (x == y) {
        igual = 1;
    } else {
        igual = 0;
    }
    
    int diferente = 0;
    if (x != y) {
        diferente = 1;
    } else {
        diferente = 0;
    }
    
    // resultado final: 1 + 15 + 0 + 1 = 17
    return resultado + mayor + igual + diferente;
}
