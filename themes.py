"""Theme definitions and application for NotepadPlus."""

from dataclasses import dataclass, field
from typing import Dict
from PyQt5.QtGui import QColor


@dataclass
class Theme:
    name: str
    editor_bg: str
    editor_fg: str
    gutter_bg: str
    gutter_fg: str
    caret_color: str
    caret_line_bg: str
    selection_bg: str
    selection_fg: str
    margin_bg: str
    fold_margin_bg: str
    fold_marker_fg: str
    fold_marker_bg: str
    brace_match_bg: str
    brace_match_fg: str
    edge_color: str
    whitespace_fg: str
    # Lexer token colors
    keyword_fg: str = "#0000FF"
    string_fg: str = "#008000"
    comment_fg: str = "#808080"
    number_fg: str = "#FF8000"
    operator_fg: str = "#000000"
    identifier_fg: str = "#000000"
    preprocessor_fg: str = "#804000"
    class_name_fg: str = "#0000FF"
    function_fg: str = "#000080"
    # UI colors
    tab_bar_bg: str = "#E0E0E0"
    status_bar_bg: str = "#E0E0E0"
    status_bar_fg: str = "#000000"
    menu_bg: str = "#F0F0F0"
    menu_fg: str = "#000000"


THEMES: Dict[str, Theme] = {
    "Default": Theme(
        name="Default",
        editor_bg="#FFFFFF",
        editor_fg="#000000",
        gutter_bg="#E4E4E4",
        gutter_fg="#2B91AF",
        caret_color="#000000",
        caret_line_bg="#FFFCD5",
        selection_bg="#3399FF",
        selection_fg="#FFFFFF",
        margin_bg="#E4E4E4",
        fold_margin_bg="#F0F0F0",
        fold_marker_fg="#808080",
        fold_marker_bg="#FFFFFF",
        brace_match_bg="#80FF00",
        brace_match_fg="#FF0000",
        edge_color="#D0D0D0",
        whitespace_fg="#C0C0C0",
        keyword_fg="#0000FF",
        string_fg="#008000",
        comment_fg="#808080",
        number_fg="#FF8000",
        operator_fg="#000000",
        identifier_fg="#000000",
        preprocessor_fg="#804000",
        class_name_fg="#2B91AF",
        function_fg="#000080",
        tab_bar_bg="#E0E0E0",
        status_bar_bg="#E0E0E0",
        status_bar_fg="#000000",
    ),
    "Dark": Theme(
        name="Dark",
        editor_bg="#1E1E1E",
        editor_fg="#D4D4D4",
        gutter_bg="#1E1E1E",
        gutter_fg="#858585",
        caret_color="#AEAFAD",
        caret_line_bg="#2A2A2A",
        selection_bg="#264F78",
        selection_fg="#FFFFFF",
        margin_bg="#1E1E1E",
        fold_margin_bg="#252526",
        fold_marker_fg="#C5C5C5",
        fold_marker_bg="#2D2D2D",
        brace_match_bg="#0D4441",
        brace_match_fg="#DCDCAA",
        edge_color="#404040",
        whitespace_fg="#404040",
        keyword_fg="#569CD6",
        string_fg="#CE9178",
        comment_fg="#6A9955",
        number_fg="#B5CEA8",
        operator_fg="#D4D4D4",
        identifier_fg="#9CDCFE",
        preprocessor_fg="#C586C0",
        class_name_fg="#4EC9B0",
        function_fg="#DCDCAA",
        tab_bar_bg="#252526",
        status_bar_bg="#007ACC",
        status_bar_fg="#FFFFFF",
        menu_bg="#2D2D2D",
        menu_fg="#D4D4D4",
    ),
    "Monokai": Theme(
        name="Monokai",
        editor_bg="#272822",
        editor_fg="#F8F8F2",
        gutter_bg="#272822",
        gutter_fg="#90908A",
        caret_color="#F8F8F0",
        caret_line_bg="#3E3D32",
        selection_bg="#49483E",
        selection_fg="#F8F8F2",
        margin_bg="#272822",
        fold_margin_bg="#2D2E27",
        fold_marker_fg="#90908A",
        fold_marker_bg="#3E3D32",
        brace_match_bg="#49483E",
        brace_match_fg="#E6DB74",
        edge_color="#49483E",
        whitespace_fg="#49483E",
        keyword_fg="#F92672",
        string_fg="#E6DB74",
        comment_fg="#75715E",
        number_fg="#AE81FF",
        operator_fg="#F92672",
        identifier_fg="#F8F8F2",
        preprocessor_fg="#F92672",
        class_name_fg="#A6E22E",
        function_fg="#66D9EF",
        tab_bar_bg="#1E1F1C",
        status_bar_bg="#414339",
        status_bar_fg="#F8F8F2",
        menu_bg="#2D2E27",
        menu_fg="#F8F8F2",
    ),
    "Solarized Dark": Theme(
        name="Solarized Dark",
        editor_bg="#002B36",
        editor_fg="#839496",
        gutter_bg="#002B36",
        gutter_fg="#586E75",
        caret_color="#839496",
        caret_line_bg="#073642",
        selection_bg="#073642",
        selection_fg="#93A1A1",
        margin_bg="#002B36",
        fold_margin_bg="#00303B",
        fold_marker_fg="#586E75",
        fold_marker_bg="#073642",
        brace_match_bg="#073642",
        brace_match_fg="#B58900",
        edge_color="#073642",
        whitespace_fg="#073642",
        keyword_fg="#859900",
        string_fg="#2AA198",
        comment_fg="#586E75",
        number_fg="#D33682",
        operator_fg="#839496",
        identifier_fg="#268BD2",
        preprocessor_fg="#CB4B16",
        class_name_fg="#B58900",
        function_fg="#268BD2",
        tab_bar_bg="#073642",
        status_bar_bg="#073642",
        status_bar_fg="#839496",
        menu_bg="#002B36",
        menu_fg="#839496",
    ),
    "Solarized Light": Theme(
        name="Solarized Light",
        editor_bg="#FDF6E3",
        editor_fg="#657B83",
        gutter_bg="#FDF6E3",
        gutter_fg="#93A1A1",
        caret_color="#657B83",
        caret_line_bg="#EEE8D5",
        selection_bg="#EEE8D5",
        selection_fg="#586E75",
        margin_bg="#FDF6E3",
        fold_margin_bg="#F5EFDC",
        fold_marker_fg="#93A1A1",
        fold_marker_bg="#EEE8D5",
        brace_match_bg="#EEE8D5",
        brace_match_fg="#B58900",
        edge_color="#EEE8D5",
        whitespace_fg="#EEE8D5",
        keyword_fg="#859900",
        string_fg="#2AA198",
        comment_fg="#93A1A1",
        number_fg="#D33682",
        operator_fg="#657B83",
        identifier_fg="#268BD2",
        preprocessor_fg="#CB4B16",
        class_name_fg="#B58900",
        function_fg="#268BD2",
        tab_bar_bg="#EEE8D5",
        status_bar_bg="#EEE8D5",
        status_bar_fg="#657B83",
        menu_bg="#FDF6E3",
        menu_fg="#657B83",
    ),
}


