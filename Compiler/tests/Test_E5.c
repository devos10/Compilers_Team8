// IF-ELSE ANIDADOS, FOR ANIDADO, OPERACIONES COMPLEJAS
// Este test verifica: estructuras de control anidadas, expresiones complejas
//
// Ejecución: py main.py Test_E5.c -o Test_E5_outcput
// (genera Test_E5_output.exe)

int main() {
    int resultado = 0;
    int x = 10;
    int y = 5;
    
    // If-else anidado
    if (x > y) {
        if (x > 8) {
            resultado = 100;
        } else {
            resultado = 50;
        }
    } else {
        resultado = 0;
    }
    // resultado = 100
    
    // For anidado - suma acumulada
    int suma = 0;
    int i = 0;
    int j = 0;
    
    for (i = 1; i <= 3; i = i + 1) {
        for (j = 1; j <= 2; j = j + 1) {
            suma = suma + i + j;
        }
    }
    // i=1: j=1,2 -> suma += (1+1)+(1+2) = 2+3 = 5
    // i=2: j=1,2 -> suma += (2+1)+(2+2) = 3+4 = 7, total = 12
    // i=3: j=1,2 -> suma += (3+1)+(3+2) = 4+5 = 9, total = 21
    
    // Operaciones complejas
    int a = 7;
    int b = 3;
    int c = 2;
    int complejo = (a + b) * c - (a - b) / c;
    // complejo = (7+3)*2 - (7-3)/2 = 10*2 - 4/2 = 20 - 2 = 18
    
    // resultado final: 100 + 21 + 18 = 139
    return resultado + suma + complejo;
}
