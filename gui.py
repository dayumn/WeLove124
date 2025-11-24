import os
import sys
import queue
import threading
from PyQt5.QtGui import QFont, QKeySequence, QTextCursor, QTextCharFormat, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import (QWidget, QApplication, QMainWindow, QFileDialog,
                            QHBoxLayout, QVBoxLayout,QTextEdit,
                            QShortcut, QInputDialog, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                            QMenu, QTabWidget, QAction)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
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

class TabManager: # For managing multiple files
    def __init__(self):
        self.tabs = {} # stores {tab_index: {"text_input": widget, "file_manager": manager, "content_manager": manager}}


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
    
    # check text as user types
    text_input.textChanged.connect(lambda: highlight_words(text_input))

    return text_input

# Helper function for specific color
def highlight_words(text_input):
    KEYWORD_COLORS = { 
        # code delimiters 
        "HAI": "#FF6B9D",
        "KTHXBYE": "#FF6B9D",
        
        # variable section delimiters
        "WAZZUP": "#FFA500",
        "BUHBYE": "#FFA500",
        
        # variable keywords 
        "I HAS A": "#569CD6",
        "ITZ": "#569CD6",
        " R ": "#569CD6",
        
        # output/input keywords 
        "VISIBLE": "#C586C0",
        "GIMMEH": "#C586C0",
        
        # operators and separators 
        "AN": "#D4D4D4",
        
        # type keywords 
        "NOOB": "#4EC9B0",
        "NUMBR": "#4EC9B0",
        "NUMBAR": "#4EC9B0",
        "YARN": "#4EC9B0",
        "TROOF": "#4EC9B0",
        
        # boolean values 
        "WIN": "#D7BA7D",
        "FAIL": "#D7BA7D",
    }
    
    COMMENT_START = "BTW"  # comment starter
    MULTI_COMMENT = "OBTW"
    COMMENT_COLOR = "#6A9955"  #  comments
    
    # block signals to prevent infinite loop
    text_input.blockSignals(True)
    
    cursor = text_input.textCursor()
    current_pos = cursor.position()

    # set all text to default color 
    cursor.select(QTextCursor.Document)
    default = QTextCharFormat()
    default.setForeground(QColor("#D4D4D4"))
    cursor.setCharFormat(default)

    # highlight comments first (so they override keywords)
    current_text = text_input.toPlainText()
    lines = current_text.split('\n')
    char_count = 0
    
    for line in lines:
        comment_index = line.find(COMMENT_START or MULTI_COMMENT) 
        if comment_index != -1: # iff it exist
            # found comment, highlight from comment start to end of line
            start_pos = char_count + comment_index # find where BTW starts
            end_pos = char_count + len(line) # find \n
            
            # update cursor position
            cursor = text_input.textCursor()
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
            
            format = QTextCharFormat()
            format.setForeground(QColor(COMMENT_COLOR))
            cursor.setCharFormat(format)
        
        char_count += len(line) + 1  # +1 for the \n

    # highlight each keyword (but comments will stay green)
    text_input.moveCursor(QTextCursor.Start)

    for word, color in KEYWORD_COLORS.items():
        index = 0
        while index < len(current_text):
            index = current_text.find(word, index)
            if index == -1:
                break

            # check if this word is inside a comment
            line_start = current_text.rfind('\n', 0, index) + 1
            line_text = current_text[line_start:current_text.find('\n', index) if current_text.find('\n', index) != -1 else len(current_text)]
            comment_pos = line_text.find(COMMENT_START)
            
            # only highlight if not in a comment
            if comment_pos == -1 or (index - line_start) < comment_pos:
                cursor = text_input.textCursor()
                cursor.setPosition(index)
                cursor.setPosition(index + len(word), QTextCursor.KeepAnchor)

                format = QTextCharFormat()
                format.setForeground(QColor(color))
                cursor.setCharFormat(format)

            index += len(word)

    # restore cursor position
    cursor = text_input.textCursor()
    cursor.setPosition(current_pos)
    text_input.setTextCursor(cursor)
    
    #unblock
    text_input.blockSignals(False)


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

