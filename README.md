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

## Installation

### Download the .deb package (recommended)

Download `notepadplus_1.0.0_amd64.deb` from the [releases](https://github.com/frankkahle/lnoteplus/releases) page, or directly from the `dist/` folder in this repo, then:

```bash
sudo dpkg -i notepadplus_1.0.0_amd64.deb
sudo apt-get install -f   # install dependencies if needed
```

This installs NotepadPlus system-wide with a desktop entry, icon, and the `notepadplus` command. Dependencies (`python3-pyqt5`, `python3-pyqt5.qsci`) are pulled in automatically.

### Install from source

```bash
git clone https://github.com/frankkahle/lnoteplus.git
cd lnoteplus
sudo ./install.sh
```

The installer handles dependencies, copies the application to `/opt/notepadplus/`, creates the `notepadplus` command, and adds a desktop entry with icon to your application menu.

### Build the .deb yourself

```bash
git clone https://github.com/frankkahle/lnoteplus.git
cd lnoteplus
./build-deb.sh
sudo dpkg -i dist/notepadplus_1.0.0_amd64.deb
```

## Usage

```bash
# Launch from anywhere
notepadplus

# Open specific files
notepadplus file1.py file2.txt

# Start fresh (ignore saved session)
notepadplus -n
```

Or find **NotepadPlus** in your application menu.

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

Settings are stored in `~/.config/notepadplus/`:

| File | Purpose |
|---|---|
| `settings.json` | Editor preferences, theme, font, etc. |
| `session.json` | Open tabs, cursor positions, scroll state |
| `macros.json` | Saved macros |

All settings can be changed from **Tools > Preferences** within the app.

## Uninstall

```bash
# If installed via .deb
sudo dpkg -r notepadplus

# If installed via install.sh
sudo /opt/notepadplus/uninstall.sh
```

User settings at `~/.config/notepadplus/` are preserved. Remove them manually if desired.

## Supported Platforms

Tested on Ubuntu/Debian-based distributions (Ubuntu 22.04+, Debian 12+, Linux Mint, Pop!_OS, etc.).

## License

MIT

## Author

Frank Kahle - [sos-tech.ca](https://sos-tech.ca)
