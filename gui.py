import os
import sys
import queue
import threading
from PyQt5.QtGui import QFont, QKeySequence, QTextCursor, QTextCharFormat, QColor, QIcon, QFontDatabase, QPixmap
from PyQt5.QtWidgets import (QWidget, QApplication, QMainWindow, QFileDialog,
                            QHBoxLayout, QVBoxLayout,QTextEdit,
                            QShortcut, QInputDialog, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                            QMenu, QTabWidget, QAction, QFrame)
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
    
    def __init__(self, global_font):
        super().__init__()
        self.input_queue = queue.Queue()
        self.waiting_for_input = False
        self.input_buffer = ""
        self.input_start_pos = 0
        self.input_requested.connect(self._request_input_slot)
        self.global_font = global_font  
        self.setup_ui()
    
    def setup_ui(self):
        inter = QFont(self.global_font, 11)
        self.setFont(inter)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #181818;
                color: #FAFAFA;
                border: none;
                padding: 20px;
                border-top: 1px solid #393939;   
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

# Helper function to reset zoom
def reset_zoom(text_input, default_size, global_font):
    inter_font =  QFont(global_font, default_size)
    text_input.setFont(inter_font)
    text_input.setFont(global_font)

def text_edit(text_editor, file_manager, content_manager, parent_widget, global_font): # Text editor panel
    editor_layout = QVBoxLayout() # main vertical layout
    text_editor.setLayout(editor_layout)
    text_editor.setStyleSheet("background-color: #1F1F1F; border: none;")   
    text_input = QTextEdit() 
    text_input.setPlaceholderText("Type here...")

    # custom font
    consolas_font =  QFont(global_font, 11)
    text_input.setFont(consolas_font)
    text_input.setStyleSheet("border: none; color: #FAFAFA;") 


    editor_layout.addWidget(text_input)

    # keyboard shortcuts 
    save_shortcut = QShortcut(QKeySequence.Save, text_input) # bind key to saving
    copy_shortcut = QShortcut(QKeySequence.Copy, text_input) # bind key to copying
    paste_shortcut = QShortcut(QKeySequence.Paste, text_input) # bind key to pasting
    cut_shortcut = QShortcut(QKeySequence.Cut, text_input) # bind key to cutting 
    undo_shortcut = QShortcut(QKeySequence.Undo, text_input) # bind key to undo
    redo_shortcut = QShortcut(QKeySequence.Redo, text_input) # bind key to redo
    selectall_shortcut = QShortcut(QKeySequence.SelectAll, text_input) # bind key to select all
    zoom_in_shortcut = QShortcut(QKeySequence.ZoomIn, text_input)  # Ctrl+Plus (Cmd+Plus on Mac)
    zoom_in_shortcut.activated.connect(text_input.zoomIn)
    zoom_out_shortcut = QShortcut(QKeySequence.ZoomOut, text_input)  # Ctrl+Minus (Cmd+Minus on Mac)
    zoom_out_shortcut.activated.connect(text_input.zoomOut)
    zoom_reset_shortcut = QShortcut(QKeySequence("Ctrl+0"), text_input) # for resetting zoom
    zoom_reset_shortcut.activated.connect(lambda: reset_zoom(text_input, 9, global_font))
    zoom_reset_shortcut_mac = QShortcut(QKeySequence("Meta+0"), text_input)
    zoom_reset_shortcut_mac.activated.connect(lambda: reset_zoom(text_input, 9, global_font))

    # keyboard shortcut actions
    save_shortcut.activated.connect(lambda: save_and_store(text_input, file_manager, content_manager, parent_widget))
    copy_shortcut.activated.connect(lambda: text_input.copy())
    paste_shortcut.activated.connect(lambda: text_input.paste())
    cut_shortcut.activated.connect(lambda: text_input.cut())
    undo_shortcut.activated.connect(lambda: text_input.undo())
    redo_shortcut.activated.connect(lambda: text_input.redo())
    selectall_shortcut.activated.connect(lambda: text_input.selectAll())
    zoom_in_shortcut.activated.connect(lambda: text_input.zoomIn())
    zoom_out_shortcut.activated.connect(lambda: text_input.zoomOut())
    zoom_reset_shortcut.activated.connect(lambda: reset_zoom(text_input, 11, global_font))
    zoom_reset_shortcut_mac.activated.connect(lambda: reset_zoom(text_input, 11, global_font))

  
    
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
        if line.find(MULTI_COMMENT) != -1:
            # for multi-line comments, highlight entire line
            start_pos = char_count + line.find(MULTI_COMMENT)
            end_pos = char_count + len(line)
            
            cursor = text_input.textCursor()
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
            
            format = QTextCharFormat()
            format.setForeground(QColor(COMMENT_COLOR))
            cursor.setCharFormat(format)

       
        comment_index = line.find(COMMENT_START) # find index of comment start BTW
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
    
    def run_interpreter():
        """Run interpreter - output and input are sequential in the console"""
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
                console_widget.write(f"Parse Error: {AST.error.as_string()}", "#FF6B6B")
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
                # Handle special case where text might have no newline
                end = kwargs.get('end', '\n')
                if end == '\n':
                    console_widget.write(text, "#FAFAFA")
                else:
                    # Write without newline
                    cursor = console_widget.textCursor()
                    cursor.movePosition(QTextCursor.End)
                    format = QTextCharFormat()
                    format.setForeground(QColor("#FAFAFA"))
                    cursor.setCharFormat(format)
                    cursor.insertText(text)
                    console_widget.setTextCursor(cursor)
                    console_widget.ensureCursorVisible()
            
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
                error_msg = result.error.as_string() if hasattr(result.error, 'as_string') else str(result.error)
                console_widget.write(error_msg, "#FF6B6B")
            else:
                console_widget.write("\n=== Execution complete ===", "#95E1D3")
            
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


