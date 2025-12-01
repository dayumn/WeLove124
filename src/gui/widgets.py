"""
UI Widget Classes for LOLCODE IDE
Contains all custom widget implementations
"""

import queue
import time
import builtins

from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QPainter
from PyQt5.QtWidgets import QWidget, QTextEdit, QPlainTextEdit, QApplication
from PyQt5.QtCore import Qt, QThread, QSize, pyqtSignal

from src.lexer import tokenizer
from src.parser.parser import Parser
from src.interpreter.runtime import SymbolTable, Context
from src.interpreter.interpreter import Interpreter


# ============================================================================
# CONSTANTS
# ============================================================================

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
    
    def _request_input_slot(self): # flag once toggled, toggle waiting for input
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
        
        # Prevent editing previous content
        if cursor.position() < self.input_start_pos:
            cursor.setPosition(self.input_start_pos)
            self.setTextCursor(cursor)
        
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Extract user input
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
            
            # Queue the input
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
            # Tokenization
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
            
            # Parsing
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
            
            # Interpretation
            try:
                self.symbol_table_obj = SymbolTable()
                context = Context('<program>')
                context.symbol_table = self.symbol_table_obj
                
                interpreter = Interpreter()
                self.output_ready.emit("--- Program Output ---", COLORS['INFO'])
                
                # Redirect I/O to console
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
                
                # Check for runtime errors
                if result and hasattr(result, 'error') and result.error:
                    error_msg = (result.error.as_string() if hasattr(result.error, 'as_string')
                               else str(result.error))
                    self.output_ready.emit(error_msg, COLORS['ERROR'])
                else:
                    self.output_ready.emit("\n=== Execution complete ===", COLORS['SUCCESS'])
                
                # Update symbol table
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
        
        # Connect signals
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