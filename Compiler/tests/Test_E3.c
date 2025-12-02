// CICLOS WHILE Y FOR, OPERACIONES UNARIAS
// Este test verifica: loops (while, for), operadores unarios, acumuladores
//
// Ejecución: py main.py Test_E3.c --asm-only
// (NO ensambla ni enlaza)

int main() {
    int suma = 0;
    int contador = 1;
    
    // While loop - suma de 1 a 5
    while (contador <= 5) {
        suma = suma + contador;
        contador = contador + 1;
    }
    // suma = 1+2+3+4+5 = 15
    
    // For loop - resta de 5 a 1
    int resta = 0;
    int i = 0;
    for (i = 5; i > 0; i = i - 1) {
        resta = resta + i;
    }
    // resta = 5+4+3+2+1 = 15
    
    // Operación unaria
    int negativo = -10;
    int positivo = -negativo;  // positivo = 10
    
    // resultado: 15 + 15 + 10 = 40
    return suma + resta + positivo;
}