def create_table(parent_widget, label1, label2, global_font): # Func for creating tables
    token_layout = QVBoxLayout()
    parent_widget.setLayout(token_layout) # set it as layout for the identifier/lexeme widget 
    
    table = QTableWidget()
    table.setColumnCount(2)

    # headers
    header_label1 = QTableWidgetItem(label1)
    header_label2 = QTableWidgetItem(label2)
    header_label1.setTextAlignment(Qt.AlignCenter)  # center horizontally & vertically
    header_label2.setTextAlignment(Qt.AlignCenter)
    table.setHorizontalHeaderItem(0, header_label1)
    table.setHorizontalHeaderItem(1, header_label2)
    
    # set to center
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setEditTriggers(QTableWidget.NoEditTriggers)  # so table can't be edited
    
    #### STYLE #####
    table.setStyleSheet("""
        QTableWidget {
            background-color: #1F1F1F;
            color: #FAFAFA;
            border: 1px solid #393939;
            gridline-color: none;
        }
        QHeaderView::section {
            background-color: #1F1F1F;
            color: #FAFAFA;
            border: none;
            border-bottom: 1px solid #393939;
            padding: 5px;

        }
      QTableWidget::item {
            padding: 5px;
            border: none;
            font-size: 7px;
            color: #FAFAFA;
        }
                        
        QTableCornerButton::section {
        background-color: #1F1F1F;   
        border: none;
        }
    """)


    # set font
    inter_font =  QFont(global_font, 10)
    table.setFont(inter_font)
    table.horizontalHeader().setFont(inter_font)
    
   
    ####  END OF STYLE #####
    token_layout.addWidget(table)
    token_layout.setContentsMargins(0,0,0,0)
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
            
       
            lexeme = item.get('value', '')
            description = item.get('category', '')

            lex_item = QTableWidgetItem(lexeme)
            desc_item = QTableWidgetItem(description)
            lex_item.setTextAlignment(Qt.AlignCenter)
            desc_item.setTextAlignment(Qt.AlignCenter)

            # font
            font = lex_item.font()
            font.setPointSize(9)
            lex_item.setFont(font)
            
            table.setItem(row_position, 0, lex_item)
            table.setItem(row_position, 1, desc_item)


    
    table.setStyleSheet("""
        QTableWidget::item {
            padding: 5px;
            border: none;
            font-size: 7px;
            color: #FAFAFA;
        }
                        
        QHeaderView::section {
            background-color: #1F1F1F;
            color: #FAFAFA;
            border: none;
            border-bottom: 1px solid #393939;
            padding: 5px;

        }
                        
        QTableCornerButton::section {
        background-color: #1F1F1F;   
        border: none;
        }
    """)

