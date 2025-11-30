import os
import sys
import queue
import time
import platform
import builtins
from pathlib import Path
from PyQt5.QtGui import (QFont, QKeySequence, QTextCursor, QTextCharFormat, 
                         QColor, QIcon, QFontDatabase, QPixmap, QPainter)
from PyQt5.QtWidgets import (QWidget, QApplication, QMainWindow, QFileDialog,
                             QHBoxLayout, QVBoxLayout, QTextEdit,
                             QShortcut, QInputDialog, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                             QMenu, QTabWidget, QAction, QFrame, QPlainTextEdit)
from PyQt5.QtCore import Qt, QThread, QSize, pyqtSignal
from src.lexer import tokenizer
from src.parser.parser import Parser
from src.interpreter.runtime import SymbolTable, Context
from src.interpreter.interpreter import Interpreter

# ============================================================================
# CONSTANTS
# ============================================================================
BASE_DIR = Path(__file__).parent.absolute()
IS_MACOS = platform.system() == "Darwin"
# Color scheme
COLORS = {
    'BACKGROUND': '#181818',
    'EDITOR_BG': '#1F1F1F',
    'TEXT': '#FAFAFA',
    'COMMENT': '#6A9955',
    'BORDER': '#393939',
    'ACCENT': '#007ACC',
    'SUCCESS': '#95E1D3',
    'INFO': '#4ECDC4',
    'ERROR': '#FF6B6B',
}

# Keyword colors for syntax highlighting
KEYWORD_COLORS = {
    "HAI": "#FF6B9D",
    "KTHXBYE": "#FF6B9D",
    "WAZZUP": "#FFA500",
    "BUHBYE": "#FFA500",
    "I HAS A": "#569CD6",
    "ITZ": "#569CD6",
    " R ": "#569CD6",
    "VISIBLE": "#C586C0",
    "GIMMEH": "#C586C0",
    "AN": "#D4D4D4",
    "NOOB": "#4EC9B0",
    "NUMBR": "#4EC9B0",
    "NUMBAR": "#4EC9B0",
    "YARN": "#4EC9B0",
    "TROOF": "#4EC9B0",
    "WIN": "#D7BA7D",
    "FAIL": "#D7BA7D",
}


# ============================================================================
# MANAGER CLASSES
# ============================================================================

class TextContentManager:
    """Manages text content persistence for a single file"""
    def __init__(self):
        self.saved_content = None


class FileManager:
    """Manages file names and paths for a single file"""
    def __init__(self):
        self.file_name = None


class LexemeManager:
    """Manages lexeme tokens (deprecated - kept for compatibility)"""
    def __init__(self):
        self.saved_lexemes = None


# ============================================================================
# INTERACTIVE CONSOLE WIDGET
# ============================================================================

class InteractiveConsole(QTextEdit):
    """
    Interactive console widget that handles both output display and user input.
    Thread-safe implementation for use with interpreter worker threads.
    """
    input_requested = pyqtSignal()
    
    def __init__(self, font_family):
        super().__init__()
        self.input_queue = queue.Queue()
        self.waiting_for_input = False
        self.input_start_pos = 0
        self.font_family = font_family
        self.input_requested.connect(self._request_input_slot)
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize console UI styling"""
        font = QFont(self.font_family, 11)
        self.setFont(font)
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['BACKGROUND']};
                color: {COLORS['TEXT']};
                border: none;
                padding: 20px;
                border-top: 1px solid {COLORS['BORDER']};   
            }}
        """)
        self.setReadOnly(True)
        self.setMinimumHeight(150)
    
    def write(self, text, color=None):
        """Write text to console with optional color"""
        if color is None:
            color = COLORS['TEXT']
            
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        
        cursor.insertText(text + "\n")
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
    
    def clear(self):
        """Clear console and reset input state"""
        super().clear()
        self.waiting_for_input = False
    
    def _request_input_slot(self):
        """Enable input mode (must be called from main thread)"""
        self.waiting_for_input = True
        self.input_start_pos = self.textCursor().position()
        self.setReadOnly(False)
        self.setFocus()
    
    def request_input(self):
        """Request input from user - thread-safe"""
        self.input_requested.emit()
    
    def keyPressEvent(self, event):
        """Handle keyboard input"""
        if not self.waiting_for_input:
            event.ignore()
            return
        
        cursor = self.textCursor()
        
        # prevent editing previous content
        if cursor.position() < self.input_start_pos:
            cursor.setPosition(self.input_start_pos)
            self.setTextCursor(cursor)
        
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # extract user input
            cursor.movePosition(QTextCursor.End)
            cursor.setPosition(self.input_start_pos, QTextCursor.KeepAnchor)
            user_input = cursor.selectedText()
            
            # move to end and add newline
            cursor.clearSelection()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText("\n")
            self.setTextCursor(cursor)
            
            # disable input mode
            self.waiting_for_input = False
            self.setReadOnly(True)
            
            # queue the input
            self.input_queue.put(user_input)
            event.accept()
            
        elif event.key() == Qt.Key_Backspace:
            if cursor.position() <= self.input_start_pos:
                event.ignore()
                return
            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
    
    def get_input(self, timeout=60):
        """
        Get input from user with timeout.
        Blocks while processing Qt events to keep UI responsive.
        """
        self.request_input()
        elapsed = 0
        
        while self.input_queue.empty() and elapsed < timeout:
            QApplication.processEvents()
            time.sleep(0.01)
            elapsed += 0.01
        
        if self.input_queue.empty():
            raise TimeoutError("Input timed out")
        
        return self.input_queue.get()