def get_theme(name):
    """Get a theme by name, defaulting to Dark."""
    return THEMES.get(name, THEMES["Dark"])


def get_theme_names():
    """Return list of available theme names."""
    return list(THEMES.keys())


def apply_theme_to_editor(editor, theme):
    """Apply a theme's colors to a QScintilla editor widget."""
    from PyQt5.Qsci import QsciScintilla

    editor.setColor(QColor(theme.editor_fg))
    editor.setPaper(QColor(theme.editor_bg))
    editor.setCaretForegroundColor(QColor(theme.caret_color))
    editor.setCaretLineBackgroundColor(QColor(theme.caret_line_bg))
    editor.setCaretLineVisible(True)

    editor.setSelectionBackgroundColor(QColor(theme.selection_bg))
    editor.setSelectionForegroundColor(QColor(theme.selection_fg))

    # Line number margin
    editor.setMarginsBackgroundColor(QColor(theme.gutter_bg))
    editor.setMarginsForegroundColor(QColor(theme.gutter_fg))

    # Fold margin
    editor.setFoldMarginColors(QColor(theme.fold_margin_bg), QColor(theme.fold_margin_bg))

    # Brace matching
    editor.setMatchedBraceBackgroundColor(QColor(theme.brace_match_bg))
    editor.setMatchedBraceForegroundColor(QColor(theme.brace_match_fg))
    editor.setUnmatchedBraceBackgroundColor(QColor("#FF0000"))
    editor.setUnmatchedBraceForegroundColor(QColor("#FFFFFF"))

    # Edge line
    editor.setEdgeColor(QColor(theme.edge_color))

    # Whitespace
    editor.setWhitespaceForegroundColor(QColor(theme.whitespace_fg))


def apply_theme_to_lexer(lexer, theme):
    """Apply theme colors to a lexer's token styles."""
    from PyQt5.QtGui import QFont

    if lexer is None:
        return

    # Default style
    lexer.setDefaultColor(QColor(theme.editor_fg))
    lexer.setDefaultPaper(QColor(theme.editor_bg))

    # Set paper for all styles (up to 128 possible styles)
    for style_num in range(128):
        lexer.setPaper(QColor(theme.editor_bg), style_num)

    # Common token mappings - most lexers use similar style numbers
    # We use keyword(), comment(), string() etc. methods where available
    lexer_class_name = type(lexer).__name__

    # Apply colors using description-based approach
    for style_num in range(128):
        desc = ""
        try:
            desc = lexer.description(style_num).lower()
        except Exception:
            continue
        if not desc:
            continue

        color = None
        if "keyword" in desc:
            color = theme.keyword_fg
        elif "comment" in desc:
            color = theme.comment_fg
        elif "string" in desc or "literal" in desc:
            color = theme.string_fg
        elif "number" in desc:
            color = theme.number_fg
        elif "operator" in desc:
            color = theme.operator_fg
        elif "preprocessor" in desc or "decorator" in desc:
            color = theme.preprocessor_fg
        elif "class" in desc or "type" in desc:
            color = theme.class_name_fg
        elif "function" in desc or "method" in desc:
            color = theme.function_fg
        elif "identifier" in desc:
            color = theme.identifier_fg
        elif "default" in desc:
            color = theme.editor_fg

        if color:
            lexer.setColor(QColor(color), style_num)


