import string

class TokenType:
    # Palabras reservadas
    IF="IF"; ELSE="ELSE"; END="END"; DO="DO"; WHILE="WHILE"
    SWITCH="SWITCH"; CASE="CASE"; INT="INT"; FLOAT="FLOAT"
    MAIN="MAIN"; CIN="CIN"; COUT="COUT"; THEN="THEN"
    # CORRECCIÓN 1: agregar BOOL, TRUE, FALSE como palabras reservadas
    BOOL="BOOL"; TRUE="TRUE"; FALSE="FALSE"

    # Identificadores y números
    ID="ID"; NUM_INT="NUM_INT"; NUM_FLOAT="NUM_FLOAT"

    # Operadores aritméticos
    MAS="MAS"; MENOS="MENOS"; MUL="MUL"; DIV="DIV"; MOD="MOD"; POT="POT"
    INC="INC"; DEC="DEC"

    # Operadores relacionales
    LT="LT"; LE="LE"; GT="GT"; GE="GE"; NE="NE"; EQ="EQ"

    # CORRECCIÓN 2: agregar SHL (<<) y SHR (>>) como tipos de token
    SHL="SHL"; SHR="SHR"

    # Operadores lógicos
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
    "if":     TokenType.IF,
    "else":   TokenType.ELSE,
    "end":    TokenType.END,
    "do":     TokenType.DO,
    "while":  TokenType.WHILE,
    "switch": TokenType.SWITCH,
    "case":   TokenType.CASE,
    "int":    TokenType.INT,
    "float":  TokenType.FLOAT,
    "bool":   TokenType.BOOL,    
    "true":   TokenType.TRUE,    
    "false":  TokenType.FALSE,   
    "main":   TokenType.MAIN,
    "cin":    TokenType.CIN,
    "cout":   TokenType.COUT,
    "then":   TokenType.THEN,
}

class Scanner:

    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.erroMsg = ""
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
        # CORRECCIÓN 3: eliminado el print(ord(...)) de depuración
        while self.current_char and self.current_char in [' ', '\t', '\n', '\r']:
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
        if self.current_char == "/" and self.avanzarNoConsumir() == "/":
            while self.current_char and self.current_char != "\n":
                self.avanzar()
        elif self.current_char == "/" and self.avanzarNoConsumir() == "*":
            self.avanzar()
            self.avanzar()
            while self.current_char:
                if self.current_char == "*" and self.avanzarNoConsumir() == "/":
                    self.avanzar()
                    self.avanzar()
                    break
                self.avanzar()

    # NÚMEROS
    def get_position(self):
        return (self.line, self.col)

    def number(self):
        start_line = self.line
        start_col = self.col
        num = ""

        while self.current_char and self.current_char.isdigit():
            num += self.current_char
            self.avanzar()

        if self.current_char == ".":
            if self.avanzarNoConsumir() and self.avanzarNoConsumir().isdigit():
                num += "."
                self.avanzar()
                while self.current_char and self.current_char.isdigit():
                    num += self.current_char
                    self.avanzar()
                return (TokenType.NUM_FLOAT, num, start_line, start_col, "")
            else:
                num += "."
                self.erroMsg = "No se puede declarar un numero con caracteres"
                self.avanzar()
                return (TokenType.ERROR, num, start_line, start_col, self.erroMsg)

        return (TokenType.NUM_INT, num, start_line, start_col, "")

    # IDENTIFICADORES Y PALABRAS RESERVADAS
    def identifier(self):
        start_line = self.line
        start_col = self.col
        result = ""

        while self.current_char and (self.current_char.isalnum() or self.current_char == "_"):
            result += self.current_char
            self.avanzar()

        token_type = palabrasReservadas.get(result, TokenType.ID)
        return (token_type, result, start_line, start_col, "")

    # CADENAS
    def string(self):
        start_line = self.line
        start_col = self.col
        result = '"'
        self.avanzar()

        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.avanzar()

        if self.current_char is None:
            return ("ERROR", result, start_line, start_col, "String sin cerrar")

        result += '"'
        self.avanzar()
        return ("STRING", result, start_line, start_col, "")

    # CARACTERES
    def char(self):
        start_line = self.line
        start_col = self.col
        result = "'"
        self.avanzar()

        if self.current_char is None:
            return ("ERROR", result, start_line, start_col, "Char sin cerrar")

        if self.current_char == "'":
            result += "'"
            self.avanzar()
            return ("CHAR", result, start_line, start_col, "")

        result += self.current_char
        self.avanzar()

        if self.current_char is None:
            return ("ERROR", result, start_line, start_col, "Char sin cerrar")

        if self.current_char == "'":
            result += "'"
            self.avanzar()
            return ("CHAR", result, start_line, start_col, "")
        else:
            return ("ERROR", result, start_line, start_col, "Char inválido (más de un carácter)")

    def getToken(self):
        while self.current_char:
            start_line = self.line
            start_col = self.col

            self.saltarEspacio()

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

            # Identificadores y palabras reservadas (incluye bool/true/false)
            if self.current_char.isalpha() or self.current_char == "_":
                return self.identifier()

            # Strings
            if self.current_char == '"':
                return self.string()

            # Char
            if self.current_char == "'":
                return self.char()

            # ── Operadores dobles (sin espacio entre caracteres) ──────────
            # CORRECCIÓN 2a: >> → SHR  (debe ir ANTES que el simple >)
            if self.current_char == ">" and self.avanzarNoConsumir() == ">":
                self.avanzar()
                self.avanzar()
                return (TokenType.SHR, ">>", start_line, start_col, "")

            # CORRECCIÓN 2b: << → SHL  (debe ir ANTES que el simple <)
            if self.current_char == "<" and self.avanzarNoConsumir() == "<":
                self.avanzar()
                self.avanzar()
                return (TokenType.SHL, "<<", start_line, start_col, "")

            # ── Operadores dobles (pueden tener espacio entre caracteres) ──
            if self.current_char == "+" and self.peek_no_whitespace() == "+":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.INC, "++", start_line, start_col, "")

            if self.current_char == "-" and self.peek_no_whitespace() == "-":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.DEC, "--", start_line, start_col, "")

            if self.current_char == "=" and self.peek_no_whitespace() == "=":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.EQ, "==", start_line, start_col, "")

            if self.current_char == "!" and self.peek_no_whitespace() == "=":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.NE, "!=", start_line, start_col, "")

            if self.current_char == "<" and self.peek_no_whitespace() == "=":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.LE, "<=", start_line, start_col, "")

            if self.current_char == ">" and self.peek_no_whitespace() == "=":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.GE, ">=", start_line, start_col, "")

            if self.current_char == "&" and self.peek_no_whitespace() == "&":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.AND, "&&", start_line, start_col, "")

            if self.current_char == "|" and self.peek_no_whitespace() == "|":
                self.avanzarSaltandoEspacios()
                self.avanzar()
                return (TokenType.OR, "||", start_line, start_col, "")

            # ── Operadores y símbolos simples ─────────────────────────────
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
                ";": TokenType.PUNCOM,
            }

            token_type = simple_tokens.get(char, TokenType.ERROR)
            if token_type == TokenType.ERROR:
                return (token_type, char, start_line, start_col, "Caracter invalido")

            return (token_type, char, start_line, start_col, "")

        return (TokenType.ENDFILE, "", self.line, self.col, "")