import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTextEdit,
    QVBoxLayout, QHBoxLayout, QTabWidget,
    QFileDialog, QMessageBox, QMenuBar, QMenu,QLabel,
    QWidgetAction,QTreeWidgetItem, QTreeWidget
)
from PyQt6.QtGui import QAction, QPainter, QTextFormat
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtWidgets import QPlainTextEdit
from contador_lineas import CodeEditor
from PyQt6.QtGui import QAction, QIcon
from lexico import Scanner
import os
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
base_path = os.path.dirname(__file__)
abrir_icon = os.path.join(base_path, "icons/abrir.png")
nuevo_icon = os.path.join(base_path, "icons/nuevo.png")
cerrar_icon = os.path.join(base_path, "icons/cerrar.png")
guardar_icon = os.path.join(base_path, "icons/guardar.png")
ejecutar_icon = os.path.join(base_path, "icons/ejecutar.png")
guardarComo_icon = os.path.join(base_path, "icons/guardarComo.png")
salir_icon = os.path.join(base_path, "icons/salir.png")


def _build_tree_html(tree_json: str) -> str:
    """
        Genera una página HTML completa con el árbol colapsable.
        tree_json es el string JSON producido por TreePrinter.toJson().
        """
    return f"""<!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    body{{font-family:system-ui,sans-serif;font-size:13px;margin:0;padding:8px;
            background:#fff;color:#1a1a1a}}
    .node-wrap{{margin:0;padding:0}}
    .node-row{{display:flex;align-items:center;gap:6px;padding:3px 6px;
                border-radius:6px;cursor:pointer;user-select:none;min-height:28px}}
    .node-row:hover{{background:#f3f3f3}}
    .toggle-btn{{width:14px;height:14px;display:flex;align-items:center;
                justify-content:center;flex-shrink:0;color:#888;font-size:10px;
                transition:transform 0.15s}}
    .toggle-btn.open{{transform:rotate(90deg)}}
    .toggle-btn.leaf{{opacity:0}}
    .node-icon{{width:20px;height:20px;border-radius:4px;display:flex;
                align-items:center;justify-content:center;flex-shrink:0;
                font-size:10px;font-weight:600}}
    .node-label{{font-size:13px;color:#1a1a1a}}
    .children{{padding-left:20px;border-left:1.5px solid #e0e0e0;margin-left:13px}}
    .role-tag{{font-size:10px;color:#999;padding:2px 0 0 4px;font-family:monospace}}
    
    .kind-program .node-icon{{background:#EEEDFE;color:#3C3489}}
    .kind-decl .node-icon{{background:#E6F1FB;color:#0C447C}}
    .kind-stmt .node-icon{{background:#E1F5EE;color:#085041}}
    .kind-op .node-icon{{background:#FAEEDA;color:#854F0B}}
    .kind-type .node-icon{{background:#FAECE7;color:#712B13}}
    .kind-id .node-icon{{background:#F1EFE8;color:#444441}}
    .kind-const .node-icon{{background:#EAF3DE;color:#27500A}}
    .kind-logic .node-icon{{background:#FBEAF0;color:#72243E}}
    .kind-str .node-icon{{background:#FCEBEB;color:#791F1F}}
    .kind-bool .node-icon{{background:#E1F5EE;color:#0F6E56}}
    </style>
    </head>
    <body>
    <div id="root"></div>
    <script>
    const TREE = {tree_json};
    
    function buildNode(node){{
    if(!node) return null;
    const info = node.display || {{}};
    const wrap = document.createElement('div');
    wrap.className = 'node-wrap';
    
    const row = document.createElement('div');
    row.className = 'node-row ' + (info.cls||'');
    
    const kids = (node.children||[]).filter(Boolean);
    const hasSibling = !!node.sibling;
    
    const toggle = document.createElement('span');
    toggle.className = 'toggle-btn' + (kids.length ? ' open' : ' leaf');
    toggle.innerHTML = '&#9654;';
    
    const icon = document.createElement('span');
    icon.className = 'node-icon';
    icon.textContent = info.icon || '?';
    
    const lbl = document.createElement('span');
    lbl.className = 'node-label';
    lbl.textContent = info.label || node.nodekind;
    
    row.appendChild(toggle);
    row.appendChild(icon);
    row.appendChild(lbl);
    wrap.appendChild(row);
    
    if(kids.length){{
        const cw = document.createElement('div');
        cw.className = 'children';
        const roles = ['child[0]','child[1]','child[2]'];
        kids.forEach((child, i)=>{{
        const rl = document.createElement('div');
        rl.className='role-tag';
        rl.textContent = roles[i]||'child';
        cw.appendChild(rl);
        cw.appendChild(buildNode(child));
        // hermanos del hijo
        let sib = child.sibling;
        while(sib){{
            const sl = document.createElement('div');
            sl.className='role-tag';
            sl.textContent='sibling';
            cw.appendChild(sl);
            cw.appendChild(buildNode(sib));
            sib = sib.sibling;
        }}
        }});
        wrap.appendChild(cw);
        row.addEventListener('click', ()=>{{
        const open = cw.style.display !== 'none';
        cw.style.display = open ? 'none' : '';
        toggle.classList.toggle('open', !open);
        }});
    }}
    return wrap;
    }}
    
    const root = document.getElementById('root');
    if(TREE){{ root.appendChild(buildNode(TREE)); }}
    else{{ root.textContent = 'Árbol vacío'; }}
    </script>
    </body>
    </html>"""
