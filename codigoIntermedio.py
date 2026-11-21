# ============================================================
# codigo_intermedio.py
# Generador de código de tres direcciones (cuádruplas)
# Formato: (operacion,arg1,arg2,resultado)
# ============================================================
from parse import NodeKind, StmtKind, ExpKind, DeclKind


class TDCODE:

    ARIT = {"MAS": "add", "MENOS": "sub", "MUL": "mul",
            "DIV": "div", "MOD": "mod", "POT": "pow"}
    REL  = {"LT": "lt", "LE": "le", "GT": "gt",
            "GE": "ge", "EQ": "eq", "NE": "ne"}
    LOG  = {"AND": "and", "OR": "or"}

    def __init__(self):
        self.temp_count  = 0
        self.label_count = 0
        self.instrucciones = []

    # ── Utilidades ───────────────────────────────────────────
    def newtemp(self):
        """Genera una nueva variable temporal (t1, t2, ...)"""
        self.temp_count += 1
        return f"t{self.temp_count}"

    def newlabel(self):
        """Genera una nueva etiqueta (L1, L2, ...)"""
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, op, a="", b="", r=""):
        self.instrucciones.append(f"({op},{a},{b},{r})")

    # ── Punto de entrada ─────────────────────────────────────
    def generate(self, tree):
        """Genera el código intermedio de todo el programa."""
        self.temp_count    = 0
        self.label_count   = 0
        self.instrucciones = []
        self.gencode(tree)
        self.emit("halt")
        return self.instrucciones

    # ── Recorrido de listas (hermanos) ───────────────────────
    def gen_list(self, node):
        """Genera código de una lista de sentencias enlazadas por sibling."""
        while node is not None:
            self.gencode(node)
            node = node.sibling

    # ── Despacho por tipo de nodo ────────────────────────────
    def gencode(self, node):
        """
        Sentencias/programa/declaraciones: emite instrucciones.
        Expresiones: emite instrucciones y devuelve el operando
        (constante, id o temporal) donde queda el resultado.
        """
        if node is None:
            return ""

        if node.nodekind == NodeKind.PROGRAM_K:
            self.gen_list(node.children[0])
            return ""

        if node.nodekind == NodeKind.DECL_K:
            return ""      # las declaraciones no generan código

        if node.nodekind == NodeKind.STMT_K:
            self.gen_stmt(node)
            return ""

        if node.nodekind == NodeKind.EXP_K:
            return self.gen_exp(node)

        return ""

    # ── Sentencias ───────────────────────────────────────────
    def gen_stmt(self, node):
        sk = node.kind.get("stmt")

        # id = expresion ;   →  (asn,valor,id,)
        if sk == StmtKind.ASSIGN_K:
            if node.children[0] is not None:
                valor = self.gen_exp(node.children[0])
                self.emit("asn", valor, node.attr.get("name"))

        # cin >> id ;        →  (rd,id,,)
        elif sk == StmtKind.SENT_IN_K:
            self.emit("rd", node.attr.get("name"))

        # cout << salida ;   →  (wri,valor,,)
        elif sk == StmtKind.SENT_OUT_K:
            self.gen_output(node.children[0])

        # if cond then ... [else ...] end
        elif sk == StmtKind.SELECTION_K:
            cond  = self.gen_exp(node.children[0])
            l_fin = self.newlabel()
            if node.children[2] is not None:
                l_else = self.newlabel()
                self.emit("jf", cond, "", l_else)
                self.gen_list(node.children[1])
                self.emit("jmp", "", "", l_fin)
                self.emit("lab", l_else)
                self.gen_list(node.children[2])
                self.emit("lab", l_fin)
            else:
                self.emit("jf", cond, "", l_fin)
                self.gen_list(node.children[1])
                self.emit("lab", l_fin)

        # while cond ... end
        elif sk == StmtKind.ITERATION_K:
            l_ini = self.newlabel()
            l_fin = self.newlabel()
            self.emit("lab", l_ini)
            cond = self.gen_exp(node.children[0])
            self.emit("jf", cond, "", l_fin)
            self.gen_list(node.children[1])
            self.emit("jmp", "", "", l_ini)
            self.emit("lab", l_fin)

        # do ... while cond ;
        elif sk == StmtKind.REPETITION_K:
            l_ini = self.newlabel()
            self.emit("lab", l_ini)
            self.gen_list(node.children[0])
            cond = self.gen_exp(node.children[1])
            self.emit("jt", cond, "", l_ini)

    def gen_output(self, node):
        """cout << a << b : un (wri,...) por cada elemento."""
        if node is None:
            return
        if node.nodekind == NodeKind.EXP_K and \
           node.kind.get("exp") == ExpKind.OP_K and \
           node.attr.get("op") == "SHL":
            self.gen_output(node.children[0])
            self.gen_output(node.children[1])
        else:
            self.emit("wri", self.gen_exp(node))

    # ── Expresiones ──────────────────────────────────────────
    def gen_exp(self, node):
        if node is None:
            return ""
        ek = node.kind.get("exp")

        if ek == ExpKind.CONST_K:
            return str(node.attr.get("val"))

        if ek == ExpKind.BOOL_K:
            return "1" if node.attr.get("val") else "0"

        if ek == ExpKind.STRING_K:
            return str(node.attr.get("val"))

        if ek == ExpKind.ID_K:
            return str(node.attr.get("name"))

        if ek == ExpKind.OP_K:
            op = node.attr.get("op")

            # x++ / x--  (sufijo: el resultado es el valor anterior)
            if op in ("INC", "DEC"):
                operando = self.gen_exp(node.children[0])
                t = self.newtemp()
                self.emit("asn", operando, t)
                self.emit("add" if op == "INC" else "sub",
                          operando, "1", operando)
                return t

            izq = self.gen_exp(node.children[0])
            der = self.gen_exp(node.children[1])
            t   = self.newtemp()
            codigo = self.ARIT.get(op) or self.REL.get(op) or op.lower()
            self.emit(codigo, izq, der, t)
            return t

        if ek == ExpKind.LOGIC_K:
            op = node.attr.get("op")
            if op == "NOT":
                v = self.gen_exp(node.children[0])
                t = self.newtemp()
                self.emit("not", v, "", t)
                return t
            izq = self.gen_exp(node.children[0])
            der = self.gen_exp(node.children[1])
            t   = self.newtemp()
            self.emit(self.LOG.get(op, op.lower()), izq, der, t)
            return t

        return ""