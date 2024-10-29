class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index] if self.tokens else None
        self.past_token = None

    def error(self, message):
        if(self.current_token):
            line, column = self.current_token[2], self.current_token[3]
        else:
            line, column = self.past_token[2], self.past_token[3]

        raise SyntaxError(f"Error sintáctico (línea {line}, columna {column}): {message}")

    def consume(self, expected_type):
        if(self.current_token):
            self.past_token = self.current_token
        if self.current_token and self.current_token[0] == expected_type:
            self.current_token_index += 1
            if self.current_token_index < len(self.tokens):
                self.current_token = self.tokens[self.current_token_index]
            else:
                self.current_token = None
        else:
            self.error(f"Se esperaba {expected_type}, pero se encontró {self.current_token[0] if self.current_token else 'EOF'}.")

    def debug(self):
        print("DEBUGGIANDO: \nToken Actual: ", self.current_token,"\n")

    def parse(self):
        self.consume('tk_newline')
        self.statement_list()


    def statement_list(self):
        while self.current_token and self.current_token[0] != 'EOF':
            self.statement()  # Parse una declaración
        # Si no hay más tokens, simplemente retorna, lo que representa ε

    def statement(self):
        #simples
        current_token=self.current_token[0]
        if current_token == 'tk_print':
            self.print_statement()
        elif current_token == 'tk_pass':
            self.consume('tk_pass')  # Consume pass
        elif current_token == 'tk_import' or current_token == 'tk_from':
            self.import_statement()
        elif current_token == 'tk_return':
            self.return_statement()
        elif current_token == 'id': #assigment_statement
            self.consume('id')  # Consume el identificador
            if(self.current_token[0]=='tk_delim_('):
                self.function_call()  # Parsea una llamada a función
            else:
                self.assignment_statement()        
        #compuestas
        elif  current_token == 'tk_if' or current_token == 'tk_elif' or current_token == 'tk_else':
            self.if_statement()
        elif current_token == 'tk_while':
            self.while_statement()
        elif current_token == 'tk_for':
            self.for_statement()
        elif current_token == 'tk_def':#function_statement
            self.function_definition()
        elif current_token == 'tk_class':
            self.class_definition()
        elif current_token == 'tk_try' or current_token == 'tk_except' or current_token == 'tk_finally ':
            self.try_statement()
        elif current_token == 'tk_dedent':
            self.consume('tk_dedent')
        elif current_token == 'tk_indent':
            self.error("Unexpected Indent.")
        elif current_token=='tk_newline':
            self.consume('tk_newline')
        else:
            self.error(f"No se reconocio: {self.current_token[0]}")

#simples
    def print_statement(self):
        self.consume('tk_print')
        self.consume('tk_delim_(')
        self.expression()
        self.consume('tk_delim_)')

    def import_statement(self):
        if self.current_token[0] == 'tk_import':
            self.consume('tk_import')        # Consume 'import'
            self.module_name()                # Analiza el nombre del módulo
        elif self.current_token[0] == 'tk_from':
            self.consume('tk_from')           # Consume 'from'
            self.module_name()                 # Analiza el nombre del módulo
            self.consume('tk_import')          # Consume 'import'
            self.identifier_list()             # Analiza la lista de identificadores

    def return_statement(self):
        self.consume('tk_return')          # Consume 'return'
        if(self.current_token[0]=='tk_delim_;'):
            self.consume('tk_delim_;')
        if self.current_token and self.current_token[0] != 'tk_delim_;':  # Si hay una expresión
            self.expression()               # Analiza la expresión que se devuelve
        

    def assignment_statement(self):
        self.consume('tk_delim_=')          # Consume el operador de asignación ':='
        self.expression()                 # Analiza la expresión asignada

