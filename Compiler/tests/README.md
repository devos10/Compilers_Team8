# 📁 Carpeta de Tests del Compilador

Esta carpeta contiene casos de prueba para validar todas las fases del compilador.

---

## ✅ Casos de Éxito (Test_E1 - Test_E5)

### **Test_E1.c** - Operaciones Básicas
- **Características:** Asignaciones simples, operaciones binarias (+, -, *, /, %), return
- **Ejecución:** `py main.py tests\Test_E1.c`
- **Resultado esperado:** Retorna 998

### **Test_E2.c** - Condicionales
- **Características:** Operaciones relacionales (<, >, <=, >=, ==, !=), if-else
- **Ejecución:** `py main.py tests\Test_E2.c --show-ir --show-asm`
- **Resultado esperado:** Retorna 17
- **Banderas:** Muestra IR y ASM, genera .exe

### **Test_E3.c** - Ciclos y Unarios
- **Características:** While loop, for loop, operadores unarios (-)
- **Ejecución:** `py main.py tests\Test_E3.c --asm-only`
- **Resultado esperado:** Solo genera .asm (NO .exe)
- **Banderas:** Solo ensamblador, no ensambla

### **Test_E4.c** - Funciones
- **Características:** Declaración de funciones, parámetros, llamadas, retornos
- **Ejecución:** `py main.py tests\Test_E4.c --show-ir`
- **Resultado esperado:** Retorna 30
- **Banderas:** Muestra IR, genera .exe

### **Test_E5.c** - Estructuras Complejas
- **Características:** If-else anidados, for anidado, expresiones complejas
- **Ejecución:** `py main.py tests\Test_E5.c --show-ir --show-asm -o Test_E5_output`
- **Resultado esperado:** Retorna 139
- **Banderas:** Muestra IR y ASM, genera Test_E5_output.exe

---

## ❌ Casos de Error (Test_ER1 - Test_ER6)

### **Test_ER1.c** - Error Léxico
- **Error:** Carácter inesperado '@'
- **Fase de fallo:** FASE 1 - Análisis Léxico
- **Ejecución:** `py main.py tests\Test_ER1.c`
- **Mensaje esperado:** `✗ Error léxico: Carácter inesperado '@' en L10 C15`

### **Test_ER2.c** - Error Sintáctico
- **Error:** Falta punto y coma
- **Fase de fallo:** FASE 2 - Análisis Sintáctico
- **Ejecución:** `py main.py tests\Test_ER2.c`
- **Mensaje esperado:** `✗ Error sintáctico: Se esperaba ';'`

### **Test_ER3.c** - Error Semántico
- **Error:** Variable no declarada 'z'
- **Fase de fallo:** FASE 2 - Análisis Sintáctico (valida durante parsing)
- **Ejecución:** `py main.py tests\Test_ER3.c`
- **Mensaje esperado:** `SemanticError: Uso de variable no declarada 'z'`

### **Test_ER4.c** - Error Sintáctico (paréntesis)
- **Error:** Falta ')' en if statement
- **Fase de fallo:** FASE 2 - Análisis Sintáctico
- **Ejecución:** `py main.py tests\Test_ER4.c`
- **Mensaje esperado:** `✗ Error sintáctico`

### **Test_ER5.c** - Error Semántico (función)
- **Error:** Función 'calcular' no declarada
- **Fase de fallo:** FASE 2 - Análisis Sintáctico (valida durante parsing)
- **Ejecución:** `py main.py tests\Test_ER5.c`
- **Mensaje esperado:** `SemanticError: Función 'calcular' no declarada`

### **Test_ER6.c** - Archivo Vacío
- **Error:** No contiene función main
- **Fase de fallo:** FASE 2 - Análisis Sintáctico
- **Ejecución:** `py main.py tests\Test_ER6.c`
- **Mensaje esperado:** Error sintáctico o EOF inesperado

---

## 📊 Resumen de Cobertura

### Características Probadas:
- ✅ Declaraciones de variables
- ✅ Asignaciones simples y compuestas
- ✅ Operaciones binarias: +, -, *, /, %
- ✅ Operaciones relacionales: <, >, <=, >=, ==, !=
- ✅ Operaciones unarias: -
- ✅ Control flow: if, if-else, if-else anidados
- ✅ Ciclos: while, for, for anidado
- ✅ Funciones: declaración, parámetros (hasta 4), llamadas, retornos
- ✅ Expresiones complejas

### Errores Probados:
- ✅ Error léxico (carácter inválido)
- ✅ Error sintáctico (falta ;)
- ✅ Error sintáctico (falta paréntesis)
- ✅ Error semántico (variable no declarada)
- ✅ Error semántico (función no declarada)
- ✅ Archivo sin contenido válido

### Banderas Probadas:
- ✅ Sin banderas (compilación completa)
- ✅ `--show-ir` (muestra IR)
- ✅ `--show-asm` (muestra ensamblador)
- ✅ `--show-ir --show-asm` (muestra ambos)
- ✅ `--asm-only` (solo genera .asm)
- ✅ `-o nombre` (especifica nombre de salida)

---

## 🧪 Ejecutar Todos los Tests

### Tests de éxito:
```bash
py main.py tests\Test_E1.c
py main.py tests\Test_E2.c --show-ir --show-asm
py main.py tests\Test_E3.c --asm-only
py main.py tests\Test_E4.c --show-ir
py main.py tests\Test_E5.c --show-ir --show-asm -o Test_E5_output
```

### Tests de error:
```bash
py main.py tests\Test_ER1.c
py main.py tests\Test_ER2.c
py main.py tests\Test_ER3.c
py main.py tests\Test_ER4.c
py main.py tests\Test_ER5.c
py main.py tests\Test_ER6.c
```

---

## 📝 Notas

- Los tests de éxito deben compilar sin errores y generar ejecutables funcionales
- Los tests de error deben fallar en la fase específica indicada
- Cada test incluye comentarios explicativos sobre qué prueba y cómo ejecutarlo
- Los valores de retorno calculados están documentados en los comentarios
