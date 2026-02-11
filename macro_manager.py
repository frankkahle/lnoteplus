"""Macro recording and playback for NotepadPlus."""

import json
import os
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.Qsci import QsciScintilla

MACRO_DIR = os.path.expanduser("~/.config/notepadplus")
MACRO_FILE = os.path.join(MACRO_DIR, "macros.json")


class MacroManager(QObject):
    """Records and plays back editing macros."""

    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._recording = False
        self._macro = []
        self._saved_macros = {}
        os.makedirs(MACRO_DIR, exist_ok=True)
        self._load_macros()

    @property
    def is_recording(self):
        return self._recording

    def start_recording(self, editor):
        """Start recording macro on the given editor."""
        if self._recording:
            return
        self._recording = True
        self._macro = []
        self._editor = editor
        # Use SCN_MACRORECORD via Scintilla
        editor.SendScintilla(QsciScintilla.SCI_STARTRECORD)
        editor.SCN_MACRORECORD = True
        # Connect to the macro record signal
        editor.SCN_MACRORECORD = True
        self.recording_started.emit()

    def stop_recording(self, editor):
        """Stop recording macro."""
        if not self._recording:
            return
        self._recording = False
        editor.SendScintilla(QsciScintilla.SCI_STOPRECORD)
        self.recording_stopped.emit()

    def record_action(self, message, wparam, lparam):
        """Record a single macro action (called from SCN_MACRORECORD handler)."""
        if self._recording:
            self._macro.append((message, wparam, lparam))

    def playback(self, editor, times=1):
        """Play back the recorded macro."""
        if not self._macro:
            return

        editor.beginUndoAction()
        for _ in range(times):
            for message, wparam, lparam in self._macro:
                if isinstance(lparam, str):
                    editor.SendScintilla(message, wparam, lparam.encode("utf-8"))
                else:
                    editor.SendScintilla(message, wparam, lparam)
        editor.endUndoAction()

    def save_macro(self, name):
        """Save the current macro with a name."""
        if not self._macro:
            return
        self._saved_macros[name] = [
            (m, w, l if not isinstance(l, bytes) else l.decode("utf-8", errors="replace"))
            for m, w, l in self._macro
        ]
        self._persist_macros()

    def load_macro(self, name):
        """Load a saved macro by name."""
        if name in self._saved_macros:
            self._macro = [
                (m, w, l) for m, w, l in self._saved_macros[name]
            ]

    def get_saved_macro_names(self):
        """Return list of saved macro names."""
        return list(self._saved_macros.keys())

    def delete_macro(self, name):
        """Delete a saved macro."""
        if name in self._saved_macros:
            del self._saved_macros[name]
            self._persist_macros()

    def has_macro(self):
        """Check if there's a recorded macro available."""
        return len(self._macro) > 0

    def _persist_macros(self):
        try:
            with open(MACRO_FILE, "w", encoding="utf-8") as f:
                json.dump(self._saved_macros, f, indent=2)
        except OSError:
            pass

    def _load_macros(self):
        if os.path.exists(MACRO_FILE):
            try:
                with open(MACRO_FILE, "r", encoding="utf-8") as f:
                    self._saved_macros = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._saved_macros = {}
