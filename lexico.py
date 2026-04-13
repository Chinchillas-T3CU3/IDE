import string

class TokenType:
    # Palabras reservadas
    IF="IF"; ELSE="ELSE"; END="END"; DO="DO"; WHILE="WHILE"
    SWITCH="SWITCH"; CASE="CASE"; INT="INT"; FLOAT="FLOAT"
    MAIN="MAIN"; CIN="CIN"; COUT="COUT"

    # Identificadores y números
    ID="ID"; NUM_INT="NUM_INT"; NUM_FLOAT="NUM_FLOAT"

    # Operadores
    MAS="MAS"; MENOS="MENOS"; MUL="MUL"; DIV="DIV"; MOD="MOD"; POT="POT"
    INC="INC"; DEC="DEC"

    LT="LT"; LE="LE"; GT="GT"; GE="GE"; NE="NE"; EQ="EQ"

    AND="AND"; OR="OR"; NOT="NOT"

    ASSIGN="ASSIGN"

    # Símbolos
    LPAREN="LPAREN"; RPAREN="RPAREN"
    LBRACE="LBRACE"; RBRACE="RBRACE"
    COMA="COMA"; PUNCOM="PUNCOM"
    STRING="STRING"; CHAR="CHAR"

    ENDFILE="EOF"
    ERROR="ERROR"

palabrasReservadas = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "end": TokenType.END,
    "do": TokenType.DO,
    "while": TokenType.WHILE,
    "switch": TokenType.SWITCH,
    "case": TokenType.CASE,
    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "main": TokenType.MAIN,
    "cin": TokenType.CIN,
    "cout": TokenType.COUT
}

