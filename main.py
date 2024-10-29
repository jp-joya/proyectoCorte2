import sys
from lexerC import lex  # Import lexer
from parser import Parser  # Import parser

def main():
    if len(sys.argv) != 2:
            print("Uso: python3 main.py <input_file>")
            sys.exit(1)

    input_file = sys.argv[1]

    # Llama al lexer para obtener los tokens
    tokens = lex(input_file)
    
    # Inicializa el parser con los tokens  
    parser = Parser(tokens)
    
    for token in tokens:
         print(token,'\n')
    
    try:
        parser.parse()          # Intenta analizar los tokens
        print("Análisis completado sin errores sintácticos.")
    except SyntaxError as e:
        print(e)
if __name__ == "__main__":
    main()

