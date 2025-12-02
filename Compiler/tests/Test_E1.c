// ASIGNACIONES SIMPLES, OPERACIONES BINARIAS, RETURN
// Este test verifica: declaraciones, asignaciones, operaciones aritméticas básicas
//
// Ejecución: py main.py Test_E1.c --show-ir --show-asm
// (Muestra IR y ASM, genera .exe)

int main() {
    int a = 10;
    int b = 5;
    int suma = a + b;
    int resta = a - b;
    int mult = a * b;
    int div = a / b;
    int mod = a % b;
    
    int resultado = (suma + resta) * mult - div + mod;
    // resultado = (15 + 5) * 50 - 2 + 0 = 20 * 50 - 2 = 998
    
    return resultado;
}
