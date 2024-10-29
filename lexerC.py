# Palabras reservadas de Python
reserved_words = {
    'False', 'await', 'else', 'import',
    'None', 'break', 'except', 'in', 'raise',
    'True', 'class', 'finally', 'is', 'return',
    'and', 'continue', 'for', 'lambda', 'try',
    'as', 'def', 'from', 'nonlocal', 'while',
    'assert', 'del', 'global', 'not', 'with',
    'async', 'elif', 'if', 'or', 'yield', 'print'
}

# Palabras claves suaves
soft_keywords = {'match', 'case', 'type', '_', 'pass'}

# Operadores
operators = {
    '+', '-', '*', '**', '/', '//', '%', '@',
    '<<', '>>', '&', '|', '^', '~', ':=',
    '<', '>', '<=', '>=', '==', '!=', "!"
}

# Delimitadores
delimiters = {
    '(', ')', '[', ']', '{', '}', ',', ':', '.', ';', '@', '=', 
    '->', '+=', '-=', '*=', '/=', '//=', '%=', '@=', '&=', '|=', '^=', 
    '>>=', '<<=', '**='
}

# Identificar tipos de caracteres
def is_digit(c):
    return '0' <= c <= '9'

def is_letter(c):
    return 'a' <= c <= 'z' or 'A' <= c <= 'Z'

def is_whitespace(c):
    return c in ' \t'

def is_operator(c):
    return c in operators

def is_delimiter(c):
    return c in delimiters

def is_valid_start(c):
    return is_letter(c) or c == '_'

def is_valid_identifier(s):
    return s[0] == '_' or is_letter(s[0])

# Analizador léxico
def lex(file_input):
    with open(file_input, 'r') as file:
        content = file.readlines()  # Leer línea por línea

    tokens = []
    line_num = 0
    column_num = 1
    indent_stack = [0]  # Pila de niveles de indentación para rastrear la profundidad actual

    for line in content:
        line_num += 1
        stripped_line = line.lstrip()  # Línea sin espacios iniciales

        # Ignorar líneas en blanco
        if not stripped_line:
            continue

        # Calcular la cantidad de espacios/tabs al inicio de la línea
        indent_level = len(line) - len(stripped_line)

        # Generar tokens de INDENT o DEDENT según corresponda
        if indent_level > indent_stack[-1]:  # Aumento de indentación
            indent_stack.append(indent_level)
            tokens.append(('tk_indent', '', line_num, column_num))
        while indent_level < indent_stack[-1]:  # Reducción de indentación
            indent_stack.pop()
            tokens.append(('tk_dedent', '', line_num, column_num))

        # Generar token de nueva línea
        tokens.append(('tk_newline', '', line_num, column_num))

        # Restablecer column_num para la nueva línea
        column_num = 1

        # Procesar la línea actual
        i = 0
        while i < len(stripped_line):
            char = stripped_line[i]

            # Ignorar espacios en blanco
            if is_whitespace(char):
                column_num += 1
                i += 1
                continue

            # Comentarios (ignorar línea)
            if char == '#':
                break  # Ignora el resto de la línea

            # Palabras reservadas y identificadores
            if is_letter(char) or char == '_':
                start = i
                while i < len(stripped_line) and (is_letter(stripped_line[i]) or is_digit(stripped_line[i]) or stripped_line[i] == '_'):
                    i += 1
                lexeme = stripped_line[start:i]
                if not is_valid_identifier(lexeme):
                    print(f'>>> Error léxico (línea {line_num}, posición {column_num}): identificador no válido "{lexeme}".')
                    tokens.append(('tk_error', f'identificador no válido: {lexeme}', line_num, column_num))
                elif lexeme in reserved_words:
                    tokens.append((f'tk_{lexeme}', lexeme, line_num, column_num))
                elif lexeme in soft_keywords:
                    tokens.append((f'tk_{lexeme}', lexeme, line_num, column_num))
                else:
                    tokens.append(('id', lexeme, line_num, column_num))
                column_num += (i - start)
                continue

            # Números enteros y flotantes
            if is_digit(char):
                start = i
                is_float = False
                while i < len(stripped_line) and is_digit(stripped_line[i]):
                    i += 1
                if i < len(stripped_line) and stripped_line[i] == '.':
                    is_float = True
                    i += 1
                    while i < len(stripped_line) and is_digit(stripped_line[i]):
                        i += 1
                lexeme = stripped_line[start:i]
                token_type = 'tk_float' if is_float else 'tk_entero'
                tokens.append((token_type, lexeme, line_num, column_num))
                column_num += (i - start)
                continue

            # Literales imaginarios
            if is_digit(char) or char == '.':
                start = i
                while i < len(stripped_line) and (is_digit(stripped_line[i]) or stripped_line[i] == '.'):
                    i += 1
                if i < len(stripped_line) and (stripped_line[i] == 'j' or stripped_line[i] == 'J'):
                    i += 1
                    tokens.append(('tk_imag', stripped_line[start:i], line_num, column_num))
                    column_num += (i - start)
                else:
                    lexeme = stripped_line[start:i]
                    token_type = 'tk_float' if '.' in lexeme else 'tk_entero'
                    tokens.append((token_type, lexeme, line_num, column_num))
                continue

            # Operadores
            if char in operators:
                start = i
                i += 1
                while i < len(stripped_line) and stripped_line[start:i] in operators:
                    i += 1
                lexeme = stripped_line[start:i-1]
                tokens.append((f'tk_op_{lexeme}', lexeme, line_num, column_num))
                column_num += (i - start)
                continue

            # Delimitadores
            if char in delimiters:
                tokens.append((f'tk_delim_{char}', char, line_num, column_num))
                column_num += 1
                i += 1
                continue

            # Cadenas de texto (entre comillas)
            if char == '"':
                start = i
                i += 1
                while i < len(stripped_line) and stripped_line[i] != '"':
                    i += 1
                if i < len(stripped_line):
                    i += 1
                    lexeme = stripped_line[start:i]
                    tokens.append(('tk_cadena', lexeme, line_num, column_num))
                    column_num += (i - start)
                else:
                    print(f'>>> Error léxico (línea {line_num}, posición {column_num}): cadena de texto sin cierre.')
                    tokens.append(('tk_error', 'cadena sin cierre', line_num, column_num))
                continue

            # Error léxico para caracteres no reconocidos
            if char.isprintable() and not (is_whitespace(char) or is_letter(char) or is_digit(char) or is_operator(char) or is_delimiter(char)):
                print(f'>>> Error léxico (línea {line_num}, posición {column_num}): caracter no reconocido "{char}".')
                tokens.append(('tk_error', f'caracter no reconocido: {char}', line_num, column_num))
                i += 1
                column_num += 1
                continue

            i += 1
            column_num += 1

    # Al final del archivo, generar tokens DEDENT para volver al nivel 0
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(('tk_dedent', '', line_num, column_num))

    return tokens

def write_tokens_to_file(tokens, output_file):
    with open(output_file, 'w') as f:
        for token in tokens:
            if len(token) == 3:
                f.write(f'<{token[0]},{token[1]},{token[2]}>\n')
            else:
                f.write(f'<{token[0]},{token[1]},{token[2]},{token[3]}>\n')
