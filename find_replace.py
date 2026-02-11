"""Find/Replace dialog for NotepadPlus."""

import os
import re
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QTabWidget,
    QWidget,
    QGroupBox,
    QFileDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QComboBox,
    QMessageBox,
)
from PyQt5.Qsci import QsciScintilla


class FindReplaceDialog(QDialog):
    """Modeless find/replace dialog."""

    def __init__(self, parent=None, tab_manager=None):
        super().__init__(parent)
        self._tab_manager = tab_manager
        self._search_history = []
        self._replace_history = []

        self.setWindowTitle("Find / Replace")
        self.setMinimumWidth(500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        # Find tab
        find_widget = QWidget()
        self._build_find_tab(find_widget)
        self._tabs.addTab(find_widget, "Find")

        # Replace tab
        replace_widget = QWidget()
        self._build_replace_tab(replace_widget)
        self._tabs.addTab(replace_widget, "Replace")

        # Find in Files tab
        fif_widget = QWidget()
        self._build_find_in_files_tab(fif_widget)
        self._tabs.addTab(fif_widget, "Find in Files")

        # Status label
        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

    def _build_find_tab(self, parent):
        layout = QGridLayout(parent)

        layout.addWidget(QLabel("Find:"), 0, 0)
        self._find_input = QComboBox()
        self._find_input.setEditable(True)
        self._find_input.setInsertPolicy(QComboBox.InsertAtTop)
        self._find_input.setMinimumWidth(300)
        layout.addWidget(self._find_input, 0, 1, 1, 2)

        # Options
        opts = QGroupBox("Options")
        opts_layout = QVBoxLayout(opts)
        self._match_case = QCheckBox("Match &case")
        self._whole_word = QCheckBox("Whole &word")
        self._regex = QCheckBox("Regular e&xpression")
        self._wrap_around = QCheckBox("Wrap ar&ound")
        self._wrap_around.setChecked(True)
        opts_layout.addWidget(self._match_case)
        opts_layout.addWidget(self._whole_word)
        opts_layout.addWidget(self._regex)
        opts_layout.addWidget(self._wrap_around)
        layout.addWidget(opts, 1, 0, 1, 2)

        # Buttons
        btn_layout = QVBoxLayout()
        self._find_next_btn = QPushButton("Find &Next")
        self._find_next_btn.setDefault(True)
        self._find_next_btn.clicked.connect(self.find_next)
        btn_layout.addWidget(self._find_next_btn)

        self._find_prev_btn = QPushButton("Find &Previous")
        self._find_prev_btn.clicked.connect(self.find_previous)
        btn_layout.addWidget(self._find_prev_btn)

        self._count_btn = QPushButton("C&ount")
        self._count_btn.clicked.connect(self.count_matches)
        btn_layout.addWidget(self._count_btn)

        self._highlight_btn = QPushButton("&Highlight All")
        self._highlight_btn.clicked.connect(self.highlight_all)
        btn_layout.addWidget(self._highlight_btn)

        btn_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout, 0, 3, 3, 1)

    def _build_replace_tab(self, parent):
        layout = QGridLayout(parent)

        layout.addWidget(QLabel("Find:"), 0, 0)
        self._replace_find_input = QComboBox()
        self._replace_find_input.setEditable(True)
        self._replace_find_input.setInsertPolicy(QComboBox.InsertAtTop)
        self._replace_find_input.setMinimumWidth(300)
        layout.addWidget(self._replace_find_input, 0, 1, 1, 2)

        layout.addWidget(QLabel("Replace:"), 1, 0)
        self._replace_input = QComboBox()
        self._replace_input.setEditable(True)
        self._replace_input.setInsertPolicy(QComboBox.InsertAtTop)
        layout.addWidget(self._replace_input, 1, 1, 1, 2)

        # Options
        opts = QGroupBox("Options")
        opts_layout = QVBoxLayout(opts)
        self._replace_match_case = QCheckBox("Match &case")
        self._replace_whole_word = QCheckBox("Whole &word")
        self._replace_regex = QCheckBox("Regular e&xpression")
        self._replace_wrap = QCheckBox("Wrap ar&ound")
        self._replace_wrap.setChecked(True)
        opts_layout.addWidget(self._replace_match_case)
        opts_layout.addWidget(self._replace_whole_word)
        opts_layout.addWidget(self._replace_regex)
        opts_layout.addWidget(self._replace_wrap)
        layout.addWidget(opts, 2, 0, 1, 2)

        # Buttons
        btn_layout = QVBoxLayout()
        find_next = QPushButton("Find &Next")
        find_next.clicked.connect(self._replace_find_next)
        btn_layout.addWidget(find_next)

        replace_btn = QPushButton("&Replace")
        replace_btn.clicked.connect(self.replace)
        btn_layout.addWidget(replace_btn)

        replace_all_btn = QPushButton("Replace &All")
        replace_all_btn.clicked.connect(self.replace_all)
        btn_layout.addWidget(replace_all_btn)

        btn_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout, 0, 3, 4, 1)

    def _build_find_in_files_tab(self, parent):
        layout = QVBoxLayout(parent)

        # Search input
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Find:"))
        self._fif_input = QComboBox()
        self._fif_input.setEditable(True)
        self._fif_input.setInsertPolicy(QComboBox.InsertAtTop)
        row1.addWidget(self._fif_input)
        layout.addLayout(row1)

        # Directory
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Directory:"))
        self._fif_dir = QLineEdit()
        self._fif_dir.setText(os.getcwd())
        row2.addWidget(self._fif_dir)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_directory)
        row2.addWidget(browse_btn)
        layout.addLayout(row2)

        # Filters
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Filter:"))
        self._fif_filter = QLineEdit("*.*")
        row3.addWidget(self._fif_filter)
        self._fif_case = QCheckBox("Match case")
        row3.addWidget(self._fif_case)
        self._fif_regex = QCheckBox("Regex")
        row3.addWidget(self._fif_regex)
        layout.addLayout(row3)

        # Search button
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self._find_in_files)
        layout.addWidget(search_btn)

        # Results
        self._fif_results = QTreeWidget()
        self._fif_results.setHeaderLabels(["File", "Line", "Text"])
        self._fif_results.setColumnWidth(0, 200)
        self._fif_results.setColumnWidth(1, 50)
        self._fif_results.itemDoubleClicked.connect(self._fif_item_clicked)
        layout.addWidget(self._fif_results)

        self._fif_status = QLabel("")
        layout.addWidget(self._fif_status)

    def _browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory", self._fif_dir.text())
        if dir_path:
            self._fif_dir.setText(dir_path)

    # --- Find Operations ---

    def _get_editor(self):
        if self._tab_manager:
            return self._tab_manager.current_editor()
        return None

    def _get_find_text(self):
        """Get search text from the active tab's find input."""
        tab_idx = self._tabs.currentIndex()
        if tab_idx == 0:
            return self._find_input.currentText()
        elif tab_idx == 1:
            return self._replace_find_input.currentText()
        return ""

    def _get_flags(self, tab_idx=None):
        """Get search flags based on checkboxes."""
        if tab_idx is None:
            tab_idx = self._tabs.currentIndex()

        if tab_idx == 0:
            case = self._match_case.isChecked()
            word = self._whole_word.isChecked()
            regex = self._regex.isChecked()
            wrap = self._wrap_around.isChecked()
        else:
            case = self._replace_match_case.isChecked()
            word = self._replace_whole_word.isChecked()
            regex = self._replace_regex.isChecked()
            wrap = self._replace_wrap.isChecked()

        return case, word, regex, wrap

    def find_next(self):
        """Find the next occurrence."""
        editor = self._get_editor()
        if not editor:
            return False

        text = self._get_find_text()
        if not text:
            return False

        case, word, regex, wrap = self._get_flags()

        # Start search from current position
        found = editor.findFirst(text, regex, case, word, wrap, True)
        if found:
            self._status_label.setText("")
        else:
            self._status_label.setText("No matches found")
        return found

    def find_previous(self):
        """Find the previous occurrence."""
        editor = self._get_editor()
        if not editor:
            return False

        text = self._get_find_text()
        if not text:
            return False

        case, word, regex, wrap = self._get_flags()

        # Search backwards
        line, col = editor.getCursorPosition()
        if editor.hasSelectedText():
            line, col, _, _ = editor.getSelection()

        found = editor.findFirst(text, regex, case, word, wrap, False, line, col)
        if found:
            self._status_label.setText("")
        else:
            self._status_label.setText("No matches found")
        return found

    def _replace_find_next(self):
        """Find next from replace tab."""
        editor = self._get_editor()
        if not editor:
            return False

        text = self._replace_find_input.currentText()
        if not text:
            return False

        case, word, regex, wrap = self._get_flags(1)
        found = editor.findFirst(text, regex, case, word, wrap, True)
        if not found:
            self._status_label.setText("No matches found")
        else:
            self._status_label.setText("")
        return found

    def replace(self):
        """Replace the current match and find next."""
        editor = self._get_editor()
        if not editor:
            return

        if not editor.hasSelectedText():
            self._replace_find_next()
            return

        replace_text = self._replace_input.currentText()
        editor.replace(replace_text)
        self._replace_find_next()

    def replace_all(self):
        """Replace all occurrences."""
        editor = self._get_editor()
        if not editor:
            return

        find_text = self._replace_find_input.currentText()
        replace_text = self._replace_input.currentText()
        if not find_text:
            return

        case, word, regex, wrap = self._get_flags(1)

        editor.beginUndoAction()

        # Start from beginning
        count = 0
        editor.setCursorPosition(0, 0)
        while editor.findFirst(find_text, regex, case, word, False, True):
            editor.replace(replace_text)
            count += 1
            if count > 100000:  # Safety limit
                break

        editor.endUndoAction()
        self._status_label.setText(f"Replaced {count} occurrence(s)")

    def count_matches(self):
        """Count all matches in the current document."""
        editor = self._get_editor()
        if not editor:
            return

        text = self._get_find_text()
        if not text:
            return

        case, word, regex, wrap = self._get_flags()
        content = editor.text()

        try:
            if regex:
                flags = 0 if case else re.IGNORECASE
                matches = len(re.findall(text, content, flags))
            else:
                if not case:
                    content = content.lower()
                    text = text.lower()
                if word:
                    pattern = r"\b" + re.escape(text) + r"\b"
                    matches = len(re.findall(pattern, content))
                else:
                    matches = content.count(text)
        except re.error:
            matches = 0

        self._status_label.setText(f"{matches} match(es) found")

    def highlight_all(self):
        """Highlight all matches using indicators."""
        editor = self._get_editor()
        if not editor:
            return

        text = self._get_find_text()
        if not text:
            return

        # Use indicator 0 for highlighting
        INDICATOR = 0
        editor.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, INDICATOR, 7)  # INDIC_ROUNDBOX
        editor.SendScintilla(QsciScintilla.SCI_INDICSETFORE, INDICATOR, 0x0066FF)
        editor.SendScintilla(QsciScintilla.SCI_INDICSETALPHA, INDICATOR, 100)
        editor.SendScintilla(QsciScintilla.SCI_INDICSETOUTLINEALPHA, INDICATOR, 200)

        # Clear previous highlights
        editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, INDICATOR)
        editor.SendScintilla(
            QsciScintilla.SCI_INDICATORCLEARRANGE, 0, editor.length()
        )

        case, word, regex, wrap = self._get_flags()
        content = editor.text()

        try:
            if regex:
                flags = 0 if case else re.IGNORECASE
                for match in re.finditer(text, content, flags):
                    start = match.start()
                    length = match.end() - start
                    encoded_start = len(content[:start].encode("utf-8"))
                    encoded_length = len(content[start : start + length].encode("utf-8"))
                    editor.SendScintilla(
                        QsciScintilla.SCI_INDICATORFILLRANGE,
                        encoded_start,
                        encoded_length,
                    )
            else:
                search_content = content
                search_text = text
                if not case:
                    search_content = content.lower()
                    search_text = text.lower()

                start = 0
                count = 0
                while True:
                    pos = search_content.find(search_text, start)
                    if pos == -1:
                        break
                    if word:
                        before = pos == 0 or not search_content[pos - 1].isalnum()
                        after = (
                            pos + len(search_text) >= len(search_content)
                            or not search_content[pos + len(search_text)].isalnum()
                        )
                        if not (before and after):
                            start = pos + 1
                            continue

                    encoded_pos = len(content[:pos].encode("utf-8"))
                    encoded_len = len(content[pos : pos + len(text)].encode("utf-8"))
                    editor.SendScintilla(
                        QsciScintilla.SCI_INDICATORFILLRANGE,
                        encoded_pos,
                        encoded_len,
                    )
                    start = pos + 1
                    count += 1
                    if count > 100000:
                        break
        except re.error:
            pass

    # --- Find in Files ---

    def _find_in_files(self):
        """Search for text in files within a directory."""
        search_text = self._fif_input.currentText()
        if not search_text:
            return

        directory = self._fif_dir.text()
        if not os.path.isdir(directory):
            QMessageBox.warning(self, "Error", "Invalid directory")
            return

        file_filter = self._fif_filter.text() or "*.*"
        use_case = self._fif_case.isChecked()
        use_regex = self._fif_regex.isChecked()

        self._fif_results.clear()
        total_matches = 0

        import fnmatch
        import glob

        # Collect files matching filter
        patterns = [p.strip() for p in file_filter.split(";")]
        files = set()
        for pattern in patterns:
            for filepath in glob.glob(os.path.join(directory, "**", pattern), recursive=True):
                if os.path.isfile(filepath):
                    files.add(filepath)

        for filepath in sorted(files):
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    for line_num, line in enumerate(f, 1):
                        match = False
                        if use_regex:
                            try:
                                flags = 0 if use_case else re.IGNORECASE
                                if re.search(search_text, line, flags):
                                    match = True
                            except re.error:
                                break
                        else:
                            if use_case:
                                match = search_text in line
                            else:
                                match = search_text.lower() in line.lower()

                        if match:
                            item = QTreeWidgetItem([
                                os.path.relpath(filepath, directory),
                                str(line_num),
                                line.strip()[:200],
                            ])
                            item.setData(0, Qt.UserRole, filepath)
                            item.setData(1, Qt.UserRole, line_num)
                            self._fif_results.addTopLevelItem(item)
                            total_matches += 1

                            if total_matches > 10000:
                                break
            except (OSError, UnicodeDecodeError):
                continue

            if total_matches > 10000:
                break

        self._fif_status.setText(f"Found {total_matches} match(es) in {len(files)} file(s)")

    def _fif_item_clicked(self, item, column):
        """Open file at the matched line when double-clicked."""
        filepath = item.data(0, Qt.UserRole)
        line_num = item.data(1, Qt.UserRole)
        if filepath and self._tab_manager:
            editor = self._tab_manager.open_file(filepath)
            if editor and line_num:
                editor.go_to_line(line_num)

    # --- Public Interface ---

    def show_find(self):
        """Show dialog with Find tab active."""
        self._tabs.setCurrentIndex(0)
        editor = self._get_editor()
        if editor and editor.hasSelectedText():
            self._find_input.setEditText(editor.selectedText())
        self._find_input.lineEdit().selectAll()
        self._find_input.setFocus()
        self.show()
        self.raise_()
        self.activateWindow()

    def show_replace(self):
        """Show dialog with Replace tab active."""
        self._tabs.setCurrentIndex(1)
        editor = self._get_editor()
        if editor and editor.hasSelectedText():
            self._replace_find_input.setEditText(editor.selectedText())
        self._replace_find_input.lineEdit().selectAll()
        self._replace_find_input.setFocus()
        self.show()
        self.raise_()
        self.activateWindow()

    def show_find_in_files(self):
        """Show dialog with Find in Files tab active."""
        self._tabs.setCurrentIndex(2)
        self._fif_input.setFocus()
        self.show()
        self.raise_()
        self.activateWindow()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            tab_idx = self._tabs.currentIndex()
            if tab_idx == 0:
                self.find_next()
            elif tab_idx == 1:
                self._replace_find_next()
            elif tab_idx == 2:
                self._find_in_files()
        else:
            super().keyPressEvent(event)
