import sys
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtWidgets import (QWidget, QApplication, QMainWindow, QFileDialog,
                            QHBoxLayout, QVBoxLayout,QTextEdit,
                            QShortcut, QInputDialog, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from src.lexer import tokenizer


# For managing persistence
class TextContentManager:
    def __init__(self):
        self.saved_content = None

class FileManager: # for filename
    def __init__(self):
        self.file_name = None

class LexemeManager: # for lexeme tokens
    def __init__(self):
        self.saved_lexemes = None


def text_edit(text_editor, file_manager, content_manager, parent_widget): # Text editor panel
    editor_layout = QVBoxLayout() # main vertical layout
    text_editor.setLayout(editor_layout)

    text_input = QTextEdit() # text input
    text_input.setPlaceholderText("Type here...")

    font = QFont("Consolas",11) # Customize Font
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


def execute_code(content_manager, lexeme_manager, token_table, identifier_table): # Func for calling tokenizer
    if content_manager.saved_content is None:
        print("Error: Please save the file first (Ctrl+S)")
        return
    try:  
        result = tokenizer.tokenize(content_manager.saved_content) # call tokenizer
        print("Tokenization result:", result)

        lexeme_manager.saved_lexemes = result
        print("Generating lexemes...")
        
        update_token_view(token_table, result)

    except ImportError:
        print("Error: tokenizer.py not found")
    except Exception as e:
        print(f"Error during tokenization: {e}")


def save_input(text_input, file_manager, parent_widget): # Save as <filename>.txt to be passed into parser
   
    if file_manager.file_name is None:
        file_name, ok = QInputDialog.getText(parent_widget, 'Save File', 'Enter file name:')
        
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


def create_token_view(parent_widget, label1, label2): # Func for creating tables
    token_layout = QVBoxLayout()
    parent_widget.setLayout(token_layout)
    
    table = QTableWidget()
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels([label1, label2])
   
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)

    table.setEditTriggers(QTableWidget.NoEditTriggers)  # so table can't be edited
    
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
    
    token_layout.addWidget(table)
    
    return table


def update_token_view(table, lexemes): # update table with the lexemes
    if lexemes is None:
        print("Error! Empty lexemes!")
        return
    
    table.setRowCount(0)
    
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
            # anything else
            else:
                table.setItem(row_position, 0, QTableWidgetItem(str(item)))
                table.setItem(row_position, 1, QTableWidgetItem(''))
    
    # if lexemes is a dictionary
    elif isinstance(lexemes, dict):
        for lexeme, description in lexemes.items():
            row_position = table.rowCount()
            table.insertRow(row_position)
            
            table.setItem(row_position, 0, QTableWidgetItem(str(lexeme)))
            table.setItem(row_position, 1, QTableWidgetItem(str(description)))


def file_open(text_input, file_manager, content_manager, file_button): # open file and load content
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getOpenFileName(
        None, "Select a File", "", "All Files (*);;Text Files (*.txt);;Python Files (*.py)", options=options
    )
    
    if file_name:
        try:
            with open(file_name, 'r') as file:
                content = file.read()
                text_input.setPlainText(content)
                file_manager.file_name = file_name
                content_manager.saved_content = content  # store content so execute can work
                
                # show filename on button
                import os
                file_button.setText(os.path.basename(file_name))
                
                print(f"File opened: {file_name}")
        except Exception as e:
            print(f"Error opening file: {e}")


def layout(win):
    main_widget = QWidget()
    win.setCentralWidget(main_widget)

    file_manager = FileManager()
    content_manager = TextContentManager()
    lexeme_manager = LexemeManager()
    
    main_layout = QVBoxLayout()
    side_layout = QHBoxLayout()
    minor_layout = QVBoxLayout()
    main_widget.setLayout(main_layout)

    text_editor = QWidget() # text editor
    file_searcher = QPushButton('Open File') # add dynamic name instead of open file later
    token_view_widget = QWidget() # lexeme tokens view
    terminal = QWidget() # terminal
    identifier_view_widget = QWidget() # identifier
    
    # create text editor first
    text_input = text_edit(text_editor, file_manager, content_manager, win)
    
    token_table = create_token_view(token_view_widget, "Lexeme", "Classification")
    identifier_table = create_token_view(identifier_view_widget, "Identifier", "Value")

    execute_button = QPushButton("Execute", win) # execute button
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

    execute_button.clicked.connect(lambda: execute_code(content_manager, lexeme_manager, token_table, identifier_table)) # execs code, calls parser
    file_searcher.clicked.connect(lambda: file_open(text_input, file_manager, content_manager, file_searcher)) # prompts file search

    text_editor.setStyleSheet("background-color: #1E1E1E;")
    token_view_widget.setStyleSheet("background-color: #1A1A1A;")
    terminal.setStyleSheet("background-color: #1F1F1F;")
    identifier_view_widget.setStyleSheet("background-color: #1F1F1F;")

    # minor layout
    minor_layout.addWidget(file_searcher, 1)
    minor_layout.addWidget(text_editor,2)

    side_layout.addLayout(minor_layout,2)
    side_layout.addWidget(token_view_widget,1)
    side_layout.addWidget(identifier_view_widget,1)

    # vertical layout
    main_layout.addLayout(side_layout,2)
    main_layout.addWidget(execute_button,1)
    main_layout.addWidget(terminal,1)



def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(0, 0, 600, 400)
    win.setWindowTitle("WeLove124")

    layout(win)
    win.show()

    # exit
    sys.exit(app.exec_())


main()