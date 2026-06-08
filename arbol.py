import json

# Mapeo de operadores
OPS = {
    "MAS": "+", "MENOS": "-", "MUL": "*", "DIV": "/",
    "MOD": "%", "POT": "^", "LT": "<", "LE": "<=",
    "GT": ">", "GE": ">=", "EQ": "==", "NE": "!=",
    "ASSIGN": "=", "INC": "++", "DEC": "--",
    "AND": "&&", "OR": "||", "NOT": "!",
    "SHL": "<<", "SHR": ">>"
}

class TreePrinter:
    """
    Convierte el árbol sintáctico en un dict JSON-serializable
    y también genera HTML colapsable con formato similar al ejemplo.
    """

    def toDict(self, tree):
        """Devuelve el árbol completo como dict Python (JSON-serializable)."""
        return self._nodeToDict(tree)

    def toJson(self, tree):
        return json.dumps(self.toDict(tree), ensure_ascii=False, indent=2)

    def printTree(self, tree, output_lines=None, level=0):
        """Mantiene compatibilidad con el código existente"""
        json_str = self.toJson(tree)
        if output_lines is None:
            output_lines = []
        output_lines.append(json_str)
        return output_lines

    def getFormattedText(self, tree):
        """Devuelve el árbol como texto formateado (sin HTML)"""
        lines = []
        self._nodeToText(tree, lines, 0)
        return "\n".join(lines)

    def getCollapsibleHTML(self, tree):
        """Genera HTML colapsable con el formato de texto deseado"""
        return self._generateHTML(tree)

    def _nodeToText(self, node, lines, level):
        """Convierte el árbol a texto formateado (similar al ejemplo)"""
        if node is None:
            return
        
        indent = "    " * level
        
        while node is not None:
            line = indent
            text = self._getNodeText(node)
            line += text
            lines.append(line)
            
            # Procesar hijos
            for child in node.children:
                if child is not None:
                    self._nodeToText(child, lines, level + 1)
            
            # Procesar siguiente hermano
            node = node.sibling

    def _getNodeText(self, node):
        """Obtiene el texto formateado para un nodo"""
        if node.nodekind == "ProgramK":
            return "Program"
        
        elif node.nodekind == "StmtK":
            kind = node.kind.get('stmt')
            
            if kind == "SelectionK":
                return "If"
            elif kind == "IterationK":
                return "While"
            elif kind == "RepetitionK":
                return "Repeat"
            elif kind == "AssignK":
                name = node.attr.get('name', '?')
                return f"Assign to: {name}"
            elif kind == "SentInK":
                name = node.attr.get('name', '?')
                return f"Read: {name}"
            elif kind == "SentOutK":
                return "Write"
            else:
                return str(kind)
        
        elif node.nodekind == "ExpK":
            kind = node.kind.get('exp')
            
            if kind == "OpK":
                op = node.attr.get('op', '?')
                op_str = OPS.get(op, str(op))
                return f"Op: {op_str}"
            elif kind == "ConstK":
                val = node.attr.get('val', '?')
                return f"Const: {val}"
            elif kind == "BoolK":
                val = node.attr.get('val', '?')
                return f"Bool: {val}"
            elif kind == "IdK":
                name = node.attr.get('name', '?')
                if isinstance(name, list):
                    name = ', '.join(name)
                return f"Id: {name}"
            elif kind == "StringK":
                val = node.attr.get('val', '?')
                return f"String: {val}"
            elif kind == "LogicK":
                op = node.attr.get('op', '?')
                op_str = OPS.get(op, str(op))
                return f"Logic: {op_str}"
            else:
                return f"Exp: {kind}"
        
        elif node.nodekind == "DeclK":
            kind = node.kind.get('decl')
            
            if kind == "VarDeclK":
                return "Variable Declaration"
            elif kind == "TypeK":
                type_val = node.attr.get('type', '?')
                return f"Type: {type_val}"
            else:
                return f"Decl: {kind}"
        
        else:
            return f"Unknown: {node.nodekind}"


    def _nodeToDict(self, node):
        if node is None:
            return None

        d = {
            "nodekind": node.nodekind,
            "kind":     node.kind,
            "attr":     self._safeAttr(node.attr),
            "type":     getattr(node, "type", "Void"),
            "lineno":   getattr(node, "lineno", 0),
            "children": [self._nodeToDict(c) for c in (node.children or []) if c is not None],
            "sibling":  self._nodeToDict(node.sibling),
            "display":  self._displayInfo(node),
        }
        return d

    def _safeAttr(self, attr):
        if not attr:
            return {}
        out = {}
        for k, v in attr.items():
            if isinstance(v, bool):
                out[k] = v
            elif isinstance(v, (int, float)):
                out[k] = v
            else:
                out[k] = str(v)
        return out

    def _displayInfo(self, node):
        k = node.nodekind

        if k == "ProgramK":
            return {"icon": "P", "label": "Programa", "cls": "kind-program"}

        if k == "DeclK":
            dk = node.kind.get("decl", "")
            if dk == "VarDeclK":
                return {"icon": "D", "label": "Declaración de variable", "cls": "kind-decl"}
            if dk == "TypeK":
                t = node.attr.get("type", "?")
                return {"icon": "T", "label": f"Tipo: {t}", "cls": "kind-type"}

        if k == "StmtK":
            sk = node.kind.get("stmt", "")
            has_else = node.children[2] is not None if node.children else False
            labels = {
                "SelectionK":  ("if", f"If{'-Else' if has_else else ''}", "kind-stmt"),
                "IterationK":  ("wh", "While", "kind-stmt"),
                "RepetitionK": ("do", "Do-While", "kind-stmt"),
                "AssignK":     ("=",  f"Asignar: {node.attr.get('name','?')}", "kind-stmt"),
                "SentInK":     ("in", f"Leer (cin): {node.attr.get('name','?')}", "kind-stmt"),
                "SentOutK":    ("out","Escribir (cout)", "kind-stmt"),
            }
            if sk in labels:
                icon, label, cls = labels[sk]
                return {"icon": icon, "label": label, "cls": cls}

        if k == "ExpK":
            ek = node.kind.get("exp", "")
            if ek == "OpK":
                raw = node.attr.get("op", "?")
                op = OPS.get(raw, raw)
                return {"icon": "op", "label": f"Op: {op}", "cls": "kind-op"}
            if ek == "ConstK":
                return {"icon": "#", "label": f"Constante: {node.attr.get('val','?')}", "cls": "kind-const"}
            if ek == "BoolK":
                return {"icon": "b", "label": f"Bool: {node.attr.get('val','?')}", "cls": "kind-bool"}
            if ek == "IdK":
                return {"icon": "id", "label": f"Id: {node.attr.get('name','?')}", "cls": "kind-id"}
            if ek == "StringK":
                return {"icon": '"', "label": f"Cadena: {node.attr.get('val','?')}", "cls": "kind-str"}
            if ek == "LogicK":
                raw = node.attr.get("op", "?")
                op = OPS.get(raw, raw)
                return {"icon": "&&", "label": f"Lógico: {op}", "cls": "kind-logic"}

        return {"icon": "?", "label": "Nodo desconocido", "cls": "kind-id"}