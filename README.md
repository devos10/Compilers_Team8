<h1 align="center">
  <img src="https://github.com/user-attachments/assets/3abebde3-8ee0-40d0-ae38-82c52246b528" width="60" height="60" />
  ⚙ Proyecto: Lexical Analyzer (Lexer)
  <img src="https://github.com/user-attachments/assets/fe29e172-7262-4289-820a-1c08eecaa61b" width="60" height="60" />
</h1>

Repositorio correspondiente a la *Práctica de Análisis Léxico* dentro de la materia de *Compiladores*.  
Este proyecto implementa un *Lexer* en Python.

---

##Información del equipo
| Nombre completo                     | Número de cuenta |
|----------------------------------   |------------------|
| Araiza Valdés Diego Antonio         | 423032833        |
| Arroyo Solano Victor Julian         | 423529834        |
| Jaramillo Rodríguez Leslie Citlalli | 320318931        |
| Salas Hernández Camila Alexandra    | 320332825        |
| Velazquez Caudillo Osbaldo          | 320341704        |

| Campo        | Detalle        |
|--------------|----------------|
| *Materia*  | Compiladores   |
| *Proyecto* | Lexer (Análisis Léxico) |
| *Semestre* | 2026-1         |

---

## Introducción
El análisis léxico es la primera fase en la construcción de un compilador.  
El *Lexer* recibe el código fuente como entrada y lo convierte en una *secuencia de tokens*.  
Cada token se clasifica en categorías como palabras reservadas, identificadores, operadores, constantes, literales y signos de puntuación.  

---

##Problem Formulation
El objetivo de este proyecto es diseñar e implementar un *analizador léxico* que:  
- Lea un archivo de entrada en un lenguaje basado en C.  
- Identifique y clasifique los tokens.  
- Muestre como salida la lista de tokens junto con su categoría y el conteo total.  

---

##Motivation
Los tokens producidos son los *bloques fundamentales* del compilador.  
En fases posteriores (análisis sintáctico y semántico), la estructura del programa dependerá de que el lexer funcione de forma correcta y robusta.  

---

## Objectives
- Clasificar tokens en las siguientes categorías:
  - *Keyword*
  - *Identifier*
  - *Operator*
  - *Constant*
  - *Literal*
  - *Punctuation sign*
- El programa debe mostrar:
  - *Número de tokens encontrados*.  
  - *Listado completo de tokens con su clasificación*.  

---

##Technologies
- *Lenguaje:* Python  
- *Librerías utilizadas:*
  - re → Expresiones regulares para la definición de tokens.  
  - unittest → Pruebas unitarias del analizador.  

---

##Theoretical Framework
- *Lexeme:* Secuencia de caracteres que corresponde al patrón de un token.  
- *Token:* Unidad mínima reconocida por el compilador (ejemplo: if, +, x).  
- *Lexer:* Programa que agrupa caracteres en tokens y los pasa al parser.  

El diseño se basó en expresiones regulares:  
- Se concatenaron las regex de cada tipo de token con el operador |.  
- Con re.finditer() se buscaron coincidencias en el código fuente.  
- Cada coincidencia se clasificó en su tipo de token correspondiente.  

---

##Development

###Design Considerations
- *Keywords:* if, else, while, int, return, print  
- *Operators:* +, -, *, /, =, ==, !=, <, >, <=, >=, &&, ||  
- *Constants:* [0-9]+  
- *Identifiers:* [a-zA-Z][a-zA-Z0-9_]*  
- *Punctuation:* (, ), {, }, ;, ,  
- *Comments:* //.*  
- *Literals:* "...", '...'  

###Implementation
- Archivo principal: src/lexer.py  
- Clase principal: Lexer  
  - tokenize() → Retorna la lista de tokens (tipo, valor).  
  - get_token_count() → Retorna el número total de tokens.  

---

##Results
El analizador léxico clasifica correctamente los tokens del lenguaje definido.  
Los casos de prueba validan su funcionamiento.  
