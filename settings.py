"""Settings persistence using JSON configuration."""

import json
import os
from PyQt5.QtCore import QObject, pyqtSignal


DEFAULT_SETTINGS = {
    "recent_files": [],
    "max_recent_files": 15,
    "font_family": "Consolas",
    "font_size": 11,
    "theme": "Default",
    "word_wrap": False,
    "tab_size": 4,
    "use_tabs": False,
    "auto_indent": True,
    "show_whitespace": False,
    "show_eol": False,
    "show_line_numbers": True,
    "show_code_folding": True,
    "edge_column": 80,
    "show_edge_line": False,
    "default_encoding": "utf-8",
    "default_eol": "LF",
    "window_geometry": None,
    "window_state": None,
    "auto_save_session": True,
    "restore_session": True,
    "highlight_current_line": True,
    "brace_matching": True,
    "auto_close_brackets": False,
    "zoom_level": 0,
}

CONFIG_DIR = os.path.expanduser("~/.config/notepadplus")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")


class Settings(QObject):
    """Application settings backed by a JSON file."""

    settings_changed = pyqtSignal(str, object)  # key, value

    def __init__(self):
        super().__init__()
        self._data = dict(DEFAULT_SETTINGS)
        self._ensure_config_dir()
        self.load()

    def _ensure_config_dir(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)

    def load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                for key, value in stored.items():
                    if key in DEFAULT_SETTINGS:
                        self._data[key] = value
            except (json.JSONDecodeError, OSError):
                pass

    def save(self):
        self._ensure_config_dir()
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except OSError:
            pass

    def get(self, key, default=None):
        return self._data.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        old = self._data.get(key)
        self._data[key] = value
        if old != value:
            self.settings_changed.emit(key, value)
            self.save()

    def add_recent_file(self, filepath):
        recents = self._data.get("recent_files", [])
        filepath = os.path.abspath(filepath)
        if filepath in recents:
            recents.remove(filepath)
        recents.insert(0, filepath)
        max_recent = self._data.get("max_recent_files", 15)
        self._data["recent_files"] = recents[:max_recent]
        self.save()

    def get_recent_files(self):
        return list(self._data.get("recent_files", []))

    def clear_recent_files(self):
        self._data["recent_files"] = []
        self.save()