def execute_code(tab_widget, lexeme_manager, token_table, symbol_table, console_widget):
    # get current tab's content manager
    current_index = tab_widget.currentIndex()
    if current_index == -1:
        console_widget.write("Error: No file open", "#FF6B6B")
        return
    
    current_tab = tab_widget.widget(current_index)
    content_manager = current_tab.property("content_manager")
    
    if content_manager.saved_content is None:
        console_widget.write("Error: Please save the file first (Ctrl+S)", "#FF6B6B")
        return
    
    # find all GIMMEH statements before running interpreter
    gimmeh_variables = []
    lines = content_manager.saved_content.split('\n')
    
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith("GIMMEH"):
            parts = line_stripped.split()
            if len(parts) >= 2:
                variable_name = parts[1]
                gimmeh_variables.append(variable_name)  # keep all, even duplicates
    
    # prompt for all GIMMEH statements upfront
    gimmeh_inputs = []
    if gimmeh_variables:
        var_list = ", ".join(gimmeh_variables)
        user_input, ok = QInputDialog.getText(
            None,
            'GIMMEH',
            f'Enter values for ({var_list}) separated by commas:'
        )
        
        if ok and user_input:
            values = [v.strip() for v in user_input.split(',')]
            
            if len(values) == len(gimmeh_variables):
                gimmeh_inputs = values  # store as list in order
                console_widget.write(f"GIMMEH inputs: {gimmeh_inputs}", "#95E1D3")
            else:
                console_widget.write(f"Error: Expected {len(gimmeh_variables)} values, got {len(values)}", "#FF6B6B")
                return
        else:
            console_widget.write("Input cancelled", "#FF6B6B")
            return
    
    # append gimmeh values to content
    content = content_manager.saved_content
    for value in gimmeh_inputs:
        content += "\n" + value
    
    # temporarily update content for execution
    original_content = content_manager.saved_content
    content_manager.saved_content = content
    
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
                content_manager.saved_content = original_content  # restore
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
            
            # Restore original content
            content_manager.saved_content = original_content

        except Exception as e:
            console_widget.write(f"Error: {str(e)}", "#FF6B6B")
            import traceback
            console_widget.write(traceback.format_exc(), "#FF6B6B")
            content_manager.saved_content = original_content  # restore
    
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
    return table


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


