import os
import sys
from PyQt5.QtGui import QFont, QKeySequence, QTextCharFormat, QColor, QTextCursor, QIcon, QPixmap
from PyQt5.QtWidgets import (QWidget, QApplication, QMainWindow, QFileDialog,
                            QHBoxLayout, QVBoxLayout,QTextEdit,
                            QShortcut, QInputDialog, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                            QMenu, QTabWidget, QAction )
from PyQt5.QtCore import Qt, QSize
from src.lexer import tokenizer


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

def execute_code(tab_widget, lexeme_manager, token_table, identifier_table):
    # get current tab's content manager
    current_index = tab_widget.currentIndex()
    if current_index == -1:
        print("Error: No file open")
        return
    
    current_tab = tab_widget.widget(current_index)
    content_manager = current_tab.property("content_manager")
    
    if content_manager.saved_content is None:
        print("Error: Please save the file first (Ctrl+S)")
        return
    try:  
        # find all GIMMEH statements
        gimmeh_variables = []
        lines = content_manager.saved_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith("GIMMEH"):
                parts = line.split()
                if len(parts) >= 2:
                    variable_name = parts[1]
                    gimmeh_variables.append(variable_name)  # keep all, even duplicates
        
        # prompt for all GIMMEH statements
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
                    print(f"GIMMEH inputs: {gimmeh_inputs}")
                else:
                    print(f"Error: Expected {len(gimmeh_variables)} values, got {len(values)}") # in any case user had less/more inputs
                    return
            else:
                print("Input cancelled")
                return
        
        # append gimmeh values to content
        content = content_manager.saved_content
        for value in gimmeh_inputs:
            content += "\n" + value
        
        content_manager.saved_content = content  # update
        
        # tokenize with updated content !! ONCE PARSER DONE PASS AS  PARAMETER FOR GIMMEH THE DICTIONARY/THE ACTUAL VALUES ItsELF!!
        result = tokenizer.tokenize(content_manager.saved_content)
        
        print("Tokenization result:", result)
        lexeme_manager.saved_lexemes = result
        print("Generating lexemes...")
        
        update_token_view(token_table, result)

    except Exception as e:
        print(f"Error during tokenization: {e}")





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
    
    # if lexemes is a dictionary (for symbol table)
    elif isinstance(lexemes, dict):
        for lexeme, description in lexemes.items(): 
            row_position = table.rowCount()
            table.insertRow(row_position)
            
            table.setItem(row_position, 0, QTableWidgetItem(str(lexeme)))
            table.setItem(row_position, 1, QTableWidgetItem(str(description)))


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
    tab_widget.addTab(text_editor, tab_name)
    tab_widget.setCurrentWidget(text_editor)

    return text_editor

