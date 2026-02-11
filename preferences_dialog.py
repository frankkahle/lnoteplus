"""Preferences/settings dialog for NotepadPlus."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QFormLayout,
    QLabel,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QPushButton,
    QFontComboBox,
    QGroupBox,
    QDialogButtonBox,
)
from PyQt5.QtGui import QFontDatabase
from themes import get_theme_names


class PreferencesDialog(QDialog):
    """Application preferences dialog."""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._changes = {}

        self.setWindowTitle("Preferences")
        self.setMinimumSize(500, 450)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._build_ui()
        self._load_current_settings()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        # General tab
        general = QWidget()
        self._build_general_tab(general)
        self._tabs.addTab(general, "General")

        # Appearance tab
        appearance = QWidget()
        self._build_appearance_tab(appearance)
        self._tabs.addTab(appearance, "Appearance")

        # File tab
        file_tab = QWidget()
        self._build_file_tab(file_tab)
        self._tabs.addTab(file_tab, "File")

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Apply).clicked.connect(self._apply)
        layout.addWidget(buttons)

    def _build_general_tab(self, parent):
        layout = QVBoxLayout(parent)

        # Editor settings
        editor_group = QGroupBox("Editor")
        form = QFormLayout(editor_group)

        self._tab_size = QSpinBox()
        self._tab_size.setRange(1, 16)
        form.addRow("Tab size:", self._tab_size)

        self._use_tabs = QCheckBox("Use tabs instead of spaces")
        form.addRow(self._use_tabs)

        self._auto_indent = QCheckBox("Auto-indent")
        form.addRow(self._auto_indent)

        self._word_wrap = QCheckBox("Word wrap by default")
        form.addRow(self._word_wrap)

        self._show_whitespace = QCheckBox("Show whitespace")
        form.addRow(self._show_whitespace)

        self._highlight_line = QCheckBox("Highlight current line")
        form.addRow(self._highlight_line)

        self._brace_matching = QCheckBox("Brace matching")
        form.addRow(self._brace_matching)

        self._show_line_numbers = QCheckBox("Show line numbers")
        form.addRow(self._show_line_numbers)

        self._show_folding = QCheckBox("Show code folding")
        form.addRow(self._show_folding)

        layout.addWidget(editor_group)

        # Edge line
        edge_group = QGroupBox("Edge Line")
        edge_form = QFormLayout(edge_group)

        self._show_edge = QCheckBox("Show edge line")
        edge_form.addRow(self._show_edge)

        self._edge_column = QSpinBox()
        self._edge_column.setRange(1, 500)
        edge_form.addRow("Column:", self._edge_column)

        layout.addWidget(edge_group)

        # Encoding
        enc_group = QGroupBox("Default Encoding")
        enc_form = QFormLayout(enc_group)

        self._encoding = QComboBox()
        self._encoding.addItems(["utf-8", "utf-8-sig", "utf-16", "latin-1", "ascii"])
        enc_form.addRow("Encoding:", self._encoding)

        self._eol_mode = QComboBox()
        self._eol_mode.addItems(["LF", "CRLF", "CR"])
        enc_form.addRow("EOL mode:", self._eol_mode)

        layout.addWidget(enc_group)
        layout.addStretch()

    def _build_appearance_tab(self, parent):
        layout = QVBoxLayout(parent)

        # Theme
        theme_group = QGroupBox("Theme")
        theme_form = QFormLayout(theme_group)

        self._theme = QComboBox()
        self._theme.addItems(get_theme_names())
        theme_form.addRow("Theme:", self._theme)

        layout.addWidget(theme_group)

        # Font
        font_group = QGroupBox("Font")
        font_form = QFormLayout(font_group)

        self._font_family = QFontComboBox()
        self._font_family.setFontFilters(QFontComboBox.MonospacedFonts)
        font_form.addRow("Font:", self._font_family)

        self._font_size = QSpinBox()
        self._font_size.setRange(6, 72)
        font_form.addRow("Size:", self._font_size)

        layout.addWidget(font_group)
        layout.addStretch()

    def _build_file_tab(self, parent):
        layout = QVBoxLayout(parent)

        session_group = QGroupBox("Session")
        session_form = QFormLayout(session_group)

        self._auto_save_session = QCheckBox("Auto-save session on exit")
        session_form.addRow(self._auto_save_session)

        self._restore_session = QCheckBox("Restore session on startup")
        session_form.addRow(self._restore_session)

        layout.addWidget(session_group)

        recent_group = QGroupBox("Recent Files")
        recent_form = QFormLayout(recent_group)

        self._max_recent = QSpinBox()
        self._max_recent.setRange(1, 50)
        recent_form.addRow("Max recent files:", self._max_recent)

        layout.addWidget(recent_group)
        layout.addStretch()

    def _load_current_settings(self):
        """Populate UI from current settings."""
        s = self._settings
        self._tab_size.setValue(s.get("tab_size", 4))
        self._use_tabs.setChecked(s.get("use_tabs", False))
        self._auto_indent.setChecked(s.get("auto_indent", True))
        self._word_wrap.setChecked(s.get("word_wrap", False))
        self._show_whitespace.setChecked(s.get("show_whitespace", False))
        self._highlight_line.setChecked(s.get("highlight_current_line", True))
        self._brace_matching.setChecked(s.get("brace_matching", True))
        self._show_line_numbers.setChecked(s.get("show_line_numbers", True))
        self._show_folding.setChecked(s.get("show_code_folding", True))
        self._show_edge.setChecked(s.get("show_edge_line", False))
        self._edge_column.setValue(s.get("edge_column", 80))

        # Encoding
        enc = s.get("default_encoding", "utf-8")
        idx = self._encoding.findText(enc)
        if idx >= 0:
            self._encoding.setCurrentIndex(idx)

        eol = s.get("default_eol", "LF")
        idx = self._eol_mode.findText(eol)
        if idx >= 0:
            self._eol_mode.setCurrentIndex(idx)

        # Theme
        theme = s.get("theme", "Dark")
        idx = self._theme.findText(theme)
        if idx >= 0:
            self._theme.setCurrentIndex(idx)

        # Font
        self._font_family.setCurrentFont(
            __import__("PyQt5.QtGui", fromlist=["QFont"]).QFont(
                s.get("font_family", "Consolas")
            )
        )
        self._font_size.setValue(s.get("font_size", 11))

        # Session
        self._auto_save_session.setChecked(s.get("auto_save_session", True))
        self._restore_session.setChecked(s.get("restore_session", True))
        self._max_recent.setValue(s.get("max_recent_files", 15))

    def _collect_changes(self):
        """Collect all changed settings."""
        changes = {}
        s = self._settings

        mappings = [
            ("tab_size", self._tab_size.value()),
            ("use_tabs", self._use_tabs.isChecked()),
            ("auto_indent", self._auto_indent.isChecked()),
            ("word_wrap", self._word_wrap.isChecked()),
            ("show_whitespace", self._show_whitespace.isChecked()),
            ("highlight_current_line", self._highlight_line.isChecked()),
            ("brace_matching", self._brace_matching.isChecked()),
            ("show_line_numbers", self._show_line_numbers.isChecked()),
            ("show_code_folding", self._show_folding.isChecked()),
            ("show_edge_line", self._show_edge.isChecked()),
            ("edge_column", self._edge_column.value()),
            ("default_encoding", self._encoding.currentText()),
            ("default_eol", self._eol_mode.currentText()),
            ("theme", self._theme.currentText()),
            ("font_family", self._font_family.currentFont().family()),
            ("font_size", self._font_size.value()),
            ("auto_save_session", self._auto_save_session.isChecked()),
            ("restore_session", self._restore_session.isChecked()),
            ("max_recent_files", self._max_recent.value()),
        ]

        for key, value in mappings:
            if s.get(key) != value:
                changes[key] = value

        return changes

    def _apply(self):
        """Apply changes without closing."""
        changes = self._collect_changes()
        for key, value in changes.items():
            self._settings.set(key, value)

    def _accept(self):
        """Apply changes and close."""
        self._apply()
        self.accept()