def create_new_tab(tab_widget, win, file_name = None, content = None):
    # create new manager for this tab
    file_manager = FileManager()
    content_manager = TextContentManager()

    #create new text editor widget
    text_editor = QWidget()
    text_editor.setStyleSheet("background-color: #1E1E1E;")

    # create text input
    text_input = text_edit(text_editor, file_manager, content_manager, win)

    # if content is provided:
    if content:
        text_input.setPlainText(content)
        content_manager.saved_content = content
    if file_name:
        file_manager.file_name = file_name
    
    # store managers in widget prop
    text_editor.setProperty("file_manager", file_manager)
    text_editor.setProperty("content_manager", content_manager)
    text_editor.setProperty("text_input", text_input)

    # add tab
    tab_name = os.path.basename(file_name) if file_name else "Untitled"
    index = tab_widget.addTab(text_editor, tab_name)
    
    # add custom close button with icon
    close_btn = QPushButton()
    close_btn.setIcon(QIcon('src/assets/x.png'))
    close_btn.setIconSize(QSize(16, 16))
    close_btn.setFixedSize(16, 16)
    close_btn.setFlat(True)
    close_btn.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            border: none;
            padding: 0px;
        }
        QPushButton:hover {
            background-color: rgba(200, 200, 200, 0.2);
            border-radius: 2px;
        }
    """)
    close_btn.clicked.connect(lambda: tab_widget.removeTab(index))
    tab_widget.tabBar().setTabButton(index, tab_widget.tabBar().RightSide, close_btn)
  
    
    tab_widget.setCurrentWidget(text_editor)

    return text_editor

def file_open(tab_widget, win): # open file and load content
    options = QFileDialog.Options() # opens file manager
    file_name, _ = QFileDialog.getOpenFileName(
        None, "Select a File", "", "All Files (*);;Text Files (*.txt);;LOLCode Files (*.lol)", options=options
    )
    
    if file_name: # if exists
        try:
            with open(file_name, 'r') as file:
                content = file.read()
               # create new tab with file content
                create_new_tab(tab_widget, win, file_name, content)
                print(f"File opened: {file_name}")
        except Exception as e:
            print(f"Error opening file: {e}")

def save_current_tab(tab_widget, win): # For saving current tab's status
    current_index = tab_widget.currentIndex()
    if current_index == -1:
        return
    
    current_tab = tab_widget.widget(current_index)
    text_input = current_tab.property("text_input")
    file_manager = current_tab.property("file_manager")
    content_manager = current_tab.property("content_manager")
    
    save_and_store(text_input, file_manager, content_manager, win)

def layout(win):
    main_widget = QWidget()
    win.setCentralWidget(main_widget)

    # for data persistence
    lexeme_manager = LexemeManager()
    
    main_layout = QVBoxLayout()
    side_layout = QHBoxLayout()
    minor_layout = QVBoxLayout()
    right_column = QVBoxLayout()
    file_searcher_layout = QHBoxLayout()
    main_widget.setLayout(main_layout)

    ######### FILE SEARCHER WIDGETS #########  
    menu_btn = QPushButton()
    menu_btn.setFixedSize(25,25)
    menu_btn.setIcon(QIcon('src/assets/hamburger.png'))
    menu_btn.setIconSize(QSize(25,25))
    menu_btn.setFlat(True)

    file_icon = QLabel()
    file_icon.setFixedSize(25,25)
    icon = QPixmap('src/assets/folder.png')
    icon = icon.scaled(25,25,Qt.KeepAspectRatio, Qt.SmoothTransformation)
    file_icon.setPixmap(icon)

    exec_btn = QPushButton()
    exec_btn.setFixedSize(25,25)
    exec_btn.setIcon(QIcon('src/assets/play-button.png'))
    exec_btn.setIconSize(QSize(25,25))
    exec_btn.setFlat(True)
    
    # create menu
    menu = QMenu(win)
    new_file_action = QAction('New File',win)
    open_file_action = QAction('Open File',win)
    save_file_action = QAction('Save File',win)

    menu.addAction(new_file_action)
    menu.addAction(open_file_action)
    menu.addAction(save_file_action)

    ######### END OF FILE SEARCHER WIDGETS #########  

    # tab widget for multiple files
    tab_widget = QTabWidget()
    tab_widget.setTabsClosable(True)
    tab_widget.setMovable(True)

    # set font
     # set default application font
    font = QFont("San Francisco", 10)  
    tab_widget.setFont(font)

    
    file_searcher = QPushButton('Open File') 
    file_searcher_layout.addWidget(menu_btn,1)
    file_searcher_layout.addWidget(file_searcher, 2)
    file_searcher_layout.addWidget(file_icon,1)
    file_searcher_layout.addWidget(exec_btn,1)
    
    # right column widgets
    symbol_table_widget = QWidget()
    token_view_widget = QWidget()
    
    # console at bottom
    console = InteractiveConsole()
  
    # create symbol table and lexeme table (vertically stacked)
    symbol_table = create_table(symbol_table_widget, "Identifier", "Value")
    token_table = create_table(token_view_widget, "Lexeme", "Classification")

    ##### STYLE ##############
    tab_widget.setStyleSheet("""
        QTabWidget::pane {
            border: none;
            background-color: #1E1E1E;
        }
        
        QTabBar::tab {
            background-color: #2D2D2D;
            color: #CCCCCC;
            padding: 8px 24px 8px 12px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #1E1E1E;
            color: #FFFFFF;
            border-bottom: 2px solid #007ACC;
        }
        QTabBar::tab:hover {
            background-color: #3E3E3E;
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

    token_view_widget.setStyleSheet("background-color: #1A1A1A;")
    symbol_table_widget.setStyleSheet("background-color: #1F1F1F;")
    ###### STYLE ###########

    # connect actions
    new_file_action.triggered.connect(lambda: create_new_tab(tab_widget, win))
    open_file_action.triggered.connect(lambda: file_open(tab_widget, win))
    save_file_action.triggered.connect(lambda: save_current_tab(tab_widget, win))
    
    menu_btn.clicked.connect(lambda: menu.exec_(menu_btn.mapToGlobal(menu_btn.rect().bottomLeft())))
    exec_btn.clicked.connect(lambda: execute_code(tab_widget, lexeme_manager, token_table, symbol_table, console))
    file_searcher.clicked.connect(lambda: file_open(tab_widget, win))

    # create initial empty tab
    create_new_tab(tab_widget, win)

    # left column layout
    minor_layout.addWidget(tab_widget, 2)

    # right column layout (symbol table on top, lexeme table on bottom)
    right_column.addWidget(symbol_table_widget, 1)
    right_column.addWidget(token_view_widget, 1)

    # main horizontal layout
    side_layout.addLayout(minor_layout, 3)
    side_layout.addLayout(right_column, 2)

    # vertical layout
    main_layout.addLayout(file_searcher_layout, 0)
    main_layout.addLayout(side_layout, 3)
    main_layout.addWidget(console, 1)


def main():
    app = QApplication(sys.argv)
    win = QMainWindow()

     # Set default application font
    font = QFont("San Francisco", 10) 
    app.setFont(font)
    app.setWindowIcon(QIcon('src/assets/lolcode.png'))
    win.setGeometry(0, 0, 600, 400)
    win.setWindowTitle("WeLove124")
    win.setStyleSheet("""
        QMainWindow {
            background-color: #181818;
            color: #FAFAFA;
        }
        
        QScrollBar:vertical {
            background-color: #1E1E1E;
            width: 14px;
            border: none;
        }
        
        QScrollBar::handle:vertical {
            background-color: #424242;
            min-height: 30px;
            border-radius: 7px;
            margin: 2px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #4F4F4F;
        }
        
        QScrollBar::handle:vertical:pressed {
            background-color: #565656;
        }
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: none;
        }
        
        QScrollBar:horizontal {
            background-color: #1E1E1E;
            height: 14px;
            border: none;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #424242;
            min-width: 30px;
            border-radius: 7px;
            margin: 2px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #4F4F4F;
        }
        
        QScrollBar::handle:horizontal:pressed {
            background-color: #565656;
        }
        
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal {
            background: none;
        }
    """)

    layout(win)
    win.show()

    sys.exit(app.exec_())


main()