# ==============================================================================================================================
# (c)  2025 Nano volt  The cryptic ide  for more copy right information visit https://github.com/Nano-Volt/crypric?tab=Apache-2.0-1-ov-file
#=====================================================================================================================================

import sys
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                            QHBoxLayout, QWidget, QMenuBar, QFileDialog, 
                            QMessageBox, QStatusBar, QSplitter, QTreeWidget,
                            QTreeWidgetItem, QTabWidget, QToolBar, QPushButton,
                            QLabel, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (QFont, QTextCharFormat, QColor, QSyntaxHighlighter, 
                        QTextDocument, QAction, QIcon, QPixmap, QPainter)

class CrypticHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define syntax highlighting rules
        self.highlighting_rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = ["fn", "loop", "print", "return", "if", "else", "while", "break", "continue"]
        for keyword in keywords:
            pattern = rf"\b{keyword}\b"
            self.highlighting_rules.append((re.compile(pattern), keyword_format))
        
        # Types
        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#4EC9B0"))
        types = ["int", "string", "bool"]
        for typ in types:
            pattern = rf"\b{typ}\b"
            self.highlighting_rules.append((re.compile(pattern), type_format))
        
        # String literals
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((re.compile(r'".*?"'), string_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append((re.compile(r'\b[0-9]+\b'), number_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'//.*'), comment_format))
    
    def highlightBlock(self, text):
        for pattern, format_style in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format_style)

class CodeEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                selection-background-color: #555555;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        
        # Set up syntax highlighter
        self.highlighter = CrypticHighlighter(self.document())
        
        # Enable line wrapping
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Set tab width
        font_metrics = self.fontMetrics()
        self.setTabStopDistance(font_metrics.horizontalAdvance(' ') * 4)

class FileExplorer(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderLabel("Files")
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #252526;
                color: #cccccc;
                border: none;
                outline: none;
            }
            QTreeWidget::item {
                padding: 2px;
            }
            QTreeWidget::item:selected {
                background-color: #37373d;
            }
            QTreeWidget::item:hover {
                background-color: #2a2d2e;
            }
        """)
        
        # Add some example items
        root = QTreeWidgetItem(self)
        root.setText(0, "Project")
        
        file1 = QTreeWidgetItem(root)
        file1.setText(0, "main.cryp")
        
        file2 = QTreeWidgetItem(root)
        file2.setText(0, "utils.cryp")
        
        self.expandAll()

class OutputPanel(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumHeight(150)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.append("Ready - Cryptic IDE")

class CrypticIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Cryptic IDE - Professional")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QMenuBar {
                background-color: #2d2d30;
                color: #cccccc;
                border: none;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #3c3c3c;
            }
            QMenu {
                background-color: #2d2d30;
                color: #cccccc;
                border: 1px solid #3c3c3c;
            }
            QMenu::item {
                padding: 6px 20px;
            }
            QMenu::item:selected {
                background-color: #3c3c3c;
            }
            QToolBar {
                background-color: #2d2d30;
                border: none;
                spacing: 3px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8a;
            }
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
            QSplitter::handle {
                background-color: #3c3c3c;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom: 1px solid #1e1e1e;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for resizable panels
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # File explorer
        self.file_explorer = FileExplorer()
        main_splitter.addWidget(self.file_explorer)
        
        # Editor area with vertical splitter
        editor_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Tab widget for multiple files
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Add initial tab
        self.code_editor = CodeEditor()
        self.tab_widget.addTab(self.code_editor, "Untitled.cryp")
        
        editor_splitter.addWidget(self.tab_widget)
        
        # Output panel
        self.output_panel = OutputPanel()
        editor_splitter.addWidget(self.output_panel)
        
        # Set splitter sizes
        editor_splitter.setSizes([600, 150])
        
        main_splitter.addWidget(editor_splitter)
        main_splitter.setSizes([200, 1000])
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Connect file explorer
        self.file_explorer.itemDoubleClicked.connect(self.on_file_selected)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('Save As...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        undo_action = QAction('Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.code_editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.code_editor.redo)
        edit_menu.addAction(redo_action)
        
        # Run menu
        run_menu = menubar.addMenu('Run')
        
        run_action = QAction('Run Code', self)
        run_action.setShortcut('F5')
        run_action.triggered.connect(self.run_code)
        run_menu.addAction(run_action)
        
    def create_toolbar(self):
        toolbar = self.addToolBar('Main')
        
        # New file button
        new_btn = QPushButton('New')
        new_btn.clicked.connect(self.new_file)
        toolbar.addWidget(new_btn)
        
        # Open file button
        open_btn = QPushButton('Open')
        open_btn.clicked.connect(self.open_file)
        toolbar.addWidget(open_btn)
        
        # Save file button
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_file)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        # Run button
        run_btn = QPushButton('▶ Run')
        run_btn.clicked.connect(self.run_code)
        toolbar.addWidget(run_btn)
        
    def new_file(self):
        new_editor = CodeEditor()
        index = self.tab_widget.addTab(new_editor, "Untitled.cryp")
        self.tab_widget.setCurrentIndex(index)
        self.current_file = None
        self.status_bar.showMessage("New file created")
        
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            'Open File', 
            '', 
            'Cryptic files (*.cryp);;All files (*.*)'
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                new_editor = CodeEditor()
                new_editor.setPlainText(content)
                
                filename = file_path.split('/')[-1]
                index = self.tab_widget.addTab(new_editor, filename)
                self.tab_widget.setCurrentIndex(index)
                
                self.current_file = file_path
                self.setWindowTitle(f"Cryptic IDE - {filename}")
                self.status_bar.showMessage(f"Opened: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not open file:\n{str(e)}')
    
    def save_file(self):
        current_editor = self.tab_widget.currentWidget()
        if not current_editor:
            return
            
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(current_editor.toPlainText())
                self.status_bar.showMessage(f"Saved: {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not save file:\n{str(e)}')
        else:
            self.save_as_file()
    
    def save_as_file(self):
        current_editor = self.tab_widget.currentWidget()
        if not current_editor:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Save File',
            '',
            'Cryptic files (*.cryp);;All files (*.*)'
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(current_editor.toPlainText())
                
                self.current_file = file_path
                filename = file_path.split('/')[-1]
                current_index = self.tab_widget.currentIndex()
                self.tab_widget.setTabText(current_index, filename)
                self.setWindowTitle(f"Cryptic IDE - {filename}")
                self.status_bar.showMessage(f"Saved: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not save file:\n{str(e)}')
    
    def run_code(self):
        current_editor = self.tab_widget.currentWidget()
        if not current_editor:
            return
            
        code = current_editor.toPlainText()
        
        # Clear output panel
        self.output_panel.clear()
        self.output_panel.append("Running Cryptic code...")
        self.output_panel.append("=" * 40)
        self.output_panel.append(code)
        self.output_panel.append("=" * 40)
        self.output_panel.append("Execution completed.")
        
        self.status_bar.showMessage("Code executed")
    
    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            # If it's the last tab, create a new empty one
            current_editor = self.tab_widget.widget(index)
            current_editor.clear()
            self.tab_widget.setTabText(index, "Untitled.cryp")
            self.current_file = None
    
    def on_file_selected(self, item):
        # Simulate opening a file from file explorer
        filename = item.text(0)
        if filename.endswith('.cryp'):
            self.status_bar.showMessage(f"Selected: {filename}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better dark theme support
    
    ide = CrypticIDE()
    ide.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
