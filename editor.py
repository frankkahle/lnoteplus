"""QScintilla editor widget wrapper for NotepadPlus."""

import os
import codecs
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QFontMetrics
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.Qsci import QsciScintilla
from lexer_manager import get_lexer_for_file, get_language_name, get_lexer_for_language
from themes import apply_theme_to_editor, apply_theme_to_lexer, get_theme

# Bookmark marker number
BOOKMARK_MARKER = 8
BOOKMARK_MASK = 1 << BOOKMARK_MARKER


class Editor(QsciScintilla):
    """Enhanced QScintilla editor widget."""

    file_saved = pyqtSignal(str)  # filepath
    modification_changed = pyqtSignal(bool)
    cursor_position_changed = pyqtSignal(int, int)  # line, col
    file_externally_modified = pyqtSignal()

    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self._file_path = None
        self._encoding = "utf-8"
        self._eol_mode_name = "LF"
        self._language = "Plain Text"
        self._settings = settings
        self._file_watcher = None
        self._ignore_next_change = False
        self._last_mtime = None

        self._setup_editor()
        self._setup_margins()
        self._setup_folding()
        self._setup_signals()

    def _setup_editor(self):
        """Configure base editor settings."""
        # Font
        font_family = "Consolas"
        font_size = 11
        if self._settings:
            font_family = self._settings.get("font_family", "Consolas")
            font_size = self._settings.get("font_size", 11)

        font = QFont(font_family, font_size)
        font.setFixedPitch(True)
        self.setFont(font)
        self.setMarginsFont(font)

        # Tab settings
        tab_size = 4
        use_tabs = False
        if self._settings:
            tab_size = self._settings.get("tab_size", 4)
            use_tabs = self._settings.get("use_tabs", False)

        self.setTabWidth(tab_size)
        self.setIndentationsUseTabs(use_tabs)
        self.setTabIndents(True)
        self.setBackspaceUnindents(True)

        # Auto-indent
        auto_indent = True
        if self._settings:
            auto_indent = self._settings.get("auto_indent", True)
        self.setAutoIndent(auto_indent)

        # Brace matching
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Current line
        self.setCaretLineVisible(True)

        # Edge line
        self.setEdgeMode(QsciScintilla.EdgeNone)
        edge_col = 80
        if self._settings:
            edge_col = self._settings.get("edge_column", 80)
            if self._settings.get("show_edge_line", False):
                self.setEdgeMode(QsciScintilla.EdgeLine)
        self.setEdgeColumn(edge_col)

        # Word wrap
        wrap = False
        if self._settings:
            wrap = self._settings.get("word_wrap", False)
        self.setWrapMode(QsciScintilla.WrapWord if wrap else QsciScintilla.WrapNone)
        self.setWrapVisualFlags(QsciScintilla.WrapFlagByBorder)

        # EOL
        self.setEolVisibility(False)

        # Whitespace
        show_ws = False
        if self._settings:
            show_ws = self._settings.get("show_whitespace", False)
        self.setWhitespaceVisibility(
            QsciScintilla.WsVisible if show_ws else QsciScintilla.WsInvisible
        )

        # Scrolling
        self.SendScintilla(QsciScintilla.SCI_SETSCROLLWIDTHTRACKING, 1)
        self.SendScintilla(QsciScintilla.SCI_SETSCROLLWIDTH, 1)

        # Multi-cursor support
        self.SendScintilla(QsciScintilla.SCI_SETMULTIPLESELECTION, 1)
        self.SendScintilla(QsciScintilla.SCI_SETADDITIONALSELECTIONTYPING, 1)
        self.SendScintilla(QsciScintilla.SCI_SETMULTIPASTE, 1)

        # UTF-8 encoding for the editor
        self.setUtf8(True)

    def _setup_margins(self):
        """Set up editor margins (line numbers, bookmarks, folding)."""
        # Margin 0: Line numbers
        show_lines = True
        if self._settings:
            show_lines = self._settings.get("show_line_numbers", True)

        if show_lines:
            self.setMarginType(0, QsciScintilla.NumberMargin)
            self._update_line_number_width()
        else:
            self.setMarginWidth(0, 0)

        # Margin 1: Symbols (bookmarks)
        self.setMarginType(1, QsciScintilla.SymbolMargin)
        self.setMarginWidth(1, 16)
        self.setMarginSensitivity(1, True)
        self.setMarginMarkerMask(1, BOOKMARK_MASK)

        # Bookmark marker style
        self.markerDefine(QsciScintilla.Circle, BOOKMARK_MARKER)
        self.setMarkerBackgroundColor(QColor("#1E90FF"), BOOKMARK_MARKER)
        self.setMarkerForegroundColor(QColor("#FFFFFF"), BOOKMARK_MARKER)

    def _setup_folding(self):
        """Set up code folding."""
        show_folding = True
        if self._settings:
            show_folding = self._settings.get("show_code_folding", True)

        if show_folding:
            self.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        else:
            self.setFolding(QsciScintilla.NoFoldStyle)

    def _setup_signals(self):
        """Connect internal signals."""
        self.modificationChanged.connect(self._on_modification_changed)
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.linesChanged.connect(self._update_line_number_width)
        self.marginClicked.connect(self._on_margin_clicked)

    def _update_line_number_width(self):
        """Update line number margin width based on line count."""
        lines = max(self.lines(), 1)
        digits = len(str(lines))
        # Use setMarginWidth with a string pattern for auto-sizing
        self.setMarginWidth(0, "0" * (digits + 1) + "0")

    def _on_modification_changed(self, modified):
        self.modification_changed.emit(modified)

    def _on_cursor_position_changed(self, line, col):
        self.cursor_position_changed.emit(line, col)

    def _on_margin_clicked(self, margin, line, modifiers):
        if margin == 1:
            self.toggle_bookmark(line)

    # --- File Operations ---

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, path):
        self._file_path = path

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, enc):
        self._encoding = enc

    @property
    def eol_mode_name(self):
        return self._eol_mode_name

    @property
    def language(self):
        return self._language

    @property
    def is_modified(self):
        return self.isModified()

    def load_file(self, filepath, encoding=None):
        """Load a file into the editor."""
        if encoding is None:
            encoding = self._detect_encoding(filepath)

        try:
            with open(filepath, "r", encoding=encoding, errors="replace") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError) as e:
            QMessageBox.critical(self, "Error", f"Cannot open file:\n{e}")
            return False

        self._file_path = os.path.abspath(filepath)
        self._encoding = encoding
        self._detect_eol(content)

        self.setText(content)
        self.setModified(False)

        # Set up syntax highlighting
        self._apply_lexer()

        # Track file modification time
        try:
            self._last_mtime = os.path.getmtime(self._file_path)
        except OSError:
            self._last_mtime = None

        return True

    def save_file(self, filepath=None):
        """Save editor content to file."""
        if filepath:
            self._file_path = os.path.abspath(filepath)

        if not self._file_path:
            return False

        content = self.text()

        # Normalize EOL
        eol = self._get_eol_chars()
        if eol != "\n":
            content = content.replace("\r\n", "\n").replace("\r", "\n")
            content = content.replace("\n", eol)

        try:
            encoding = self._encoding
            if encoding.lower().replace("-", "") == "utf8bom":
                with open(self._file_path, "wb") as f:
                    f.write(codecs.BOM_UTF8)
                    f.write(content.encode("utf-8"))
            else:
                with open(self._file_path, "w", encoding=encoding, errors="replace") as f:
                    f.write(content)
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Cannot save file:\n{e}")
            return False

        self._ignore_next_change = True
        self.setModified(False)

        try:
            self._last_mtime = os.path.getmtime(self._file_path)
        except OSError:
            self._last_mtime = None

        self.file_saved.emit(self._file_path)
        return True

    def check_external_modification(self):
        """Check if the file was modified externally."""
        if not self._file_path or not os.path.exists(self._file_path):
            return False
        try:
            mtime = os.path.getmtime(self._file_path)
            if self._last_mtime is not None and mtime != self._last_mtime:
                self._last_mtime = mtime
                return True
        except OSError:
            pass
        return False

    def reload_file(self):
        """Reload the current file from disk."""
        if self._file_path and os.path.exists(self._file_path):
            pos = self.getCursorPosition()
            scroll_value = self.verticalScrollBar().value() if self.verticalScrollBar() else 0
            self.load_file(self._file_path, self._encoding)
            self.setCursorPosition(*pos)
            if self.verticalScrollBar():
                self.verticalScrollBar().setValue(scroll_value)

    def _detect_encoding(self, filepath):
        """Detect file encoding with BOM check and fallback."""
        try:
            with open(filepath, "rb") as f:
                raw = f.read(4)
                if raw.startswith(codecs.BOM_UTF8):
                    return "utf-8-sig"
                if raw.startswith(codecs.BOM_UTF16_LE):
                    return "utf-16-le"
                if raw.startswith(codecs.BOM_UTF16_BE):
                    return "utf-16-be"

            # Try utf-8
            with open(filepath, "r", encoding="utf-8") as f:
                f.read()
            return "utf-8"
        except (UnicodeDecodeError, OSError):
            return "latin-1"

    def _detect_eol(self, content):
        """Detect end-of-line style."""
        if "\r\n" in content:
            self._eol_mode_name = "CRLF"
            self.setEolMode(QsciScintilla.EolWindows)
        elif "\r" in content:
            self._eol_mode_name = "CR"
            self.setEolMode(QsciScintilla.EolMac)
        else:
            self._eol_mode_name = "LF"
            self.setEolMode(QsciScintilla.EolUnix)

    def _get_eol_chars(self):
        eol_map = {"CRLF": "\r\n", "CR": "\r", "LF": "\n"}
        return eol_map.get(self._eol_mode_name, "\n")

    def set_eol_mode(self, mode_name):
        """Set EOL mode: 'CRLF', 'LF', or 'CR'."""
        self._eol_mode_name = mode_name
        eol_modes = {
            "CRLF": QsciScintilla.EolWindows,
            "LF": QsciScintilla.EolUnix,
            "CR": QsciScintilla.EolMac,
        }
        self.setEolMode(eol_modes.get(mode_name, QsciScintilla.EolUnix))
        self.convertEols(self.eolMode())

    def set_encoding(self, encoding):
        """Change the encoding for this file."""
        self._encoding = encoding

    # --- Syntax Highlighting ---

    def _apply_lexer(self):
        """Apply appropriate lexer for the current file."""
        lexer = get_lexer_for_file(self._file_path, self)
        self._language = get_language_name(self._file_path)
        self.setLexer(lexer)
        if lexer:
            lexer.setFont(self.font())

    def set_language(self, language_name):
        """Manually set language/lexer."""
        self._language = language_name
        lexer = get_lexer_for_language(language_name, self)
        self.setLexer(lexer)
        if lexer:
            lexer.setFont(self.font())

    def apply_theme(self, theme):
        """Apply a theme to this editor."""
        apply_theme_to_editor(self, theme)
        if self.lexer():
            apply_theme_to_lexer(self.lexer(), theme)

    # --- Bookmarks ---

    def toggle_bookmark(self, line=None):
        """Toggle bookmark on the given or current line."""
        if line is None:
            line, _ = self.getCursorPosition()
        if self.markersAtLine(line) & BOOKMARK_MASK:
            self.markerDelete(line, BOOKMARK_MARKER)
        else:
            self.markerAdd(line, BOOKMARK_MARKER)

    def next_bookmark(self):
        """Move cursor to next bookmark."""
        line, _ = self.getCursorPosition()
        next_line = self.markerFindNext(line + 1, BOOKMARK_MASK)
        if next_line == -1:
            next_line = self.markerFindNext(0, BOOKMARK_MASK)
        if next_line >= 0:
            self.setCursorPosition(next_line, 0)

    def prev_bookmark(self):
        """Move cursor to previous bookmark."""
        line, _ = self.getCursorPosition()
        prev_line = self.markerFindPrevious(line - 1, BOOKMARK_MASK)
        if prev_line == -1:
            prev_line = self.markerFindPrevious(self.lines() - 1, BOOKMARK_MASK)
        if prev_line >= 0:
            self.setCursorPosition(prev_line, 0)

    def clear_bookmarks(self):
        """Remove all bookmarks."""
        self.markerDeleteAll(BOOKMARK_MARKER)

    # --- Editing Helpers ---

    def duplicate_line(self):
        """Duplicate the current line or selection."""
        if self.hasSelectedText():
            text = self.selectedText()
            line_from, col_from, line_to, col_to = self.getSelection()
            self.setCursorPosition(line_to, col_to)
            self.insert(text)
        else:
            line, col = self.getCursorPosition()
            line_text = self.text(line)
            self.setCursorPosition(line, len(line_text.rstrip("\r\n")))
            eol = self._get_eol_chars()
            self.insert(eol + line_text.rstrip("\r\n"))
            self.setCursorPosition(line + 1, col)

    def move_line_up(self):
        """Move the current line up."""
        line, col = self.getCursorPosition()
        if line == 0:
            return
        self.beginUndoAction()
        current = self.text(line).rstrip("\r\n")
        above = self.text(line - 1).rstrip("\r\n")
        self.setSelection(line - 1, 0, line, self.lineLength(line))
        eol = self._get_eol_chars()
        self.replaceSelectedText(current + eol + above + eol)
        self.setCursorPosition(line - 1, col)
        self.endUndoAction()

    def move_line_down(self):
        """Move the current line down."""
        line, col = self.getCursorPosition()
        if line >= self.lines() - 1:
            return
        self.beginUndoAction()
        current = self.text(line).rstrip("\r\n")
        below = self.text(line + 1).rstrip("\r\n")
        self.setSelection(line, 0, line + 1, self.lineLength(line + 1))
        eol = self._get_eol_chars()
        self.replaceSelectedText(below + eol + current + eol)
        self.setCursorPosition(line + 1, col)
        self.endUndoAction()

    def delete_line(self):
        """Delete the current line."""
        line, col = self.getCursorPosition()
        self.beginUndoAction()
        if line < self.lines() - 1:
            self.setSelection(line, 0, line + 1, 0)
        else:
            # Last line
            length = self.lineLength(line)
            if line > 0:
                prev_length = self.lineLength(line - 1)
                self.setSelection(line - 1, prev_length - len(self._get_eol_chars()), line, length)
            else:
                self.setSelection(line, 0, line, length)
        self.removeSelectedText()
        self.endUndoAction()

    def toggle_comment(self):
        """Toggle line comment for the current line or selection."""
        # Determine comment string based on language
        comment_map = {
            "Python": "#",
            "Bash": "#",
            "Ruby": "#",
            "Perl": "#",
            "YAML": "#",
            "Makefile": "#",
            "C": "//",
            "C++": "//",
            "Java": "//",
            "C#": "//",
            "JavaScript": "//",
            "TypeScript": "//",
            "JSON": "//",
            "CSS": "//",
            "Lua": "--",
            "SQL": "--",
            "HTML": "",
            "XML": "",
            "Batch": "REM ",
        }
        comment_str = comment_map.get(self._language, "#")
        if not comment_str:
            return

        self.beginUndoAction()

        if self.hasSelectedText():
            line_from, _, line_to, col_to = self.getSelection()
            if col_to == 0 and line_to > line_from:
                line_to -= 1
        else:
            line_from, _ = self.getCursorPosition()
            line_to = line_from

        # Check if all lines are commented
        all_commented = True
        for line_num in range(line_from, line_to + 1):
            text = self.text(line_num).lstrip()
            if text and not text.startswith(comment_str):
                all_commented = False
                break

        for line_num in range(line_from, line_to + 1):
            text = self.text(line_num)
            if all_commented:
                # Remove comment
                stripped = text.lstrip()
                indent = text[: len(text) - len(stripped)]
                if stripped.startswith(comment_str + " "):
                    new_text = indent + stripped[len(comment_str) + 1:]
                elif stripped.startswith(comment_str):
                    new_text = indent + stripped[len(comment_str):]
                else:
                    continue
                self.setSelection(line_num, 0, line_num, self.lineLength(line_num))
                self.replaceSelectedText(new_text)
            else:
                # Add comment
                stripped = text.lstrip()
                if not stripped:
                    continue
                indent = text[: len(text) - len(stripped)]
                new_text = indent + comment_str + " " + stripped
                self.setSelection(line_num, 0, line_num, self.lineLength(line_num))
                self.replaceSelectedText(new_text)

        self.endUndoAction()

    def go_to_line(self, line_number):
        """Move cursor to specified line (1-based)."""
        line = max(0, line_number - 1)
        self.setCursorPosition(line, 0)
        self.ensureLineVisible(line)

    def get_file_size(self):
        """Return file size as human-readable string."""
        if self._file_path and os.path.exists(self._file_path):
            size = os.path.getsize(self._file_path)
        else:
            size = len(self.text().encode(self._encoding, errors="replace"))

        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"

    def get_insert_mode(self):
        """Return whether in insert or overwrite mode."""
        return "OVR" if self.overwriteMode() else "INS"

    def toggle_overwrite(self):
        """Toggle insert/overwrite mode."""
        self.setOverwriteMode(not self.overwriteMode())

    # --- Zoom ---

    def zoom_in(self):
        self.zoomIn()

    def zoom_out(self):
        self.zoomOut()

    def zoom_reset(self):
        self.zoomTo(0)

    def wheelEvent(self, event):
        """Handle Ctrl+Scroll for zoom."""
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn()
            elif delta < 0:
                self.zoomOut()
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        """Handle special keys."""
        if event.key() == Qt.Key_Insert and event.modifiers() == Qt.NoModifier:
            self.toggle_overwrite()
            return
        super().keyPressEvent(event)

    def update_font(self, family, size):
        """Update editor font."""
        font = QFont(family, size)
        font.setFixedPitch(True)
        self.setFont(font)
        self.setMarginsFont(font)
        if self.lexer():
            self.lexer().setFont(font)
        self._update_line_number_width()
