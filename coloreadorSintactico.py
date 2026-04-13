from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression

class ColoreadorSintactico(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.reglas=[]

        #COLORES 

        def colores(color,bold=False):
            fmt=QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            
            return fmt
        

        self.numeros_color = colores("#29F800")     
        self.palabras_reservadas_color = colores("#ff69b4")    
        self.comentarios_color = colores("#008000")    
        self.operadores_aritmeticos_color = colores("#ff0000")      
        self.operadores_relacionales_color = colores("#00bfff")        
        self.operadores_logicos_color = colores("#ff8c00")      
        self.simbolos_color = colores("#ffff00")     
        self.asignacion_color = colores("#992ccb", True)  

  
        # REGLAS
   

        # Números
        self.reglas.append((r"\b\d+(\.\d+)?\b", self.numeros_color))

        # Palabras reservadas
        palabrasReservadas = ["if","else","end","do","while","switch","case","int","float","main","cin","cout"]
        for word in palabrasReservadas:
            self.reglas.append((fr"\b{word}\b", self.palabras_reservadas_color))

        # Operadores aritméticos
        self.reglas.append((r"\+\+|--|\+|-|\*|/|%|\^", self.operadores_aritmeticos_color))
        #self.reglas.append((r"\+\s*\+|-\s*-", self.operadores_aritmeticos_color))

        # Lógicos
        #self.reglas.append((r"&&|\|\||!", self.operadores_logicos_color))
        #self.reglas.append((r"&\s*&|\|\s*\||!", self.operadores_logicos_color))

        # Símbolos
        self.reglas.append((r"[(){};,\"']", self.simbolos_color))

        # Asignación
        #self.reglas.append((r"=", self.asignacion_color))

        # Relacionales
        #self.reglas.append((r"<=|>=|==|!=|<|>", self.operadores_relacionales_color))
        #self.reglas.append((r"<\s*=|>\s*=|=\s*=|!\s*=", self.operadores_relacionales_color))

        # Comentarios
        self.reglas.append((r"//[^\n]*", self.comentarios_color))


    # APLICAR COLORES
    def highlightBlock(self, text):
        for pattern, fmt in self.reglas:
            expression = QRegularExpression(pattern)
            it = expression.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(),  fmt )


        # OPERADORES
        if self.previousBlockState() == 2:
            stripped = text.lstrip()
        
            if stripped:
                first_char = stripped[0]
                pos = text.find(first_char)

                if first_char in ["&", "|"]:
                    fmt = self.operadores_logicos_color
                    self.setFormat(pos, 1, fmt)

                elif first_char == "=":
                    fmt = self.operadores_relacionales_color
                    self.setFormat(pos, 1, fmt)

                elif first_char in ["<", ">", "!"]:
                    # solo válidos si forman <= >= !=
                    fmt = self.operadores_relacionales_color
                    self.setFormat(pos, 1, fmt)

            self.setCurrentBlockState(0)

        i = 0
        while i < len(text):
            c = text[i]

            # SOLO operadores que pueden ser dobles
            if c in ["&", "|", "=", "!", "<", ">"]:
                j = i + 1

                # Saltar espacios
                while j < len(text) and text[j].isspace():
                    j += 1

                
                # CASO DOBLE (==, !=,>=,<=)
                
                if j < len(text) and text[j] == c:
                    length = j - i + 1

                    if c in ["&","|"]:
                        fmt = self.operadores_logicos_color
                    else:
                        fmt = self.operadores_relacionales_color

                    self.setFormat(i, length, fmt)
                    i = j + 1
                    continue

                # =========================
                # CASO ESPECIAL !=
                # =========================
                elif c == "!" and j < len(text) and text[j] == "=":
                    length = j - i + 1
                    self.setFormat(i, length, self.operadores_relacionales_color)
                    i = j + 1
                    continue

                # =========================
                # CASO ESPECIAL <= >=
                # =========================
                elif c in ["<", ">"] and j < len(text) and text[j] == "=":
                    length = j - i + 1
                    self.setFormat(i, length, self.operadores_relacionales_color)
                    i = j + 1
                    continue

                # =========================
                # CASO SIMPLE (= SOLO)
                # =========================
                else:
                    if c == "=":
                        if j >= len(text) or text[j] != "=":
                            self.setFormat(i, 1, self.asignacion_color)

                    elif c in ["<", ">"]:
                        self.setFormat(i, 1, self.operadores_relacionales_color)

                    elif c == "!":
                        # Solo válido si NO forma !=
                        if j >= len(text) or text[j] != "=":
                            self.setFormat(i, 1, self.operadores_logicos_color)

                    # Estado multilinea
                    if i == len(text) - 1:
                        if c in ["&", "|", "=","!","<",">"]:
                            self.setCurrentBlockState(2)

            i += 1


        # COMENTARIOS MULTILÍNEA /* */
        # Estado 0: Normal, Estado 1: Dentro de un bloque de comentario
        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            # Si no venimos de un comentario abierto, buscamos el inicio '/*'
            match = QRegularExpression(r"/\*").match(text)
            startIndex = match.capturedStart()
        else:
            # Si la línea anterior dejó el comentario abierto, empezamos desde el inicio (0)
            startIndex = 0

        while startIndex >= 0:
            # Buscamos el final '*/'
            endMatch = QRegularExpression(r"\*/").match(text, startIndex)
            endIndex = endMatch.capturedStart()
            
            commentLength = 0
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + endMatch.capturedLength()

            self.setFormat(startIndex, commentLength, self.comentarios_color)
            
            nextStartMatch = QRegularExpression(r"/\*").match(text, startIndex + commentLength)
            startIndex = nextStartMatch.capturedStart()