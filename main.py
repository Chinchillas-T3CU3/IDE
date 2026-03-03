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
import os
base_path = os.path.dirname(__file__)
abrir_icon = os.path.join(base_path, "icons/abrir.png")
nuevo_icon = os.path.join(base_path, "icons/nuevo.png")
guardar_icon = os.path.join(base_path, "icons/guardar.png")
ejecutar_icon = os.path.join(base_path, "icons/ejecutar.png")



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
        self.setWindowTitle(f"ChinchIDE - {self.file_name}")
        if self.file_name!="SinTitulo":
            self.loadFile(self.file_name)
        CompilerIDE.open_windows.append(self)

    def initUI(self):

        # ===== Editor =====
        self.editor = CodeEditor()

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
        layout_horizontal.addWidget(self.editor, 2)
        layout_horizontal.addWidget(self.tabs, 1)

        layout_principal = QVBoxLayout()
        layout_principal.addLayout(layout_horizontal)
        layout_principal.addWidget(self.error_panel)

        central_widget.setLayout(layout_principal)

        # ====== Menú superior ======
        self.createMenu()

    # ==========================
    # Menú
    # ==========================
    def createMenu(self):

        menubar = self.menuBar()

        open_icon_action = QAction(QIcon(abrir_icon), "Open", self)
        open_icon_action.triggered.connect(self.openFile)

        save_icon_action = QAction(QIcon(guardar_icon), "Save", self)
        save_icon_action.triggered.connect(self.saveFile)

        compile_icon_action = QAction(QIcon(ejecutar_icon), "Compilar", self)
        compile_icon_action.triggered.connect(self.compileCode)

        # ----- File -----
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

        #------ iconos ------
        menubar.addAction(open_icon_action)
        menubar.addAction(save_icon_action)
        menubar.addAction(compile_icon_action)





    # ==========================
    # Funciones del menú
    # ==========================
    def openFile(self):
        fileName_aux=self.file_name
        fileName, _ = QFileDialog.getOpenFileName(self,"Open File","","VIC Files (*.vic)")
        if fileName!=fileName_aux and fileName_aux!="SinTitulo":
            new_window=CompilerIDE(fileName)
            new_window.show()
        else:
            self.loadFile(fileName)
        

    def saveFile(self):
        fileName=self.file_name
        if fileName=="SinTitulo":
            fileName, _ = QFileDialog.getSaveFileName(
            self,"Save File","", "VIC Files (*.vic)")
            if fileName:
                    with open(fileName, "w", encoding="latin-1") as file:
                        file.write(self.editor.toPlainText())
                        self.file_name=fileName
                        self.setWindowTitle(f"ChinchIDE - {fileName}")
        else:
            if fileName:
                    with open(fileName, "w", encoding="latin-1") as file:
                        file.write(self.editor.toPlainText())
                        self.file_name=fileName
                        self.setWindowTitle(f"ChinchIDE - {fileName}")



    def newFile(self):
        new_window=CompilerIDE()
        new_window.show()


        

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

        print("Numero de ventanas:" + str(len(CompilerIDE.open_windows)))
        if len(CompilerIDE.open_windows)==1:
            sys.exit()

        index=CompilerIDE.open_windows.index(self)
        if index==0:
            self.hide()

        else:
            if self in CompilerIDE.open_windows:
                index=CompilerIDE.open_windows.index(self)
                CompilerIDE.open_windows.remove(self)
                print(index)

            
   

    def saveAsFile(self):
        fileName, _ = QFileDialog.getSaveFileName(
            self,"Save File","", "VIC Files (*.vic)")
        if fileName:
            if not fileName.endswith(".vic"):
                fileName+=".vic"
            with open(fileName, "w", encoding="latin-1") as file:
                file.write(self.editor.toPlainText())
                self.file_name=fileName
                self.setWindowTitle(f"ChinchIDE - {fileName}")

    def exitIDE(self):
        sys.exit()


    def loadFile(self,fileName):
        if not fileName:
            return

        try:
            with open(fileName, "r", encoding="latin-1") as file:
                contenido = file.read()
                self.editor.setPlainText(contenido)
                self.file_name = fileName
                self.setWindowTitle(f"ChinchIDE - {fileName}")
        except Exception as e:
             QMessageBox.critical(self, "Error", str(e))

    def compileCode(self):

        code = self.editor.toPlainText()

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

        # Simulación
        self.tab_lexico.setText("Resultado análisis léxico")
        self.tab_sintactico.setText("Resultado análisis sintáctico")
        self.tab_semantico.setText("Resultado análisis semántico")
        self.tab_tabla.setText("Tabla de símbolos")
        self.tab_codigo.setText("Código intermedio generado")
        self.error_lexico.setText("Errores de análisis léxico")
        self.error_sintactico.setText("Errores de análisis sintáctico")
        self.error_semantico.setText("Errores de análisis semántico")
        self.result_compilado.setText("Resultado completo")

        QMessageBox.information(self, "Compilación", "Proceso terminado")


# ===============================
# Ejecutar aplicación
# ===============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CompilerIDE()
    window.show()
    sys.exit(app.exec())