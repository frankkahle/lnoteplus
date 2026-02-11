"""Tab widget managing multiple editor instances for NotepadPlus."""

import os
from PyQt5.QtCore import pyqtSignal, Qt, QMimeData
from PyQt5.QtWidgets import (
    QTabWidget,
    QTabBar,
    QMessageBox,
    QFileDialog,
    QMenu,
    QAction,
    QApplication,
)
from editor import Editor


class TabManager(QTabWidget):
    """Tab widget that manages multiple editor tabs."""

    current_editor_changed = pyqtSignal(object)  # Editor or None
    tab_count_changed = pyqtSignal(int)
    file_opened = pyqtSignal(str)  # filepath

    def __init__(self, settings=None, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._untitled_count = 0

        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setAcceptDrops(True)

        # Tab bar context menu
        self.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabBar().customContextMenuRequested.connect(self._tab_context_menu)

        # Signals
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_current_changed)

    def current_editor(self):
        """Return the currently active editor."""
        return self.currentWidget()

    def _on_current_changed(self, index):
        editor = self.widget(index)
        self.current_editor_changed.emit(editor)

    # --- Tab Operations ---

    def new_tab(self, filepath=None):
        """Create a new tab, optionally loading a file."""
        editor = Editor(self, self._settings)

        if filepath and os.path.exists(filepath):
            if not editor.load_file(filepath):
                return None

            # Check if file is already open
            for i in range(self.count()):
                existing = self.widget(i)
                if existing.file_path and os.path.abspath(existing.file_path) == os.path.abspath(filepath):
                    self.setCurrentIndex(i)
                    return existing

            title = os.path.basename(filepath)
            index = self.addTab(editor, title)
            self.setTabToolTip(index, filepath)
            self.file_opened.emit(filepath)
        else:
            self._untitled_count += 1
            title = f"Untitled {self._untitled_count}"
            index = self.addTab(editor, title)

        # Connect editor signals
        editor.modification_changed.connect(
            lambda modified, ed=editor: self._on_editor_modified(ed, modified)
        )
        editor.cursor_position_changed.connect(
            lambda line, col: self.current_editor_changed.emit(self.current_editor())
        )

        self.setCurrentIndex(index)
        self.tab_count_changed.emit(self.count())
        return editor

    def open_file(self, filepath=None):
        """Open a file in a new tab (show dialog if no path given)."""
        if not filepath:
            filepaths, _ = QFileDialog.getOpenFileNames(
                self,
                "Open File",
                "",
                "All Files (*);;Python (*.py);;C/C++ (*.c *.cpp *.h *.hpp);;"
                "JavaScript (*.js *.jsx *.ts *.tsx);;HTML (*.html *.htm);;"
                "Text (*.txt);;XML (*.xml);;JSON (*.json)",
            )
            for fp in filepaths:
                self.new_tab(fp)
            return

        # Check if already open
        filepath = os.path.abspath(filepath)
        for i in range(self.count()):
            existing = self.widget(i)
            if existing.file_path and os.path.abspath(existing.file_path) == filepath:
                self.setCurrentIndex(i)
                return existing

        return self.new_tab(filepath)

    def save(self, editor=None):
        """Save the current or specified editor's file."""
        if editor is None:
            editor = self.current_editor()
        if editor is None:
            return False

        if not editor.file_path:
            return self.save_as(editor)

        if editor.save_file():
            self._update_tab_title(editor)
            return True
        return False

    def save_as(self, editor=None):
        """Save the current editor's file with a new name."""
        if editor is None:
            editor = self.current_editor()
        if editor is None:
            return False

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            editor.file_path or "",
            "All Files (*);;Python (*.py);;C/C++ (*.c *.cpp *.h *.hpp);;"
            "JavaScript (*.js);;HTML (*.html);;Text (*.txt)",
        )
        if filepath:
            editor.file_path = filepath
            if editor.save_file():
                self._update_tab_title(editor)
                # Re-apply lexer for new file extension
                editor._apply_lexer()
                return True
        return False

    def save_all(self):
        """Save all modified files."""
        for i in range(self.count()):
            editor = self.widget(i)
            if editor.is_modified:
                self.save(editor)

    def close_tab(self, index=None):
        """Close a tab, prompting to save if modified."""
        if index is None:
            index = self.currentIndex()
        if index < 0 or index >= self.count():
            return False

        editor = self.widget(index)
        if editor.is_modified:
            name = self.tabText(index).rstrip(" *")
            reply = QMessageBox.question(
                self,
                "Save Changes",
                f'Save changes to "{name}"?',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )
            if reply == QMessageBox.Save:
                if not self.save(editor):
                    return False
            elif reply == QMessageBox.Cancel:
                return False

        self.removeTab(index)
        editor.deleteLater()
        self.tab_count_changed.emit(self.count())
        return True

    def close_all_tabs(self):
        """Close all tabs."""
        while self.count() > 0:
            if not self.close_tab(0):
                return False
        return True

    def close_other_tabs(self, index):
        """Close all tabs except the specified one."""
        i = self.count() - 1
        while i >= 0:
            if i != index:
                if not self.close_tab(i):
                    return False
                if index > i:
                    index -= 1
            i -= 1
        return True

    def _on_editor_modified(self, editor, modified):
        """Update tab title when modification state changes."""
        self._update_tab_title(editor)

    def _update_tab_title(self, editor):
        """Update the tab title to reflect file name and modification state."""
        index = self.indexOf(editor)
        if index < 0:
            return

        if editor.file_path:
            title = os.path.basename(editor.file_path)
        else:
            title = self.tabText(index).rstrip(" *")

        if editor.is_modified:
            title += " *"

        self.setTabText(index, title)
        if editor.file_path:
            self.setTabToolTip(index, editor.file_path)

    def _tab_context_menu(self, pos):
        """Show context menu for tab bar."""
        index = self.tabBar().tabAt(pos)
        if index < 0:
            return

        menu = QMenu(self)

        close_action = menu.addAction("Close")
        close_action.triggered.connect(lambda: self.close_tab(index))

        close_others = menu.addAction("Close Others")
        close_others.triggered.connect(lambda: self.close_other_tabs(index))

        close_all = menu.addAction("Close All")
        close_all.triggered.connect(self.close_all_tabs)

        menu.addSeparator()

        editor = self.widget(index)
        if editor and editor.file_path:
            copy_path = menu.addAction("Copy File Path")
            copy_path.triggered.connect(
                lambda: QApplication.clipboard().setText(editor.file_path)
            )

            open_folder = menu.addAction("Open Containing Folder")
            open_folder.triggered.connect(
                lambda: os.system(f'xdg-open "{os.path.dirname(editor.file_path)}"')
            )

        menu.exec_(self.tabBar().mapToGlobal(pos))

    # --- Drag and Drop ---

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if filepath and os.path.isfile(filepath):
                self.open_file(filepath)
        event.acceptProposedAction()

    # --- Session Support ---

    def get_session_data(self):
        """Return session data for all open tabs."""
        tabs = []
        for i in range(self.count()):
            editor = self.widget(i)
            line, col = editor.getCursorPosition()
            scroll = editor.verticalScrollBar().value() if editor.verticalScrollBar() else 0
            tabs.append({
                "file_path": editor.file_path,
                "cursor_line": line,
                "cursor_col": col,
                "scroll_position": scroll,
                "encoding": editor.encoding,
            })
        return {
            "tabs": tabs,
            "active_index": self.currentIndex(),
        }

    def restore_session_data(self, data):
        """Restore tabs from session data."""
        for tab_data in data.get("tabs", []):
            fp = tab_data.get("file_path")
            if fp and os.path.exists(fp):
                editor = self.new_tab(fp)
                if editor:
                    editor.setCursorPosition(
                        tab_data.get("cursor_line", 0),
                        tab_data.get("cursor_col", 0),
                    )
                    scroll = tab_data.get("scroll_position", 0)
                    if editor.verticalScrollBar():
                        editor.verticalScrollBar().setValue(scroll)

        active = data.get("active_index", 0)
        if 0 <= active < self.count():
            self.setCurrentIndex(active)