def update_symbol_table(table, symbol_table_obj): # Update table func
    table.setRowCount(0)
    
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

            type_name = type(value).__name__
            lolcode_type = type_map.get(type_name, lambda v: 'UNKNOWN')(value)
            display_value = f"{value} ({lolcode_type})"

            id_item = QTableWidgetItem(var_name)
            id_item = QTableWidgetItem(var_name)
            id_item.setTextAlignment(Qt.AlignCenter)

            font = id_item.font()
            font.setPointSize(9)
            id_item.setFont(font)

            val_item = QTableWidgetItem(display_value)
            val_item.setTextAlignment(Qt.AlignCenter)

            font2 = val_item.font()
            font2.setPointSize(9)
            val_item.setFont(font2)

            table.setItem(row_position, 0, id_item)
            table.setItem(row_position, 1, val_item)

    table.setStyleSheet("""
        QTableWidget::item {
            padding: 5px;
            border: none;
            color: #FAFAFA;
        }
                        
        QHeaderView::section {
            background-color: #1F1F1F;
            color: #FAFAFA;
            border: none;
            border-bottom: 1px solid #393939;
            padding: 5px;

        }
                        
        QTableCornerButton::section {
        background-color: #1F1F1F;   
        border: none;
        }
    """)



            


def create_new_tab(tab_widget, win,  global_font, file_name = None, content = None): # create new tab function
    # create new manager for this tab
    file_manager = FileManager()
    content_manager = TextContentManager()

    #create new text editor widget
    text_editor = QWidget()
    text_editor.setStyleSheet("background-color: #1F1F1F; border: none; padding: 20px;")

    # create text input
    text_input = text_edit(text_editor, file_manager, content_manager, win, global_font)

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

def file_open(tab_widget, win, global_font): # open file and load content
    options = QFileDialog.Options() # opens file manager
    file_name, _ = QFileDialog.getOpenFileName(
        None, "Select a File", "", "All Files (*);;Text Files (*.txt);;LOLCode Files (*.lol)", options=options
    )
    
    if file_name: # if exists
        try:
            with open(file_name, 'r') as file:
                content = file.read()
               # create new tab with file content
                create_new_tab(tab_widget, win, global_font, file_name, content )
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