def get_app_stylesheet(theme):
    """Generate a Qt stylesheet for the application based on theme."""
    return f"""
        QMainWindow {{
            background-color: {theme.editor_bg};
        }}
        QMenuBar {{
            background-color: {theme.menu_bg};
            color: {theme.menu_fg};
            border-bottom: 1px solid {theme.edge_color};
        }}
        QMenuBar::item:selected {{
            background-color: {theme.selection_bg};
            color: {theme.selection_fg};
        }}
        QMenu {{
            background-color: {theme.menu_bg};
            color: {theme.menu_fg};
            border: 1px solid {theme.edge_color};
        }}
        QMenu::item:selected {{
            background-color: {theme.selection_bg};
            color: {theme.selection_fg};
        }}
        QMenu::separator {{
            height: 1px;
            background-color: {theme.edge_color};
        }}
        QTabWidget::pane {{
            border: 1px solid {theme.edge_color};
        }}
        QTabBar {{
            background-color: {theme.tab_bar_bg};
        }}
        QTabBar::tab {{
            background-color: {theme.tab_bar_bg};
            color: {theme.editor_fg};
            padding: 6px 14px;
            border: 1px solid {theme.edge_color};
            border-bottom: none;
            margin-right: 1px;
        }}
        QTabBar::tab:selected {{
            background-color: {theme.editor_bg};
            color: {theme.editor_fg};
        }}
        QTabBar::tab:hover {{
            background-color: {theme.selection_bg};
        }}
        QStatusBar {{
            background-color: {theme.status_bar_bg};
            color: {theme.status_bar_fg};
            border-top: 1px solid {theme.edge_color};
        }}
        QStatusBar QLabel {{
            color: {theme.status_bar_fg};
            padding: 0 8px;
        }}
        QToolBar {{
            background-color: {theme.tab_bar_bg};
            border-bottom: 1px solid {theme.edge_color};
            spacing: 2px;
            padding: 2px;
        }}
        QToolButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 3px;
            padding: 3px;
            color: {theme.editor_fg};
        }}
        QToolButton:hover {{
            background-color: {theme.selection_bg};
            border: 1px solid {theme.edge_color};
        }}
        QToolButton:pressed {{
            background-color: {theme.caret_line_bg};
        }}
        QDialog {{
            background-color: {theme.menu_bg};
            color: {theme.menu_fg};
        }}
        QLabel {{
            color: {theme.menu_fg};
        }}
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {theme.editor_bg};
            color: {theme.editor_fg};
            border: 1px solid {theme.edge_color};
            padding: 3px;
        }}
        QCheckBox {{
            color: {theme.menu_fg};
        }}
        QPushButton {{
            background-color: {theme.tab_bar_bg};
            color: {theme.editor_fg};
            border: 1px solid {theme.edge_color};
            padding: 5px 15px;
            border-radius: 3px;
        }}
        QPushButton:hover {{
            background-color: {theme.selection_bg};
            color: {theme.selection_fg};
        }}
        QPushButton:pressed {{
            background-color: {theme.caret_line_bg};
        }}
        QComboBox {{
            background-color: {theme.editor_bg};
            color: {theme.editor_fg};
            border: 1px solid {theme.edge_color};
            padding: 3px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {theme.menu_bg};
            color: {theme.menu_fg};
            selection-background-color: {theme.selection_bg};
            selection-color: {theme.selection_fg};
        }}
        QSpinBox {{
            background-color: {theme.editor_bg};
            color: {theme.editor_fg};
            border: 1px solid {theme.edge_color};
        }}
        QGroupBox {{
            color: {theme.menu_fg};
            border: 1px solid {theme.edge_color};
            margin-top: 6px;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            padding: 0 5px;
        }}
        QListWidget {{
            background-color: {theme.editor_bg};
            color: {theme.editor_fg};
            border: 1px solid {theme.edge_color};
        }}
        QListWidget::item:selected {{
            background-color: {theme.selection_bg};
            color: {theme.selection_fg};
        }}
        QTreeWidget {{
            background-color: {theme.editor_bg};
            color: {theme.editor_fg};
            border: 1px solid {theme.edge_color};
        }}
        QTreeWidget::item:selected {{
            background-color: {theme.selection_bg};
            color: {theme.selection_fg};
        }}
        QScrollBar:vertical {{
            background-color: {theme.tab_bar_bg};
            width: 14px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {theme.fold_marker_fg};
            min-height: 20px;
            border-radius: 3px;
            margin: 2px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background-color: {theme.tab_bar_bg};
            height: 14px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {theme.fold_marker_fg};
            min-width: 20px;
            border-radius: 3px;
            margin: 2px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
    """
