import re

# ==================== Enumeraciones para el Árbol ====================
class NodeKind:
    STMT_K    = "StmtK"
    EXP_K     = "ExpK"
    DECL_K    = "DeclK"
    PROGRAM_K = "ProgramK"

class StmtKind:
    SELECTION_K  = "SelectionK"   # if
    ITERATION_K  = "IterationK"   # while
    REPETITION_K = "RepetitionK"  # do-while
    SENT_IN_K    = "SentInK"      # cin
    SENT_OUT_K   = "SentOutK"     # cout
    ASSIGN_K     = "AssignK"      # asignación

class ExpKind:
    OP_K     = "OpK"      # Operador aritmético / relacional
    CONST_K  = "ConstK"   # Constante numérica
    BOOL_K   = "BoolK"    # Constante booleana
    ID_K     = "IdK"      # Identificador
    STRING_K = "StringK"  # Cadena
    LOGIC_K  = "LogicK"   # Operador lógico

class DeclKind:
    VAR_DECL_K = "VarDeclK"  # Declaración de variable
    TYPE_K     = "TypeK"     # Tipo de dato

class ExpType:
    VOID    = "Void"
    INTEGER = "Integer"
    FLOAT   = "Float"
    BOOLEAN = "Boolean"
    STRING  = "String"

# ==================== Nodo del Árbol ====================
class TreeNode:
    def __init__(self):
        self.children = [None] * 3
        self.sibling  = None
        self.lineno   = 0
        self.nodekind = None
        self.kind     = {}
        self.attr     = {}
        self.type     = ExpType.VOID

