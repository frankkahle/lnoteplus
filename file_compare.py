"""Side-by-side file comparison for NotepadPlus."""

import difflib
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QSplitter,
    QWidget,
)
from PyQt5.Qsci import QsciScintilla
from themes import apply_theme_to_editor, get_theme

# Marker numbers for diff highlighting
MARKER_ADDED = 10
MARKER_REMOVED = 11
MARKER_CHANGED = 12


class FileCompareDialog(QDialog):
    """Side-by-side file comparison dialog."""

    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self._settings = settings
        self.setWindowTitle("Compare Files")
        self.resize(1200, 700)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # File selection row
        file_row = QHBoxLayout()

        self._left_label = QLabel("File 1: (none)")
        file_row.addWidget(self._left_label)
        left_btn = QPushButton("Browse...")
        left_btn.clicked.connect(lambda: self._open_file("left"))
        file_row.addWidget(left_btn)

        file_row.addSpacing(20)

        self._right_label = QLabel("File 2: (none)")
        file_row.addWidget(self._right_label)
        right_btn = QPushButton("Browse...")
        right_btn.clicked.connect(lambda: self._open_file("right"))
        file_row.addWidget(right_btn)

        layout.addLayout(file_row)

        # Compare button and navigation
        btn_row = QHBoxLayout()
        compare_btn = QPushButton("Compare")
        compare_btn.clicked.connect(self._compare)
        btn_row.addWidget(compare_btn)

        self._prev_btn = QPushButton("Previous Diff")
        self._prev_btn.clicked.connect(self._prev_diff)
        self._prev_btn.setEnabled(False)
        btn_row.addWidget(self._prev_btn)

        self._next_btn = QPushButton("Next Diff")
        self._next_btn.clicked.connect(self._next_diff)
        self._next_btn.setEnabled(False)
        btn_row.addWidget(self._next_btn)

        self._status = QLabel("")
        btn_row.addWidget(self._status)
        btn_row.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(close_btn)

        layout.addLayout(btn_row)

        # Side-by-side editors
        splitter = QSplitter(Qt.Horizontal)

        self._left_editor = self._create_editor()
        self._right_editor = self._create_editor()

        splitter.addWidget(self._left_editor)
        splitter.addWidget(self._right_editor)
        splitter.setSizes([600, 600])

        layout.addWidget(splitter)

        # Synchronized scrolling
        self._left_editor.verticalScrollBar().valueChanged.connect(
            self._sync_scroll_right
        )
        self._right_editor.verticalScrollBar().valueChanged.connect(
            self._sync_scroll_left
        )

        self._left_file = None
        self._right_file = None
        self._diff_lines = []
        self._current_diff = -1

    def _create_editor(self):
        """Create a read-only QScintilla editor for comparison."""
        editor = QsciScintilla(self)
        editor.setReadOnly(True)
        editor.setMarginType(0, QsciScintilla.NumberMargin)
        editor.setMarginWidth(0, "00000")
        editor.setMarginWidth(1, 0)

        # Define markers for diff highlighting
        editor.markerDefine(QsciScintilla.Background, MARKER_ADDED)
        editor.setMarkerBackgroundColor(QColor("#2EA04370"), MARKER_ADDED)

        editor.markerDefine(QsciScintilla.Background, MARKER_REMOVED)
        editor.setMarkerBackgroundColor(QColor("#F8514970"), MARKER_REMOVED)

        editor.markerDefine(QsciScintilla.Background, MARKER_CHANGED)
        editor.setMarkerBackgroundColor(QColor("#D29E2270"), MARKER_CHANGED)

        # Apply theme
        theme_name = "Dark"
        if self._settings:
            theme_name = self._settings.get("theme", "Dark")
        theme = get_theme(theme_name)
        apply_theme_to_editor(editor, theme)

        return editor

    def _open_file(self, side):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as e:
            self._status.setText(f"Error: {e}")
            return

        if side == "left":
            self._left_file = filepath
            self._left_label.setText(f"File 1: {filepath}")
            self._left_editor.setReadOnly(False)
            self._left_editor.setText(content)
            self._left_editor.setReadOnly(True)
        else:
            self._right_file = filepath
            self._right_label.setText(f"File 2: {filepath}")
            self._right_editor.setReadOnly(False)
            self._right_editor.setText(content)
            self._right_editor.setReadOnly(True)

    def _compare(self):
        """Perform the comparison."""
        left_text = self._left_editor.text()
        right_text = self._right_editor.text()

        if not left_text and not right_text:
            self._status.setText("No files loaded")
            return

        # Clear existing markers
        self._left_editor.markerDeleteAll(MARKER_ADDED)
        self._left_editor.markerDeleteAll(MARKER_REMOVED)
        self._left_editor.markerDeleteAll(MARKER_CHANGED)
        self._right_editor.markerDeleteAll(MARKER_ADDED)
        self._right_editor.markerDeleteAll(MARKER_REMOVED)
        self._right_editor.markerDeleteAll(MARKER_CHANGED)

        left_lines = left_text.splitlines(True)
        right_lines = right_text.splitlines(True)

        matcher = difflib.SequenceMatcher(None, left_lines, right_lines)
        self._diff_lines = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            elif tag == "replace":
                for line_num in range(i1, i2):
                    self._left_editor.markerAdd(line_num, MARKER_CHANGED)
                for line_num in range(j1, j2):
                    self._right_editor.markerAdd(line_num, MARKER_CHANGED)
                self._diff_lines.append(("changed", i1, j1))
            elif tag == "delete":
                for line_num in range(i1, i2):
                    self._left_editor.markerAdd(line_num, MARKER_REMOVED)
                self._diff_lines.append(("removed", i1, j1))
            elif tag == "insert":
                for line_num in range(j1, j2):
                    self._right_editor.markerAdd(line_num, MARKER_ADDED)
                self._diff_lines.append(("added", i1, j1))

        diff_count = len(self._diff_lines)
        if diff_count == 0:
            self._status.setText("Files are identical")
        else:
            self._status.setText(f"{diff_count} difference(s) found")

        self._prev_btn.setEnabled(diff_count > 0)
        self._next_btn.setEnabled(diff_count > 0)
        self._current_diff = -1

    def _next_diff(self):
        """Navigate to the next difference."""
        if not self._diff_lines:
            return
        self._current_diff = (self._current_diff + 1) % len(self._diff_lines)
        self._go_to_diff(self._current_diff)

    def _prev_diff(self):
        """Navigate to the previous difference."""
        if not self._diff_lines:
            return
        self._current_diff = (self._current_diff - 1) % len(self._diff_lines)
        self._go_to_diff(self._current_diff)

    def _go_to_diff(self, index):
        """Scroll both editors to the specified diff."""
        _, left_line, right_line = self._diff_lines[index]
        self._left_editor.ensureLineVisible(left_line)
        self._left_editor.setCursorPosition(left_line, 0)
        self._right_editor.ensureLineVisible(right_line)
        self._right_editor.setCursorPosition(right_line, 0)
        self._status.setText(
            f"Diff {index + 1} of {len(self._diff_lines)}"
        )

    def _sync_scroll_right(self, value):
        self._right_editor.verticalScrollBar().blockSignals(True)
        self._right_editor.verticalScrollBar().setValue(value)
        self._right_editor.verticalScrollBar().blockSignals(False)

    def _sync_scroll_left(self, value):
        self._left_editor.verticalScrollBar().blockSignals(True)
        self._left_editor.verticalScrollBar().setValue(value)
        self._left_editor.verticalScrollBar().blockSignals(False)

    def set_files(self, left_path, right_path):
        """Pre-load files for comparison."""
        if left_path:
            self._open_file_path("left", left_path)
        if right_path:
            self._open_file_path("right", right_path)

    def _open_file_path(self, side, filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError:
            return

        if side == "left":
            self._left_file = filepath
            self._left_label.setText(f"File 1: {filepath}")
            self._left_editor.setReadOnly(False)
            self._left_editor.setText(content)
            self._left_editor.setReadOnly(True)
        else:
            self._right_file = filepath
            self._right_label.setText(f"File 2: {filepath}")
            self._right_editor.setReadOnly(False)
            self._right_editor.setText(content)
            self._right_editor.setReadOnly(True)
