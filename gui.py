import os
import sys
import queue
import threading
from PyQt5.QtGui import QFont, QKeySequence, QTextCursor, QTextCharFormat, QColor
from PyQt5.QtWidgets import (QWidget, QApplication, QMainWindow, QFileDialog,
                            QHBoxLayout, QVBoxLayout,QTextEdit, QLineEdit,
                            QShortcut, QInputDialog, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QEventLoop
from src.lexer import tokenizer
from src.parser.parser import Parser
from src.interpreter.runtime import SymbolTable, Context
from src.interpreter.interpreter import Interpreter
from src.interpreter.values import Number, String, Boolean, Noob, Function


# For managing persistence
class TextContentManager: # for text input
    def __init__(self):
        self.saved_content = None

class FileManager: # for filename
    def __init__(self):
        self.file_name = None

class LexemeManager: # for lexeme tokens
    def __init__(self):
        self.saved_lexemes = None

class InteractiveConsole(QTextEdit):
    """Interactive console widget that handles input/output in a single text area"""
    input_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.input_queue = queue.Queue()
        self.waiting_for_input = False
        self.input_buffer = ""
        self.input_start_pos = 0
        self.input_requested.connect(self._request_input_slot)
        self.setup_ui()
    
    def setup_ui(self):
        console_font = QFont("Consolas", 10)
        self.setFont(console_font)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #FAFAFA;
                border: none;
                padding: 10px;
            }
        """)
        self.setReadOnly(False)
    
    def write(self, text, color="#FAFAFA"):
        """Write text to console output"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Set text color
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        
        cursor.insertText(text + "\n")
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
    
    def clear(self):
        """Clear console output"""
        super().clear()
        self.waiting_for_input = False
        self.input_buffer = ""
    
    def _request_input_slot(self):
        """Enable input mode (called from main thread via signal)"""
        self.waiting_for_input = True
        self.input_buffer = ""
        self.input_start_pos = self.textCursor().position()
        self.setReadOnly(False)
        self.setFocus()
    
    def request_input(self):
        """Request input - can be called from any thread"""
        self.input_requested.emit()
    
    def keyPressEvent(self, event):
        """Handle key press events for input"""
        if not self.waiting_for_input:
            # Prevent editing when not waiting for input
            event.ignore()
            return
        
        cursor = self.textCursor()
        
        # Prevent editing previous content
        if cursor.position() < self.input_start_pos:
            cursor.setPosition(self.input_start_pos)
            self.setTextCursor(cursor)
        
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Get the input from the current line
            cursor.movePosition(QTextCursor.End)
            cursor.setPosition(self.input_start_pos, QTextCursor.KeepAnchor)
            user_input = cursor.selectedText()
            
            # Move to end and add newline
            cursor.clearSelection()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText("\n")
            self.setTextCursor(cursor)
            
            # Disable input mode
            self.waiting_for_input = False
            self.setReadOnly(True)
            
            # Put input in queue
            self.input_queue.put(user_input)
            event.accept()
        elif event.key() == Qt.Key_Backspace:
            # Prevent backspace from deleting past the input start
            if cursor.position() <= self.input_start_pos:
                event.ignore()
                return
            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
    
    def get_input(self):
        """Get input from queue (blocking but processes events)"""
        # Request input (signal will trigger on main thread)
        self.request_input()
        
        # Wait for input with event processing
        while self.input_queue.empty():
            QApplication.processEvents()
            import time
            time.sleep(0.01)  # Small sleep to prevent busy waiting
        
        return self.input_queue.get()


def text_edit(text_editor, file_manager, content_manager, parent_widget): # Text editor panel
    editor_layout = QVBoxLayout() # main vertical layout
    text_editor.setLayout(editor_layout)

    text_input = QTextEdit() 
    text_input.setPlaceholderText("Type here...")

    # custom font
    font = QFont("Consolas",11) 
    text_input.setStyleSheet("border: none; color: #FAFAFA;") 
    text_input.setFont(font)

    editor_layout.addWidget(text_input)

    # create ctrl+s shortcut for saving
    save_shortcut = QShortcut(QKeySequence("Ctrl+S"), text_input) # bind key to saving
    save_shortcut.activated.connect(lambda: save_and_store(text_input, file_manager, content_manager, parent_widget))
    
    return text_input


def save_and_store(text_input, file_manager, content_manager, parent_widget): # for text persistence
    text_content = save_input(text_input, file_manager, parent_widget)
    if text_content is not None:
        content_manager.saved_content = text_content

