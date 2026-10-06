# ============================================================
# Tabla de símbolos + Analizador Semántico para ChinchIDE
# ============================================================

SIZE  = 211
SHIFT = 4


# ─────────────────────────────────────────────────────────────
# ESTRUCTURAS DE LA TABLA HASH
# ─────────────────────────────────────────────────────────────

class LineList:
    """Lista enlazada de líneas donde aparece una variable."""
    def __init__(self, lineno):
        self.lineno = lineno
        self.next   = None


class BucketList:
    """Entrada en la tabla hash."""
    def __init__(self, name, lineno, memloc, var_type="Void"):
        self.name   = name
        self.memloc = memloc
        self.type   = var_type
        self.lines  = LineList(lineno)
        self.next   = None


# ─────────────────────────────────────────────────────────────
# TABLA DE SÍMBOLOS
# ─────────────────────────────────────────────────────────────

class SymbolTable:

    def __init__(self):
        self.hash_table = [None] * SIZE
        self.location   = 0

    def _hash(self, key: str) -> int:
        temp = 0
        for ch in key:
            temp = ((temp << SHIFT) + ord(ch)) % SIZE
        return temp

    def st_insert(self, name: str, lineno: int, var_type: str = "Void"):
        """Inserta una variable nueva (solo desde declaraciones)."""
        h          = self._hash(name)
        new_bucket = BucketList(name, lineno, self.location, var_type)
        new_bucket.next    = self.hash_table[h]
        self.hash_table[h] = new_bucket
        self.location     += 1

    def st_add_line(self, name: str, lineno: int) -> bool:
        """Agrega línea de uso a una variable ya declarada."""
        bucket = self.st_lookup(name)
        if bucket is None:
            return False
        t = bucket.lines
        while t.next is not None:
            t = t.next
        t.next = LineList(lineno)
        return True

    def st_lookup(self, name: str):
        """Devuelve BucketList o None."""
        h      = self._hash(name)
        bucket = self.hash_table[h]
        while bucket is not None and bucket.name != name:
            bucket = bucket.next
        return bucket

    def st_lookup_location(self, name: str) -> int:
        b = self.st_lookup(name)
        if b:
            return b.memloc
        else:
            return -1

    def get_all_symbols(self) -> list:
        """Devuelve lista de (name, type, memloc, [linenos]) ordenada por memloc."""
        symbols = []
        for i in range(SIZE):
            bucket = self.hash_table[i]
            while bucket is not None:
                nums = []
                t = bucket.lines
                while t is not None:
                    nums.append(t.lineno)
                    t = t.next
                nums=sorted(nums)
                symbols.append((bucket.name, bucket.type, bucket.memloc, nums))
                bucket = bucket.next
        symbols.sort(key=lambda x: x[2])
        return symbols

    def printSymTab(self) -> str:
        lines = []
        lines.append("=" * 65)
        lines.append("TABLA DE SÍMBOLOS")
        lines.append("=" * 65)
        lines.append(f"{'Variable':<15} {'Tipo':<12} {'Ubicación':<12} Líneas de uso")
        lines.append(f"{'-'*15} {'-'*12} {'-'*12} {'-'*20}")
        for name, vtype, memloc, nums in self.get_all_symbols():
            lines.append(f"{name:<15} {vtype:<12} {memloc:<12} {', '.join(str(n) for n in nums)}")
        lines.append("=" * 65)
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# NODO ANOTADO
# Copia del TreeNode con información semántica adicional
# ─────────────────────────────────────────────────────────────

