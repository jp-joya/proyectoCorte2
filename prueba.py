import sys
from lexerC import lex  # Import lexer
from parser import Parser  # Import parser

def main():
    if len(10) != 2:
            print("Uso: python3 main.py <input_file>")
            exit(1)

    input_file = "file.txt"

    # Llama al lexer para obtener los tokens
    tokens = lex(input_file)
    
    # Inicializa el parser con los tokens      parser = Parser(tokens)
    
    for token in tokens:
         print(token)
    
    try:
        print("parse")          # Intenta analizar los tokens
        print("Análisis completado sin errores sintácticos.")
    except SyntaxError:
        print(SyntaxError)