# ==================== Parser ====================
class Parser:

    TOKEN_LEXEMA = {
        "MAIN": "main",   "LBRACE": "{",   "RBRACE": "}",
        "LPAREN": "(",    "RPAREN": ")",
        "INT": "int",     "FLOAT": "float", "BOOL": "bool",
        "IF": "if",       "ELSE": "else",   "END": "end",
        "WHILE": "while", "DO": "do",       "THEN": "then",
        "CIN": "cin",     "COUT": "cout",
        "ASSIGN": "=",    "PUNCOM": ";",    "COMA": ",",
        "MAS": "+",  "MENOS": "-",  "MUL": "*",   "DIV": "/",
        "MOD": "%",  "POT": "^",    "INC": "++",  "DEC": "--",
        "LT": "<",   "LE": "<=",    "GT": ">",    "GE": ">=",
        "EQ": "==",  "NE": "!=",    "SHL": "<<",  "SHR": ">>",
        "AND": "&&", "OR": "||",    "NOT": "!",
        "TRUE": "true", "FALSE": "false",
        "EOF": "fin de archivo",
    }

    def _lexema(self, token):
        return self.TOKEN_LEXEMA.get(token, token)

    def __init__(self, tokens_file="tokens.txt"):
        self.tokens        = []
        self.pos           = 0
        self.current_token = None
        self.current_lex   = None
        self.current_line  = 1
        self.current_col   = 1
        self.error         = False
        self.error_list    = []
        self.load_tokens(tokens_file)

    # ─────────────────────────────────────────────
    # Carga de tokens
    # ─────────────────────────────────────────────
    def load_tokens(self, tokens_file):
        try:
            with open(tokens_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("EOF ->"):
                    token_type = "EOF"
                    lexema     = ""
                    match = re.search(r'línea\s+(\d+),\s+columna\s+(\d+)', line)
                    line_num = int(match.group(1)) if match else 1
                    col_num  = int(match.group(2)) if match else 1
                    self.tokens.append({'type': token_type, 'lexema': lexema,
                                        'line': line_num,  'col': col_num})
                    continue

                pattern = r'^(\S+)\s+(.+?)\s+\|\s+Línea:\s+(\d+)\s+\|\s+Columna:\s+(\d+)'
                match   = re.match(pattern, line)

                if match:
                    self.tokens.append({
                        'type':   match.group(1).strip(),
                        'lexema': match.group(2).strip(),
                        'line':   int(match.group(3)),
                        'col':    int(match.group(4)),
                    })
                else:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        token_part = parts[0].strip().split()
                        token_type = token_part[0] if token_part else ""
                        lexema     = ' '.join(token_part[1:]) if len(token_part) >= 2 else ""
                        line_match = re.search(r'Línea:\s*(\d+)',   parts[1])
                        col_match  = re.search(r'Columna:\s*(\d+)', parts[2])
                        self.tokens.append({
                            'type':   token_type,
                            'lexema': lexema,
                            'line':   int(line_match.group(1)) if line_match else 1,
                            'col':    int(col_match.group(1))  if col_match  else 1,
                        })

            if not self.tokens:
                print("No se encontraron tokens en el archivo")
                self.error = True

        except FileNotFoundError:
            print(f"No se encontró el archivo {tokens_file}")
            self.error = True
        except Exception as e:
            print(f"Error cargando tokens: {e}")
            self.error = True

    # ─────────────────────────────────────────────
    # Utilidades del parser
    # ─────────────────────────────────────────────
    def getNextToken(self):
        if self.pos < len(self.tokens):
            info = self.tokens[self.pos]
            self.current_token = info['type']
            self.current_lex   = info['lexema']
            self.current_line  = info['line']
            self.current_col   = info['col']
            self.pos += 1
        else:
            self.current_token = "EOF"
            self.current_lex   = ""
        return self.current_token

    def match(self, expected):
        if self.current_token == expected:
            self.getNextToken()
        else:
            esperado   = self._lexema(expected)
            encontrado = self.current_lex if self.current_lex else self._lexema(self.current_token)
            self.syntaxError(f"se esperaba '{esperado}', se encontró '{encontrado}'")

    def syntaxError(self, message):
        error_msg = (f"Error sintáctico en la línea {self.current_line}, "
                     f"columna {self.current_col}: {message}")
        self.error_list.append(error_msg)
        print(error_msg)
        self.error = True
        self.saveErrorsToFile()

    def saveErrorsToFile(self):
        try:
            with open("erroresSin.txt", "w", encoding="utf-8") as f:
                if self.error_list:
                    f.write("ERRORES SINTÁCTICOS\n")
                    for i, e in enumerate(self.error_list, 1):
                        f.write(f"{i}. {e}\n")
                else:
                    f.write("")
        except Exception as e:
            print(f"Error guardando errores sintácticos: {e}")

    # ─────────────────────────────────────────────
    # Constructores de nodos
    # ─────────────────────────────────────────────
    def newProgramNode(self):
        t = TreeNode(); t.nodekind = NodeKind.PROGRAM_K; t.lineno = self.current_line; return t

    def newStmtNode(self, kind):
        t = TreeNode(); t.nodekind = NodeKind.STMT_K; t.kind = {'stmt': kind}; t.lineno = self.current_line; return t

    def newExpNode(self, kind):
        t = TreeNode(); t.nodekind = NodeKind.EXP_K; t.kind = {'exp': kind}; t.lineno = self.current_line; t.type = ExpType.VOID; return t

    def newDeclNode(self, kind):
        t = TreeNode(); t.nodekind = NodeKind.DECL_K; t.kind = {'decl': kind}; t.lineno = self.current_line; return t

    # ══════════════════════════════════════════════════════════════
    # GRAMÁTICA COMPLETA — implementación en orden jerárquico
    # ══════════════════════════════════════════════════════════════

    # ─── 1. programa ─────────────────────────────────────────────
    def programa(self):
        """
        programa → main { lista_declaracion }
        """
        t = self.newProgramNode()
        self.match("MAIN")
        self.match("LBRACE")

        first_decl = last_decl = None
        while self.current_token in ["INT","FLOAT","BOOL","IF","WHILE","DO","CIN","COUT","ID"]:
            decl = self.declaracion()
            if decl is not None:
                if first_decl is None:
                    first_decl = last_decl = decl
                else:
                    while last_decl.sibling is not None:
                        last_decl = last_decl.sibling
                    last_decl.sibling = decl
                    last_decl = decl

        t.children[0] = first_decl
        self.match("RBRACE")
        return t

    # ─── 2. lista_declaracion / declaracion ──────────────────────
    def declaracion(self):
        """
        lista_declaracion → lista_declaracion declaracion | declaracion
        declaracion       → declaracion_variable | lista_sentencias
        """
        if self.current_token in ["INT","FLOAT","BOOL"]:
            return self.declaracion_variable()
        elif self.current_token in ["IF","WHILE","DO","CIN","COUT","ID"]:
            return self.lista_sentencias()
        return None

    # ─── 3. declaracion_variable ─────────────────────────────────
    def declaracion_variable(self):
        """
        declaracion_variable → tipo identificador ;
        """
        t = self.newDeclNode(DeclKind.VAR_DECL_K)
        t.children[0] = self.tipo()
        t.children[1] = self.identificador()
        self.match("PUNCOM")
        return t

    # ─── 4. tipo ─────────────────────────────────────────────────
    def tipo(self):
        """
        tipo → int | float | bool
        """
        t = self.newDeclNode(DeclKind.TYPE_K)
        if self.current_token == "INT":
            t.attr['type'] = ExpType.INTEGER;  self.match("INT")
        elif self.current_token == "FLOAT":
            t.attr['type'] = ExpType.FLOAT;    self.match("FLOAT")
        elif self.current_token == "BOOL":
            t.attr['type'] = ExpType.BOOLEAN;  self.match("BOOL")
        else:
            self.syntaxError("se esperaba 'int', 'float' o 'bool'")
        return t

    # ─── 5. identificador ────────────────────────────────────────
    def identificador(self):
        """
        identificador → id | identificador , id
        """
        t = self.newExpNode(ExpKind.ID_K)
        t.attr['name'] = self.current_lex
        self.match("ID")
        p = t
        while self.current_token == "COMA":
            self.match("COMA")
            q = self.newExpNode(ExpKind.ID_K)
            q.attr['name'] = self.current_lex
            self.match("ID")
            p.sibling = q
            p = q
        return t

    # ─── 6. lista_sentencias ─────────────────────────────────────
    def lista_sentencias(self, stop_tokens=None):
        """
        lista_sentencias → lista_sentencias sentencia | ε
        """
        if stop_tokens is None:
            stop_tokens = []
        first_stmt = last_stmt = None
        while self.current_token in ["IF","WHILE","DO","CIN","COUT","ID"] \
                and self.current_token not in stop_tokens:
            stmt = self.sentencia()
            if stmt is not None:
                if first_stmt is None:
                    first_stmt = last_stmt = stmt
                else:
                    while last_stmt.sibling is not None:
                        last_stmt = last_stmt.sibling
                    last_stmt.sibling = stmt
                    last_stmt = stmt
        return first_stmt

    # ─── 7. sentencia ────────────────────────────────────────────
    def sentencia(self):
        """
        sentencia → seleccion | iteracion | repeticion
                  | sent_in  | sent_out  | asignacion
        """
        if   self.current_token == "IF":    return self.seleccion()
        elif self.current_token == "WHILE": return self.iteracion()
        elif self.current_token == "DO":    return self.repeticion()
        elif self.current_token == "CIN":   return self.sent_in()
        elif self.current_token == "COUT":  return self.sent_out()
        elif self.current_token == "ID":    return self.asignacion()
        else:
            self.syntaxError("token inesperado al inicio de sentencia")
            self.getNextToken()
            return None

    # ─── 8. seleccion ────────────────────────────────────────────
    def seleccion(self):
        """
        seleccion → if expresion_logica then lista_sentencias
                    [ else lista_sentencias ] end
        """
        t = self.newStmtNode(StmtKind.SELECTION_K)
        self.match("IF")
        t.children[0] = self.expresion_logica()
        self.match("THEN")
        t.children[1] = self.lista_sentencias()
        if self.current_token == "ELSE":
            self.match("ELSE")
            t.children[2] = self.lista_sentencias()
        self.match("END")
        return t

    # ─── 9. iteracion ────────────────────────────────────────────
    def iteracion(self):
        """
        iteracion → while expresion_logica lista_sentencias end
        """
        t = self.newStmtNode(StmtKind.ITERATION_K)
        self.match("WHILE")
        t.children[0] = self.expresion_logica()
        t.children[1] = self.lista_sentencias()
        self.match("END")
        return t

    # ─── 10. repeticion ──────────────────────────────────────────
    def repeticion(self):
        """
        repeticion → do lista_sentencias while expresion_logica ;
        """
        t = self.newStmtNode(StmtKind.REPETITION_K)
        self.match("DO")
        t.children[0] = self.lista_sentencias(stop_tokens=["WHILE"])
        self.match("WHILE")
        t.children[1] = self.expresion_logica()
        self.match("PUNCOM")
        return t

    # ─── 11. sent_in ─────────────────────────────────────────────
    def sent_in(self):
        """
        sent_in → cin >> id ;
        """
        t = self.newStmtNode(StmtKind.SENT_IN_K)
        self.match("CIN")
        self.match("SHR")
        t.attr['name'] = self.current_lex
        self.match("ID")
        self.match("PUNCOM")
        return t

    # ─── 12. sent_out ────────────────────────────────────────────
    def sent_out(self):
        """
        sent_out → cout << salida ;
        """
        t = self.newStmtNode(StmtKind.SENT_OUT_K)
        self.match("COUT")
        self.match("SHL")
        t.children[0] = self.salida()
        self.match("PUNCOM")
        return t

    # ─── 13. salida ──────────────────────────────────────────────
    def salida(self):
        """
        salida → cadena | expresion_logica
               | cadena << expresion_logica
               | expresion_logica << cadena
        """
        t = None
        if self.current_token == "STRING":
            t = self.cadena()
            if self.current_token == "SHL":
                p = self.newExpNode(ExpKind.OP_K)
                p.attr['op'] = "SHL"
                p.children[0] = t
                self.match("SHL")
                p.children[1] = self.expresion_logica()
                t = p
        else:
            t = self.expresion_logica()
            if self.current_token == "SHL":
                p = self.newExpNode(ExpKind.OP_K)
                p.attr['op'] = "SHL"
                p.children[0] = t
                self.match("SHL")
                p.children[1] = self.cadena()
                t = p
        return t

    # ─── 14. asignacion ──────────────────────────────────────────
    def asignacion(self):
        """
        asignacion → id = sent_expresion
        """
        t = self.newStmtNode(StmtKind.ASSIGN_K)
        t.attr['name'] = self.current_lex
        self.match("ID")
        self.match("ASSIGN")
        t.children[0] = self.sent_expresion()
        return t

    # ─── 15. sent_expresion ──────────────────────────────────────
    def sent_expresion(self):
        """
        sent_expresion → expresion_logica ; | ;
        """
        if self.current_token == "PUNCOM":
            self.match("PUNCOM")
            return None
        t = self.expresion_logica()
        self.match("PUNCOM")
        return t

    # ─── 16. expresion_logica ────────────────────────────────────
    def expresion_logica(self):
        """
        expresion_logica → expresion
                         | expresion_logica op_log expresion
        op_log → && | ||
        """
        t = self.expresion()
        while self.current_token in ["AND", "OR"]:
            p = self.newExpNode(ExpKind.LOGIC_K)
            p.children[0] = t
            p.attr['op']   = self.current_token
            t = p
            self.match(self.current_token)
            t.children[1] = self.expresion()
        return t

    # ─── 17. expresion ───────────────────────────────────────────
    def expresion(self):
        """
        expresion → expresion_simple [ rel_op expresion_simple ]
        rel_op    → < | <= | > | >= | == | !=
        """
        t = self.expresion_simple()
        if self.current_token in ["LT","LE","GT","GE","EQ","NE"]:
            p = self.newExpNode(ExpKind.OP_K)
            p.children[0] = t
            p.attr['op']   = self.current_token
            t = p
            self.match(self.current_token)
            t.children[1] = self.expresion_simple()
        return t

    # ─── 18. expresion_simple ────────────────────────────────────
    def expresion_simple(self):
        """
        expresion_simple → expresion_simple suma_op termino
                         | expresion_simple inc_op
                         | termino
        suma_op → + | -
        inc_op  → ++ | --
        """
        t = self.termino()
        while self.current_token in ["MAS","MENOS","INC","DEC"]:
            p = self.newExpNode(ExpKind.OP_K)
            p.children[0] = t
            p.attr['op']   = self.current_token
            t = p
            if self.current_token in ["INC","DEC"]:
                self.match(self.current_token)          # sufijo unario
            else:
                self.match(self.current_token)
                t.children[1] = self.termino()         # binario
        return t

    # ─── 19. termino ─────────────────────────────────────────────
    def termino(self):
        """
        termino → termino mult_op factor | factor
        mult_op → * | / | %
        """
        t = self.factor()
        while self.current_token in ["MUL","DIV","MOD"]:
            p = self.newExpNode(ExpKind.OP_K)
            p.children[0] = t
            p.attr['op']   = self.current_token
            t = p
            self.match(self.current_token)
            p.children[1] = self.factor()
        return t

    # ─── 20. factor ──────────────────────────────────────────────
    def factor(self):
        """
        factor  → factor pot_op dato | dato
        pot_op  → ^
        """
        t = self.dato()
        while self.current_token == "POT":
            p = self.newExpNode(ExpKind.OP_K)
            p.children[0] = t
            p.attr['op']   = self.current_token
            t = p
            self.match("POT")
            t.children[1] = self.dato()
        return t

    # ─── 21. dato ────────────────────────────────────────────────
    def dato(self):
        """
        dato → componente
        (AND y OR se manejan SOLO en expresion_logica, no aqui,
         para evitar que consuman el && antes de que expresion_logica lo vea)
        """
        return self.componente()

    # ─── 22. componente ──────────────────────────────────────────
    def componente(self):
        """
        componente → ( expresion_logica ) | número | id | bool | ! componente
        op_logico  → !
        """
        t = None
        if self.current_token == "LPAREN":
            self.match("LPAREN")
            t = self.expresion_logica()
            self.match("RPAREN")

        elif self.current_token in ["NUM_INT","NUM_FLOAT"]:
            t = self.newExpNode(ExpKind.CONST_K)
            if self.current_token == "NUM_INT":
                try:    t.attr['val'] = int(self.current_lex)
                except: t.attr['val'] = self.current_lex
                t.type = ExpType.INTEGER
            else:
                try:    t.attr['val'] = float(self.current_lex)
                except: t.attr['val'] = self.current_lex
                t.type = ExpType.FLOAT
            self.match(self.current_token)

        elif self.current_token == "ID":
            t = self.newExpNode(ExpKind.ID_K)
            t.attr['name'] = self.current_lex
            self.match("ID")

        elif self.current_token in ["TRUE","FALSE"]:
            t = self.newExpNode(ExpKind.BOOL_K)
            t.attr['val'] = self.current_lex.upper() == "TRUE"
            t.type = ExpType.BOOLEAN
            self.match(self.current_token)

        elif self.current_token == "NOT":
            t = self.newExpNode(ExpKind.LOGIC_K)
            t.attr['op'] = "NOT"
            self.match("NOT")
            t.children[0] = self.componente()

        else:
            self.syntaxError("token inesperado en componente")
            self.getNextToken()

        return t

    # ─── 23. cadena ──────────────────────────────────────────────
    def cadena(self):
        """
        cadena → "cualquier texto"
        """
        t = self.newExpNode(ExpKind.STRING_K)
        t.attr['val'] = self.current_lex
        t.type = ExpType.STRING
        self.match("STRING")
        return t

    # ─────────────────────────────────────────────
    # Punto de entrada
    # ─────────────────────────────────────────────
    def parse(self):
        self.getNextToken()
        t = self.programa()
        if self.current_token != "EOF":
            self.syntaxError("se terminó el código antes de lo esperado")
        self.saveErrorsToFile()
        return t