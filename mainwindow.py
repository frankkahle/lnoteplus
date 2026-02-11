"""Main window for NotepadPlus: menus, toolbar, statusbar."""

import os
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QKeySequence, QFont
from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    QMenu,
    QToolBar,
    QStatusBar,
    QLabel,
    QInputDialog,
    QMessageBox,
    QApplication,
    QSplitter,
    QFileDialog,
)
from PyQt5.Qsci import QsciScintilla
from tab_manager import TabManager
from find_replace import FindReplaceDialog
from file_compare import FileCompareDialog
from preferences_dialog import PreferencesDialog
from session_manager import SessionManager
from macro_manager import MacroManager
from settings import Settings
from themes import get_theme, get_app_stylesheet, apply_theme_to_editor, apply_theme_to_lexer
from lexer_manager import get_available_languages


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, settings=None):
        super().__init__()
        self._settings = settings or Settings()
        self._session_manager = SessionManager()
        self._macro_manager = MacroManager(self)
        self._find_dialog = None
        self._check_timer = None

        self.setWindowTitle("NotepadPlus")
        self.resize(1100, 700)

        self._setup_central_widget()
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_statusbar()
        self._apply_current_theme()
        self._setup_connections()
        self._restore_geometry()
        self._setup_file_check_timer()

    def _setup_central_widget(self):
        """Set up the tab manager as central widget."""
        self._tab_manager = TabManager(self._settings, self)
        self.setCentralWidget(self._tab_manager)

    def _setup_connections(self):
        """Connect signals."""
        self._tab_manager.current_editor_changed.connect(self._on_editor_changed)
        self._tab_manager.tab_count_changed.connect(self._on_tab_count_changed)
        self._tab_manager.file_opened.connect(
            lambda fp: self._settings.add_recent_file(fp)
        )
        self._settings.settings_changed.connect(self._on_settings_changed)

    def _setup_file_check_timer(self):
        """Set up periodic file modification check."""
        self._check_timer = QTimer(self)
        self._check_timer.timeout.connect(self._check_file_modifications)
        self._check_timer.start(2000)

    def _check_file_modifications(self):
        """Check if any open files were modified externally."""
        if not self.isActiveWindow():
            return
        editor = self._tab_manager.current_editor()
        if editor and editor.file_path and editor.check_external_modification():
            reply = QMessageBox.question(
                self,
                "File Changed",
                f'"{os.path.basename(editor.file_path)}" has been modified by another program.\n'
                "Do you want to reload it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes:
                editor.reload_file()

    # --- Actions ---

    def _create_actions(self):
        """Create all menu/toolbar actions."""
        # File actions
        self._new_action = self._make_action("New", "Ctrl+N", self._new_file)
        self._open_action = self._make_action("Open...", "Ctrl+O", self._open_file)
        self._save_action = self._make_action("Save", "Ctrl+S", self._save_file)
        self._save_as_action = self._make_action("Save As...", "Ctrl+Shift+S", self._save_as)
        self._save_all_action = self._make_action("Save All", None, self._save_all)
        self._close_action = self._make_action("Close", "Ctrl+W", self._close_tab)
        self._close_all_action = self._make_action("Close All", None, self._close_all)
        self._print_action = self._make_action("Print...", "Ctrl+P", self._print_file)
        self._exit_action = self._make_action("Exit", "Alt+F4", self.close)

        # Edit actions
        self._undo_action = self._make_action("Undo", "Ctrl+Z", self._undo)
        self._redo_action = self._make_action("Redo", "Ctrl+Y", self._redo)
        self._cut_action = self._make_action("Cut", "Ctrl+X", self._cut)
        self._copy_action = self._make_action("Copy", "Ctrl+C", self._copy)
        self._paste_action = self._make_action("Paste", "Ctrl+V", self._paste)
        self._select_all_action = self._make_action("Select All", "Ctrl+A", self._select_all)
        self._duplicate_action = self._make_action("Duplicate Line", "Ctrl+D", self._duplicate_line)
        self._move_up_action = self._make_action("Move Line Up", "Alt+Up", self._move_line_up)
        self._move_down_action = self._make_action("Move Line Down", "Alt+Down", self._move_line_down)
        self._delete_line_action = self._make_action("Delete Line", "Ctrl+Shift+K", self._delete_line)
        self._toggle_comment_action = self._make_action("Toggle Comment", "Ctrl+/", self._toggle_comment)

        # Search actions
        self._find_action = self._make_action("Find...", "Ctrl+F", self._show_find)
        self._replace_action = self._make_action("Replace...", "Ctrl+H", self._show_replace)
        self._find_in_files_action = self._make_action("Find in Files...", "Ctrl+Shift+F", self._show_find_in_files)
        self._find_next_action = self._make_action("Find Next", "F3", self._find_next)
        self._find_prev_action = self._make_action("Find Previous", "Shift+F3", self._find_prev)
        self._goto_action = self._make_action("Go to Line...", "Ctrl+G", self._goto_line)
        self._toggle_bookmark_action = self._make_action("Toggle Bookmark", "Ctrl+F2", self._toggle_bookmark)
        self._next_bookmark_action = self._make_action("Next Bookmark", "F2", self._next_bookmark)
        self._prev_bookmark_action = self._make_action("Previous Bookmark", "Shift+F2", self._prev_bookmark)
        self._clear_bookmarks_action = self._make_action("Clear All Bookmarks", None, self._clear_bookmarks)

        # View actions
        self._word_wrap_action = self._make_action("Word Wrap", None, self._toggle_word_wrap)
        self._word_wrap_action.setCheckable(True)
        self._word_wrap_action.setChecked(self._settings.get("word_wrap", False))

        self._whitespace_action = self._make_action("Show Whitespace", None, self._toggle_whitespace)
        self._whitespace_action.setCheckable(True)
        self._whitespace_action.setChecked(self._settings.get("show_whitespace", False))

        self._zoom_in_action = self._make_action("Zoom In", "Ctrl++", self._zoom_in)
        self._zoom_out_action = self._make_action("Zoom Out", "Ctrl+-", self._zoom_out)
        self._zoom_reset_action = self._make_action("Reset Zoom", "Ctrl+0", self._zoom_reset)

        self._fullscreen_action = self._make_action("Full Screen", "F11", self._toggle_fullscreen)
        self._fullscreen_action.setCheckable(True)

        # Macro actions
        self._macro_record_action = self._make_action("Start Recording", "Ctrl+Shift+R", self._macro_start)
        self._macro_stop_action = self._make_action("Stop Recording", "Ctrl+Shift+R", self._macro_stop)
        self._macro_stop_action.setEnabled(False)
        self._macro_play_action = self._make_action("Playback", "Ctrl+Shift+P", self._macro_play)
        self._macro_save_action = self._make_action("Save Macro...", None, self._macro_save)

    def _make_action(self, text, shortcut, slot):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        return action

    # --- Menus ---

    def _create_menus(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self._new_action)
        file_menu.addAction(self._open_action)
        file_menu.addAction(self._save_action)
        file_menu.addAction(self._save_as_action)
        file_menu.addAction(self._save_all_action)
        file_menu.addSeparator()
        file_menu.addAction(self._close_action)
        file_menu.addAction(self._close_all_action)
        file_menu.addSeparator()

        # Recent files submenu
        self._recent_menu = file_menu.addMenu("Recent Files")
        self._update_recent_files_menu()

        file_menu.addSeparator()
        file_menu.addAction(self._print_action)
        file_menu.addSeparator()
        file_menu.addAction(self._exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self._undo_action)
        edit_menu.addAction(self._redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self._cut_action)
        edit_menu.addAction(self._copy_action)
        edit_menu.addAction(self._paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self._select_all_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self._duplicate_action)
        edit_menu.addAction(self._move_up_action)
        edit_menu.addAction(self._move_down_action)
        edit_menu.addAction(self._delete_line_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self._toggle_comment_action)

        # Search menu
        search_menu = menubar.addMenu("&Search")
        search_menu.addAction(self._find_action)
        search_menu.addAction(self._replace_action)
        search_menu.addAction(self._find_in_files_action)
        search_menu.addSeparator()
        search_menu.addAction(self._find_next_action)
        search_menu.addAction(self._find_prev_action)
        search_menu.addSeparator()
        search_menu.addAction(self._goto_action)
        search_menu.addSeparator()

        # Bookmarks submenu
        bookmark_menu = search_menu.addMenu("Bookmarks")
        bookmark_menu.addAction(self._toggle_bookmark_action)
        bookmark_menu.addAction(self._next_bookmark_action)
        bookmark_menu.addAction(self._prev_bookmark_action)
        bookmark_menu.addSeparator()
        bookmark_menu.addAction(self._clear_bookmarks_action)

        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self._word_wrap_action)
        view_menu.addAction(self._whitespace_action)
        view_menu.addSeparator()
        view_menu.addAction(self._zoom_in_action)
        view_menu.addAction(self._zoom_out_action)
        view_menu.addAction(self._zoom_reset_action)
        view_menu.addSeparator()
        view_menu.addAction(self._fullscreen_action)

        # Encoding menu
        encoding_menu = menubar.addMenu("E&ncoding")
        self._encoding_actions = {}
        for enc in ["UTF-8", "UTF-8 BOM", "UTF-16", "Latin-1", "ASCII"]:
            action = encoding_menu.addAction(enc)
            action.setCheckable(True)
            action.triggered.connect(lambda checked, e=enc: self._set_encoding(e))
            self._encoding_actions[enc] = action

        encoding_menu.addSeparator()
        convert_menu = encoding_menu.addMenu("Convert to...")
        for enc in ["UTF-8", "UTF-8 BOM", "UTF-16", "Latin-1", "ASCII"]:
            action = convert_menu.addAction(enc)
            action.triggered.connect(lambda checked, e=enc: self._convert_encoding(e))

        # Language menu
        language_menu = menubar.addMenu("&Language")
        for lang in get_available_languages():
            action = language_menu.addAction(lang)
            action.triggered.connect(lambda checked, l=lang: self._set_language(l))

        # Macro menu
        macro_menu = menubar.addMenu("&Macro")
        macro_menu.addAction(self._macro_record_action)
        macro_menu.addAction(self._macro_stop_action)
        macro_menu.addAction(self._macro_play_action)
        macro_menu.addSeparator()
        macro_menu.addAction(self._macro_save_action)

        # Saved macros submenu
        self._saved_macros_menu = macro_menu.addMenu("Saved Macros")
        self._update_saved_macros_menu()

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        compare_action = tools_menu.addAction("Compare Files...")
        compare_action.triggered.connect(self._compare_files)
        tools_menu.addSeparator()
        prefs_action = tools_menu.addAction("Preferences...")
        prefs_action.triggered.connect(self._show_preferences)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = help_menu.addAction("About NotepadPlus")
        about_action.triggered.connect(self._show_about)

    def _update_recent_files_menu(self):
        self._recent_menu.clear()
        recent = self._settings.get_recent_files()
        if not recent:
            action = self._recent_menu.addAction("(empty)")
            action.setEnabled(False)
            return

        for filepath in recent:
            action = self._recent_menu.addAction(filepath)
            action.triggered.connect(lambda checked, fp=filepath: self._open_recent(fp))

        self._recent_menu.addSeparator()
        clear = self._recent_menu.addAction("Clear Recent Files")
        clear.triggered.connect(self._clear_recent_files)

    def _update_saved_macros_menu(self):
        self._saved_macros_menu.clear()
        names = self._macro_manager.get_saved_macro_names()
        if not names:
            action = self._saved_macros_menu.addAction("(none)")
            action.setEnabled(False)
            return

        for name in names:
            action = self._saved_macros_menu.addAction(name)
            action.triggered.connect(
                lambda checked, n=name: self._play_saved_macro(n)
            )

    # --- Toolbar ---

    def _create_toolbar(self):
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(__import__("PyQt5.QtCore", fromlist=["QSize"]).QSize(20, 20))

        toolbar.addAction(self._new_action)
        toolbar.addAction(self._open_action)
        toolbar.addAction(self._save_action)
        toolbar.addAction(self._save_all_action)
        toolbar.addSeparator()
        toolbar.addAction(self._undo_action)
        toolbar.addAction(self._redo_action)
        toolbar.addSeparator()
        toolbar.addAction(self._cut_action)
        toolbar.addAction(self._copy_action)
        toolbar.addAction(self._paste_action)
        toolbar.addSeparator()
        toolbar.addAction(self._find_action)
        toolbar.addAction(self._replace_action)
        toolbar.addSeparator()
        toolbar.addAction(self._zoom_in_action)
        toolbar.addAction(self._zoom_out_action)
        toolbar.addSeparator()
        toolbar.addAction(self._word_wrap_action)

    # --- Status Bar ---

    def _create_statusbar(self):
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)

        self._pos_label = QLabel("Ln 1, Col 1")
        self._pos_label.setMinimumWidth(120)
        self._statusbar.addPermanentWidget(self._pos_label)

        self._enc_label = QLabel("UTF-8")
        self._enc_label.setMinimumWidth(80)
        self._statusbar.addPermanentWidget(self._enc_label)

        self._eol_label = QLabel("LF")
        self._eol_label.setMinimumWidth(50)
        self._statusbar.addPermanentWidget(self._eol_label)

        self._lang_label = QLabel("Plain Text")
        self._lang_label.setMinimumWidth(100)
        self._statusbar.addPermanentWidget(self._lang_label)

        self._size_label = QLabel("")
        self._size_label.setMinimumWidth(80)
        self._statusbar.addPermanentWidget(self._size_label)

        self._mode_label = QLabel("INS")
        self._mode_label.setMinimumWidth(40)
        self._statusbar.addPermanentWidget(self._mode_label)

    def _update_statusbar(self, editor=None):
        if editor is None:
            editor = self._tab_manager.current_editor()

        if editor is None:
            self._pos_label.setText("Ln 1, Col 1")
            self._enc_label.setText("")
            self._eol_label.setText("")
            self._lang_label.setText("")
            self._size_label.setText("")
            self._mode_label.setText("")
            return

        line, col = editor.getCursorPosition()
        self._pos_label.setText(f"Ln {line + 1}, Col {col + 1}")
        self._enc_label.setText(editor.encoding.upper())
        self._eol_label.setText(editor.eol_mode_name)
        self._lang_label.setText(editor.language)
        self._size_label.setText(editor.get_file_size())
        self._mode_label.setText(editor.get_insert_mode())

        # Update encoding menu checkmarks
        enc_map = {
            "utf-8": "UTF-8",
            "utf-8-sig": "UTF-8 BOM",
            "utf-16": "UTF-16",
            "utf-16-le": "UTF-16",
            "utf-16-be": "UTF-16",
            "latin-1": "Latin-1",
            "ascii": "ASCII",
        }
        current_enc = enc_map.get(editor.encoding.lower(), "")
        for name, action in self._encoding_actions.items():
            action.setChecked(name == current_enc)

    # --- Signal Handlers ---

    def _on_editor_changed(self, editor):
        self._update_statusbar(editor)
        if editor:
            title = os.path.basename(editor.file_path) if editor.file_path else "Untitled"
            self.setWindowTitle(f"{title} - NotepadPlus")
        else:
            self.setWindowTitle("NotepadPlus")

    def _on_tab_count_changed(self, count):
        if count == 0:
            self._update_statusbar(None)

    def _on_settings_changed(self, key, value):
        if key == "theme":
            self._apply_current_theme()
        elif key in ("font_family", "font_size"):
            self._apply_font_change()
        elif key == "word_wrap":
            self._word_wrap_action.setChecked(value)
        self._update_recent_files_menu()

    # --- File Operations ---

    def _new_file(self):
        self._tab_manager.new_tab()

    def _open_file(self):
        self._tab_manager.open_file()
        self._update_recent_files_menu()

    def _open_recent(self, filepath):
        if os.path.exists(filepath):
            self._tab_manager.open_file(filepath)
        else:
            QMessageBox.warning(self, "File Not Found", f"File not found:\n{filepath}")

    def _clear_recent_files(self):
        self._settings.clear_recent_files()
        self._update_recent_files_menu()

    def _save_file(self):
        self._tab_manager.save()
        self._update_statusbar()
        self._update_recent_files_menu()

    def _save_as(self):
        self._tab_manager.save_as()
        self._update_statusbar()
        self._update_recent_files_menu()

    def _save_all(self):
        self._tab_manager.save_all()

    def _close_tab(self):
        self._tab_manager.close_tab()

    def _close_all(self):
        self._tab_manager.close_all_tabs()

    def _print_file(self):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            editor.document() if hasattr(editor, 'document') else None

    # --- Edit Operations ---

    def _undo(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.undo()

    def _redo(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.redo()

    def _cut(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.cut()

    def _copy(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.copy()

    def _paste(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.paste()

    def _select_all(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.selectAll()

    def _duplicate_line(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.duplicate_line()

    def _move_line_up(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.move_line_up()

    def _move_line_down(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.move_line_down()

    def _delete_line(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.delete_line()

    def _toggle_comment(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.toggle_comment()

    # --- Search Operations ---

    def _get_find_dialog(self):
        if self._find_dialog is None:
            self._find_dialog = FindReplaceDialog(self, self._tab_manager)
        return self._find_dialog

    def _show_find(self):
        self._get_find_dialog().show_find()

    def _show_replace(self):
        self._get_find_dialog().show_replace()

    def _show_find_in_files(self):
        self._get_find_dialog().show_find_in_files()

    def _find_next(self):
        dialog = self._get_find_dialog()
        if not dialog.isVisible():
            dialog.show_find()
        else:
            dialog.find_next()

    def _find_prev(self):
        dialog = self._get_find_dialog()
        if not dialog.isVisible():
            dialog.show_find()
        else:
            dialog.find_previous()

    def _goto_line(self):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        max_line = editor.lines()
        line, ok = QInputDialog.getInt(
            self, "Go to Line", f"Line number (1 - {max_line}):", 1, 1, max_line
        )
        if ok:
            editor.go_to_line(line)

    def _toggle_bookmark(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.toggle_bookmark()

    def _next_bookmark(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.next_bookmark()

    def _prev_bookmark(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.prev_bookmark()

    def _clear_bookmarks(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.clear_bookmarks()

    # --- View Operations ---

    def _toggle_word_wrap(self):
        editor = self._tab_manager.current_editor()
        if editor:
            if editor.wrapMode() == QsciScintilla.WrapNone:
                editor.setWrapMode(QsciScintilla.WrapWord)
                self._word_wrap_action.setChecked(True)
            else:
                editor.setWrapMode(QsciScintilla.WrapNone)
                self._word_wrap_action.setChecked(False)

    def _toggle_whitespace(self):
        editor = self._tab_manager.current_editor()
        if editor:
            if editor.whitespaceVisibility() == QsciScintilla.WsInvisible:
                editor.setWhitespaceVisibility(QsciScintilla.WsVisible)
                self._whitespace_action.setChecked(True)
            else:
                editor.setWhitespaceVisibility(QsciScintilla.WsInvisible)
                self._whitespace_action.setChecked(False)

    def _zoom_in(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.zoom_in()

    def _zoom_out(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.zoom_out()

    def _zoom_reset(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.zoom_reset()

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self._fullscreen_action.setChecked(False)
        else:
            self.showFullScreen()
            self._fullscreen_action.setChecked(True)

    # --- Encoding ---

    def _set_encoding(self, encoding_name):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        enc_map = {
            "UTF-8": "utf-8",
            "UTF-8 BOM": "utf-8-sig",
            "UTF-16": "utf-16",
            "Latin-1": "latin-1",
            "ASCII": "ascii",
        }
        enc = enc_map.get(encoding_name, "utf-8")
        editor.set_encoding(enc)
        self._update_statusbar()

    def _convert_encoding(self, encoding_name):
        """Convert file encoding (re-save with new encoding)."""
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        self._set_encoding(encoding_name)
        if editor.file_path:
            editor.save_file()

    # --- Language ---

    def _set_language(self, language):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        editor.set_language(language)
        theme = get_theme(self._settings.get("theme", "Dark"))
        editor.apply_theme(theme)
        self._update_statusbar()

    # --- Macros ---

    def _macro_start(self):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        self._macro_manager.start_recording(editor)
        self._macro_record_action.setEnabled(False)
        self._macro_stop_action.setEnabled(True)
        self._statusbar.showMessage("Recording macro...")

    def _macro_stop(self):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        self._macro_manager.stop_recording(editor)
        self._macro_record_action.setEnabled(True)
        self._macro_stop_action.setEnabled(False)
        self._statusbar.showMessage("Macro recorded", 3000)

    def _macro_play(self):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        if not self._macro_manager.has_macro():
            self._statusbar.showMessage("No macro recorded", 3000)
            return
        times, ok = QInputDialog.getInt(
            self, "Playback Macro", "Number of times:", 1, 1, 10000
        )
        if ok:
            self._macro_manager.playback(editor, times)

    def _macro_save(self):
        if not self._macro_manager.has_macro():
            self._statusbar.showMessage("No macro to save", 3000)
            return
        name, ok = QInputDialog.getText(self, "Save Macro", "Macro name:")
        if ok and name:
            self._macro_manager.save_macro(name)
            self._update_saved_macros_menu()

    def _play_saved_macro(self, name):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        self._macro_manager.load_macro(name)
        self._macro_manager.playback(editor)

    # --- Tools ---

    def _compare_files(self):
        dialog = FileCompareDialog(self, self._settings)
        dialog.exec_()

    def _show_preferences(self):
        dialog = PreferencesDialog(self._settings, self)
        dialog.exec_()

    def _show_about(self):
        QMessageBox.about(
            self,
            "About NotepadPlus",
            "<h2>NotepadPlus</h2>"
            "<p>A Notepad++-like text editor for Linux</p>"
            "<p>Built with Python, PyQt5, and QScintilla</p>"
            "<p>Using the Scintilla editing engine</p>",
        )

    # --- Theme ---

    def _apply_current_theme(self):
        theme_name = self._settings.get("theme", "Dark")
        theme = get_theme(theme_name)

        # Apply Qt stylesheet
        self.setStyleSheet(get_app_stylesheet(theme))

        # Apply to all open editors
        for i in range(self._tab_manager.count()):
            editor = self._tab_manager.widget(i)
            editor.apply_theme(theme)

    def _apply_font_change(self):
        family = self._settings.get("font_family", "Consolas")
        size = self._settings.get("font_size", 11)
        for i in range(self._tab_manager.count()):
            editor = self._tab_manager.widget(i)
            editor.update_font(family, size)

    # --- Window State ---

    def _restore_geometry(self):
        geo = self._settings.get("window_geometry")
        state = self._settings.get("window_state")
        if geo:
            from PyQt5.QtCore import QByteArray
            import base64
            try:
                self.restoreGeometry(QByteArray(base64.b64decode(geo)))
            except Exception:
                pass
        if state:
            from PyQt5.QtCore import QByteArray
            import base64
            try:
                self.restoreState(QByteArray(base64.b64decode(state)))
            except Exception:
                pass

    def _save_geometry(self):
        import base64
        geo = base64.b64encode(bytes(self.saveGeometry())).decode("ascii")
        state = base64.b64encode(bytes(self.saveState())).decode("ascii")
        self._settings.set("window_geometry", geo)
        self._settings.set("window_state", state)

    # --- Session ---

    def restore_session(self):
        """Restore the previous session."""
        if self._settings.get("restore_session", True):
            return self._session_manager.restore_session(self._tab_manager)
        return False

    def open_files(self, filepaths):
        """Open files from command line arguments."""
        for fp in filepaths:
            if os.path.exists(fp):
                self._tab_manager.open_file(fp)

    # --- Close Event ---

    def closeEvent(self, event):
        # Save session
        if self._settings.get("auto_save_session", True):
            self._session_manager.save_session(self._tab_manager)

        # Save geometry
        self._save_geometry()

        # Check for unsaved files
        for i in range(self._tab_manager.count()):
            editor = self._tab_manager.widget(i)
            if editor.is_modified:
                self._tab_manager.setCurrentIndex(i)
                name = self._tab_manager.tabText(i).rstrip(" *")
                reply = QMessageBox.question(
                    self,
                    "Save Changes",
                    f'Save changes to "{name}"?',
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    QMessageBox.Save,
                )
                if reply == QMessageBox.Save:
                    if not self._tab_manager.save(editor):
                        event.ignore()
                        return
                elif reply == QMessageBox.Cancel:
                    event.ignore()
                    return

        event.accept()