def layout(win, global_font, global_font1): # Main Layout
    main_widget = QWidget()
    win.setCentralWidget(main_widget)

    # for data persistence
    lexeme_manager = LexemeManager()
    
    main_layout = QVBoxLayout()
    side_layout = QVBoxLayout()
    minor_layout = QVBoxLayout()
    right_column = QVBoxLayout()
    search_button_layout = QHBoxLayout()
    file_searcher_layout = QHBoxLayout()
    main_widget.setLayout(main_layout)

    ######### FILE SEARCHER WIDGETS #########  
    menu_btn = QPushButton()
    menu_btn.setFixedSize(25,25)
    menu_btn.setIcon(QIcon('src/assets/hamburger.png'))
    menu_btn.setIconSize(QSize(25,25))
    menu_btn.setFlat(True)

    file_icon = QLabel()
    file_icon.setFixedSize(15,15)
    icon = QPixmap('src/assets/search.png')
    icon = icon.scaled(15,15,Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
    inter_font =  QFont(global_font, 9)
    tab_widget.setFont(inter_font)

    # TO DO: fix icon alignment with text | fix color of icon !!
    file_searcher = QPushButton('Open File')
    file_searcher.setFixedHeight(30)
    file_searcher.setFont(inter_font)
    file_searcher.setIcon(QIcon(file_icon.pixmap()))
     
    # search file 
    search_button_layout.addWidget(file_searcher)
   

    # main file searcher layout !! TO DO: fix icon hover !!
    file_searcher_layout.addWidget(menu_btn,1)
    file_searcher_layout.addStretch(1)
    file_searcher_layout.addLayout(search_button_layout, 1)
    file_searcher_layout.addStretch(1)
    file_searcher_layout.addWidget(exec_btn,1)
    file_searcher_layout.setContentsMargins(10,10,10,10)
    file_searcher_layout.borderWidth = 1
    
    
    
    # right column widgets
    symbol_table_widget = QWidget()
    token_view_widget = QWidget()
    
    # console at bottom
    console = InteractiveConsole(global_font1)
  
    # create symbol table and lexeme table (vertically stacked)
    symbol_table = create_table(symbol_table_widget, "Identifier", "Value", global_font)
    token_table = create_table(token_view_widget, "Lexeme", "Classification", global_font)

    # container layot for text editor, console, symbol table, lexeme table
    container_frame = QFrame()

    #------ STYLE------#
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
            background-color: #1F1F1F;
            color: #A2A2A2;
            border: 1px solid #393939;
            padding: 5px 5px;
            border-radius: 5px;
            max-width: 500px;   
            font-size: 14px;

        }
       
    """)

    token_view_widget.setStyleSheet("background-color: #1A1A1A;border-right: 1px solid #393939; border-radius: 7px;")
    symbol_table_widget.setStyleSheet("background-color: #1F1F1F; border-right: 1px solid #393939; border-radius: 7px;")
    container_frame.setStyleSheet("border-top: 1px solid #393939; border-bottom: 1px solid #393939;border-right:1px solid #393939;  margin: 0px; padding: 0px;")
    #------ END OF STYLE ------#

    # connect actions
    new_file_action.triggered.connect(lambda: create_new_tab(tab_widget, win, global_font1))
    open_file_action.triggered.connect(lambda: file_open(tab_widget, win, global_font1))
    save_file_action.triggered.connect(lambda: save_current_tab(tab_widget, win))
    
    menu_btn.clicked.connect(lambda: menu.exec_(menu_btn.mapToGlobal(menu_btn.rect().bottomLeft())))
    exec_btn.clicked.connect(lambda: execute_code(tab_widget, lexeme_manager, token_table, symbol_table, console))
    file_searcher.clicked.connect(lambda: file_open(tab_widget, win, global_font1))
    
    # create general shortcuts
    openfile_shortcut = QShortcut(QKeySequence("Ctrl+O"), win) # bind key to open file
    openfile_shortcutMac = QShortcut(QKeySequence("Meta+O"), win) # bind key to open file (macOS)
    runfile_shortcut = QShortcut(QKeySequence("Ctrl+R"), win) # bind key to run file
    runfile_shortcutMac = QShortcut(QKeySequence("Meta+R"), win) # bind key to run file (macOS)
    new_file_action_shortcut = QShortcut(QKeySequence("Ctrl+N"), win) # bind key to new file
    new_file_action_shortcutMac = QShortcut(QKeySequence("Meta+N"), win) # bind key to new file (macOS)

    # shortcut actions
    openfile_shortcut.activated.connect(lambda: file_open(tab_widget, win, global_font1))
    openfile_shortcutMac.activated.connect(lambda: file_open(tab_widget, win, global_font1))
    runfile_shortcutMac.activated.connect(lambda: execute_code(tab_widget, lexeme_manager, token_table, symbol_table, console))
    runfile_shortcut.activated.connect(lambda: execute_code(tab_widget, lexeme_manager, token_table, symbol_table, console))
    new_file_action_shortcut.activated.connect(lambda: create_new_tab(tab_widget, win, global_font1))
    new_file_action_shortcutMac.activated.connect(lambda: create_new_tab(tab_widget, win, global_font1))

    # create initial empty tab
    create_new_tab(tab_widget, win, global_font1)

    # text editor layout
    minor_layout.addWidget(tab_widget, 2)
    minor_layout.setContentsMargins(0,0,0,0)

    # right column layout (symbol table on top, lexeme table on bottom)
    right_column.addWidget(symbol_table_widget, 1)
    right_column.addWidget(token_view_widget, 1)
    right_column.setContentsMargins(10,15,10,15)
    right_column.setSpacing(20)
   
    # main horizontal layout
    main_frame = QFrame()
    main_frame.setLayout(side_layout)
    side_layout.addLayout(minor_layout, 3)
    side_layout.addWidget(console, 2)
    side_layout.setContentsMargins(0,0,0,0)
    side_layout.setSpacing(0)

    # container layout
    container_layout = QHBoxLayout()
    container_layout.addWidget(main_frame, 3)
    container_layout.addLayout(right_column, 1)
    container_layout.setContentsMargins(0,0,0,0)
    container_frame.setLayout(container_layout)

    # vertical layout
    main_layout.addLayout(file_searcher_layout, 0)
    main_layout.addWidget(container_frame)
    main_layout.setContentsMargins(0,0,0,0)


def main(): # Main Function
    app = QApplication(sys.argv)
    win = QMainWindow()
    app.setWindowIcon(QIcon('src/assets/lolcode.png'))
    win.setGeometry(0, 0, 600, 400)
    win.setWindowTitle("WeLove124")

    # set global font
    global_font_custom = QFontDatabase().addApplicationFont("src/assets/font/inter.ttf")
    global_font_custom1 = QFontDatabase().addApplicationFont("src/assets/font/Consolas.ttf")  
    global_font_family = QFontDatabase.applicationFontFamilies(global_font_custom)[0]
    global_font_family1 = QFontDatabase.applicationFontFamilies(global_font_custom1)[0]

    #--- VSCODE-LIKE THEME STYLESHEET ----
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

    #--- END OF THEME STYLESHEET ----

    layout(win, global_font_family, global_font_family1)
    win.show()

    sys.exit(app.exec_())


main()