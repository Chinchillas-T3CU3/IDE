from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QTextCursor
from PyQt6.QtCore import QObject


class ColoreadorGlobal(QObject):
    def __init__(self, document):
        super().__init__()
        self.document = document

        def colores(color, bold=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            return fmt

        self.numeros_color = colores("#29F800")
        self.palabras_reservadas_color = colores("#ff69b4", True)
        self.comentarios_color = colores("#008000")
        self.operadores_aritmeticos_color = colores("#ff0000")
        self.operadores_relacionales_color = colores("#00bfff")
        self.operadores_logicos_color = colores("#ff8c00")
        self.simbolos_color = colores("#ffff00")
        self.asignacion_color = colores("#992ccb", True)

        self.palabrasReservadas = {
            "if","else","end","do","while",
            "switch","case","int","float",
            "main","cin","cout"
        }

        self.document.contentsChanged.connect(self.resaltar)

   
    def resaltar(self):
        self.document.blockSignals(True)
        texto = self.document.toPlainText()
        cursor = QTextCursor(self.document)

        # limpiar formato
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(QTextCharFormat())

        i = 0
        while i < len(texto):
            c = texto[i]

    
            # COMENTARIOS //
            if texto[i:i+2] == "//":
                start = i
                while i < len(texto) and texto[i] != "\n":
                    i += 1
                self.pintar(cursor, start, i-start, self.comentarios_color)
                continue


            # COMENTARIOS /* */
            if texto[i:i+2] == "/*":
                start = i
                i += 2
                while i < len(texto)-1 and texto[i:i+2] != "*/":
                    i += 1
                i += 2
                self.pintar(cursor, start, i-start, self.comentarios_color)
                continue

            
            # NÚMEROS
            if c.isdigit():
                start = i
                while i < len(texto) and (texto[i].isdigit() or texto[i] == "."):
                    i += 1
                self.pintar(cursor, start, i-start, self.numeros_color)
                continue

        
            # PALABRAS

            if c.isalpha():
                start = i
                while i < len(texto) and texto[i].isalnum():
                    i += 1
                palabra = texto[start:i]

                if palabra in self.palabrasReservadas:
                    self.pintar(cursor, start, i-start, self.palabras_reservadas_color)
                continue

    
            # OPERADORES MULTILÍNEA
            if c in ["&", "|", "=", "!", "<", ">"]:
                start = i
                j = i + 1

                while j < len(texto) and texto[j].isspace():
                    j += 1

                if j < len(texto):
                    # && ||
                    if c in ["&","|"] and texto[j] == c:
                        self.pintar(cursor, start, j-start+1, self.operadores_logicos_color)
                        i = j + 1
                        continue

                    # == != <= >=
                    if (c == "=" and texto[j] == "=") or \
                       (c == "!" and texto[j] == "=") or \
                       (c in ["<", ">"] and texto[j] == "="):

                        self.pintar(cursor, start, j-start+1, self.operadores_relacionales_color)
                        i = j + 1
                        continue

                # asignación simple
                if c == "=":
                    self.pintar(cursor, i, 1, self.asignacion_color)

                i += 1
                continue

            # ARITMÉTICOS
            if c in "+-*/%^":
                self.pintar(cursor, i, 1, self.operadores_aritmeticos_color)
                i += 1
                continue


            # SÍMBOLOS
            if c in "(){};,\"'":
                self.pintar(cursor, i, 1, self.simbolos_color)
                i += 1
                continue

            i += 1
        self.document.blockSignals(False)

    # =========================
    # FUNCIÓN AUXILIAR
    # =========================
    def pintar(self, cursor, pos, length, formato):
        cursor.setPosition(pos)
        cursor.setPosition(pos + length, QTextCursor.MoveMode.KeepAnchor)
        cursor.setCharFormat(formato)