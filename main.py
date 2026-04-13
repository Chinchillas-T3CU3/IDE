import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTextEdit,
    QVBoxLayout, QHBoxLayout, QTabWidget,
    QFileDialog, QMessageBox, QMenuBar, QMenu,QLabel,
    QWidgetAction
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
        self.tab_sintactico = QTextEdit()
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

        self.lexicoCode()

        # Simulación
        self.tab_sintactico.setText("Resultado análisis sintáctico")
        self.tab_semantico.setText("Resultado análisis semántico")
        self.tab_tabla.setText("Tabla de símbolos")
        self.tab_codigo.setText("Código intermedio generado")
        self.error_sintactico.setText("Errores de análisis sintáctico")
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
                errorMsg=scanner.erroMsg

            if token == "ERROR":
                errors_output.append(f"Error -> {lex} en línea {line}, columna {col}, {errorMsg}")
            else:
                tokens_output.append(f"{token} -> {lex}")

            if token == "EOF":
                break

        with open("tokens.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(tokens_output))

        with open("errores.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(errors_output))

        self.tab_lexico.setText("\n".join(tokens_output))
        self.error_lexico.setText("\n".join(errors_output))


    def SintacticCode(self):
        self.tab_sintactico.setText("Resultado análisis sintáctico")
        self.error_sintactico.setText("Errores de análisis sintáctico")
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