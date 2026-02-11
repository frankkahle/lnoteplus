#!/usr/bin/env python3
"""NotepadPlus - A Notepad++-like text editor for Linux.

Built with Python 3, PyQt5, and QScintilla (Scintilla editing engine).
"""

import sys
import os
import argparse

# Ensure the application directory is in the path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from settings import Settings
from mainwindow import MainWindow


def parse_args():
    parser = argparse.ArgumentParser(
        description="NotepadPlus - A Notepad++-like text editor for Linux"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to open on startup",
    )
    parser.add_argument(
        "-n", "--new",
        action="store_true",
        help="Start with a new empty tab (ignore session)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Enable high-DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("NotepadPlus")
    app.setOrganizationName("NotepadPlus")

    settings = Settings()
    window = MainWindow(settings)

    # Restore session or open files
    if args.files:
        window.open_files([os.path.abspath(f) for f in args.files])
    elif not args.new:
        if not window.restore_session():
            window.open_files([])  # No session to restore

    # Ensure at least one tab is open
    if window._tab_manager.count() == 0:
        window._tab_manager.new_tab()

    window.show()

    # Apply theme after show to ensure proper rendering
    window._apply_current_theme()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
