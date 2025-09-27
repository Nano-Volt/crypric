# ==============================================================================================================================
# (c)  2025 Nano volt  The cryptic ide  for more copy right  visit https://github.com/Nano-Volt/crypric?tab=Apache-2.0-1-ov-file
#=====================================================================================================================================

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QWidget, QFileDialog, QMessageBox, QMenuBar, 
                             QToolBar, QStatusBar, QSplitter, QDockWidget, 
                             QListWidget, QLabel, QDialog, QDialogButtonBox, 
                             QLineEdit, QFormLayout, QHBoxLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase, QSyntaxHighlighter, QTextCharFormat, 
                       QColor, QKeySequence, QAction, QIcon, QPalette, QTextCursor
import re


class CrypticHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
     
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = ["fn", "loop", "print", "return", "if", "else", "while", "break", "continue"]
        for word in keywords:
            pattern = r'\b' + word + r'\b'
            self.highlighting_rules.append((pattern, keyword_format))
        
        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#4EC9B0"))
        types = ["int", "string", "bool"]
        for word in types:
            pattern = r'\b' + word + r'\b'
            self.highlighting_rules.append((pattern, type_format))
        
   
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', string_format))
        
    
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append((r'\b[0-9]+\b', number_format))
        
     
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((r'//[^\n]*', comment_format))
    
    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start, length = match.span()
                self.setFormat(start, length, format)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return self.sizeHint()
    
    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.lineNumberArea = LineNumberArea(self)
        
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        
       
        font = QFont("Consolas", 12)
        self.setFont(font)
    
        self.highlighter = CrypticHighlighter(self.document())
    
    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def updateLineNumberAreaWidth(self, newBlockCount):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
    
    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
    
    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#2D2D30"))
        
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(0, top, self.lineNumberArea.width(), self.fontMetrics().height(),
                                Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1
    
    def highlightCurrentLine(self):
        extraSelections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor("#2D2D30").lighter(120)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        
        self.setExtraSelections(extraSelections)


class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.setModal(False)
        
        layout = QFormLayout(self)
        
        self.findField = QLineEdit()
        self.replaceField = QLineEdit()
        
        layout.addRow("Find:", self.findField)
        layout.addRow("Replace with:", self.replaceField)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)
    
    def getFindText(self):
        return self.findField.text()
    
    def getReplaceText(self):
        return self.replaceField.text()


class CrypticIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.findDialog = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Cryptic IDE")
        self.setGeometry(100, 100, 1200, 800)
        
   
        self.applyDarkTheme()
      
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
     
        layout = QVBoxLayout(central_widget)
        
      
        self.editor = CodeEditor()
        layout.addWidget(self.editor)
        
     
        self.createMenus()
    
        self.createToolbar()
        
      
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        
        self.editor.cursorPositionChanged.connect(self.updateStatusBar)
        
        #
        self.createFileExplorer()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(1000)
    
    def applyDarkTheme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        self.setPalette(dark_palette)
    
    def createMenus(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.newFile)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open', self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.openFile)
        file_menu.addAction(open_action)
        
        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.saveFile)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('Save As...', self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.saveFileAs)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        undo_action = QAction('Undo', self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('Redo', self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction('Cut', self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction('Copy', self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('Paste', self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction('Find and Replace', self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self.showFindDialog)
        edit_menu.addAction(find_action)
        

        run_menu = menubar.addMenu('Run')
        
        run_action = QAction('Run Code', self)
        run_action.setShortcut('F5')
        run_action.triggered.connect(self.runFile)
        run_menu.addAction(run_action)
        

        view_menu = menubar.addMenu('View')
        
        toggle_explorer_action = QAction('Toggle File Explorer', self)
        toggle_explorer_action.triggered.connect(self.toggleFileExplorer)
        view_menu.addAction(toggle_explorer_action)
    
    def createToolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        new_action = QAction("New", self)
        new_action.triggered.connect(self.newFile)
        toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.openFile)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.saveFile)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        run_action = QAction("Run", self)
        run_action.triggered.connect(self.runFile)
        toolbar.addAction(run_action)
    
    def createFileExplorer(self):
        self.file_explorer = QDockWidget("File Explorer", self)
        self.file_list = QListWidget()
        self.file_explorer.setWidget(self.file_list)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.file_explorer)
        
        self.file_list.itemDoubleClicked.connect(self.openFileFromExplorer)
    
    def toggleFileExplorer(self):
        if self.file_explorer.isVisible():
            self.file_explorer.hide()
        else:
            self.file_explorer.show()
    
    def updateFileExplorer(self, directory):
        self.file_list.clear()
        if directory:
            try:
                for item in os.listdir(directory):
                    self.file_list.addItem(item)
            except OSError:
                pass
    
    def openFileFromExplorer(self, item):
        if self.current_file:
            directory = os.path.dirname(self.current_file)
            file_path = os.path.join(directory, item.text())
            if os.path.isfile(file_path):
                self.loadFile(file_path)
    
    def newFile(self):
        self.editor.clear()
        self.current_file = None
        self.setWindowTitle("Cryptic IDE - New File")
        self.statusBar.showMessage("New file created")
    
    def openFile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Cryptic File", "", "Cryptic Files (*.cryp);;All Files (*)"
        )
        
        if file_path:
            self.loadFile(file_path)
    
    def loadFile(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                self.editor.setPlainText(content)
                self.current_file = file_path
                self.setWindowTitle(f"Cryptic IDE - {os.path.basename(file_path)}")
                self.statusBar.showMessage(f"Loaded {file_path}")
                
                # Update file explorer
                self.updateFileExplorer(os.path.dirname(file_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
    
    def saveFile(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w') as file:
                    file.write(self.editor.toPlainText())
                self.statusBar.showMessage(f"Saved {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
        else:
            self.saveFileAs()
    
    def saveFileAs(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Cryptic File", "", "Cryptic Files (*.cryp);;All Files (*)"
        )
        
        if file_path:
            if not file_path.endswith('.cryp'):
                file_path += '.cryp'
            
            try:
                with open(file_path, 'w') as file:
                    file.write(self.editor.toPlainText())
                self.current_file = file_path
                self.setWindowTitle(f"Cryptic IDE - {os.path.basename(file_path)}")
                self.statusBar.showMessage(f"Saved {file_path}")
                
                self.updateFileExplorer(os.path.dirname(file_path))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
    
    def runFile(self):
        code = self.editor.toPlainText()
        QMessageBox.information(self, "Run Cryptic", f"Running code:\n\n{code}")
    
    def showFindDialog(self):
        if not self.findDialog:
            self.findDialog = FindReplaceDialog(self)
            self.findDialog.accepted.connect(self.findReplace)
        
        self.findDialog.show()
        self.findDialog.raise_()
        self.findDialog.activateWindow()
    
    def findReplace(self):
        find_text = self.findDialog.getFindText()
        replace_text = self.findDialog.getReplaceText()
        
        if find_text:
            cursor = self.editor.textCursor()
            document = self.editor.document()
            
            # Find the text
            found = document.find(find_text, cursor)
            
            if not found.isNull():
                self.editor.setTextCursor(found)
                
                if replace_text:
                    found.insertText(replace_text)
            else:
                QMessageBox.information(self, "Find", "Text not found")
    
    def updateStatusBar(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.statusBar.showMessage(f"Line: {line}, Column: {col}")
    
    def updateStatus(self):

        pass
    
    def closeEvent(self, event):
        if self.editor.document().isModified():
            reply = QMessageBox.question(
                self, 'Unsaved Changes',
                'You have unsaved changes. Do you want to save before exiting?',
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.saveFile()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("Cryptic IDE")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("CrypticLang")
    
    ide = CrypticIDE()
    ide.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
