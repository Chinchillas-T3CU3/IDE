# ============================================================
# codigo_tm.py
# Generador de codigo para la maquina TM (equivale a code.c + cgen.c)
#   - Emitter : utilidades de emision   (code.c)
#   - CGen    : generador de codigo     (cgen.c), extendido a todo
#               el lenguaje del compilador. Usa flotantes y cadenas
#               nativos de la TM extendida
# ============================================================
import unicodedata
from parse import NodeKind, StmtKind, ExpKind

# Registros de la TM (igual que Tiny)
AC  = 0     # acumulador
AC1 = 1     # acumulador auxiliar
GP  = 5     # puntero global (variables)
MP  = 6     # puntero de memoria (temporales)
PC  = 7     # contador de programa
# Registros 2 y 3: temporales de uso interno (%, ^, ++, --)
# TM extendida: ADDF SUBF MULF DIVF ITOF FTOI, OUT r,1,0 (float),
# OUT r,2,0 (cadena), LDC r,3.14(0) y  dir: STR "texto"


# ─────────────────────────────────────────────────────────────
# code.c  →  Emitter
# ─────────────────────────────────────────────────────────────
class Emitter:

    def __init__(self, trace=True):
        self.trace       = trace
        self.emitLoc     = 0      # ubicacion de la instruccion actual
        self.highEmitLoc = 0      # ubicacion mas alta emitida
        self.instr       = {}     # loc -> texto de la instruccion
        self.notes       = {}     # loc -> comentarios previos

    def emitComment(self, c):
        if self.trace:
            self.notes.setdefault(self.emitLoc, []).append(c)

    def _put(self, body, c):
        texto = f"{self.emitLoc:3d}:  {body} "
        if self.trace and c:
            texto += f"\t{c}"
        self.instr[self.emitLoc] = texto
        self.emitLoc += 1
        if self.highEmitLoc < self.emitLoc:
            self.highEmitLoc = self.emitLoc

    def emitRO(self, op, r, s, t, c=""):
        """Instruccion solo-registros: op r,s,t"""
        self._put(f"{op:>5s}  {r},{s},{t}", c)

    def emitRM(self, op, r, d, s, c=""):
        """Instruccion registro-memoria: op r,d(s)"""
        self._put(f"{op:>5s}  {r},{d}({s})", c)

    def emitSkip(self, howMany):
        i = self.emitLoc
        self.emitLoc += howMany
        if self.highEmitLoc < self.emitLoc:
            self.highEmitLoc = self.emitLoc
        return i

    def emitBackup(self, loc):
        if loc > self.highEmitLoc:
            self.emitComment("BUG in emitBackup")
        self.emitLoc = loc

    def emitRestore(self):
        self.emitLoc = self.highEmitLoc

    def emitRM_Abs(self, op, r, a, c=""):
        """Convierte una direccion absoluta en referencia relativa al pc."""
        self._put(f"{op:>5s}  {r},{a - (self.emitLoc + 1)}({PC})", c)

    def text(self):
        lineas = []
        for loc in range(self.highEmitLoc):
            for nota in self.notes.get(loc, []):
                lineas.append(f"* {nota}")
            if loc in self.instr:
                lineas.append(self.instr[loc])
        for nota in self.notes.get(self.highEmitLoc, []):
            lineas.append(f"* {nota}")
        return "\n".join(lineas) + "\n"