# ===============================
# Ventana principal
# ===============================
class CompilerIDE(QMainWindow):
    open_windows = []
    def __init__(self, fileName="SinTitulo"):
        super().__init__()
        self.file_name = fileName
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("QMenu::item { padding: 5px 25px 5px 25px; }")
        self.initUI()
        self.setWindowTitle(f"ChinchIDE ")
        if self.file_name!="SinTitulo":
            self.loadFile(self.file_name)
        CompilerIDE.open_windows.append(self)

    def initUI(self):

        # ===== Editor =====
        self.editor_tabs = QTabWidget()
        #self.editor = CodeEditor()
        #self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        #self.editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(
            lambda : self.closeFile())
        tab_count = self.editor_tabs.count()
        if tab_count==0:
             self.createEditorTab()

        # ===== Tabs de resultados =====
        self.tabs = QTabWidget()
        self.tab_lexico = QTextEdit()
        self.tab_sintactico = QTreeWidget()  # Cambiar a QTreeWidget
        self.tab_sintactico.setHeaderLabel("Árbol Sintáctico")  # Título
        self.tab_sintactico.setIndentation(20)  # Indentación
        self.tab_semantico = QTextEdit()
        self.tab_tabla = QTextEdit()
        self.tab_codigo = QTextEdit()

        self.tabs.addTab(self.tab_lexico, "Léxico")
        self.tabs.addTab(self.tab_sintactico, "Sintáctico")
        self.tabs.addTab(self.tab_semantico, "Semántico")
        self.tabs.addTab(self.tab_tabla, "Tabla de Simbolos")
        self.tabs.addTab(self.tab_codigo, "Código Intermedio")

        # ===== Panel de errores =====
        self.error_panel = QTabWidget()
        self.error_panel.setMaximumHeight(150)
        self.error_lexico = QTextEdit()
        self.error_sintactico = QTextEdit()
        self.error_semantico = QTextEdit()
        self.result_compilado = QTextEdit()

        self.error_panel.addTab(self.error_lexico, "Errores Léxico")
        self.error_panel.addTab(self.error_sintactico, "Errores Sintáctico")
        self.error_panel.addTab(self.error_semantico, " ErroresSemántico")
        self.error_panel.addTab(self.result_compilado, "Resultado de ejecución")

        # ===== Layout principal =====
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout_horizontal = QHBoxLayout()
        #layout_horizontal.addWidget(self.editor, 2)
        layout_horizontal.addWidget(self.editor_tabs, 2)
        layout_horizontal.addWidget(self.tabs, 1)

        layout_principal = QVBoxLayout()
        layout_principal.addLayout(layout_horizontal)
        layout_principal.addWidget(self.error_panel)

        central_widget.setLayout(layout_principal)

        # ====== Menú superior ======
        self.createMenu()
        # ====== Linea Columna ======
        self.label_posicion = QLabel("Línea: 1  Columna: 1")
        self.statusBar().addWidget(self.label_posicion)
        self.editor_tabs.currentChanged.connect(self.updateStatusBar)


    # ==========================
    # Menú
    # ==========================
    def createMenu(self):

        menubar = self.menuBar()

        open_icon_action = QAction(QIcon(abrir_icon), "Open", self)
        open_icon_action.triggered.connect(self.openFile)

        save_icon_action = QAction(QIcon(guardar_icon), "Save", self)
        save_icon_action.triggered.connect(self.saveFile)

        new_icon_action = QAction(QIcon(nuevo_icon), "New", self)
        new_icon_action.triggered.connect(self.newFile)

        close_icon_action = QAction(QIcon(cerrar_icon), "Close", self)
        close_icon_action.triggered.connect(self.closeFile)

        salir_icon_action = QAction(QIcon(salir_icon), "Salir", self)
        salir_icon_action.triggered.connect(self.exitIDE)

        compile_icon_action = QAction(QIcon(ejecutar_icon), "Compilar", self)
        compile_icon_action.triggered.connect(self.compileCode)

        guardarComo_icon_action = QAction(QIcon(guardarComo_icon), "Save as", self)
        guardarComo_icon_action.triggered.connect(self.saveAsFile)

        # ----- Archivo -----
        file_menu = menubar.addMenu("Archivo")

        new_action = QAction("Nuevo", self)
        new_action.triggered.connect(self.newFile)
        file_menu.addAction(new_action)

        open_action = QAction("Abrir", self)
        open_action.triggered.connect(self.openFile)
        file_menu.addAction(open_action)

        close_action = QAction("Cerrar", self)
        close_action.triggered.connect(self.closeFile)
        file_menu.addAction(close_action)

        save_action = QAction("Guardar", self)
        save_action.triggered.connect(self.saveFile)
        file_menu.addAction(save_action)

        save_as_action = QAction("Guardar Como", self)
        save_as_action.triggered.connect(self.saveAsFile)
        file_menu.addAction(save_as_action)

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.exitIDE)
        file_menu.addAction(exit_action)



        # ----- Compilar -----
        build_menu = menubar.addMenu("Compilar")

        compile_action = QAction("Compilar", self)
        compile_action.triggered.connect(self.compileCode)
        build_menu.addAction(compile_action)
        lexico_action = QAction("Analisis Lexico", self)
        lexico_action.triggered.connect(self.lexicoCode)
        build_menu.addAction(lexico_action)
        sintactic_action = QAction("Analisis Sintactico", self)
        sintactic_action.triggered.connect(self.SintacticCode)
        build_menu.addAction(sintactic_action)
        semantic_action = QAction("Analisis Semantico", self)
        semantic_action.triggered.connect(self.semanticCode)
        build_menu.addAction(semantic_action)
        #Tabsimbol_action = QAction("Tabla de Simbolos", self)
        #Tabsimbol_action.triggered.connect(self.TabSimbolCode)
        #build_menu.addAction(compile_action)
        InterCode_action = QAction("Codigo Intermedio", self)
        InterCode_action.triggered.connect(self.InterCodeCode)
        build_menu.addAction(InterCode_action)

        #------ iconos ------
        menubar.addAction(new_icon_action)
        menubar.addAction(open_icon_action)
        menubar.addAction(close_icon_action)
        menubar.addAction(save_icon_action)
        menubar.addAction(guardarComo_icon_action)
        menubar.addAction(salir_icon_action)
        menubar.addAction(compile_icon_action)
        menubar.addAction(lexico_action)
        menubar.addAction(sintactic_action)
        menubar.addAction(semantic_action)
        menubar.addAction(InterCode_action)
    
        


    def updateStatusBar(self):
        editor = self.currentEditor()
        if editor:
            line = editor.currentLine()
            col = editor.currentCol()
            self.label_posicion.setText(f"Línea: {line}  Columna: {col}")



    # ==========================
    # Funciones del menú
    # ==========================
    def createEditorTab(self, content="", file_name="SinTitulo"):
        editor = CodeEditor()
        editor.setPlainText(content)
        editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        editor.cursorPositionChanged.connect(self.updateStatusBar)
        index = self.editor_tabs.addTab(editor, os.path.basename(file_name))
        self.editor_tabs.setCurrentIndex(index)

        return editor

    def openFile(self):
        #fileName_aux=self.file_name
        #fileName, _ = QFileDialog.getOpenFileName(self,"Open File","","VIC Files (*.vic)")
        #if fileName!=fileName_aux and fileName_aux!="SinTitulo":
        #    new_window=CompilerIDE(fileName)
        #    new_window.show()
        #else:
        #    self.loadFile(fileName)
        fileName, _ = QFileDialog.getOpenFileName(self,"Open File","","VIC Files (*.vic)")

        if not fileName:
            return

        try:
            with open(fileName, "r", encoding="latin-1") as file:
                content = file.read()
                editor=self.createEditorTab(content, fileName)
                editor.file_path = fileName
                editor.cursorPositionChanged.connect(self.updateStatusBar)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            

    def saveFile(self):
        editor = self.currentEditor()
        index = self.editor_tabs.currentIndex()

        if not hasattr(editor, "file_path") or editor.file_path == "SinTitulo":
            fileName, _ = QFileDialog.getSaveFileName(self,"Save File","","VIC Files (*.vic)")

            if not fileName:
                return

            if not fileName.endswith(".vic"):
                fileName += ".vic"

            editor.file_path = fileName

        with open(editor.file_path, "w", encoding="latin-1") as file:
            file.write(editor.toPlainText())

  
        tab_name = os.path.basename(editor.file_path)
        self.editor_tabs.setTabText(index, tab_name)

        print("Guardado correctamente:", editor.file_path)
        
    
        
        #    if fileName:
        #            with open(fileName, "w", encoding="latin-1") as file:
        #                file.write(self.currentEditor().toPlainText())
        #                self.file_name=fileName
        #                index = self.editor_tabs.setCurrentIndex(index)
        #                self.currentEditor()
        #else:
        #    if fileName:
        #            with open(fileName, "w", encoding="latin-1") as file:
        #                file.write(self.currentEditor().toPlainText())
        #                self.file_name=fileName
        #                self.setWindowTitle(f"ChinchIDE - {fileName}")



    def newFile(self):
        #new_window=CompilerIDE()
        #new_window.show()
        self.createEditorTab()


        

    def closeFile(self):
        fileName=self.file_name
        respuesta = QMessageBox.question(
        self,
        "Confirmar",
        "¿Deseas guardar los cambios?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if respuesta==QMessageBox.StandardButton.Yes:
            self.saveFile()


        index=self.editor_tabs.currentIndex()
        self.editor_tabs.removeTab(index)

        #tab_count = self.editor_tabs.count()
        #if tab_count==0:
         #    self.createEditorTab()


        

        #print("Numero de ventanas:" + str(len(CompilerIDE.open_windows)))
        #if len(CompilerIDE.open_windows)==1:
            #sys.exit()

        #index=CompilerIDE.open_windows.index(self)
        #if index==0:
            #self.hide()

        #else:
            #if self in CompilerIDE.open_windows:
            #    index=CompilerIDE.open_windows.index(self)
            #    CompilerIDE.open_windows.remove(self)
            #    print(index)

            
   

    def saveAsFile(self):
        #fileName, _ = QFileDialog.getSaveFileName(
        #    self,"Save File","", "VIC Files (*.vic)")
        #if fileName:
        #    if not fileName.endswith(".vic"):
        #        fileName+=".vic"
        #    with open(fileName, "w", encoding="latin-1") as file:
        #        file.write(self.currentEditor().toPlainText())
        #        self.file_name=fileName
        #        self.editor_tabs

        editor = self.currentEditor()
        index = self.editor_tabs.currentIndex()
        fileName=self.file_name
        fileName, _ = QFileDialog.getSaveFileName(self,"Save File","", "VIC Files (*.vic)")
        if not fileName.endswith(".vic"):
            fileName+=".vic"

        editor.file_path = fileName
        with open(fileName, "w", encoding="latin-1") as file:
            file.write(editor.toPlainText())
            tab_name = os.path.basename(editor.file_path)
            self.editor_tabs.setTabText(index, tab_name)


    def exitIDE(self):
        sys.exit()

    def currentEditor(self):
        return self.editor_tabs.currentWidget()


    def loadFile(self,fileName):
        if not fileName:
            return

        try:
            with open(fileName, "r", encoding="latin-1") as file:
                contenido = file.read()
                self.editor.setPlainText(contenido)
                self.file_name = fileName
                self.setWindowTitle(f"ChinchIDE - {fileName}")
                self.createEditorTab(content=file.read)
        except Exception as e:
             QMessageBox.critical(self, "Error", str(e))

    def compileCode(self):

        code = self.currentEditor().toPlainText()
        # Limpia resultados
        self.tab_lexico.clear()
        self.tab_sintactico.clear()
        self.tab_semantico.clear()
        self.tab_tabla.clear()
        self.tab_codigo.clear()
        self.error_lexico.clear()
        self.error_sintactico.clear()
        self.error_semantico.clear()
        self.result_compilado.clear()

        #self.lexicoCode()
        self.SintacticCode()

        # Simulación
        #self.tab_sintactico.setText("Resultado análisis sintáctico")
        self.tab_semantico.setText("Resultado análisis semántico")
        self.tab_tabla.setText("Tabla de símbolos")
        self.tab_codigo.setText("Código intermedio generado")
        #self.error_sintactico.setText("Errores de análisis sintáctico")
        self.error_semantico.setText("Errores de análisis semántico")
        self.result_compilado.setText("Resultado completo")

        QMessageBox.information(self, "Compilación", "Proceso terminado")

    def lexicoCode(self):
        code = self.currentEditor().toPlainText()
        scanner = Scanner(code)

        tokens_output = []
        errors_output = []

        while True:
            result = scanner.getToken()

            if len(result) == 5:
                token, lex, line, col, errorMsg = result
            else:
                token, lex = result
                line = scanner.line
                col = scanner.col
                errorMsg = scanner.erroMsg

            if token == "ERROR":
                errors_output.append(f"Error -> {lex} en línea {line}, columna {col} - {errorMsg}")
            elif token == "EOF":
                tokens_output.append(f"EOF -> Fin del archivo (línea {line}, columna {col})")
                break
            else:
                # Mostrar token con línea y columna
                tokens_output.append(f"{token:<15}  {lex} | Línea: {line:<3} | Columna: {col:<3}")

        with open("tokens.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(tokens_output))

        with open("errores.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(errors_output))

        self.tab_lexico.setText("\n".join(tokens_output))
        self.error_lexico.setText("\n".join(errors_output))


    def SintacticCode(self):
        """Realiza primero el análisis léxico y luego el sintáctico"""
        
        # Limpiar resultados anteriores
        self.tab_sintactico.clear()
        self.error_sintactico.clear()
        
        code = self.currentEditor().toPlainText()
        if not code.strip():
            self.tab_sintactico.setHeaderLabel("No hay código para analizar")
            self.error_sintactico.setText("El editor está vacío")
            return
        
        print("=" * 50)
        print("FASE 1: Análisis Léxico")
        print("=" * 50)
        
        self.lexicoCode()
        
        if not os.path.exists("tokens.txt"):
            self.tab_sintactico.setHeaderLabel("Error: No se pudo generar tokens.txt")
            self.error_sintactico.setText("El análisis léxico falló")
            return
        
        errores_lexicos = False
        if os.path.exists("errores.txt"):
            with open("errores.txt", "r", encoding="utf-8") as f:
                errores = f.read().strip()
                if errores:
                    errores_lexicos = True
        
        if errores_lexicos:
            with open("errores.txt", "r", encoding="utf-8") as f:
                errores = f.read()
                self.tab_sintactico.setHeaderLabel(" Errores Léxicos")
                self.error_sintactico.setText(f" Errores léxicos encontrados:\n\n{errores}")
                return
        
        print("\n" + "=" * 50)
        print("FASE 2: Análisis Sintáctico")
        print("=" * 50)
        
        try:
            from parse import Parser
            from arbol import TreePrinter
            
            parser = Parser("tokens.txt")
            syntax_tree = parser.parse()
            
            # Construir el árbol en QTreeWidget
            if syntax_tree is not None:
                self.buildTreeWidget(syntax_tree)
            else:
                self.tab_sintactico.setHeaderLabel("No se pudo generar el árbol sintáctico")
            
            # Leer errores sintácticos
            if os.path.exists("erroresSin.txt"):
                with open("erroresSin.txt", "r", encoding="utf-8") as f:
                    errores_sintacticos = f.read()
                
                if errores_sintacticos.strip() and "No se encontraron errores" not in errores_sintacticos:
                    self.error_sintactico.setText(f" {errores_sintacticos}")
                    print("SINTAXIS: Se encontraron errores")
                else:
                    self.error_sintactico.setText("Análisis sintáctico completado sin errores")
                    print("SINTAXIS: Completado sin errores")
                    self.error_sintactico.clear()
            else:
                self.error_sintactico.setText(" Análisis sintáctico completado sin errores")
                self.error_sintactico.clear()
                    
        except Exception as e:
            self.tab_sintactico.setHeaderLabel(f"Error: {str(e)}")
            self.error_sintactico.setText(str(e))
            import traceback
            traceback.print_exc()

    def getNodeText(self, node):
        """Obtiene el texto a mostrar para un nodo con formato específico"""
        
        if node.nodekind == "ProgramK":
            return "Programa"
        
        elif node.nodekind == "StmtK":
            kind = node.kind.get('stmt')
            
            if kind == "SelectionK":  # If
                return "Seleccion"
            
            elif kind == "IterationK":  # While
                return "Iteracion"
            
            elif kind == "RepetitionK":  # Do-While / Repeat
                return "Repeticion"
            
            elif kind == "AssignK":  # Asignación
                name = node.attr.get('name', '?')
                return f"Asignación a: {name}"
            
            elif kind == "SentInK":  # cin >> id
                name = node.attr.get('name', '?')
                return f"Leer: {name}"
            
            elif kind == "SentOutK":  # cout <<
                return "Escribir"
            
            else:
                return str(kind)
        
        elif node.nodekind == "ExpK":
            kind = node.kind.get('exp')
            
            if kind == "OpK":  # Operador
                op = node.attr.get('op', '?')
                # Convertir código de operador a símbolo legible
                op_str = self._getOperatorSymbol(op)
                return f"Operador: {op_str}"
            
            elif kind == "ConstK":  # Constante numérica
                val = node.attr.get('val', '?')
                return f"Constante: {val}"
            
            elif kind == "BoolK":  # Booleano
                val = node.attr.get('val', '?')
                return f"Booleano: {val}"
            
            elif kind == "IdK":  # Identificador
                name = node.attr.get('name', '?')
                if isinstance(name, list):
                    name = ', '.join(name)
                return f"Id: {name}"
            
            elif kind == "StringK":  # Cadena
                val = node.attr.get('val', '?')
                return f"String: {val}"
            
            elif kind == "LogicK":  # Operador lógico
                op = node.attr.get('op', '?')
                op_str = self._getOperatorSymbol(op)
                return f"Operador Logico: {op_str}"
            
            else:
                return f"Expresion: {kind}"
        
        elif node.nodekind == "DeclK":
            kind = node.kind.get('decl')
            
            if kind == "VarDeclK":
                return "Declaracion de Variable"
            
            elif kind == "TypeK":
                type_val = node.attr.get('type', '?')
                # Convertir ExpType a string legible
                if hasattr(type_val, 'value'):
                    type_val = type_val.value
                return f"Tipo: {type_val}"
            
            else:
                return f"Declaracion: {kind}"
        
        else:
            return f"Desconocido: {node.nodekind}"

    def _getOperatorSymbol(self, op_token):
        """Convierte el token de operador a su símbolo legible"""
        op_map = {
            "MAS": "+", "MENOS": "-", "MUL": "*", "DIV": "/",
            "MOD": "%", "POT": "^", "LT": "<", "LE": "<=",
            "GT": ">", "GE": ">=", "EQ": "==", "NE": "!=",
            "ASSIGN": "=", "INC": "++", "DEC": "--",
            "AND": "&&", "OR": "||", "NOT": "!",
            "SHL": "<<", "SHR": ">>"
        }
        return op_map.get(op_token, str(op_token))

    def buildTreeWidget(self, tree):
        """Construye el QTreeWidget a partir del TreeNode"""
        self.tab_sintactico.clear()
        self.tab_sintactico.setHeaderLabel("Árbol Sintáctico (Click para expandir/colapsar)")
        self.tab_sintactico.setIndentation(20)  # Indentación para mejor visualización
        
        # Crear el nodo raíz
        root_item = QTreeWidgetItem(self.tab_sintactico)
        self.addNodeToTree(tree, root_item)
        #root_item.setExpanded(True)
        self.tab_sintactico.expandAll();
        
        # Ajustar el ancho de la columna
        self.tab_sintactico.resizeColumnToContents(0)

    def addNodeToTree(self, node, parent_item):
        """Añade un nodo y sus hijos al QTreeWidget"""
        if node is None:
            return
    
        # Determinar el texto del nodo
        node_text = self.getNodeText(node)
        
        # Crear el item
        item = QTreeWidgetItem(parent_item)
        item.setText(0, node_text)
        
        # Añadir color según tipo (opcional, para mejor visualización)
        if node.nodekind == "ProgramK":
            item.setForeground(0, Qt.GlobalColor.white)
            # Usar fuente negrita para el programa principal
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)
        elif node.nodekind == "StmtK":
            item.setForeground(0, Qt.GlobalColor.white)
        elif node.nodekind == "ExpK":
            item.setForeground(0, Qt.GlobalColor.white)
        elif node.nodekind == "DeclK":
            item.setForeground(0, Qt.GlobalColor.white)
        
        # Procesar hijos (children)
        for child in node.children:
            if child is not None:
                self.addNodeToTree(child, item)
        
        # Procesar hermanos (siblings) - esto crea nodos al mismo nivel
        if node.sibling is not None:
            self.addNodeToTree(node.sibling, parent_item)

    def semanticCode(self):
        self.tab_semantico.setText("Resultado análisis semántico")
        self.error_semantico.setText("Errores de análisis semántico")

    def TabSimbolCode(self):
        self.tab_tabla.setText("Tabla de símbolos")

    def InterCodeCode(self):
        self.tab_codigo.setText("Código intermedio generado")

    







# ===============================
# Ejecutar aplicación
# ===============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CompilerIDE()
    window.show()
    sys.exit(app.exec())