def file_open(tab_widget, win): # open file and load content
    options = QFileDialog.Options() # opens file manager
    file_name, _ = QFileDialog.getOpenFileName(
        None, "Select a File", "", "All Files (*);;Text Files (*.txt);;Python Files (*.py)", options=options
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

    # for data persistence for file name, text input and lexemes
    lexeme_manager = LexemeManager()
    
    main_layout = QVBoxLayout()
    side_layout = QHBoxLayout()
    minor_layout = QVBoxLayout()
    file_searcher_layout = QHBoxLayout() # burger icon, open file, file icon, execute button
    main_widget.setLayout(main_layout)

    ######### FILE SEARCHER WIDGETS #########  
    # add file searcher widgets
    menu_btn = QPushButton()
    menu_btn.setFixedSize(15,15)
    menu_btn.setIcon(QIcon('src/assets/hamburger.png'))
    menu_btn.setIconSize(QSize(15,15))
    menu_btn.setFlat(True)

    # file icon label
    file_icon = QLabel()
    file_icon.setFixedSize(21,21)
    icon = QPixmap('src/assets/folder.png')
    icon = icon.scaled(21,21,Qt.KeepAspectRatio, Qt.SmoothTransformation)
    file_icon.setPixmap(icon)


   # execute_btn 
    exec_btn = QPushButton()
    exec_btn.setFixedSize(21,21)
    exec_btn.setIcon(QIcon('src/assets/play-button.png'))
    exec_btn.setIconSize(QSize(21,21))
    exec_btn.setFlat(True)
    
    # create menu
    menu = QMenu(win)
    new_file_action = QAction('New File',win)
    open_file_action =QAction('Open File',win)
    save_file_action = QAction('Save File',win)

    # add action
    menu.addAction(new_file_action)
    menu.addAction(open_file_action)
    menu.addAction(save_file_action)


    ######### END OF  FILE SEARCHER WIDGETS #########  

    # tab widget for multiple files
    tab_widget = QTabWidget()
    tab_widget.setTabsClosable(True)
    tab_widget.setMovable(True)
    file_searcher = QPushButton('Open File') 
    file_searcher_layout.addWidget(menu_btn,1)
    file_searcher_layout.addWidget(file_searcher, 2)
    file_searcher_layout.addWidget(file_icon,1)
    file_searcher_layout.addWidget(exec_btn,1)
    token_view_widget = QWidget() # lexeme tokens view
    terminal = QWidget() # terminal
    identifier_view_widget = QWidget() # symbol viewer
    
  
    # create lexeme and identifier table
    token_table = create_table(token_view_widget, "Lexeme", "Classification")
    identifier_table = create_table(identifier_view_widget, "Identifier", "Value")


    ##### STYLE ##############
    tab_widget.setStyleSheet("""
        QTabWidget::pane {
            border: none;
            background-color: #1E1E1E;
        }
        QTabBar::tab {
            background-color: #2D2D2D;
            color: #CCCCCC;
            padding: 8px 12px;
            margin-right: 2px;
            font-family: 'Consolas';
            font-size: 11px;
        }
        QTabBar::tab:selected {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        QTabBar::tab:hover {
            background-color: #3E3E3E;
        }
        QTabBar::close-button {
            image: url(src/assets/x.png);
            subcontrol-position: right;
        }
        QTabBar::close-button:hover {
            background-color: #E81123;
            border-radius: 2px;
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
    terminal.setStyleSheet("background-color: #1F1F1F;")
    identifier_view_widget.setStyleSheet("background-color: #1F1F1F;")
    ###### STYLE ###########

    # connect actions
    new_file_action.triggered.connect(lambda: create_new_tab(tab_widget, win))
    open_file_action.triggered.connect(lambda: file_open(tab_widget, win))
    save_file_action.triggered.connect(lambda: save_current_tab(tab_widget, win))
    tab_widget.tabCloseRequested.connect(lambda index: tab_widget.removeTab(index))
    
    menu_btn.clicked.connect(lambda: menu.exec_(menu_btn.mapToGlobal(menu_btn.rect().bottomLeft())))
    exec_btn.clicked.connect(lambda: execute_code(tab_widget, lexeme_manager, token_table, identifier_table))
    file_searcher.clicked.connect(lambda: file_open(tab_widget, win)) # prompts file search

    # create initial empty tab
    create_new_tab(tab_widget, win)

    #layout
    minor_layout.addWidget(tab_widget,2)

    side_layout.addLayout(minor_layout,2)
    side_layout.addWidget(token_view_widget,1)
    side_layout.addWidget(identifier_view_widget,1)

    # vertical layout
    main_layout.addLayout(file_searcher_layout,1)
    main_layout.addLayout(side_layout,2)
    main_layout.addWidget(terminal,1)



def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(0, 0, 600, 400) # set dimensions
    win.setWindowTitle("WeLove124")
    win.setStyleSheet("background-color: #181818; color: #FAFAFA;")

    layout(win)
    win.show()

    # exit
    sys.exit(app.exec_())


main()