def save_input(text_input, file_manager, parent_widget): # Save as <filename>.txt to be passed into parser
   
    if file_manager.file_name is None:
        file_name, ok = QInputDialog.getText(parent_widget, 'Save File', 'Enter file name:') # promp user if non-existing file
        
        if ok and file_name:
            if not file_name.endswith('.txt'):
                file_name += '.txt'
            file_manager.file_name = file_name
        else:
            print('Save cancelled')
            return None
    
    text_content = text_input.toPlainText()
    with open(file_manager.file_name, 'w') as file:
        file.write(text_content)
    print(f"File saved as {file_manager.file_name}!")
    
    return text_content

def execute_code(content_manager, lexeme_manager, token_table, symbol_table, console_widget): # Func for calling tokenizer, parser, and interpreter
    if content_manager.saved_content is None:
        console_widget.write("Error: Please save the file first (Ctrl+S)", "#FF6B6B")
        return
    
    def run_interpreter():
        """Run interpreter - output and input are sequential"""
        try:  
            # Tokenization
            console_widget.write("=== LOLCODE INTERPRETER ===", "#4ECDC4")
            tokens = tokenizer.tokenize(content_manager.saved_content)
            lexeme_manager.saved_lexemes = tokens
            console_widget.write(f"Tokenization complete: {len(tokens)} tokens", "#95E1D3")
            update_token_view(token_table, tokens)
            
            # Parsing
            parser = Parser(tokens)
            AST = parser.parse()
            
            if AST.error:
                console_widget.write(f"Parse Error: {AST.error}", "#FF6B6B")
                return
            
            console_widget.write("Parsing complete", "#95E1D3")
            
            # Interpretation
            symbol_table_obj = SymbolTable()
            context = Context('<program>')
            context.symbol_table = symbol_table_obj
            
            lolcode_interpreter = Interpreter()
            console_widget.write("--- Program Output ---", "#4ECDC4")
            
            # Custom print function that writes to console
            import builtins
            original_print = builtins.print
            original_input = builtins.input
            
            def console_print(*args, **kwargs):
                """Custom print that writes to console widget"""
                text = ' '.join(str(arg) for arg in args)
                console_widget.write(text, "#FAFAFA")
            
            # Replace print and input
            builtins.print = console_print
            builtins.input = lambda: console_widget.get_input()
            
            try:
                result = lolcode_interpreter.visit(AST.node, context)
            finally:
                # Restore original functions
                builtins.print = original_print
                builtins.input = original_input
            
            # Check for runtime errors
            if result and result.error:
                console_widget.write(f"Runtime Error: {result.error}", "#FF6B6B")
            else:
                console_widget.write("Execution complete", "#95E1D3")
            
            # Update symbol table display
            update_symbol_table(symbol_table, symbol_table_obj)

        except Exception as e:
            console_widget.write(f"Error: {str(e)}", "#FF6B6B")
            import traceback
            console_widget.write(traceback.format_exc(), "#FF6B6B")
    
    # Clear console and start execution in a thread
    console_widget.clear()
    
    # Run in separate thread to prevent GUI blocking
    thread = threading.Thread(target=run_interpreter, daemon=True)
    thread.start()





def create_table(parent_widget, label1, label2): # Func for creating tables
    token_layout = QVBoxLayout()
    parent_widget.setLayout(token_layout) # set it as layout for the identifier/lexeme widget 
    
    table = QTableWidget()
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels([label1, label2])
   
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
    table.setEditTriggers(QTableWidget.NoEditTriggers)  # so table can't be edited
    
    #### STYLE #####
    table.setStyleSheet("""
        QTableWidget {
            background-color: #1A1A1A;
            color: #FAFAFA;
            border: none;
            gridline-color: #2A2A2A;
        }
        QHeaderView::section {
            background-color: #2A2A2A;
            color: #FAFAFA;
            padding: 5px;
            border: none;
            font-weight: medium;
        }
        QTableWidget::item {
            padding: 5px;
        }
    """)
    
    font = QFont("Consolas", 10)
    table.setFont(font)
    ####  END OF STYLE #####
    token_layout.addWidget(table)
    return table # will be used by update_token_view


def update_token_view(table, lexemes): # update table with the lexemes/identifiers
    if lexemes is None:
        print("Error: Empty")
        return
    
    table.setRowCount(0) # initialize 
    
    # if lexemes is a list
    if isinstance(lexemes, list):
        for item in lexemes:
            row_position = table.rowCount()
            table.insertRow(row_position)
            
            # if item has 2 parts
            if isinstance(item, (tuple, list)) and len(item) >= 2:
                table.setItem(row_position, 0, QTableWidgetItem(str(item[0])))
                table.setItem(row_position, 1, QTableWidgetItem(str(item[1])))
            # if item is a dictionary
            elif isinstance(item, dict):
                lexeme = item.get('value', '')
                description = item.get('category', '')
                table.setItem(row_position, 0, QTableWidgetItem(str(lexeme)))
                table.setItem(row_position, 1, QTableWidgetItem(str(description)))


