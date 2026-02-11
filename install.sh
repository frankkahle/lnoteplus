#!/bin/bash
#
# NotepadPlus Installer
# Installs NotepadPlus to /opt/notepadplus with desktop integration
#

set -e

APP_NAME="notepadplus"
INSTALL_DIR="/opt/notepadplus"
BIN_LINK="/usr/local/bin/notepadplus"
DESKTOP_FILE="/usr/share/applications/notepadplus.desktop"
ICON_DIR="/usr/share/icons/hicolor"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; exit 1; }

# Check root
if [ "$EUID" -ne 0 ]; then
    error "Please run as root: sudo ./install.sh"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "  NotepadPlus Installer"
echo "  ====================="
echo ""

# Install system dependencies
info "Checking dependencies..."

MISSING=()
python3 -c "import PyQt5" 2>/dev/null || MISSING+=("python3-pyqt5")
python3 -c "from PyQt5.Qsci import QsciScintilla" 2>/dev/null || MISSING+=("python3-pyqt5.qsci")

if [ ${#MISSING[@]} -gt 0 ]; then
    info "Installing missing packages: ${MISSING[*]}"
    apt-get update -qq
    apt-get install -y -qq "${MISSING[@]}"
else
    info "All dependencies satisfied"
fi

# Install application files
info "Installing to ${INSTALL_DIR}..."
mkdir -p "$INSTALL_DIR"

SOURCES=(
    main.py
    mainwindow.py
    tab_manager.py
    editor.py
    find_replace.py
    settings.py
    themes.py
    lexer_manager.py
    session_manager.py
    macro_manager.py
    file_compare.py
    preferences_dialog.py
)

for src in "${SOURCES[@]}"; do
    if [ -f "${SCRIPT_DIR}/${src}" ]; then
        cp "${SCRIPT_DIR}/${src}" "${INSTALL_DIR}/${src}"
    else
        error "Missing source file: ${src}"
    fi
done

# Copy resources if they exist
if [ -d "${SCRIPT_DIR}/resources" ]; then
    cp -r "${SCRIPT_DIR}/resources" "${INSTALL_DIR}/"
fi

# Create launcher script
info "Creating launcher..."
cat > "$BIN_LINK" << 'LAUNCHER'
#!/bin/bash
exec python3 /opt/notepadplus/main.py "$@"
LAUNCHER
chmod +x "$BIN_LINK"

# Generate icon (simple SVG notepad icon)
info "Installing icon..."
mkdir -p "${ICON_DIR}/48x48/apps"
mkdir -p "${ICON_DIR}/128x128/apps"
mkdir -p "${ICON_DIR}/256x256/apps"
mkdir -p "${ICON_DIR}/scalable/apps"

cat > "${ICON_DIR}/scalable/apps/notepadplus.svg" << 'SVG'
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#4A90D9;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#2C5F8A;stop-opacity:1" />
    </linearGradient>
  </defs>
  <!-- Background -->
  <rect x="16" y="16" width="224" height="224" rx="24" fill="url(#bg)" />
  <!-- Page -->
  <rect x="48" y="40" width="160" height="186" rx="8" fill="#FFFFFF" />
  <!-- Folded corner -->
  <path d="M 168 40 L 208 80 L 168 80 Z" fill="#D0D0D0" />
  <path d="M 168 40 L 208 80" stroke="#B0B0B0" stroke-width="1" fill="none" />
  <!-- Text lines -->
  <rect x="64" y="96" width="100" height="6" rx="3" fill="#4A90D9" />
  <rect x="64" y="114" width="128" height="6" rx="3" fill="#888888" />
  <rect x="64" y="132" width="80" height="6" rx="3" fill="#888888" />
  <rect x="64" y="150" width="112" height="6" rx="3" fill="#888888" />
  <rect x="64" y="168" width="96" height="6" rx="3" fill="#4A90D9" />
  <rect x="64" y="186" width="128" height="6" rx="3" fill="#888888" />
  <!-- Plus badge -->
  <circle cx="200" cy="196" r="36" fill="#E8443A" />
  <rect x="188" y="190" width="24" height="6" rx="3" fill="#FFFFFF" />
  <rect x="197" y="181" width="6" height="24" rx="3" fill="#FFFFFF" />
</svg>
SVG

# Render PNG icons from SVG if rsvg-convert is available
if command -v rsvg-convert &> /dev/null; then
    rsvg-convert -w 48 -h 48 "${ICON_DIR}/scalable/apps/notepadplus.svg" > "${ICON_DIR}/48x48/apps/notepadplus.png"
    rsvg-convert -w 128 -h 128 "${ICON_DIR}/scalable/apps/notepadplus.svg" > "${ICON_DIR}/128x128/apps/notepadplus.png"
    rsvg-convert -w 256 -h 256 "${ICON_DIR}/scalable/apps/notepadplus.svg" > "${ICON_DIR}/256x256/apps/notepadplus.png"
fi

# Create desktop entry
info "Creating desktop entry..."
cat > "$DESKTOP_FILE" << 'DESKTOP'
[Desktop Entry]
Name=NotepadPlus
Comment=A Notepad++-like text editor for Linux
Exec=notepadplus %F
Icon=notepadplus
Terminal=false
Type=Application
Categories=TextEditor;Development;Utility;
MimeType=text/plain;text/x-python;text/x-csrc;text/x-c++src;text/x-java;text/javascript;text/html;text/css;text/xml;application/json;application/x-yaml;text/x-sql;text/x-shellscript;text/x-makefile;text/x-markdown;text/x-lua;text/x-perl;text/x-ruby;
Keywords=text;editor;code;programming;notepad;
StartupNotify=true
DESKTOP

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications/ 2>/dev/null || true
fi
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "${ICON_DIR}" 2>/dev/null || true
fi

echo ""
info "Installation complete!"
echo ""
echo "  Launch from terminal:  notepadplus"
echo "  Launch from terminal:  notepadplus file1.py file2.txt"
echo "  Or find 'NotepadPlus' in your application menu"
echo ""
echo "  To uninstall:  sudo /opt/notepadplus/uninstall.sh"
echo ""