class AnnotatedNode:
    """
    Copia del nodo del AST con anotaciones semánticas:
      - type      : tipo calculado/propagado
      - value     : valor constante si se puede determinar en compilación
      - symbol    : referencia al BucketList de la tabla (si es IdK)
      - sem_error : error semántico asociado a este nodo (si aplica)
    """
    def __init__(self, original_node):
        # Copiar estructura del nodo original
        self.nodekind = original_node.nodekind
        self.kind     = dict(original_node.kind)
        self.attr     = dict(original_node.attr)
        self.lineno   = original_node.lineno
        self.type     = original_node.type   # se actualiza durante el análisis

        # Anotaciones semánticas nuevas
        self.sem_type   = "Void"   # tipo calculado/propagado en esta fase
        self.sem_value  = None     # valor constante (solo para expresiones constantes)
        self.symbol     = None     # BucketList si es un identificador
        self.sem_error  = None     # error semántico en este nodo

        # Hijos y hermano (se llenan al construir el árbol anotado)
        self.children = [None, None, None]
        self.sibling  = None

    def display_label(self) -> str:
        """Texto para mostrar en el árbol anotado."""
        OPS = {
            "MAS":"+","MENOS":"-","MUL":"*","DIV":"/","MOD":"%","POT":"^",
            "LT":"<","LE":"<=","GT":">","GE":">=","EQ":"==","NE":"!=",
            "INC":"++","DEC":"--","AND":"&&","OR":"||","NOT":"!","SHL":"<<","SHR":">>"
        }
        k  = self.nodekind
        dk = self.kind.get("decl","")
        sk = self.kind.get("stmt","")
        ek = self.kind.get("exp","")

        # ── Programa ─────────────────────────────────────────
        if k == "ProgramK":
            return "Programa"

        # ── Declaraciones ─────────────────────────────────────
        if k == "DeclK":
            if dk == "VarDeclK":
                return "Declaración de variable"
            if dk == "TypeK":
                return f"Tipo: {self.attr.get('type','?')}"

        # ── Sentencias ────────────────────────────────────────
        if k == "StmtK":
            if sk == "SelectionK":
                return "Selección (if)"
            if sk == "IterationK":
                return "Iteración (while)"
            if sk == "RepetitionK":
                return "Repetición (do-while)"
            if sk == "AssignK":
                name = self.attr.get("name","?")
                t    = f"  [tipo: {self.sem_type}]" if self.sem_type != "Void" else ""
                return f"Asignación: {name}{t}"
            if sk == "SentInK":
                name = self.attr.get("name","?")
                t    = f"  [tipo: {self.sem_type}]" if self.sem_type != "Void" else ""
                return f"Leer (cin): {name}{t}"
            if sk == "SentOutK":
                return "Escribir (cout)"

        # ── Expresiones ───────────────────────────────────────
        if k == "ExpK":
            tipo = f"  [tipo: {self.sem_type}]" if self.sem_type != "Void" else ""
            val  = f"  [val: {self.sem_value}]"  if self.sem_value is not None else ""

            if ek == "ConstK":
                return f"Constante: {self.attr.get('val','?')}{tipo}{val}"
            if ek == "BoolK":
                return f"Bool: {self.attr.get('val','?')}{tipo}"
            if ek == "IdK":
                name = self.attr.get("name","?")
                sym  = f"  [decl. línea {self.symbol.lines.lineno}]" if self.symbol else ""
                return f"Id: {name}{tipo}{sym}"
            if ek == "StringK":
                return f"Cadena: {self.attr.get('val','?')}{tipo}"
            if ek == "OpK":
                op = OPS.get(self.attr.get("op","?"), self.attr.get("op","?"))
                return f"Operador: {op}{tipo}{val}"
            if ek == "LogicK":
                op = OPS.get(self.attr.get("op","?"), self.attr.get("op","?"))
                return f"Lógico: {op}{tipo}"

        return f"Nodo: {k}"


# ─────────────────────────────────────────────────────────────
# ANALIZADOR SEMÁNTICO
# ─────────────────────────────────────────────────────────────

OPS = {
    "MAS":"+","MENOS":"-","MUL":"*","DIV":"/","MOD":"%","POT":"^",
    "LT":"<","LE":"<=","GT":">","GE":">=","EQ":"==","NE":"!=",
    "INC":"++","DEC":"--","AND":"&&","OR":"||","NOT":"!","SHL":"<<","SHR":">>"
}

