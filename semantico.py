# ============================================================
# semantico.py
# Tabla de símbolos + Analizador Semántico para ChinchIDE
# Evaluación de expresiones constantes con propagación de valores
# ============================================================

SIZE  = 211
SHIFT = 4

OPS = {
    "MAS":"+","MENOS":"-","MUL":"*","DIV":"/","MOD":"%","POT":"^",
    "LT":"<","LE":"<=","GT":">","GE":">=","EQ":"==","NE":"!=",
    "INC":"++","DEC":"--","AND":"&&","OR":"||","NOT":"!",
    "SHL":"<<","SHR":">>"
}

# ─────────────────────────────────────────────────────────────
# ESTRUCTURAS DE LA TABLA HASH
# ─────────────────────────────────────────────────────────────

class LineList:
    def __init__(self, lineno):
        self.lineno = lineno
        self.next   = None

class BucketList:
    def __init__(self, name, lineno, memloc, var_type="Void"):
        self.name   = name
        self.memloc = memloc
        self.type   = var_type
        self.value = None
        """if var_type == "Integer":
            self.value = 0
        elif var_type == "Float":
            self.value = 0.0
        elif var_type == "Boolean":
            self.value = False
        else:
            self.value = None"""
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

    def st_insert(self, name, lineno, var_type="Void"):
        h          = self._hash(name)
        new_bucket = BucketList(name, lineno, self.location, var_type)
        new_bucket.next    = self.hash_table[h]
        self.hash_table[h] = new_bucket
        self.location     += 1

    def st_add_line(self, name, lineno):
        bucket = self.st_lookup(name)
        if bucket is None:
            return False
        t = bucket.lines
        while t.next is not None:
            t = t.next
        t.next = LineList(lineno)
        return True

    def st_lookup(self, name):
        h      = self._hash(name)
        bucket = self.hash_table[h]
        while bucket is not None and bucket.name != name:
            bucket = bucket.next
        return bucket

    def st_set_value(self, name, value):
        bucket = self.st_lookup(name)
        if bucket is not None:
            bucket.value = value

    def st_get_value(self, name):
        bucket = self.st_lookup(name)
        return bucket.value if bucket else None

    def st_lookup_location(self, name):
        b = self.st_lookup(name)
        return b.memloc if b else -1

    def get_all_symbols(self):
        symbols = []
        for i in range(SIZE):
            bucket = self.hash_table[i]
            while bucket is not None:
                nums = []
                t = bucket.lines
                while t is not None:
                    nums.append(t.lineno)
                    t = t.next
                nums = sorted(nums)
                symbols.append((bucket.name, bucket.type,
                                bucket.memloc, nums, bucket.value))
                bucket = bucket.next
        symbols.sort(key=lambda x: x[2])
        return symbols

    def printSymTab(self):
        lines = []
        lines.append("=" * 75)
        lines.append("TABLA DE SÍMBOLOS")
        lines.append("=" * 75)
        lines.append(f"{'Variable':<15} {'Tipo':<12} {'Ubic.':<7} "
                     f"{'Valor':<12} Líneas de uso")
        lines.append(f"{'-'*15} {'-'*12} {'-'*7} {'-'*12} {'-'*20}")
        for name, vtype, memloc, nums, val in self.get_all_symbols():
            val_str = str(val) if val is not None else "?"
            lines.append(
                f"{name:<15} {vtype:<12} {memloc:<7} {val_str:<12} "
                f"{', '.join(str(n) for n in nums)}"
            )
        lines.append("=" * 75)
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# NODO ANOTADO
# ─────────────────────────────────────────────────────────────