class Scanner:

    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.erroMsg=""
        self.current_char = self.source[self.pos] if self.source else None

    def avanzar(self):
        if self.current_char == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1

        self.pos += 1
        if self.pos >= len(self.source):
            self.current_char = None
        else:
            self.current_char = self.source[self.pos]


    def avanzarNoConsumir(self):
        nxt = self.pos + 1
        if nxt < len(self.source):
            return self.source[nxt]
        return None

    def saltarEspacio(self):
        while self.current_char and self.current_char in [' ','\t','\n','\r']:
            print(ord(self.current_char))
            self.avanzar()

    
    def peek_no_whitespace(self):
        pos = self.pos + 1

        while pos < len(self.source) and self.source[pos] in [' ', '\t', '\n', '\r']:
            pos += 1

        if pos < len(self.source):
            return self.source[pos]

        return None
    

    def avanzarSaltandoEspacios(self):
        self.avanzar()
        while self.current_char and self.current_char in [' ', '\t', '\n', '\r']:
            self.avanzar()
            

    # COMENTARIOS
    def saltarComentario(self):
        # // comentario de línea
        if self.current_char == "/" and self.avanzarNoConsumir() == "/":
            while self.current_char and self.current_char != "\n":
                self.avanzar()

        # /* comentario multilínea */
        elif self.current_char == "/" and self.avanzarNoConsumir() == "*":
            self.avanzar()
            self.avanzar()
            while self.current_char:
                if self.current_char == "*" and self.avanzarNoConsumir() == "/":
                    self.avanzar()
                    self.avanzar()
                    break
                self.avanzar()


    # NÚMEROS (INT y FLOAT)
    def number(self):
        num = ""
        while self.current_char and self.current_char.isdigit():
            num+=self.current_char
            self.avanzar()

        if self.current_char==".":
            if self.avanzarNoConsumir() and self.avanzarNoConsumir().isdigit():
                num+="."
                self.avanzar()

                while self.current_char and self.current_char.isdigit():
                    num+=self.current_char
                    self.avanzar()
                
                return (TokenType.NUM_FLOAT,num)
            
            else:
                num+="."
                self.erroMsg="No se puede delarar un numero con caracteres"
                self.avanzar()
                return (TokenType.ERROR,num,self.line, self.col,self.erroMsg)
            
        return(TokenType.NUM_INT,num)






    # IDENTIFICADORES
    def identifier(self):
        result = ""

        while self.current_char and (self.current_char.isalnum()) or self.current_char=="_":
            result += self.current_char
            self.avanzar()

        return (palabrasReservadas.get(result, TokenType.ID), result)


    # STRINGS
    def string(self):
        result = ""
        self.avanzar()  # saltar "

        while self.current_char and self.current_char != '"':
            result += self.current_char
            self.avanzar()

        self.avanzar()  # cerrar "
        return (TokenType.STRING, result)

    # CHAR
    def char(self):
        self.avanzar()  # '
        result = self.current_char
        self.avanzar()
        if self.current_char== "'":
            self.avanzar()  # cerrar '
            return (TokenType.CHAR, result)
        else:
             return (TokenType.ERROR, result,self.line, self.col)


    
    # TOKEN 
    def getToken(self):

        while self.current_char:
            self.saltarEspacio()
            #self.saltarComentario()

            if self.current_char is None:
                break

            # Comentarios
            if self.current_char == "/":
                if self.avanzarNoConsumir() in ["/", "*"]:
                    self.saltarComentario()
                    continue

            # Números
            if self.current_char.isdigit():
                return self.number()

            # Identificadores
            if self.current_char.isalpha() or self.current_char=="_":
                return self.identifier()

            # Strings
            if self.current_char == '"':
                return self.string()

            # Char
            if self.current_char == "'":
                return self.char()
            

            """#Operadores dobles sin espacio

            if self.current_char == "+" and self.avanzarNoConsumir() == "+":
                self.avanzar()
                self.avanzar()
                return (TokenType.INC, "++")

            if self.current_char == "-" and self.avanzarNoConsumir() == "-":
                self.avanzar()
                self.avanzar()
                return (TokenType.DEC, "--")

            if self.current_char == "=" and self.avanzarNoConsumir() == "=":
                self.avanzar()
                self.avanzar()
                return (TokenType.EQ, "==")

            if self.current_char == "!" and self.avanzarNoConsumir() == "=":
                self.avanzar()
                self.avanzar()
                return (TokenType.NE, "!=")

            if self.current_char == "<" and self.avanzarNoConsumir() == "=":
                self.avanzar()
                self.avanzar()
                return (TokenType.LE, "<=")

            if self.current_char == ">" and self.avanzarNoConsumir() == "=":
                self.avanzar()
                self.avanzar()
                return (TokenType.GE, ">=")

            if self.current_char == "&" and self.avanzarNoConsumir() == "&":
                self.avanzar()
                self.avanzar()
                return (TokenType.AND, "&&")

            if self.current_char == "|" and self.avanzarNoConsumir() == "|":
                self.avanzar()
                self.avanzar()
                return (TokenType.OR, "||")


            """    

            # Operadores dobles(con espacio)
            if self.current_char == "+" and self.peek_no_whitespace() == "+":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.INC, "++")

            if self.current_char == "-" and self.peek_no_whitespace() == "-":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.DEC, "--")

            if self.current_char == "=" and self.peek_no_whitespace() == "=":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.EQ, "==")

            if self.current_char == "!" and self.peek_no_whitespace() == "=":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.NE, "!=")

            if self.current_char == "<" and self.peek_no_whitespace() == "=":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.LE, "<=")

            if self.current_char == ">" and self.peek_no_whitespace() == "=":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.GE, ">=")

            if self.current_char == "&" and self.peek_no_whitespace() == "&":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.AND, "&&")

            if self.current_char == "|" and self.peek_no_whitespace() == "|":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.OR, "||")
            
            # Operadores simples
            char = self.current_char
            self.avanzar()

            simple_tokens = {
                "+": TokenType.MAS,
                "-": TokenType.MENOS,
                "*": TokenType.MUL,
                "/": TokenType.DIV,
                "%": TokenType.MOD,
                "^": TokenType.POT,
                "<": TokenType.LT,
                ">": TokenType.GT,
                "!": TokenType.NOT,
                "=": TokenType.ASSIGN,
                "(": TokenType.LPAREN,
                ")": TokenType.RPAREN,
                "{": TokenType.LBRACE,
                "}": TokenType.RBRACE,
                ",": TokenType.COMA,
                ";": TokenType.PUNCOM
            }
            

            return (simple_tokens.get(char, TokenType.ERROR), char,self.line, self.col,"Caracter invalido")

        return (TokenType.ENDFILE, "")