def update_symbol_table(table, symbol_table_obj): # update symbol table display
    table.setRowCount(0)
    
    # Type mapping from Python classes to LOLCODE types
    type_map = {
        'Number': lambda v: 'NUMBR' if isinstance(v.value, int) else 'NUMBAR',
        'String': lambda v: 'YARN',
        'Boolean': lambda v: 'TROOF',
        'Noob': lambda v: 'NOOB',
        'Function': lambda v: 'FUNCTION'
    }
    
    if symbol_table_obj and symbol_table_obj.symbols:
        for var_name, value in symbol_table_obj.symbols.items():
            row_position = table.rowCount()
            table.insertRow(row_position)
            
            # Get value representation
            value_str = str(value)
            
            # Get type
            type_name = type(value).__name__
            lolcode_type = type_map.get(type_name, lambda v: 'UNKNOWN')(value) if type_name in type_map else type_name
            
            # Create display string
            display_value = f"{value_str} ({lolcode_type})"
            
            table.setItem(row_position, 0, QTableWidgetItem(var_name))
            table.setItem(row_position, 1, QTableWidgetItem(display_value))


def file_open(text_input, file_manager, content_manager, file_button): # open file and load content
    options = QFileDialog.Options() # opens file manager
    file_name, _ = QFileDialog.getOpenFileName(
        None, "Select a File", "", "All Files (*);;Text Files (*.txt);;Python Files (*.py)", options=options
    )
    
    if file_name: # if exists
        try:
            with open(file_name, 'r') as file:
                content = file.read()
                text_input.setPlainText(content)
                file_manager.file_name = file_name # update file name opened
                content_manager.saved_content = content  # store content so execute can work
                
                # show filename on button
                file_button.setText(os.path.basename(file_name))
                
                print(f"File opened: {file_name}")
        except Exception as e:
            print(f"Error opening file: {e}")


def layout(win):
    main_widget = QWidget()
    win.setCentralWidget(main_widget)

    # for data persistence for file name, text input and lexemes
    file_manager = FileManager()
    content_manager = TextContentManager()
    lexeme_manager = LexemeManager()
    
    main_layout = QVBoxLayout()
    main_horizontal = QHBoxLayout()  # Left and right columns
    left_column = QVBoxLayout()
    right_column = QVBoxLayout()
    main_widget.setLayout(main_layout)

    # Left column widgets
    text_editor = QWidget() # text editor
    file_searcher = QPushButton('Open File')
    
    # Right column widgets
    symbol_table_widget = QWidget() # symbol table (top right)
    token_view_widget = QWidget() # lexeme tokens view (bottom right)
    
    # Bottom widgets - Interactive Console
    console = InteractiveConsole()
    
    # create text editor first
    text_input = text_edit(text_editor, file_manager, content_manager, win)
    
    # create symbol table and lexeme table
    symbol_table = create_table(symbol_table_widget, "Identifier", "Value")
    token_table = create_table(token_view_widget, "Lexeme", "Classification")

    execute_button = QPushButton("Execute", win) # execute button
    

    ##### STYLE ##############
    execute_button.setStyleSheet("""
        QPushButton {
            background-color: #007ACC;
            color: white;
            border: none;
            padding: 10px 20px;
            font-weight: bold;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #005A9E;
        }
    """)

    file_searcher.setStyleSheet("""
        QPushButton {
            background-color: #007ACC;
            color: white;
            border: none;
            padding: 10px 20px;
            font-weight: bold;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #005A9E;
        }
    """)

    text_editor.setStyleSheet("background-color: #1E1E1E;")
    token_view_widget.setStyleSheet("background-color: #1A1A1A;")
    symbol_table_widget.setStyleSheet("background-color: #1F1F1F;")
    ###### STYLE ###########

    # buttons
    execute_button.clicked.connect(lambda: execute_code(content_manager, lexeme_manager, token_table, symbol_table, console))
    file_searcher.clicked.connect(lambda: file_open(text_input, file_manager, content_manager, file_searcher))

    # Left column layout (text editor with file button)
    left_column.addWidget(file_searcher, 0)
    left_column.addWidget(text_editor, 1)

    # Right column layout (symbol table on top, lexeme table on bottom)
    right_column.addWidget(symbol_table_widget, 1)
    right_column.addWidget(token_view_widget, 1)

    # Main horizontal layout (left and right columns)
    main_horizontal.addLayout(left_column, 3)  # Text editor takes more space
    main_horizontal.addLayout(right_column, 2)  # Tables column

    # Main vertical layout
    main_layout.addLayout(main_horizontal, 3)  # Top section
    main_layout.addWidget(execute_button, 0)    # Execute button
    main_layout.addWidget(console, 1)            # Interactive console at bottom



def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(0, 0, 600, 400) # set dimensions
    win.setWindowTitle("WeLove124")

    layout(win)
    win.show()

    # exit
    sys.exit(app.exec_())


main()