# ============================================================================
# INTERPRETER WORKER THREAD
# ============================================================================

class InterpreterWorker(QThread):
    """
    Worker thread for running LOLCODE interpreter without blocking GUI.
    Handles tokenization, parsing, and execution.
    """
    output_ready = pyqtSignal(str, str)  # (text, color)
    update_tokens = pyqtSignal(list)
    update_symbols = pyqtSignal(object)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, content, console_widget):
        super().__init__()
        self.content = content
        self.console_widget = console_widget
        self.tokens = None
        self.symbol_table_obj = None
        self._is_running = True
    
    def console_print(self, *args, **kwargs):
        """Custom print function that routes to console widget"""
        text = ' '.join(str(arg) for arg in args)
        self.output_ready.emit(text, COLORS['TEXT'])
    
    def stop(self):
        """Stop the worker thread"""
        self._is_running = False
        self.wait()
    
    def run(self):
        """Execute interpreter pipeline in worker thread"""
        try:
            # tokenization
            self.output_ready.emit("=== LOLCODE INTERPRETER ===", COLORS['INFO'])
            
            try:
                self.tokens = tokenizer.tokenize(self.content)
            except Exception as e:
                self.output_ready.emit(f"Tokenization Error: {str(e)}", COLORS['ERROR'])
                return
            
            if not self.tokens:
                self.output_ready.emit("Error: No tokens generated", COLORS['ERROR'])
                return
            
            self.output_ready.emit(
                f"Tokenization complete: {len(self.tokens)} tokens", 
                COLORS['SUCCESS']
            )
            self.update_tokens.emit(self.tokens)
            
            if not self._is_running:
                return
            
            # parsing
            try:
                parser = Parser(self.tokens)
                ast = parser.parse()
            except Exception as e:
                self.output_ready.emit(f"Parser Error: {str(e)}", COLORS['ERROR'])
                import traceback
                self.output_ready.emit(traceback.format_exc(), COLORS['ERROR'])
                return
            
            if hasattr(ast, 'error') and ast.error:
                error_msg = (ast.error.as_string() if hasattr(ast.error, 'as_string') 
                           else str(ast.error))
                self.output_ready.emit(f"Parse Error: {error_msg}", COLORS['ERROR'])
                return
            
            self.output_ready.emit("Parsing complete", COLORS['SUCCESS'])
            
            if not self._is_running:
                return
            
            # interpretation
            try:
                self.symbol_table_obj = SymbolTable()
                context = Context('<program>')
                context.symbol_table = self.symbol_table_obj
                
                interpreter = Interpreter()
                self.output_ready.emit("--- Program Output ---", COLORS['INFO'])
                
                # redirect I/O to console
                original_print = builtins.print
                original_input = builtins.input
                
                builtins.print = self.console_print
                builtins.input = lambda: self.console_widget.get_input()
                
                try:
                    result = interpreter.visit(ast.node, context)
                except Exception as e:
                    self.output_ready.emit(f"Runtime Error: {str(e)}", COLORS['ERROR'])
                    import traceback
                    self.output_ready.emit(traceback.format_exc(), COLORS['ERROR'])
                    return
                finally:
                    builtins.print = original_print
                    builtins.input = original_input
                
                # check for runtime errors
                if result and hasattr(result, 'error') and result.error:
                    error_msg = (result.error.as_string() if hasattr(result.error, 'as_string')
                               else str(result.error))
                    self.output_ready.emit(error_msg, COLORS['ERROR'])
                else:
                    self.output_ready.emit("\n=== Execution complete ===", COLORS['SUCCESS'])
                
                # update symbol table
                if self.symbol_table_obj:
                    self.update_symbols.emit(self.symbol_table_obj)
                    
            except Exception as e:
                self.output_ready.emit(f"Interpretation Error: {str(e)}", COLORS['ERROR'])
                import traceback
                self.output_ready.emit(traceback.format_exc(), COLORS['ERROR'])
                return
            
        except Exception as e:
            self.output_ready.emit(f"Unexpected Error: {str(e)}", COLORS['ERROR'])
            import traceback
            self.output_ready.emit(traceback.format_exc(), COLORS['ERROR'])
        finally:
            self.finished.emit()


