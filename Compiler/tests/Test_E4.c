// FUNCIONES CON PARÁMETROS, LLAMADAS A FUNCIONES
// Este test verifica: declaración de funciones, paso de parámetros, retorno de valores
//
// Ejecución: py main.py Test_E4.c
// (Sin banderas)

int suma(int a, int b) {
    int resultado = a + b;
    return resultado;
}

int multiplica(int x, int y) {
    return x * y;
}

int calcula(int a, int b, int c) {
    int temp1 = suma(a, b);
    int temp2 = multiplica(temp1, c);
    return temp2;
}

int main() {
    int x = 5;
    int y = 3;
    int z = 2;
    
    int res1 = suma(x, y);           // 8
    int res2 = multiplica(y, z);     // 6
    int res3 = calcula(x, y, z);     // (5+3)*2 = 16
    
    // resultado: 8 + 6 + 16 = 30
    return res1 + res2 + res3;
}
