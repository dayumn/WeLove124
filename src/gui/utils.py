"""
Utility Functions for LOLCODE IDE
Contains helper functions for syntax highlighting, file operations, etc.
"""

from PyQt5.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt


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
# SYNTAX HIGHLIGHTING
# ============================================================================

def highlight_syntax(text_input):
    """Apply syntax highlighting to LOLCODE text"""
    COMMENT_START = "BTW"
    MULTI_COMMENT_START = "OBTW"
    MULTI_COMMENT_END = "TLDR"
    
    # Block signals to prevent recursion
    text_input.blockSignals(True)
    
    cursor = text_input.textCursor()
    current_pos = cursor.position()
    
    # Reset all text to default color
    cursor.select(QTextCursor.Document)
    default_fmt = QTextCharFormat()
    default_fmt.setForeground(QColor("#D4D4D4"))
    cursor.setCharFormat(default_fmt)
    
    # Highlight comments
    content = text_input.toPlainText()
    lines = content.split('\n')
    char_count = 0
    inside_multi_comment = False
    multi_comment_start = 0
    
    for line in lines:
        # Handle multiline comments
        if not inside_multi_comment:
            start_idx = line.find(MULTI_COMMENT_START)
            if start_idx != -1:
                inside_multi_comment = True
                multi_comment_start = char_count + start_idx
        
        if inside_multi_comment:
            end_idx = line.find(MULTI_COMMENT_END)
            if end_idx != -1:
                # Highlight from start to end of TLDR
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
        
        # Handle single-line comments
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
    
    # Highlight keywords (comments will override)
    for keyword, color in KEYWORD_COLORS.items():
        index = 0
        while index < len(content):
            index = content.find(keyword, index)
            if index == -1:
                break
            
            # Check if keyword is inside a comment
            line_start = content.rfind('\n', 0, index) + 1
            line_end = content.find('\n', index)
            if line_end == -1:
                line_end = len(content)
            line_text = content[line_start:line_end]
            comment_pos = line_text.find(COMMENT_START)
            
            # Only highlight if not in comment
            if comment_pos == -1 or (index - line_start) < comment_pos:
                cursor = text_input.textCursor()
                cursor.setPosition(index)
                cursor.setPosition(index + len(keyword), QTextCursor.KeepAnchor)
                
                keyword_fmt = QTextCharFormat()
                keyword_fmt.setForeground(QColor(color))
                cursor.setCharFormat(keyword_fmt)
            
            index += len(keyword)
    
    # Restore cursor position
    cursor = text_input.textCursor()
    cursor.setPosition(current_pos)
    text_input.setTextCursor(cursor)
    
    text_input.blockSignals(False)


def reset_zoom(text_input, default_size, font_family):
    """Reset editor zoom to default size"""
    font = QFont(font_family, default_size)
    text_input.setFont(font)


# ============================================================================
# TABLE OPERATIONS
# ============================================================================

def update_token_view(table, tokens):
    """Update token table with lexeme information"""
    if not tokens:
        print("Warning: No tokens to display")
        return
    
    table.setRowCount(0)
    
    for token in tokens:
        row_pos = table.rowCount()
        table.insertRow(row_pos)
        
        # Handle different token formats
        if isinstance(token, dict):
            lexeme = str(token.get('value', ''))
            category = str(token.get('category', ''))
        else:
            # Handle token objects with attributes
            lexeme = str(getattr(token, 'value', ''))
            category_obj = getattr(token, 'category', '')
            
            # Convert TokenType enum to string if needed
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
        
        # Set font size
        font = lexeme_item.font()
        font.setPointSize(9)
        lexeme_item.setFont(font)
        category_item.setFont(font)
        
        table.setItem(row_pos, 0, lexeme_item)
        table.setItem(row_pos, 1, category_item)


def update_symbol_table(table, symbol_table_obj):
    """Update symbol table with variable information"""
    table.setRowCount(0)
    
    # Type mapping for LOLCODE types
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
            
            # Set font size
            font = name_item.font()
            font.setPointSize(9)
            name_item.setFont(font)
            value_item.setFont(font)
            
            table.setItem(row_pos, 0, name_item)
            table.setItem(row_pos, 1, value_item)