class SemanticAnalyzer:

    def __init__(self):
        self.symtab             = SymbolTable()
        self.errors             = []
        self._current_decl_type = "Void"
        self._in_declaration    = False

    # ── Traversal genérico ───────────────────────────────────
    def traverse(self, node, pre_proc, post_proc):
        if node is None:
            return

        current = node

        while current is not None:
            pre_proc(current)

            for child in current.children:
                self.traverse(child, pre_proc, post_proc)

            post_proc(current)

            current = current.sibling

            #post_proc(node)

    def _null_proc(self, node):
        pass

    # ════════════════════════════════════════════════════════
    # FASE 1 — buildSymtab (preorden sobre AST original)
    # Solo declaracion_variable inserta en la tabla.
    # ════════════════════════════════════════════════════════

    def buildSymtab(self, syntax_tree):
        self.traverse(syntax_tree, self._insertNode, self._exitDeclNode)

    def _insertNode(self, node):
        k = node.nodekind
        if k == "DeclK":
            dk = node.kind.get("decl","")
            if dk == "TypeK":
                self._current_decl_type = node.attr.get("type","Void")
                self._in_declaration    = True
            return

        if k == "ExpK" and node.kind.get("exp") == "IdK":
            name = node.attr.get("name","")
            if not name:
                return
            if self._in_declaration:
                existing = self.symtab.st_lookup(name)
                if existing is not None:
                    self._semError(node,
                        f"variable '{name}' ya fue declarada "
                        f"(primera declaración en línea {existing.lines.lineno})")
                else:
                    self.symtab.st_insert(name, node.lineno, self._current_decl_type)

    def _exitDeclNode(self, node):
        if node.nodekind == "DeclK" and node.kind.get("decl") == "VarDeclK":
            self._in_declaration    = False
            self._current_decl_type = "Void"

    # ════════════════════════════════════════════════════════
    # FASE 2 — construir árbol anotado + verificar tipos
    # ════════════════════════════════════════════════════════

    # >>> se agrega parámetro in_decl para saber si estamos
    # dentro de una declaración de variable.
    def buildAnnotatedTree(self, node, in_decl=False) -> AnnotatedNode:
        """
        Construye recursivamente el árbol anotado a partir del AST original.
        Propaga tipos de hojas a raíces (postorden implícito en la recursión).

        in_decl: True si el nodo actual (o alguno de sus ancestros) es una
                 declaración de variable. Sirve para NO registrar la línea
                 de declaración como una línea de uso.
        """
        if node is None:
            return None

        ann = AnnotatedNode(node)

        # Detectar si este nodo inicia una declaración de variable
        is_vardecl = (node.nodekind == "DeclK"
                      and node.kind.get("decl") == "VarDeclK")

        # Construir hijos primero (postorden: hijos antes que padre)
        for i, child in enumerate(node.children):
            ann.children[i] = self.buildAnnotatedTree(child, in_decl or is_vardecl)

        # Construir hermano
        ann.sibling = self.buildAnnotatedTree(node.sibling, in_decl)

        # Anotar este nodo según su tipo
        self._annotateNode(ann, in_decl)

        return ann

    # >>> CAMBIO: se agrega parámetro in_decl.
    def _annotateNode(self, ann: AnnotatedNode, in_decl=False):
        """
        Calcula y propaga atributos semánticos para un nodo.
        Los hijos ya están anotados cuando se llama a este método.
        """
        k  = ann.nodekind
        ek = ann.kind.get("exp","")
        sk = ann.kind.get("stmt","")
        dk = ann.kind.get("decl","")

        # ── Expresiones ──────────────────────────────────────
        if k == "ExpK":

            # Constante numérica
            if ek == "ConstK":
                ann.sem_type  = ann.type   # INTEGER o FLOAT, asignado por parser
                ann.sem_value = ann.attr.get("val")

            # Booleano literal
            elif ek == "BoolK":
                ann.sem_type  = "Boolean"
                ann.sem_value = ann.attr.get("val")

            # Cadena
            elif ek == "StringK":
                ann.sem_type  = "String"
                ann.sem_value = ann.attr.get("val")

            # Identificador en uso
            elif ek == "IdK":
                name   = ann.attr.get("name","")
                bucket = self.symtab.st_lookup(name)
                if bucket is None:
                    self._semErrorAnn(ann, f"variable '{name}' usada sin declarar")
                    ann.sem_type = "Void"
                else:
                    # >>>  si estamos dentro de una declaración,
                    # NO registramos la línea como uso (ya fue registrada
                    # al insertar el símbolo en buildSymtab).
                    if not in_decl:
                        self.symtab.st_add_line(name, ann.lineno)
                    ann.sem_type = bucket.type
                    ann.symbol   = bucket

            # Operador aritmético / relacional
            elif ek == "OpK":
                op   = ann.attr.get("op","")
                left  = ann.children[0]
                right = ann.children[1]
                l_t   = left.sem_type  if left  else "Void"
                r_t   = right.sem_type if right else "Void"

                if op in ["LT","LE","GT","GE","EQ","NE"]:
                    if l_t not in ["Integer","Float","Void"] or \
                       r_t not in ["Integer","Float","Void"]:
                        self._semErrorAnn(ann,
                            f"operador '{OPS.get(op,op)}' requiere operandos numéricos "
                            f"(se encontró {l_t}, {r_t})")
                    ann.sem_type = "Boolean"

                elif op in ["MAS","MENOS","MUL","DIV","MOD","POT"]:
                    if l_t not in ["Integer","Float","Void"]:
                        self._semErrorAnn(ann,
                            f"operador '{OPS.get(op,op)}' requiere operando izquierdo numérico ({l_t})")
                    if r_t not in ["Integer","Float","Void"]:
                        self._semErrorAnn(ann,
                            f"operador '{OPS.get(op,op)}' requiere operando derecho numérico ({r_t})")
                    ann.sem_type = "Float" if "Float" in [l_t, r_t] else "Integer"

                    # Propagación de valor constante
                    if left and right and \
                       left.sem_value is not None and right.sem_value is not None:
                        try:
                            lv, rv = left.sem_value, right.sem_value
                            if op == "MAS":   ann.sem_value = lv + rv
                            elif op == "MENOS": ann.sem_value = lv - rv
                            elif op == "MUL":   ann.sem_value = lv * rv
                            elif op == "DIV" and rv != 0:
                                ann.sem_value = lv // rv if ann.sem_type == "Integer" else lv / rv
                            elif op == "MOD" and rv != 0:
                                ann.sem_value = lv % rv
                            elif op == "POT":
                                ann.sem_value = lv ** rv
                        except Exception:
                            ann.sem_value = None

                elif op in ["INC","DEC"]:
                    if l_t not in ["Integer","Float","Void"]:
                        self._semErrorAnn(ann,
                            f"operador '{OPS.get(op,op)}' requiere operando numérico ({l_t})")
                    ann.sem_type = l_t

            # Operador lógico
            elif ek == "LogicK":
                op    = ann.attr.get("op","")
                left  = ann.children[0]
                right = ann.children[1]
                l_t   = left.sem_type  if left  else "Void"
                r_t   = right.sem_type if right else "Void"

                if op == "NOT":
                    if l_t not in ["Boolean","Void"]:
                        self._semErrorAnn(ann,
                            f"operador '!' requiere operando Boolean ({l_t})")
                    if left and left.sem_value is not None:
                        ann.sem_value = not left.sem_value
                else:
                    if l_t not in ["Boolean","Void"]:
                        self._semErrorAnn(ann,
                            f"operador '{OPS.get(op,op)}' requiere operando izquierdo Boolean ({l_t})")
                    if r_t not in ["Boolean","Void"]:
                        self._semErrorAnn(ann,
                            f"operador '{OPS.get(op,op)}' requiere operando derecho Boolean ({r_t})")
                ann.sem_type = "Boolean"

        # ── Sentencias ───────────────────────────────────────
        elif k == "StmtK":

            # Asignación
            if sk == "AssignK":
                name   = ann.attr.get("name","")
                bucket = self.symtab.st_lookup(name)
                expr   = ann.children[0]

                if bucket is None:
                    self._semErrorAnn(ann, f"variable '{name}' usada sin declarar")
                else:
                    self.symtab.st_add_line(name, ann.lineno)
                    ann.sem_type = bucket.type
                    ann.symbol   = bucket

                    if expr:
                        var_t  = bucket.type
                        expr_t = expr.sem_type
                        if var_t == "Integer" and expr_t == "Float":
                            self._semErrorAnn(ann,
                                f"no se puede asignar Float a '{name}' (Integer)")
                        elif var_t == "Boolean" and expr_t not in ["Boolean","Void"]:
                            self._semErrorAnn(ann,
                                f"no se puede asignar {expr_t} a '{name}' (Boolean)")
                        elif var_t == "Float" and expr_t not in ["Integer","Float","Void"]:
                            self._semErrorAnn(ann,
                                f"no se puede asignar {expr_t} a '{name}' (Float)")
                        elif var_t == "Integer" and expr_t not in ["Integer","Void"]:
                            self._semErrorAnn(ann,
                                f"no se puede asignar {expr_t} a '{name}' (Integer)")

            # cin >> id
            elif sk == "SentInK":
                name   = ann.attr.get("name","")
                bucket = self.symtab.st_lookup(name)
                if bucket is None:
                    self._semErrorAnn(ann, f"variable '{name}' usada sin declarar")
                else:
                    self.symtab.st_add_line(name, ann.lineno)
                    ann.sem_type = bucket.type
                    ann.symbol   = bucket

            # if — condición debe ser Boolean
            elif sk == "SelectionK":
                cond = ann.children[0]
                if cond and cond.sem_type not in ["Boolean","Void"]:
                    self._semErrorAnn(ann,
                        f"condición del 'if' debe ser Boolean (se encontró {cond.sem_type})")

            # while — condición debe ser Boolean
            elif sk == "IterationK":
                cond = ann.children[0]
                if cond and cond.sem_type not in ["Boolean","Void"]:
                    self._semErrorAnn(ann,
                        f"condición del 'while' debe ser Boolean (se encontró {cond.sem_type})")

            # do-while — condición debe ser Boolean
            elif sk == "RepetitionK":
                cond = ann.children[1]
                if cond and cond.sem_type not in ["Boolean","Void"]:
                    self._semErrorAnn(ann,
                        f"condición del 'do-while' debe ser Boolean (se encontró {cond.sem_type})")

        # ── Declaración de variable ───────────────────────────
        elif k == "DeclK" and dk == "TypeK":
            ann.sem_type = ann.attr.get("type","Void")

    # ── Errores ──────────────────────────────────────────────
    def _semError(self, node, message):
        lineno    = getattr(node, "lineno", 0)
        error_msg = f"Error semántico en línea {lineno}: {message}"
        self.errors.append(error_msg)
        print(error_msg)

    def _semErrorAnn(self, ann: AnnotatedNode, message):
        error_msg = f"Error semántico en línea {ann.lineno}: {message}"
        ann.sem_error = message
        self.errors.append(error_msg)
        print(error_msg)

    def saveErrorsToFile(self, filename="erroresSem.txt"):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                if self.errors:
                    f.write("ERRORES SEMÁNTICOS\n")
                    f.write("=" * 60 + "\n")
                    for i, e in enumerate(self.errors, 1):
                        f.write(f"{i}. {e}\n")
                else:
                    f.write("")
        except Exception as e:
            print(f"Error guardando errores semánticos: {e}")

    # ── Punto de entrada ─────────────────────────────────────
    def analyze(self, syntax_tree):
        """
        Ejecuta las dos fases y devuelve (annotated_tree, tabla_str, errores_str).
        """
        # Fase 1: poblar la tabla con declaraciones
        self.buildSymtab(syntax_tree)

        # Fase 2: construir árbol anotado + verificar tipos
        annotated_tree = self.buildAnnotatedTree(syntax_tree)

        self.saveErrorsToFile()

        tabla_str   = self.symtab.printSymTab()
        errores_str = "\n".join(self.errors) if self.errors \
                      else " Sin errores semánticos"

        return annotated_tree, tabla_str, errores_str