# ============================================================================
# LINE NUMBER WIDGET
# ============================================================================

class LineNumberArea(QWidget):
    """Line number display area for code editor"""
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
    
    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


# ============================================================================
# CODE EDITOR WITH LINE NUMBERS
# ============================================================================

class CodeEditor(QPlainTextEdit):
    """Code editor with line numbers and syntax highlighting"""
    def __init__(self, font_family):
        super().__init__()
        self.font_family = font_family
        self.line_number_area = LineNumberArea(self)
        
        # connect signals
        self.document().blockCountChanged.connect(self.update_line_number_area_width)
        self.verticalScrollBar().valueChanged.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.update_line_number_area)
        self.textChanged.connect(self.update_line_number_area)
        
        self.update_line_number_area_width(0)
    
    def line_number_area_width(self):
        """Calculate width needed for line numbers"""
        digits = len(str(max(1, self.document().blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance('9') * digits
    
    def update_line_number_area_width(self, _):
        """Update viewport margins for line numbers"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self):
        """Trigger repaint of line number area"""
        rect = self.viewport().rect()
        self.line_number_area.update(
            0, rect.y(), 
            self.line_number_area.width(), 
            rect.height()
        )
    
    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            cr.left(), cr.top(),
            self.line_number_area_width(), cr.height()
        )
    
    def line_number_area_paint_event(self, event):
        """Paint line numbers"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(COLORS['EDITOR_BG']))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block)
                 .translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        font = QFont(self.font_family, 11)
        painter.setFont(font)
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#4A4A4A"))
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number
                )
            
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1


# ============================================================================
# SYNTAX HIGHLIGHTING
# ============================================================================

def highlight_syntax(text_input):
    """Apply syntax highlighting to LOLCODE text"""
    COMMENT_START = "BTW"
    MULTI_COMMENT_START = "OBTW"
    MULTI_COMMENT_END = "TLDR"
    
    # block signals to prevent recursion
    text_input.blockSignals(True)
    
    cursor = text_input.textCursor()
    current_pos = cursor.position()
    
    # reset all text to default color
    cursor.select(QTextCursor.Document)
    default_fmt = QTextCharFormat()
    default_fmt.setForeground(QColor("#D4D4D4"))
    cursor.setCharFormat(default_fmt)
    
    # highlight comments
    content = text_input.toPlainText()
    lines = content.split('\n')
    char_count = 0
    inside_multi_comment = False
    multi_comment_start = 0
    
    for line in lines:
        # handle multiline comments
        if not inside_multi_comment:
            start_idx = line.find(MULTI_COMMENT_START)
            if start_idx != -1:
                inside_multi_comment = True
                multi_comment_start = char_count + start_idx
        
        if inside_multi_comment:
            end_idx = line.find(MULTI_COMMENT_END)
            if end_idx != -1:
                # highlight from start to end of TLDR
                multi_comment_end = char_count + end_idx + len(MULTI_COMMENT_END)
                
                cursor = text_input.textCursor()
                cursor.setPosition(multi_comment_start)
                cursor.setPosition(multi_comment_end, QTextCursor.KeepAnchor)
                
                comment_fmt = QTextCharFormat()
                comment_fmt.setForeground(QColor(COLORS['COMMENT']))
                cursor.setCharFormat(comment_fmt)
                
                inside_multi_comment = False
            char_count += len(line) + 1
            continue
        
        # handle single-line comments
        comment_idx = line.find(COMMENT_START)
        if comment_idx != -1:
            start_pos = char_count + comment_idx
            end_pos = char_count + len(line)
            
            cursor = text_input.textCursor()
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
            
            comment_fmt = QTextCharFormat()
            comment_fmt.setForeground(QColor(COLORS['COMMENT']))
            cursor.setCharFormat(comment_fmt)
        
        char_count += len(line) + 1
    
    # highlight keywords (comments will override)
    for keyword, color in KEYWORD_COLORS.items():
        index = 0
        while index < len(content):
            index = content.find(keyword, index)
            if index == -1:
                break
            
            # check if keyword is inside a comment
            line_start = content.rfind('\n', 0, index) + 1
            line_end = content.find('\n', index)
            if line_end == -1:
                line_end = len(content)
            line_text = content[line_start:line_end]
            comment_pos = line_text.find(COMMENT_START)
            
            # only highlight if not in comment
            if comment_pos == -1 or (index - line_start) < comment_pos:
                cursor = text_input.textCursor()
                cursor.setPosition(index)
                cursor.setPosition(index + len(keyword), QTextCursor.KeepAnchor)
                
                keyword_fmt = QTextCharFormat()
                keyword_fmt.setForeground(QColor(color))
                cursor.setCharFormat(keyword_fmt)
            
            index += len(keyword)
    
    # restore cursor position
    cursor = text_input.textCursor()
    cursor.setPosition(current_pos)
    text_input.setTextCursor(cursor)
    
    text_input.blockSignals(False)


# ============================================================================
# TABLE WIDGETS
# ============================================================================

def create_table(parent_widget, header1, header2, font_family):
    """Create a styled table widget with two columns"""
    layout = QVBoxLayout()
    parent_widget.setLayout(layout)
    
    table = QTableWidget()
    table.setColumnCount(2)
    
    # set headers
    header_item1 = QTableWidgetItem(header1)
    header_item2 = QTableWidgetItem(header2)
    header_item1.setTextAlignment(Qt.AlignCenter)
    header_item2.setTextAlignment(Qt.AlignCenter)
    table.setHorizontalHeaderItem(0, header_item1)
    table.setHorizontalHeaderItem(1, header_item2)
    
    # configure table behavior
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    
    # apply styling
    table.setStyleSheet(f"""
        QTableWidget {{
            background-color: {COLORS['EDITOR_BG']};
            color: {COLORS['TEXT']};
            border: 1px solid {COLORS['BORDER']};
            gridline-color: none;
        }}
        QHeaderView::section {{
            background-color: {COLORS['EDITOR_BG']};
            color: {COLORS['TEXT']};
            border: none;
            border-bottom: 1px solid {COLORS['BORDER']};
            padding: 5px;
        }}
        QTableWidget::item {{
            padding: 5px;
            border: none;
            color: {COLORS['TEXT']};
        }}
        QTableCornerButton::section {{
            background-color: {COLORS['EDITOR_BG']};
            border: none;
        }}
    """)
    
    # set font
    font = QFont(font_family, 10)
    table.setFont(font)
    table.horizontalHeader().setFont(font)
    
    layout.addWidget(table)
    layout.setContentsMargins(0, 0, 0, 0)
    
    return table


def update_token_view(table, tokens):
    """Update token table with lexeme information"""
    if not tokens:
        print("Warning: No tokens to display")
        return
    
    table.setRowCount(0)
    
    for token in tokens:
        row_pos = table.rowCount()
        table.insertRow(row_pos)
        
        # handle different token formats
        if isinstance(token, dict):
            lexeme = str(token.get('value', ''))
            category = str(token.get('category', ''))
        else:
            # handle token objects with attributes
            lexeme = str(getattr(token, 'value', ''))
            category_obj = getattr(token, 'category', '')
            
            # convert TokenType enum to string if needed
            if hasattr(category_obj, 'name'):
                category = category_obj.name
            elif hasattr(category_obj, 'value'):
                category = str(category_obj.value)
            else:
                category = str(category_obj)
        
        lexeme_item = QTableWidgetItem(lexeme)
        category_item = QTableWidgetItem(category)
        lexeme_item.setTextAlignment(Qt.AlignCenter)
        category_item.setTextAlignment(Qt.AlignCenter)
        
        # set font size
        font = lexeme_item.font()
        font.setPointSize(9)
        lexeme_item.setFont(font)
        category_item.setFont(font)
        
        table.setItem(row_pos, 0, lexeme_item)
        table.setItem(row_pos, 1, category_item)


def update_symbol_table(table, symbol_table_obj):
    """Update symbol table with variable information"""
    table.setRowCount(0)
    
    # type mapping for LOLCODE types
    type_map = {
        'Number': lambda v: 'NUMBR' if isinstance(v.value, int) else 'NUMBAR',
        'String': lambda v: 'YARN',
        'Boolean': lambda v: 'TROOF',
        'Noob': lambda v: 'NOOB',
        'Function': lambda v: 'FUNCTION'
    }
    
    if symbol_table_obj and symbol_table_obj.symbols:
        for var_name, value in symbol_table_obj.symbols.items():
            row_pos = table.rowCount()
            table.insertRow(row_pos)
            
            type_name = type(value).__name__
            lolcode_type = type_map.get(type_name, lambda v: 'UNKNOWN')(value)
            display_value = f"{value} ({lolcode_type})"
            
            name_item = QTableWidgetItem(var_name)
            value_item = QTableWidgetItem(display_value)
            name_item.setTextAlignment(Qt.AlignCenter)
            value_item.setTextAlignment(Qt.AlignCenter)
            
            # set font size
            font = name_item.font()
            font.setPointSize(9)
            name_item.setFont(font)
            value_item.setFont(font)
            
            table.setItem(row_pos, 0, name_item)
            table.setItem(row_pos, 1, value_item)


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def save_file(text_input, file_manager, parent_widget):
    """Save file to disk"""
    if file_manager.file_name is None:
        file_name, ok = QInputDialog.getText(parent_widget, 'Save File', 'Enter file name:')

        if ok and file_name:
            if not file_name.endswith('.txt'):
                file_name += '.txt'
            file_manager.file_name = file_name
        else:
            print('Save cancelled')
            return None
    
    content = text_input.toPlainText()
    with open(file_manager.file_name, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"File saved: {file_manager.file_name}")
    
    return content


def save_and_store(text_input, file_manager, content_manager, parent_widget):
    """Save file and store content in memory"""
    content = save_file(text_input, file_manager, parent_widget)
    if content is not None:
        content_manager.saved_content = content


def open_file(tab_widget, parent_window, font_family):
    """Open file dialog and load file content into new tab"""
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getOpenFileName(
        None,
        "Select a File",
        "",
        "All Files (*);;Text Files (*.txt);;LOLCode Files (*.lol)",
        options=options
    )
    
    if file_name:
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                content = f.read()
            create_new_tab(tab_widget, parent_window, font_family, file_name, content)
            print(f"File opened: {file_name}")
        except Exception as e:
            print(f"Error opening file: {e}")


def save_current_tab(tab_widget, parent_window):
    """Save the currently active tab"""
    current_idx = tab_widget.currentIndex()
    if current_idx == -1:
        return
    
    current_tab = tab_widget.widget(current_idx)
    text_input = current_tab.property("text_input")
    file_manager = current_tab.property("file_manager")
    content_manager = current_tab.property("content_manager")
    
    save_and_store(text_input, file_manager, content_manager, parent_window)
    
    # update tab title
    if file_manager.file_name:
        tab_name = os.path.basename(file_manager.file_name)
        tab_widget.setTabText(current_idx, tab_name)


# ============================================================================
# TAB MANAGEMENT
# ============================================================================

def create_text_editor(parent_widget, file_manager, content_manager, 
                      parent_window, font_family):
    """Create text editor with all functionality"""
    layout = QVBoxLayout()
    parent_widget.setLayout(layout)
    parent_widget.setStyleSheet(
        f"background-color: {COLORS['EDITOR_BG']}; border: none;"
    )
    
    # create code editor
    text_input = CodeEditor(font_family)
    text_input.setPlaceholderText("Type your LOLCODE here...")
    
    # set font
    font = QFont(font_family, 11)
    text_input.setFont(font)
    text_input.setStyleSheet(f"border: none; color: {COLORS['TEXT']};")
    
    layout.addWidget(text_input)
    
    # setup keyboard shortcuts
    setup_editor_shortcuts(text_input, parent_window, tab_widget=None, font_family=font_family)
    
    # syntax highlighting
    text_input.textChanged.connect(lambda: highlight_syntax(text_input))
    
    return text_input


def setup_editor_shortcuts(text_input, parent_window, tab_widget, font_family):
    """Setup all keyboard shortcuts for the editor"""
    # Zoom shortcuts
    zoom_in_shortcut = QShortcut(QKeySequence.ZoomIn, text_input)
    zoom_out_shortcut = QShortcut(QKeySequence.ZoomOut, text_input)
    
    zoom_in_shortcut.activated.connect(text_input.zoomIn)
    zoom_out_shortcut.activated.connect(text_input.zoomOut)
    
    # Reset zoom
    if IS_MACOS:
        zoom_reset = QShortcut(QKeySequence("Meta+0"), text_input)
    else:
        zoom_reset = QShortcut(QKeySequence("Ctrl+0"), text_input)
    
    zoom_reset.activated.connect(
        lambda: reset_zoom(text_input, 11, font_family)
    )
    
    # Standard shortcuts 
    copy_shortcut = QShortcut(QKeySequence.Copy, text_input)
    copy_shortcut.activated.connect(text_input.copy)
    
    paste_shortcut = QShortcut(QKeySequence.Paste, text_input)
    paste_shortcut.activated.connect(text_input.paste)
    
    cut_shortcut = QShortcut(QKeySequence.Cut, text_input)
    cut_shortcut.activated.connect(text_input.cut)
    
    undo_shortcut = QShortcut(QKeySequence.Undo, text_input)
    undo_shortcut.activated.connect(text_input.undo)
    
    redo_shortcut = QShortcut(QKeySequence.Redo, text_input)
    redo_shortcut.activated.connect(text_input.redo)
    
    select_all_shortcut = QShortcut(QKeySequence.SelectAll, text_input)
    select_all_shortcut.activated.connect(text_input.selectAll)


def reset_zoom(text_input, default_size, font_family):
    """Reset editor zoom to default size"""
    font = QFont(font_family, default_size)
    text_input.setFont(font)


def create_new_tab(tab_widget, parent_window, font_family, file_name=None, content=None):
    """Create a new tab in the tab widget"""
    # create managers
    file_manager = FileManager()
    content_manager = TextContentManager()
    
    # create editor widget
    text_editor = QWidget()
    text_editor.setStyleSheet(
        f"background-color: {COLORS['EDITOR_BG']}; border: none; padding: 20px;"
    )
    
    # Create text input
    text_input = create_text_editor(
        text_editor, file_manager, content_manager, 
        parent_window, font_family
    )
    
    # Load content if provided
    if content:
        text_input.setPlainText(content)
        content_manager.saved_content = content
    if file_name:
        file_manager.file_name = file_name
    
    # Store properties
    text_editor.setProperty("file_manager", file_manager)
    text_editor.setProperty("content_manager", content_manager)
    text_editor.setProperty("text_input", text_input)
    
    # add tab
    tab_name = os.path.basename(file_name) if file_name else "Untitled"
    idx = tab_widget.addTab(text_editor, tab_name)
    
    # create close button

    # check if not mac to add close button
    if IS_MACOS != -1:
        close_btn = QPushButton()
        close_btn.setIcon(QIcon(str(BASE_DIR / 'src/assets/x.png')))
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
        close_btn.clicked.connect(lambda: tab_widget.removeTab(idx))
        tab_widget.tabBar().setTabButton(
            idx, tab_widget.tabBar().RightSide, close_btn
        )
    
    tab_widget.setCurrentWidget(text_editor)
    
    return text_editor


# ============================================================================
# CODE EXECUTION
# ============================================================================

def execute_code(tab_widget, lexeme_manager, token_table, 
                symbol_table, console_widget):
    """Execute LOLCODE in current tab"""
    current_idx = tab_widget.currentIndex()
    if current_idx == -1:
        console_widget.write("Error: No file open", COLORS['ERROR'])
        return
    
    current_tab = tab_widget.widget(current_idx)
    content_manager = current_tab.property("content_manager")
    
    if content_manager.saved_content is None:
        console_widget.write(
            "Error: Please save the file first (Ctrl+S or Cmd+S)", 
            COLORS['ERROR']
        )
        return
    
    # Clear console
    console_widget.clear()
    
    # Stop any existing workers
    if hasattr(tab_widget, 'workers'):
        for worker in tab_widget.workers[:]:  # Copy list to avoid modification during iteration
            if worker.isRunning():
                worker.stop()
                tab_widget.workers.remove(worker)
    
    # Create worker thread
    worker = InterpreterWorker(content_manager.saved_content, console_widget)
    
    # Connect signals with error handling
    def safe_write(text, color):
        try:
            console_widget.write(text, color)
        except Exception as e:
            print(f"Error writing to console: {e}")
    
    def safe_update_tokens(tokens):
        try:
            update_token_view(token_table, tokens)
        except Exception as e:
            print(f"Error updating tokens: {e}")
            console_widget.write(f"Error updating token view: {str(e)}", COLORS['ERROR'])
    
    def safe_update_symbols(sym_table):
        try:
            update_symbol_table(symbol_table, sym_table)
        except Exception as e:
            print(f"Error updating symbols: {e}")
            console_widget.write(f"Error updating symbol table: {str(e)}", COLORS['ERROR'])
    
    def on_finished():
        try:
            console_widget.write("=== Interpreter Finished ===", COLORS['SUCCESS'])
        except:
            pass
        # Clean up worker reference
        if hasattr(tab_widget, 'workers') and worker in tab_widget.workers:
            tab_widget.workers.remove(worker)
    
    worker.output_ready.connect(safe_write)
    worker.update_tokens.connect(safe_update_tokens)
    worker.update_symbols.connect(safe_update_symbols)
    worker.finished.connect(on_finished)
    
    # Store worker to prevent garbage collection
    if not hasattr(tab_widget, 'workers'):
        tab_widget.workers = []
    tab_widget.workers.append(worker)
    
    # Start execution
    try:
        worker.start()
    except Exception as e:
        console_widget.write(f"Error starting interpreter: {str(e)}", COLORS['ERROR'])
        if worker in tab_widget.workers:
            tab_widget.workers.remove(worker)


# ============================================================================
# MAIN UI LAYOUT
# ============================================================================

def create_main_layout(window, font_family, monospace_font):
    """Create the main application layout"""
    main_widget = QWidget()
    window.setCentralWidget(main_widget)
    
    # Data managers
    lexeme_manager = LexemeManager()
    
    # Main layout
    main_layout = QVBoxLayout()
    main_widget.setLayout(main_layout)
    
    # ========== TOP TOOLBAR ==========
    toolbar_layout = QHBoxLayout()
    
    # Menu button
    menu_btn = QPushButton()
    menu_btn.setFixedSize(25, 25)
    menu_btn.setIcon(QIcon(str(BASE_DIR / 'src/assets/hamburger.png')))
    menu_btn.setIconSize(QSize(25, 25))
    menu_btn.setFlat(True)
    
    # File menu
    menu = QMenu(window)
    new_file_action = QAction('New File', window)
    open_file_action = QAction('Open File', window)
    save_file_action = QAction('Save File', window)
    menu.addAction(new_file_action)
    menu.addAction(open_file_action)
    menu.addAction(save_file_action)
    
    # Execute button
    exec_btn = QPushButton()
    exec_btn.setFixedSize(25, 25)
    exec_btn.setIcon(QIcon(str(BASE_DIR / 'src/assets/play-button.png')))
    exec_btn.setIconSize(QSize(25, 25))
    exec_btn.setFlat(True)
    
    # Open file button
    file_icon = QLabel()
    file_icon.setFixedSize(15, 15)
    icon = QPixmap(str(BASE_DIR / 'src/assets/search.png'))
    icon = icon.scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    file_icon.setPixmap(icon)
    
    file_search_btn = QPushButton('Open File')
    file_search_btn.setFixedHeight(30)
    file_search_btn.setFont(QFont(font_family, 9))
    file_search_btn.setIcon(QIcon(file_icon.pixmap()))
    file_search_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {COLORS['EDITOR_BG']};
            color: #A2A2A2;
            border: 1px solid {COLORS['BORDER']};
            padding: 5px 10px;
            border-radius: 5px;
            max-width: 500px;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: #2A2A2A;
        }}
    """)
    
    # Toolbar layout
    toolbar_layout.addWidget(menu_btn, 0)
    toolbar_layout.addStretch(1)
    toolbar_layout.addWidget(file_search_btn, 0)
    toolbar_layout.addStretch(1)
    toolbar_layout.addWidget(exec_btn, 0)
    toolbar_layout.setContentsMargins(10, 10, 10, 0)
    
    # ========== TAB WIDGET ==========
    tab_widget = QTabWidget()
    tab_widget.setTabsClosable(True)
    tab_widget.setDocumentMode(True)
    tab_widget.setMovable(True)
    tab_widget.setFont(QFont(font_family, 9))
    
    # customize tab bar
    tab_bar = tab_widget.tabBar()
    tab_bar.setExpanding(False)
    tab_bar.setLayoutDirection(Qt.LeftToRight)

    
    tab_widget.setStyleSheet(f"""
         
        QTabWidget::pane {{
            border: none;
            background-color: {COLORS['EDITOR_BG']};
        }}
        QTabBar::tab {{
            background-color: #2D2D2D;
            color: #CCCCCC;
            padding: 8px 24px 8px 12px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        QTabBar::tab:selected {{
            background-color: {COLORS['EDITOR_BG']};
            color: {COLORS['TEXT']};
            border-bottom: 2px solid {COLORS['ACCENT']};
        }}
        QTabBar::tab:hover {{
            background-color: #3E3E3E;
        }}
    """)
    
    # ========== CONSOLE ==========
    console = InteractiveConsole(monospace_font)
    
    # ========== RIGHT PANEL (TABLES) ==========
    symbol_table_widget = QWidget()
    token_view_widget = QWidget()
    
    symbol_table = create_table(symbol_table_widget, "Identifier", "Value", font_family)
    token_table = create_table(token_view_widget, "Lexeme", "Classification", font_family)
    
    symbol_table_widget.setStyleSheet(
        f"background-color: {COLORS['EDITOR_BG']}; "
        f"border-right: 1px solid {COLORS['BORDER']}; border-radius: 7px;"
    )
    token_view_widget.setStyleSheet(
        f"background-color: #1A1A1A; "
        f"border-right: 1px solid {COLORS['BORDER']}; border-radius: 7px;"
    )
    
    right_panel_layout = QVBoxLayout()
    right_panel_layout.addWidget(symbol_table_widget, 1)
    right_panel_layout.addWidget(token_view_widget, 1)
    right_panel_layout.setContentsMargins(10, 15, 10, 15)
    right_panel_layout.setSpacing(20)
    
    # ========== MAIN CONTENT AREA ==========
    content_layout = QVBoxLayout()
    content_layout.addWidget(tab_widget, 3)
    content_layout.addWidget(console, 2)
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(0)
    
    # ========== HORIZONTAL SPLIT ==========
    container_frame = QFrame()
    container_frame.setStyleSheet(
        f"border-top: 1px solid {COLORS['BORDER']}; "
        f"border-bottom: 1px solid {COLORS['BORDER']}; "
        f"border-right: 1px solid {COLORS['BORDER']};"
    )
    
    container_layout = QHBoxLayout()
    container_layout.addLayout(content_layout, 3)
    container_layout.addLayout(right_panel_layout, 1)
    container_layout.setContentsMargins(0, 0, 0, 0)
    container_frame.setLayout(container_layout)
    
    # ========== ASSEMBLE MAIN LAYOUT ==========
    main_layout.addLayout(toolbar_layout, 0)
    main_layout.addWidget(container_frame)
    main_layout.setContentsMargins(0, 0, 0, 0)
    
    # ========== CONNECT SIGNALS ==========
    new_file_action.triggered.connect(
        lambda: create_new_tab(tab_widget, window, monospace_font)
    )
    open_file_action.triggered.connect(
        lambda: open_file(tab_widget, window, monospace_font)
    )
    save_file_action.triggered.connect(
        lambda: save_current_tab(tab_widget, window)
    )
    
    menu_btn.clicked.connect(
        lambda: menu.exec_(menu_btn.mapToGlobal(menu_btn.rect().bottomLeft()))
    )
    exec_btn.clicked.connect(
        lambda: execute_code(tab_widget, lexeme_manager, token_table, 
                           symbol_table, console)
    )
    file_search_btn.clicked.connect(
        lambda: open_file(tab_widget, window, monospace_font)
    )
    
    # ========== GLOBAL SHORTCUTS ==========
    setup_global_shortcuts(window, tab_widget, lexeme_manager, 
                          token_table, symbol_table, console, monospace_font)
    
    # create initial tab
    create_new_tab(tab_widget, window, monospace_font)


def setup_global_shortcuts(window, tab_widget, lexeme_manager, 
                          token_table, symbol_table, console, font_family):
    """Setup application-wide keyboard shortcuts"""
    shortcuts = {
        # File operations
        'Ctrl+N': lambda: create_new_tab(tab_widget, window, font_family),
        'Ctrl+O': lambda: open_file(tab_widget, window, font_family),
        'Ctrl+S': lambda: save_current_tab(tab_widget, window),
        'Ctrl+R': lambda: execute_code(tab_widget, lexeme_manager, 
                                      token_table, symbol_table, console),
    }
    
    # Add macOS shortcuts
    if IS_MACOS:
        mac_shortcuts = {
            'Meta+N': lambda: create_new_tab(tab_widget, window, font_family),
            'Meta+O': lambda: open_file(tab_widget, window, font_family),
            'Meta+S': lambda: save_current_tab(tab_widget, window),
            'Meta+R': lambda: execute_code(tab_widget, lexeme_manager,
                                         token_table, symbol_table, console),
        }
        shortcuts.update(mac_shortcuts)
    
    # Create shortcuts
    for key_seq, func in shortcuts.items():
        shortcut = QShortcut(QKeySequence(key_seq), window)
        shortcut.activated.connect(func)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    app = QApplication(sys.argv)
    window = QMainWindow()
        
    # Set window properties
    try:
        icon_path = BASE_DIR / 'src/assets/lolcode.png'
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
    except Exception as e:
        print(f"Warning: Could not load icon: {e}")
    
    window.setGeometry(100, 100, 1200, 800)
    window.setWindowTitle("WeLove124 - LOLCODE IDE")
    
    # Load custom fonts
    font_id = QFontDatabase.addApplicationFont(str(BASE_DIR / "src/assets/font/inter.ttf"))
    mono_font_id = QFontDatabase.addApplicationFont(str(BASE_DIR / "src/assets/font/Consolas.ttf"))
    
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    else:
        print("ERROR: Could not load Inter font, using default")
        font_family = "Arial"
    
    if mono_font_id != -1:
        mono_font_family = QFontDatabase.applicationFontFamilies(mono_font_id)[0]
    else:
        print("ERROR: Could not load Consolas font, using default monospace")
        mono_font_family = "Courier New"
 
    # Apply global stylesheet
    window.setStyleSheet(f"""
        QMainWindow {{
            background-color: {COLORS['BACKGROUND']};
            color: {COLORS['TEXT']};
        }}
        QScrollBar:vertical {{
            background-color: {COLORS['EDITOR_BG']};
            width: 14px;
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background-color: #424242;
            min-height: 30px;
            border-radius: 7px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: #4F4F4F;
        }}
        QScrollBar::handle:vertical:pressed {{
            background-color: #565656;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        QScrollBar:horizontal {{
            background-color: {COLORS['EDITOR_BG']};
            height: 14px;
            border: none;
        }}
        QScrollBar::handle:horizontal {{
            background-color: #424242;
            min-width: 30px;
            border-radius: 7px;
            margin: 2px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: #4F4F4F;
        }}
        QScrollBar::handle:horizontal:pressed {{
            background-color: #565656;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
    """)
    
    # Create main layout
    create_main_layout(window, font_family, mono_font_family)
    
    # Show window
    window.show()
    
    sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()