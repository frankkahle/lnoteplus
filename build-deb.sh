#!/bin/bash
#
# Build a .deb package for NotepadPlus
#

set -e

VERSION="1.0.0"
ARCH="amd64"
PKG_NAME="notepadplus"
PKG_DIR="${PKG_NAME}_${VERSION}_${ARCH}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "  Building NotepadPlus ${VERSION} .deb package"
echo "  ============================================="
echo ""

# Clean previous build
rm -rf "${SCRIPT_DIR}/dist/${PKG_DIR}"
mkdir -p "${SCRIPT_DIR}/dist/${PKG_DIR}"

BUILD="${SCRIPT_DIR}/dist/${PKG_DIR}"

# DEBIAN control files
mkdir -p "${BUILD}/DEBIAN"

cat > "${BUILD}/DEBIAN/control" << EOF
Package: ${PKG_NAME}
Version: ${VERSION}
Section: editors
Priority: optional
Architecture: ${ARCH}
Depends: python3, python3-pyqt5, python3-pyqt5.qsci
Maintainer: Frank Kahle <frank@sos-tech.ca>
Homepage: https://sos-tech.ca
Description: A Notepad++-like text editor for Linux
 NotepadPlus is a feature-rich text editor built with Python 3, PyQt5,
 and QScintilla (the same Scintilla editing engine that powers Notepad++).
 .
 Features include tabbed editing, syntax highlighting for 24+ languages,
 multiple color themes, find/replace with regex, code folding, bookmarks,
 macros, session restore, and file comparison.
EOF

cat > "${BUILD}/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications/ 2>/dev/null || true
fi
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi
EOF
chmod 755 "${BUILD}/DEBIAN/postinst"

cat > "${BUILD}/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications/ 2>/dev/null || true
fi
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi
EOF
chmod 755 "${BUILD}/DEBIAN/postrm"

# Application files
APP_DIR="${BUILD}/opt/notepadplus"
mkdir -p "${APP_DIR}"

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
    cp "${SCRIPT_DIR}/${src}" "${APP_DIR}/${src}"
done

# Launcher
mkdir -p "${BUILD}/usr/local/bin"
cat > "${BUILD}/usr/local/bin/notepadplus" << 'LAUNCHER'
#!/bin/bash
exec python3 /opt/notepadplus/main.py "$@"
LAUNCHER
chmod 755 "${BUILD}/usr/local/bin/notepadplus"

# Desktop entry
mkdir -p "${BUILD}/usr/share/applications"
cat > "${BUILD}/usr/share/applications/notepadplus.desktop" << 'DESKTOP'
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

# Icon
ICON_BASE="${BUILD}/usr/share/icons/hicolor"
mkdir -p "${ICON_BASE}/scalable/apps"

cat > "${ICON_BASE}/scalable/apps/notepadplus.svg" << 'SVG'
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#4A90D9;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#2C5F8A;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect x="16" y="16" width="224" height="224" rx="24" fill="url(#bg)" />
  <rect x="48" y="40" width="160" height="186" rx="8" fill="#FFFFFF" />
  <path d="M 168 40 L 208 80 L 168 80 Z" fill="#D0D0D0" />
  <path d="M 168 40 L 208 80" stroke="#B0B0B0" stroke-width="1" fill="none" />
  <rect x="64" y="96" width="100" height="6" rx="3" fill="#4A90D9" />
  <rect x="64" y="114" width="128" height="6" rx="3" fill="#888888" />
  <rect x="64" y="132" width="80" height="6" rx="3" fill="#888888" />
  <rect x="64" y="150" width="112" height="6" rx="3" fill="#888888" />
  <rect x="64" y="168" width="96" height="6" rx="3" fill="#4A90D9" />
  <rect x="64" y="186" width="128" height="6" rx="3" fill="#888888" />
  <circle cx="200" cy="196" r="36" fill="#E8443A" />
  <rect x="188" y="190" width="24" height="6" rx="3" fill="#FFFFFF" />
  <rect x="197" y="181" width="6" height="24" rx="3" fill="#FFFFFF" />
</svg>
SVG

# Render PNG icons if possible
for size in 48 128 256; do
    mkdir -p "${ICON_BASE}/${size}x${size}/apps"
    if command -v rsvg-convert &> /dev/null; then
        rsvg-convert -w ${size} -h ${size} \
            "${ICON_BASE}/scalable/apps/notepadplus.svg" \
            > "${ICON_BASE}/${size}x${size}/apps/notepadplus.png"
    fi
done

# Set ownership (everything root:root)
# Build the .deb
cd "${SCRIPT_DIR}/dist"
dpkg-deb --build --root-owner-group "${PKG_DIR}"

echo ""
echo "  Package built: dist/${PKG_DIR}.deb"
echo ""
echo "  Install with:    sudo dpkg -i dist/${PKG_DIR}.deb"
echo "  Uninstall with:  sudo dpkg -r notepadplus"
echo ""

# Show package info
dpkg-deb --info "${PKG_DIR}.deb"
echo ""
ls -lh "${PKG_DIR}.deb"
