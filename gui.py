"""
File Structure:
    gui.py       - Main application and UI layout
    widgets.py    - Custom widget classes
    utils.py      - Utility functions and managers
"""

import os
import sys
import platform
from pathlib import Path

from PyQt5.QtGui import QFont, QIcon, QFontDatabase, QKeySequence, QPixmap
from PyQt5.QtWidgets import (QWidget, QApplication, QMainWindow, QFileDialog,
                             QHBoxLayout, QVBoxLayout, QShortcut, QInputDialog, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QMenu, QTabWidget, QAction, 
                             QFrame)
from PyQt5.QtCore import Qt, QSize

# Import custom modules
from src.gui.widgets import InteractiveConsole, InterpreterWorker, CodeEditor
from src.gui.utils import (TextContentManager, FileManager, LexemeManager,
                  highlight_syntax, reset_zoom, update_token_view, 
                  update_symbol_table, COLORS, KEYWORD_COLORS)


# ============================================================================
# CONSTANTS
# ============================================================================

BASE_DIR = Path(__file__).parent.absolute()
IS_MACOS = platform.system() == "Darwin"

# ============================================================================
# TABLE WIDGETS
# ============================================================================

def create_table(parent_widget, header1, header2, font_family):
    """Create a styled table widget with two columns"""
    layout = QVBoxLayout()
    parent_widget.setLayout(layout)
    
    table = QTableWidget()
    table.setColumnCount(2)
    
    # Set headers
    header_item1 = QTableWidgetItem(header1)
    header_item2 = QTableWidgetItem(header2)
    header_item1.setTextAlignment(Qt.AlignCenter)
    header_item2.setTextAlignment(Qt.AlignCenter)
    table.setHorizontalHeaderItem(0, header_item1)
    table.setHorizontalHeaderItem(1, header_item2)
    
    # Configure table behavior
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    
    # Apply styling
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
    
    # Set font
    font = QFont(font_family, 10)
    table.setFont(font)
    table.horizontalHeader().setFont(font)
    
    layout.addWidget(table)
    layout.setContentsMargins(0, 0, 0, 0)
    
    return table


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def save_file(text_input, file_manager, parent_widget):
    """Save file to disk"""
    if file_manager.file_name is None:
        file_name, ok = QInputDialog.getText(
            parent_widget, 
            'Save File', 
            'Enter file name:'
        )
        
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
    
    # Update tab title
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
    
    # Create code editor
    text_input = CodeEditor(font_family)
    text_input.setPlaceholderText("Type your LOLCODE here...")
    
    # Set font
    font = QFont(font_family, 11)
    text_input.setFont(font)
    text_input.setStyleSheet(f"border: none; color: {COLORS['TEXT']};")
    
    layout.addWidget(text_input)
    
    # Setup keyboard shortcuts
    setup_editor_shortcuts(text_input, parent_window, font_family)
    
    # Enable syntax highlighting
    text_input.textChanged.connect(lambda: highlight_syntax(text_input))
    
    return text_input


def setup_editor_shortcuts(text_input, parent_window, font_family):
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


def create_new_tab(tab_widget, parent_window, font_family, file_name=None, content=None):
    """Create a new tab in the tab widget"""
    # Create managers
    file_manager = FileManager()
    content_manager = TextContentManager()
    
    # Create editor widget
    text_editor = QWidget()
    text_editor.setStyleSheet(f"background-color: {COLORS['EDITOR_BG']}; border: none; padding: 20px;")
    
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
    
    # Add tab
    tab_name = os.path.basename(file_name) if file_name else "Untitled"
    idx = tab_widget.addTab(text_editor, tab_name)
    
    # Create close button
    if IS_MACOS != 1:
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
        for worker in tab_widget.workers[:]:
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
        if hasattr(tab_widget, 'workers') and worker in tab_widget.workers:
            tab_widget.workers.remove(worker)
    
    worker.output_ready.connect(safe_write)
    worker.update_tokens.connect(safe_update_tokens)
    worker.update_symbols.connect(safe_update_symbols)
    worker.finished.connect(on_finished)
    
    # Store worker
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
    
    # Create initial tab
    create_new_tab(tab_widget, window, monospace_font)


def setup_global_shortcuts(window, tab_widget, lexeme_manager, token_table, symbol_table, console, font_family):
    """Setup application-wide keyboard shortcuts"""
    shortcuts = {
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
    try:
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
        try:
            font_id = QFontDatabase.addApplicationFont(str(BASE_DIR / "src/assets/font/inter.ttf"))
            mono_font_id = QFontDatabase.addApplicationFont(str(BASE_DIR / "src/assets/font/Consolas.ttf"))
            
            if font_id != -1:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            else:
                print("Warning: Could not load Inter font, using default")
                font_family = "Arial"
            
            if mono_font_id != -1:
                mono_font_family = QFontDatabase.applicationFontFamilies(mono_font_id)[0]
            else:
                print("Warning: Could not load Consolas font, using default monospace")
                mono_font_family = "Courier New"
        except Exception as e:
            print(f"Warning: Font loading error: {e}")
            font_family = "Arial"
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
            QScrollBar::handle:horizontal:hover {{ background-color: #4F4F4F; }}
            QScrollBar::handle:horizontal:pressed {{background-color: #565656;}}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{width: 0px;}}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none }}
        """)
        
        # Create main layout
        try:
            create_main_layout(window, font_family, mono_font_family)
        except Exception as e:
            print(f"Error creating main layout: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        # Show window
        window.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()