class AnnotatedNode:
    def __init__(self, nodekind, kind, attr, lineno, original_type):
        self.nodekind  = nodekind
        self.kind      = kind
        self.attr      = attr
        self.lineno    = lineno
        self.type      = original_type
        self.sem_type  = "Void"
        self.sem_value = None
        self.symbol    = None
        self.sem_error = None
        self.children  = [None, None, None]
        self.sibling   = None

    def display_label(self):
        k  = self.nodekind
        dk = self.kind.get("decl","")
        sk = self.kind.get("stmt","")
        ek = self.kind.get("exp","")

        tipo = f"  [tipo: {self.sem_type}]" if self.sem_type not in ["Void",""] else ""
        val  = f"  [val: {self.sem_value}]" if self.sem_value is not None else ""

        if k == "ProgramK":
            return "Programa"
        if k == "DeclK":
            if dk == "VarDeclK": return "Declaración de variable"
            if dk == "TypeK":    return f"Tipo: {self.attr.get('type','?')}"
        if k == "StmtK":
            if sk == "SelectionK":  return "Selección (if)"
            if sk == "IterationK":  return "Iteración (while)"
            if sk == "RepetitionK": return "Repetición (do-while)"
            if sk == "AssignK":
                return f"Asignación: {self.attr.get('name','?')}{tipo}{val}"
            if sk == "SentInK":
                return f"Leer (cin): {self.attr.get('name','?')}{tipo}"
            if sk == "SentOutK":
                return "Escribir (cout)"
        if k == "ExpK":
            if ek == "ConstK":
                return f"Constante: {self.attr.get('val','?')}{tipo}{val}"
            if ek == "BoolK":
                return f"Bool: {self.attr.get('val','?')}{tipo}{val}"
            if ek == "IdK":
                name = self.attr.get("name","?")
                sym  = (f"  [decl. línea {self.symbol.lines.lineno}]"
                        if self.symbol else "")
                return f"Id: {name}{tipo}{val}{sym}"
            if ek == "StringK":
                return f"Cadena: {self.attr.get('val','?')}{tipo}"
            if ek == "OpK":
                op = OPS.get(self.attr.get("op","?"), self.attr.get("op","?"))
                return f"Operador: {op}{tipo}{val}"
            if ek == "LogicK":
                op = OPS.get(self.attr.get("op","?"), self.attr.get("op","?"))
                return f"Lógico: {op}{tipo}{val}"
        return f"Nodo: {k}"


# ─────────────────────────────────────────────────────────────
# ANALIZADOR SEMÁNTICO
# ─────────────────────────────────────────────────────────────

