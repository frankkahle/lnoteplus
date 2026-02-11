# NotepadPlus

A Notepad++-like text editor for Linux, built with Python 3, PyQt5, and QScintilla (the same Scintilla editing engine that powers Notepad++).

## Features

- **Tabbed editing** - Open multiple files in tabs with drag-and-drop support
- **Syntax highlighting** - 24+ languages including Python, C/C++, JavaScript, HTML, CSS, SQL, Bash, JSON, XML, Markdown, YAML, Ruby, Perl, Lua, and more
- **5 color themes** - Default (light), Dark, Monokai, Solarized Dark, Solarized Light
- **Find / Replace** - With regex, match case, whole word, highlight all, and wrap around
- **Find in Files** - Search across directories with file filters
- **Code folding** - Collapse and expand code blocks
- **Bookmarks** - Toggle, navigate, and clear bookmarks
- **Line operations** - Duplicate, move up/down, delete line, toggle comments
- **Macros** - Record, playback, and save editing macros
- **Session restore** - Automatically saves and restores open tabs, cursor positions, and scroll positions
- **File comparison** - Side-by-side diff with synchronized scrolling and diff navigation
- **Encoding support** - UTF-8, UTF-8 BOM, UTF-16, Latin-1, ASCII with detection and conversion
- **EOL handling** - Detect and convert between LF, CRLF, and CR
- **Zoom** - Ctrl+scroll wheel or Ctrl+Plus/Minus
- **External change detection** - Prompts to reload when files are modified outside the editor
- **Preferences dialog** - Customize fonts, themes, tab size, word wrap, and more
- **Notepad++ keyboard shortcuts** - Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+F, Ctrl+H, Ctrl+G, F3, Ctrl+D, and more

## Requirements

- Python 3
- PyQt5
- QScintilla

## Installation

```bash
# Ubuntu / Debian
sudo apt install python3-pyqt5 python3-pyqt5.qsci

# Or via pip
pip install PyQt5 QScintilla
```

## Usage

```bash
# Launch with empty tab
python3 main.py

# Open specific files
python3 main.py file1.py file2.txt

# Start fresh (ignore saved session)
python3 main.py -n
```

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+N | New file |
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save As |
| Ctrl+W | Close tab |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+F | Find |
| Ctrl+H | Replace |
| Ctrl+Shift+F | Find in Files |
| Ctrl+G | Go to Line |
| F3 / Shift+F3 | Find Next / Previous |
| Ctrl+D | Duplicate line |
| Ctrl+Shift+K | Delete line |
| Alt+Up/Down | Move line up/down |
| Ctrl+/ | Toggle comment |
| Ctrl+F2 | Toggle bookmark |
| F2 / Shift+F2 | Next / Previous bookmark |
| Ctrl++/- | Zoom in/out |
| Ctrl+0 | Reset zoom |
| F11 | Full screen |

## Configuration

Settings are stored in `~/.config/notepadplus/settings.json`. Sessions are saved to `~/.config/notepadplus/session.json`. Macros are saved to `~/.config/notepadplus/macros.json`.

## License

MIT

## Author

Frank Kahle - [sos-tech.ca](https://sos-tech.ca)
