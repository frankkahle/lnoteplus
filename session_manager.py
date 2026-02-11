"""Session save/restore for NotepadPlus."""

import json
import os

SESSION_DIR = os.path.expanduser("~/.config/notepadplus")
SESSION_FILE = os.path.join(SESSION_DIR, "session.json")


class SessionManager:
    """Manages saving and restoring editor sessions."""

    def __init__(self):
        os.makedirs(SESSION_DIR, exist_ok=True)

    def save_session(self, tab_manager):
        """Save current session to disk."""
        data = tab_manager.get_session_data()
        try:
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass

    def restore_session(self, tab_manager):
        """Restore session from disk."""
        if not os.path.exists(SESSION_FILE):
            return False

        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return False

        if not data.get("tabs"):
            return False

        tab_manager.restore_session_data(data)
        return True

    def clear_session(self):
        """Remove saved session file."""
        try:
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
        except OSError:
            pass