class SemanticAnalyzer:

    def __init__(self):
        self.symtab             = SymbolTable()
        self.errors             = []
        self._current_decl_type = "Void"
        self._in_declaration    = False

    # ════════════════════════════════════════════════════════
    # FASE 1 — buildSymtab (igual que antes)
    # ════════════════════════════════════════════════════════

    def buildSymtab(self, syntax_tree):
        self._traverse_build(syntax_tree)

    def _traverse_build(self, node):
        if node is None:
            return
        current = node
        while current is not None:
            self._insertNode(current)
            for child in current.children:
                self._traverse_build(child)
            self._exitDeclNode(current)
            current = current.sibling

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
    # FASE 2 — árbol anotado en ORDEN SECUENCIAL
    # Se procesa cada sentencia en el orden en que aparece,
    # usando el valor actualizado de la tabla en cada paso.
    # ════════════════════════════════════════════════════════

    def buildAnnotatedTree(self, node, in_decl=False):
        """
        Construye el árbol anotado procesando los nodos en orden:
          1. Anotar hijos de expresiones (postorden, para propagar tipos)
          2. Anotar el nodo actual
          3. Anotar hermanos EN ORDEN (para que las asignaciones anteriores
             actualicen la tabla antes de que los hermanos las usen)
        """
        if node is None:
            return None

        ann = AnnotatedNode(
            node.nodekind,
            dict(node.kind),
            dict(node.attr),
            node.lineno,
            node.type
        )

        is_vardecl = (node.nodekind == "DeclK"
                      and node.kind.get("decl") == "VarDeclK")

        # Anotar hijos primero (las expresiones necesitan postorden)
        for i, child in enumerate(node.children):
            ann.children[i] = self.buildAnnotatedTree(
                child, in_decl or is_vardecl)

        # Anotar el nodo actual con los hijos ya anotados
        self._annotateNode(ann, in_decl)

        # Anotar hermano DESPUÉS (orden secuencial: primero este nodo,
        # luego el siguiente, así la tabla ya tiene el valor actualizado)
        ann.sibling = self.buildAnnotatedTree(node.sibling, in_decl)

        return ann

    def _annotateNode(self, ann, in_decl=False):
        k  = ann.nodekind
        ek = ann.kind.get("exp","")
        sk = ann.kind.get("stmt","")
        dk = ann.kind.get("decl","")

        # ── Expresiones ──────────────────────────────────────
        if k == "ExpK":

            if ek == "ConstK":
                ann.sem_type  = ann.type
                ann.sem_value = ann.attr.get("val")

            elif ek == "BoolK":
                ann.sem_type  = "Boolean"
                ann.sem_value = ann.attr.get("val")

            elif ek == "StringK":
                ann.sem_type  = "String"
                ann.sem_value = ann.attr.get("val")

            elif ek == "IdK":
                name   = ann.attr.get("name","")
                bucket = self.symtab.st_lookup(name)
                if bucket is None:
                    self._semErrorAnn(ann, f"variable '{name}' usada sin declarar")
                    ann.sem_type  = "Void"
                    ann.sem_value = None
                else:
                    if not in_decl:
                        self.symtab.st_add_line(name, ann.lineno)
                    ann.sem_type  = bucket.type
                    ann.symbol    = bucket
                    # Tomar el valor ACTUAL de la tabla en este momento
                    ann.sem_value = bucket.value

            elif ek == "OpK":
                self._evalOp(ann)

            elif ek == "LogicK":
                self._evalLogic(ann)

        # ── Sentencias ───────────────────────────────────────
        elif k == "StmtK":

            if sk == "AssignK":
                self._evalAssign(ann)

            elif sk == "SentInK":
                name   = ann.attr.get("name","")
                bucket = self.symtab.st_lookup(name)
                if bucket is None:
                    self._semErrorAnn(ann, f"variable '{name}' usada sin declarar")
                else:
                    self.symtab.st_add_line(name, ann.lineno)
                    ann.sem_type = bucket.type
                    ann.symbol   = bucket
                    # cin invalida el valor (viene del usuario)
                    bucket.value = None

            elif sk == "SelectionK":
                cond = ann.children[0]
                if cond and cond.sem_type not in ["Boolean","Void"]:
                    self._semErrorAnn(ann,
                        f"condición del 'if' debe ser Boolean "
                        f"(se encontró {cond.sem_type})")

            elif sk == "IterationK":
                cond = ann.children[0]
                if cond and cond.sem_type not in ["Boolean","Void"]:
                    self._semErrorAnn(ann,
                        f"condición del 'while' debe ser Boolean "
                        f"(se encontró {cond.sem_type})")

            elif sk == "RepetitionK":
                cond = ann.children[1]
                if cond and cond.sem_type not in ["Boolean","Void"]:
                    self._semErrorAnn(ann,
                        f"condición del 'do-while' debe ser Boolean "
                        f"(se encontró {cond.sem_type})")

        elif k == "DeclK" and dk == "TypeK":
            ann.sem_type = ann.attr.get("type","Void")

    # ─── Evaluación de operadores aritméticos/relacionales ──
    def _evalOp(self, ann):
        op    = ann.attr.get("op","")
        left  = ann.children[0]
        right = ann.children[1]
        l_t   = left.sem_type  if left  else "Void"
        r_t   = right.sem_type if right else "Void"
        l_v   = left.sem_value  if left  else None
        r_v   = right.sem_value if right else None

        # Relacionales → Boolean
        if op in ["LT","LE","GT","GE","EQ","NE"]:
            if l_t not in ["Integer","Float","Void"] or \
               r_t not in ["Integer","Float","Void"]:
                self._semErrorAnn(ann,
                    f"operador '{OPS.get(op,op)}' requiere operandos numéricos "
                    f"(se encontró {l_t}, {r_t})")
            ann.sem_type = "Boolean"
            if l_v is not None and r_v is not None:
                try:
                    ops_map = {
                        "LT": lambda a,b: a<b,  "LE": lambda a,b: a<=b,
                        "GT": lambda a,b: a>b,  "GE": lambda a,b: a>=b,
                        "EQ": lambda a,b: a==b, "NE": lambda a,b: a!=b,
                    }
                    ann.sem_value = ops_map[op](l_v, r_v)
                except Exception:
                    ann.sem_value = None

        # Aritméticos → numérico
        elif op in ["MAS","MENOS","MUL","DIV","MOD","POT"]:
            if l_t not in ["Integer","Float","Void"]:
                self._semErrorAnn(ann,
                    f"operador '{OPS.get(op,op)}' requiere operando "
                    f"izquierdo numérico ({l_t})")
            if r_t not in ["Integer","Float","Void"]:
                self._semErrorAnn(ann,
                    f"operador '{OPS.get(op,op)}' requiere operando "
                    f"derecho numérico ({r_t})")
            ann.sem_type = "Float" if "Float" in [l_t, r_t] else "Integer"
            if l_v is not None and r_v is not None:
                try:
                    if op == "MAS":   ann.sem_value = l_v + r_v
                    elif op == "MENOS": ann.sem_value = l_v - r_v
                    elif op == "MUL":   ann.sem_value = l_v * r_v
                    elif op == "DIV" and r_v != 0:
                        ann.sem_value = (l_v // r_v
                                         if ann.sem_type == "Integer"
                                         else l_v / r_v)
                    elif op == "MOD" and r_v != 0:
                        ann.sem_value = l_v % r_v
                    elif op == "POT":
                        ann.sem_value = l_v ** r_v
                except Exception:
                    ann.sem_value = None

        # ++ / -- sufijo
        elif op in ["INC","DEC"]:
            if l_t not in ["Integer","Float","Void"]:
                self._semErrorAnn(ann,
                    f"operador '{OPS.get(op,op)}' requiere operando "
                    f"numérico ({l_t})")
            ann.sem_type = l_t

            if left and left.kind.get("exp") == "IdK":
                name = left.attr.get("name","")
                if l_v is not None:
                    # Valor conocido → propagar
                    ann.sem_value = l_v                # valor ANTES del inc/dec
                    nuevo = l_v + 1 if op == "INC" else l_v - 1
                    self.symtab.st_set_value(name, nuevo)
                    if left.symbol:
                        left.symbol.value = nuevo
                """else:
                    # Valor desconocido → asumir 0 antes del inc/dec.
                    # Resultado:  1 / 1.0  si INC,  -1 / -1.0  si DEC,
                    # según el tipo del operando (Integer o Float).
                    delta = 1 if op == "INC" else -1
                    if l_t == "Float":
                        ann.sem_value = float(delta)   # 1.0  ó  -1.0
                    else:
                        ann.sem_value = int(delta)     # 1    ó  -1

                    self.symtab.st_set_value(name, ann.sem_value)
                    if left.symbol:
                        left.symbol.value = ann.sem_value"""
            else:
                # Operando no es un Id (raro, pero por seguridad)
                if l_v is not None:
                    ann.sem_value = l_v

    # ─── Evaluación de operadores lógicos ───────────────────
    def _evalLogic(self, ann):
        op    = ann.attr.get("op","")
        left  = ann.children[0]
        right = ann.children[1]
        l_t   = left.sem_type  if left  else "Void"
        r_t   = right.sem_type if right else "Void"
        l_v   = left.sem_value  if left  else None
        r_v   = right.sem_value if right else None

        ann.sem_type = "Boolean"

        if op == "NOT":
            if l_t not in ["Boolean","Void"]:
                self._semErrorAnn(ann,
                    f"operador '!' requiere operando Boolean ({l_t})")
            if l_v is not None:
                ann.sem_value = not bool(l_v)

        elif op == "AND":
            if l_t not in ["Boolean","Void"]:
                self._semErrorAnn(ann,
                    f"operador '&&' requiere operando izquierdo Boolean ({l_t})")
            if r_t not in ["Boolean","Void"]:
                self._semErrorAnn(ann,
                    f"operador '&&' requiere operando derecho Boolean ({r_t})")
            if l_v is not None and r_v is not None:
                ann.sem_value = bool(l_v) and bool(r_v)
            elif l_v is False:
                ann.sem_value = False   # cortocircuito

        elif op == "OR":
            if l_t not in ["Boolean","Void"]:
                self._semErrorAnn(ann,
                    f"operador '||' requiere operando izquierdo Boolean ({l_t})")
            if r_t not in ["Boolean","Void"]:
                self._semErrorAnn(ann,
                    f"operador '||' requiere operando derecho Boolean ({r_t})")
            if l_v is not None and r_v is not None:
                ann.sem_value = bool(l_v) or bool(r_v)
            elif l_v is True:
                ann.sem_value = True    # cortocircuito

    # ─── Evaluación de asignación ────────────────────────────
    def _evalAssign(self, ann):
        name   = ann.attr.get("name","")
        bucket = self.symtab.st_lookup(name)
        expr   = ann.children[0]

        if bucket is None:
            self._semErrorAnn(ann, f"variable '{name}' usada sin declarar")
            return

        self.symtab.st_add_line(name, ann.lineno)
        ann.sem_type = bucket.type
        ann.symbol   = bucket

        if expr is None:
            return

        var_t  = bucket.type
        expr_t = expr.sem_type
        # Marca si hubo error de tipo, para NO propagar valor
        tipo_error = False

        # Verificación de tipos
        if var_t == "Integer" and expr_t == "Float":
            self._semErrorAnn(ann,
                f"no se puede asignar Float a '{name}' (Integer)")
            tipo_error = True
        elif var_t == "Boolean" and expr_t not in ["Boolean","Void"]:
            self._semErrorAnn(ann,
                f"no se puede asignar {expr_t} a '{name}' (Boolean)")
            tipo_error = True
        elif var_t == "Float" and expr_t not in ["Integer","Float","Void"]:
            self._semErrorAnn(ann,
                f"no se puede asignar {expr_t} a '{name}' (Float)")
            tipo_error = True
        elif var_t == "Integer" and expr_t not in ["Integer","Void"]:
            self._semErrorAnn(ann,
                f"no se puede asignar {expr_t} a '{name}' (Integer)")
            tipo_error = True

        if (expr.kind.get("exp") == "OpK"
                and expr.attr.get("op") in ("INC", "DEC")
                and expr.children[0] is not None
                and expr.children[0].kind.get("exp") == "IdK"
                and expr.children[0].attr.get("name") == name):
            ann.sem_value = bucket.value   # ya lo dejó el ++/-- en la tabla
            return

        # ── Si hubo error de tipo: no guardar valor ──────────
        # El valor de la variable queda en 0 (default de su tipo).
        # En la tabla el valor se representa como None (desconocido).
        if tipo_error:
            self.symtab.st_set_value(name, None)
            bucket.value  = None
            ann.sem_value = None
            return

        # Actualizar valor en la tabla con el resultado de la expresión
        # (aunque haya error de tipo, actualizamos para seguir propagando)
        if expr.sem_value is not None:
            self.symtab.st_set_value(name, expr.sem_value)
            bucket.value  = expr.sem_value
            ann.sem_value = expr.sem_value
        else:
            # La expresión no tiene valor conocido → la variable tampoco
            self.symtab.st_set_value(name, None)
            bucket.value  = None
            ann.sem_value = None

    # ── Errores ──────────────────────────────────────────────
    def _semError(self, node, message):
        lineno    = getattr(node, "lineno", 0)
        error_msg = f"Error semántico en línea {lineno}: {message}"
        self.errors.append(error_msg)
        print(error_msg)

    def _semErrorAnn(self, ann, message):
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
        self.buildSymtab(syntax_tree)
        annotated_tree = self.buildAnnotatedTree(syntax_tree)
        self.saveErrorsToFile()
        tabla_str   = self.symtab.printSymTab()
        errores_str = ("\n".join(self.errors) if self.errors
                       else "Sin errores semánticos")
        return annotated_tree, tabla_str, errores_str