# ─────────────────────────────────────────────────────────────
# cgen.c  →  CGen   (TM extendida con flotantes y cadenas)
#
#   int   : enteros de la TM                (ADD SUB MUL DIV)
#   float : flotantes nativos               (ADDF SUBF MULF DIVF)
#   int -> float : ITOF       float -> int : FTOI
#   cout  : OUT r,0,0 entero | OUT r,1,0 float | OUT r,2,0 cadena
#   cadenas: se guardan en la memoria de datos con  dir: STR "texto"
#   cin   : la TM lee enteros; en un float el entero se convierte (10 -> 10.0)
# ─────────────────────────────────────────────────────────────
class CGen:

    REL = {"LT": "JLT", "LE": "JLE", "GT": "JGT",
           "GE": "JGE", "EQ": "JEQ", "NE": "JNE"}

    def __init__(self, symtab, trace=True):
        self.sym       = symtab
        self.e         = Emitter(trace)
        self.tmpOffset = 0              # desplazamiento de temporales (mp)
        self.avisos    = []
        self.cadenas   = {}             # texto -> direccion en memoria de datos
        # las cadenas van despues de las variables (memloc 0 .. n-1)
        self.sig_dir   = max(1, getattr(symtab, "location", 0))

    # ── Utilidades ───────────────────────────────────────────
    def loc(self, name):
        return self.sym.st_lookup_location(name)

    def var_tipo(self, name):
        b = self.sym.st_lookup(name)
        return b.type if b is not None else "Integer"

    @staticmethod
    def lit_float(v):
        """Literal flotante para LDC: siempre lleva punto decimal."""
        s = repr(float(v))
        if "e" in s or "E" in s or "inf" in s or "nan" in s:
            s = f"{float(v):.10f}"
        if "." not in s:
            s += ".0"
        return s

    @staticmethod
    def limpia_cadena(lexema):
        """Quita las comillas y los acentos (la TM maneja ASCII)."""
        t = lexema
        if len(t) >= 2 and t[0] == '"' and t[-1] == '"':
            t = t[1:-1]
        t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
        return t.replace('"', "'")

    def dir_cadena(self, texto):
        if texto not in self.cadenas:
            self.cadenas[texto] = self.sig_dir
            self.sig_dir += len(texto) + 1
            if self.sig_dir > 900:
                self.avisos.append("las cadenas ocupan demasiada memoria de datos")
        return self.cadenas[texto]

    # ── Tipo estatico de una expresion ───────────────────────
    def tipo(self, n):
        if n is None:
            return "Void"
        ek = n.kind.get("exp")
        if ek == ExpKind.CONST_K:
            return "Float" if isinstance(n.attr.get("val"), float) else "Integer"
        if ek == ExpKind.BOOL_K:
            return "Boolean"
        if ek == ExpKind.STRING_K:
            return "String"
        if ek == ExpKind.ID_K:
            return self.var_tipo(n.attr.get("name"))
        if ek == ExpKind.OP_K:
            op = n.attr.get("op")
            if op in self.REL:
                return "Boolean"
            if op in ("INC", "DEC"):
                return self.tipo(n.children[0])
            if "Float" in (self.tipo(n.children[0]), self.tipo(n.children[1])):
                return "Float"
            return "Integer"
        if ek == ExpKind.LOGIC_K:
            return "Boolean"
        return "Integer"

    # ── Conversiones sobre AC ────────────────────────────────
    def a_float(self):
        self.e.emitRO("ITOF", AC, AC, 0, "int->float")

    def a_entero(self):
        self.e.emitRO("FTOI", AC, AC, 0, "float->int")

    # ── Punto de entrada (codeGen) ───────────────────────────
    def generate(self, tree, filename="codigo.tm"):
        e = self.e
        e.emitComment("Compilacion a codigo TM")
        e.emitComment(f"Archivo: {filename}")
        e.emitComment("Preludio estandar:")
        e.emitRM("LD", MP, 0, AC, "load maxaddress from location 0")
        e.emitRM("ST", AC, 0, AC, "clear location 0")
        e.emitComment("Fin del preludio.")
        self.cGen(tree)
        e.emitComment("Fin de la ejecucion.")
        e.emitRO("HALT", 0, 0, 0, "")
        texto = e.text()
        if self.cadenas:
            texto += "* Cadenas en la memoria de datos\n"
            for cad, d in self.cadenas.items():
                texto += f'{d:3d}:  STR "{cad}"\n'
        return texto

    def cGen(self, tree):
        while tree is not None:
            if tree.nodekind == NodeKind.PROGRAM_K:
                self.cGen(tree.children[0])
            elif tree.nodekind == NodeKind.STMT_K:
                self.genStmt(tree)
            elif tree.nodekind == NodeKind.EXP_K:
                self.genExp(tree)
            tree = tree.sibling         # DeclK: no genera codigo

    # ════════════════════════════════════════════════════════
    # SENTENCIAS
    # ════════════════════════════════════════════════════════
    def genStmt(self, tree):
        e  = self.e
        sk = tree.kind.get("stmt")

        if sk == StmtKind.SELECTION_K:
            e.emitComment("-> if")
            self.genExp(tree.children[0])
            saved1 = e.emitSkip(1)
            e.emitComment("if: salto al else va aqui")
            self.cGen(tree.children[1])
            saved2 = e.emitSkip(1)
            e.emitComment("if: salto al final va aqui")
            cur = e.emitSkip(0)
            e.emitBackup(saved1)
            e.emitRM_Abs("JEQ", AC, cur, "if: salta al else")
            e.emitRestore()
            self.cGen(tree.children[2])
            cur = e.emitSkip(0)
            e.emitBackup(saved2)
            e.emitRM_Abs("LDA", PC, cur, "salta al final")
            e.emitRestore()
            e.emitComment("<- if")

        elif sk == StmtKind.ITERATION_K:
            e.emitComment("-> while")
            inicio = e.emitSkip(0)
            e.emitComment("while: el cuerpo regresa aqui")
            self.genExp(tree.children[0])
            saved = e.emitSkip(1)
            e.emitComment("while: salto de salida va aqui")
            self.cGen(tree.children[1])
            e.emitRM_Abs("LDA", PC, inicio, "while: regresa a la condicion")
            cur = e.emitSkip(0)
            e.emitBackup(saved)
            e.emitRM_Abs("JEQ", AC, cur, "while: sale si es falso")
            e.emitRestore()
            e.emitComment("<- while")

        elif sk == StmtKind.REPETITION_K:
            e.emitComment("-> do-while")
            inicio = e.emitSkip(0)
            e.emitComment("do: el cuerpo regresa aqui")
            self.cGen(tree.children[0])
            self.genExp(tree.children[1])
            e.emitRM_Abs("JNE", AC, inicio, "do-while: repite si es verdadero")
            e.emitComment("<- do-while")

        elif sk == StmtKind.ASSIGN_K:
            e.emitComment("-> assign")
            expr = tree.children[0]
            if expr is not None:
                name = tree.attr.get("name")
                tv, te = self.var_tipo(name), self.tipo(expr)
                self.genExp(expr)
                if tv == "Float" and te == "Integer":
                    self.a_float()
                elif tv == "Integer" and te == "Float":
                    self.a_entero()
                e.emitRM("ST", AC, self.loc(name), GP, "assign: guarda el valor")
            e.emitComment("<- assign")

        elif sk == StmtKind.SENT_IN_K:
            nombre   = tree.attr.get("name")
            tipo_var = self.var_tipo(nombre) 
            if tipo_var == "Float":
                e.emitRO("IN", AC, 1, 0, "read float value")
            else:
                e.emitRO("IN", AC, 0, 0, "read integer value")
            e.emitRM("ST", AC, self.loc(tree.attr.get("name")), GP, "read: guarda")

        elif sk == StmtKind.SENT_OUT_K:
            self.genOutput(tree.children[0])

    def genOutput(self, node):
        """cout << a << "texto" << b : una salida por elemento."""
        if node is None:
            return
        if node.nodekind == NodeKind.EXP_K:
            ek = node.kind.get("exp")
            if ek == ExpKind.OP_K and node.attr.get("op") == "SHL":
                self.genOutput(node.children[0])
                self.genOutput(node.children[1])
                return
            if ek == ExpKind.STRING_K:
                d = self.dir_cadena(self.limpia_cadena(str(node.attr.get("val"))))
                self.e.emitRM("LDC", AC, d, 0, "direccion de la cadena")
                self.e.emitRO("OUT", AC, 2, 0, "write cadena")
                return
        self.genExp(node)
        if self.tipo(node) == "Float":
            self.e.emitRO("OUT", AC, 1, 0, "write float")
        else:
            self.e.emitRO("OUT", AC, 0, 0, "write int")

    # ════════════════════════════════════════════════════════
    # EXPRESIONES (el resultado siempre queda en AC)
    # ════════════════════════════════════════════════════════
    def bool_por_salto(self, jop):
        e = self.e
        e.emitRM(jop,  AC, 2, PC, "br if true")
        e.emitRM("LDC", AC, 0, AC, "false case")
        e.emitRM("LDA", PC, 1, PC, "unconditional jmp")
        e.emitRM("LDC", AC, 1, AC, "true case")

    def operandos(self, tree, cl=False, cr=False, r_int=False):
        """AC1 = operando izquierdo, AC = operando derecho.
        cl / cr: convertir izq / der de int a float.  r_int: der float->int."""
        e = self.e
        self.genExp(tree.children[0])
        if cl:
            self.a_float()
        e.emitRM("ST", AC, self.tmpOffset, MP, "op: push left")
        self.tmpOffset -= 1
        self.genExp(tree.children[1])
        if cr:
            self.a_float()
        if r_int:
            self.a_entero()
        self.tmpOffset += 1
        e.emitRM("LD", AC1, self.tmpOffset, MP, "op: load left")

    def genExp(self, tree):
        e  = self.e
        ek = tree.kind.get("exp")

        if ek == ExpKind.CONST_K:
            e.emitComment("-> Const")
            v = tree.attr.get("val")
            if isinstance(v, float):
                e.emitRM("LDC", AC, self.lit_float(v), 0, "load float const")
            else:
                e.emitRM("LDC", AC, v, 0, "load const")
            e.emitComment("<- Const")

        elif ek == ExpKind.BOOL_K:
            e.emitRM("LDC", AC, 1 if tree.attr.get("val") else 0, 0, "load bool")

        elif ek == ExpKind.ID_K:
            e.emitComment("-> Id")
            e.emitRM("LD", AC, self.loc(tree.attr.get("name")), GP, "load id value")
            e.emitComment("<- Id")

        elif ek == ExpKind.STRING_K:
            e.emitRM("LDC", AC, self.dir_cadena(
                self.limpia_cadena(str(tree.attr.get("val")))), 0, "direccion de la cadena")

        elif ek == ExpKind.OP_K:
            self.genOp(tree)

        elif ek == ExpKind.LOGIC_K:
            self.genLogic(tree)

    def genOp(self, tree):
        e  = self.e
        op = tree.attr.get("op")
        c0, c1 = tree.children[0], tree.children[1]
        e.emitComment("-> Op")

        # x++ / x--  : el valor de la expresion es el valor NUEVO
        if op in ("INC", "DEC"):
            self.genExp(c0)                                  # AC = valor actual
            if c0.kind.get("exp") == ExpKind.ID_K:
                if self.tipo(c0) == "Float":
                    e.emitRM("LDC", 2, "1.0", 0, "inc/dec: constante 1.0")
                    e.emitRO("ADDF" if op == "INC" else "SUBF", 2, AC, 2, "inc/dec: nuevo valor")
                else:
                    e.emitRM("LDC", 2, 1, 0, "inc/dec: constante 1")
                    e.emitRO("ADD" if op == "INC" else "SUB", 2, AC, 2, "inc/dec: nuevo valor")
                e.emitRM("ST", 2, self.loc(c0.attr.get("name")), GP, "inc/dec: guarda")
                e.emitRM("LD", AC, self.loc(c0.attr.get("name")), GP, "inc/dec: AC = valor nuevo")
            e.emitComment("<- Op")
            return

        tl, tr = self.tipo(c0), self.tipo(c1)
        flt = "Float" in (tl, tr)

        # Conversiones de int a float
        if op == "POT":
            cl, cr, r_int = flt and tl != "Float", False, tr == "Float"
        else:
            cl, cr, r_int = flt and tl != "Float", flt and tr != "Float", False
        self.operandos(tree, cl, cr, r_int)

        if   op == "MAS":   e.emitRO("ADDF" if flt else "ADD", AC, AC1, AC, "op +")
        elif op == "MENOS": e.emitRO("SUBF" if flt else "SUB", AC, AC1, AC, "op -")
        elif op == "MUL":   e.emitRO("MULF" if flt else "MUL", AC, AC1, AC, "op *")
        elif op == "DIV":   e.emitRO("DIVF" if flt else "DIV", AC, AC1, AC, "op /")

        elif op == "MOD":   # a % b = a - trunc(a/b)*b
            if flt:
                e.emitRO("DIVF", 2, AC1, AC, "op %: a/b")
                e.emitRO("FTOI", 2, 2, 0,    "op %: trunc")
                e.emitRO("ITOF", 2, 2, 0,    "op %: a float")
                e.emitRO("MULF", 2, 2, AC,   "op %: trunc(a/b)*b")
                e.emitRO("SUBF", AC, AC1, 2, "op %: a-trunc(a/b)*b")
            else:
                e.emitRO("DIV", 2, AC1, AC, "op %: a/b")
                e.emitRO("MUL", 2, 2, AC,   "op %: (a/b)*b")
                e.emitRO("SUB", AC, AC1, 2, "op %: a-(a/b)*b")

        elif op == "POT":   # AC1 ^ AC  (exponente entero >= 0)
            base_f = flt
            e.emitRM("LDC", 2, "1.0" if base_f else 1, 0, "op ^: resultado = 1")
            ini   = e.emitSkip(0)
            saved = e.emitSkip(1)
            e.emitRO("MULF" if base_f else "MUL", 2, 2, AC1, "op ^: resultado *= base")
            e.emitRM("LDC", 3, 1, 0,   "op ^: constante 1")
            e.emitRO("SUB", AC, AC, 3, "op ^: exponente--")
            e.emitRM_Abs("LDA", PC, ini, "op ^: repite")
            cur = e.emitSkip(0)
            e.emitBackup(saved)
            e.emitRM_Abs("JLE", AC, cur, "op ^: sale si exponente <= 0")
            e.emitRestore()
            e.emitRM("LDA", AC, 0, 2, "op ^: AC = resultado")

        elif op in self.REL:
            # El signo del resultado de SUBF coincide con el signo del entero
            # que ve JLT/JGT/..., asi que los saltos sirven para floats.
            e.emitRO("SUBF" if flt else "SUB", AC, AC1, AC, "op relacional")
            self.bool_por_salto(self.REL[op])

        else:
            e.emitComment(f"BUG: operador desconocido {op}")
        e.emitComment("<- Op")

    def genLogic(self, tree):
        e  = self.e
        op = tree.attr.get("op")
        e.emitComment("-> Logic")
        if op == "NOT":
            self.genExp(tree.children[0])
            self.bool_por_salto("JEQ")          # 0 -> 1, distinto de 0 -> 0
        else:
            self.operandos(tree)
            if op == "AND":
                e.emitRO("MUL", AC, AC1, AC, "op &&")
            elif op == "OR":
                e.emitRO("ADD", AC, AC1, AC, "op ||")
                self.bool_por_salto("JGT")      # suma > 0 -> 1
        e.emitComment("<- Logic")