#compuestas
    isInIf=False
    def if_statement(self):
        if(self.current_token[0]=='tk_if'):
            self.isInIf=True
            self.consume('tk_if')           # Consume la palabra clave 'if'
            self.expression()                # Analiza la expresión que determina la condición
            self.consume('tk_delim_:')      # Consume ':'
            self.suite()                    # Procesa la suite del bloque 'if'
        if(self.isInIf):
            while self.current_token and self.current_token[0] == 'tk_elif' and self.isInIf:
                self.consume('tk_elif')     # Consume la palabra clave 'elif'
                self.expression()            # Analiza la expresión de la condición 'elif'
                self.consume('tk_delim_:')   # Consume ':'
                self.suite()                # Procesa la suite del bloque 'elif'
            if self.current_token and self.current_token[0] == 'tk_else' and self.isInIf:
                self.isInIf=False
                self.consume('tk_else')      # Consume la palabra clave 'else'
                self.consume('tk_delim_:')   # Consume ':'
                self.suite()                # Procesa la suite del bloque 'else'
        else:
            self.error("Sintaxis Invalida; Se esperaba un if")

    def while_statement(self):
        self.consume('tk_while')        # Consume la palabra clave 'while'
        self.expression()                # Analiza la expresión que determina la condición del bucle
        self.consume('tk_delim_:')      # Consume ':'
        self.suite()                    # Procesa la suite del bucle

    def for_statement(self):
        self.consume('tk_for')          # Consume la palabra clave 'for'
        self.consume('id')               # Consume el identificador (variable del bucle)
        self.consume('tk_in')           # Consume la palabra clave 'in'
        self.expression()                # Analiza la expresión (colección iterable)
        self.consume('tk_delim_:')      # Consume ':'
        self.suite()                    # Procesa la suite del bucle

    def function_definition(self):
        self.consume('tk_def')         # Consume la palabra clave 'def'
        self.consume('id')              # Consume el identificador de la función
        self.consume('tk_delim_(')      # Consume '('
        
        self.parameter_list()           # Analiza la lista de parámetros
        self.consume('tk_delim_)')      # Consume ')'
        
        self.consume('tk_delim_:')      # Consume ':'
        self.suite()                    # Procesa la suite de la definición de la función

    def class_definition(self):
        self.consume('tk_class')  # Consume la palabra clave 'class'
        self.consume('id')         # Consume el identificador de la clase

        # Maneja la lista de identificadores (herencia opcional)
        if self.current_token and self.current_token[0] == 'tk_delim_(':
            self.consume('tk_delim_(')  # Consume '('
            self.consume('id')            # Consume el primer identificador (posible clase base)
            while self.current_token and self.current_token[0] == 'tk_delim_,':  # Si hay más identificadores
                self.consume('tk_delim_,')  # Consume la coma
                self.consume('id')            # Consume el siguiente identificador
            self.consume('tk_delim_)')  # Consume ')'

        self.consume('tk_delim_:')   # Consume ':'
        self.suite()                 # Procesa la suite de la definición de la clase

    isInTry = False
    def try_statement(self):
        if(self.current_token[0]=='tk_try'):
            self.isInTry =True
            self.consume('tk_try')       # Consume la palabra clave 'try'
            self.consume('tk_delim_:')   # Consume ':'
            self.suite()                 # Procesa el bloque suite después de 'try'
        if(self.isInTry):
            # Procesa los bloques 'except'
            while self.current_token and self.current_token[0] == 'tk_except':
                self.consume('tk_except')    # Consume la palabra clave 'except'
                if self.current_token and self.current_token[0] == 'id':
                    self.consume('id')       # Consume el primer identificador (tipo de excepción)
                    if self.current_token and self.current_token[0] == 'tk_delim_,':
                        self.consume('tk_delim_,')  # Consume la coma si hay un identificador adicional
                        self.consume('id')          # Consume el segundo identificador

                self.consume('tk_delim_:')   # Consume ':'
                self.suite()                 # Procesa el bloque suite del 'except'

            # Procesa el bloque 'finally', si está presente
            if self.current_token and self.current_token[0] == 'tk_finally':
                self.consume('tk_finally')   # Consume la palabra clave 'finally'
                self.consume('tk_delim_:')   # Consume ':'
                self.suite()                 # Procesa el bloque suite del 'finally'
        else:
            self.error("Sintaxis Invalida; Se esperaba un Try")

    def module_name(self):
        self.consume('id')  # Consume el primer identificador (nombre de módulo)
        while self.current_token and self.current_token[0] == 'tk_delim_.':  # Si hay más identificadores separados por puntos
            self.consume('tk_delim_.')  # Consume el punto
            self.consume('id')  # Consume el siguiente identificador
  
    def identifier_list(self):
        if self.current_token and self.current_token[0] == 'id':  # Verifica si la lista de identificadores no está vacía
            self.consume('id')  # Consume el primer identificador
            while self.current_token and self.current_token[0] == 'tk_delim_,':  # Si hay más identificadores
                self.consume('tk_delim_,')  # Consume la coma entre identificadores
                self.consume('id')  # Consume el siguiente identificador
        else:
            self.error("Sintaxis invalida")

    def parameter_list(self):
        if self.current_token and self.current_token[0] == 'id':  # Verifica si la lista de parámetros no está vacía
            self.consume('id')  # Consume el primer identificador (parámetro)
            while self.current_token and self.current_token[0] == 'tk_delim_,':  # Si hay más parámetros
                self.consume('tk_delim_,')  # Consume la coma entre parámetros
                self.consume('id')  # Consume el siguiente identificador (parámetro)

    def suite(self):
        self.consume('tk_indent')
        self.consume('tk_newline')

        if self.current_token and self.current_token[0] == 'tk_pass':
            self.consume('tk_pass')  # Consume 'pass' si es una suite vacía
            self.consume('tk_dedent')
        else:
            self.statement_list()  # Analiza una lista de declaraciones
            

    def expression_statement(self):
            self.expression()

    def expression(self):
        self.or_expression()

    def or_expression(self):
        self.and_expression()  # Parsea la primera and_expression
        while self.current_token and self.current_token[0] == 'tk_or':
            self.consume('tk_or')  # Consume el operador 'or'
            self.and_expression()  # Parse la siguiente and_expression

    def and_expression(self):
        self.not_expression()  # Parsea la primera not_expression
        while self.current_token and self.current_token[0] == 'tk_and':
            self.consume('tk_and')  # Consume el operador 'and'
            self.not_expression()  # Parsea la siguiente not_expression

    def not_expression(self):
        if self.current_token and self.current_token[0] == 'tk_not':
            self.consume('tk_not')  # Consume el operador 'not'
            self.not_expression()  # Parsea la siguiente not_expression
        else:
            self.comparison()# Parsea una comparación

    def comparison(self):
        self.arithmetic_expression()  # Parsea la primera arithmetic_expression
        while self.current_token and self.current_token[0] in ('tk_op_==', 'tk_op_!=', 'tk_op_<', 'tk_op_>', 'tk_op_<=', 'tk_op_>='):
            self.consume(self.current_token[0])  # Consume el operador de comparación
            self.arithmetic_expression()  # Parsea la siguiente arithmetic_expression

    def arithmetic_expression(self):
        self.term()  # Parsea el primer term
        while self.current_token and self.current_token[0] in ('tk_op_+', 'tk_op_-'):
            operator = self.current_token[0]
            self.consume(operator)  # Consume el operador '+' o '-'
            self.term()  # Parsea el siguiente term

    def term(self):
        if(self.current_token):
            self.factor()  # Parsea el primer factor
        else:
            self.error("Syntax Invalida.")
        while self.current_token and (self.current_token[0] in ('tk_op_*', 'tk_op_/', 'tk_op_%') or self.current_token[0] == ''):
            operator = self.current_token[0]
            self.consume(operator)  # Consume el operador
            self.factor()  # Parsea el siguiente factor

    def factor(self):
        if self.current_token[0] == 'tk_delim_(':
            self.consume('tk_delim_(')  # Consume '('
            self.expression()  # Parsea la expresión interna
            self.consume('tk_delim_)')  # Consume ')'


        elif self.current_token[0] in ('tk_entero', 'tk_float'):
            self.consume(self.current_token[0])  # Consume el número (entero o flotante)

        elif self.current_token[0] == 'id':  # Asumiendo que `function_call` también inicia con un identificador
            self.consume('id')  # Consume el identificador
            if(self.current_token):
                if(self.current_token[0]=='tk_delim_('):
                    self.function_call()  # Parsea una llamada a función

        elif self.current_token[0] == 'tk_cadena':
            self.consume('tk_cadena')  # Consume la cadena

        elif self.current_token[0] == 'tk_delim_[':
            self.list()  # Parsea una lista

        elif self.current_token[0] == 'tk_delim_{':
            self.dictionary()  # Parsea un diccionario

        elif self.current_token[0] in ('tk_op_+', 'tk_op_-'):
            self.unary_operation()  # Parsea una operación unaria
        else:
            self.error(f"Factor no reconocido: {self.current_token[0] if self.current_token else 'EOF'}.")

    def unary_operation(self):
        operator = self.current_token[0]  # Almacena el operador actual
        if operator in ('tk_op_+', 'tk_op_-'):
            self.consume(operator)  # Consume el operador unario
            self.factor()  # Parsea el factor que sigue
        else:
            self.error(f"Operación unaria no reconocida: {operator}.")

    def function_call(self):
        self.consume('tk_delim_(')  # Consume '(' para iniciar los argumentos
        self.argument_list()  # Analiza la lista de argumentos
        self.consume('tk_delim_)')  # Consume ')' para cerrar los argumentos

    def list(self):
        self.consume('tk_delim_[')  # Consume '[' para iniciar la lista
        if self.current_token and self.current_token[0] != 'tk_delim_]':  # Verifica si la lista no está vacía
            self.expression()  # Analiza la primera expresión de la lista
            while self.current_token and self.current_token[0] == 'tk_delim_,':  # Si hay más elementos
                self.consume('tk_delim_,')  # Consume la coma entre elementos
                self.expression()  # Analiza la siguiente expresión
        self.consume('tk_delim_]')  # Consume ']' para cerrar la lista

    def dictionary(self):
        self.consume('tk_delim_{')  # Consume '{' para iniciar el diccionario
        if self.current_token and self.current_token[0] != 'tk_delim_}':  # Verifica si el diccionario no está vacío
            self.key_value_pair()  # Analiza el primer par clave-valor
            while self.current_token and self.current_token[0] == 'tk_delim_,':  # Si hay más pares clave-valor
                self.consume('tk_delim_,')  # Consume la coma entre pares
                self.key_value_pair()  # Analiza el siguiente par clave-valor
        self.consume('tk_delim_}')  # Consume '}' para cerrar el diccionario

    def key_value_pair(self):
        self.expression()         # Analiza la expresión clave
        self.consume('tk_delim_:')  # Consume ':' para separar clave y valor
        self.expression()         # Analiza la expresión valor

    def argument_list(self):
        if self.current_token and self.current_token[0] != 'tk_delim_)':  # Verifica si la lista de argumentos no está vacía
            self.expression()  # Analiza la primera expresión en la lista de argumentos
            while self.current_token and self.current_token[0] == 'tk_delim_,':  # Si hay más argumentos
                self.consume('tk_delim_,')  # Consume la coma entre argumentos
                self.expression()  # Analiza la siguiente expresión