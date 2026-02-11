#!/bin/bash
#
# NotepadPlus Uninstaller
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

info()  { echo -e "${GREEN}[+]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1"; exit 1; }

if [ "$EUID" -ne 0 ]; then
    error "Please run as root: sudo ./uninstall.sh"
fi

echo ""
echo "  NotepadPlus Uninstaller"
echo "  ======================="
echo ""

info "Removing application files..."
rm -rf /opt/notepadplus

info "Removing launcher..."
rm -f /usr/local/bin/notepadplus

info "Removing desktop entry..."
rm -f /usr/share/applications/notepadplus.desktop

info "Removing icons..."
rm -f /usr/share/icons/hicolor/scalable/apps/notepadplus.svg
rm -f /usr/share/icons/hicolor/48x48/apps/notepadplus.png
rm -f /usr/share/icons/hicolor/128x128/apps/notepadplus.png
rm -f /usr/share/icons/hicolor/256x256/apps/notepadplus.png

if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications/ 2>/dev/null || true
fi
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi

echo ""
info "NotepadPlus has been uninstalled."
echo "  User settings remain at ~/.config/notepadplus/"
echo "  To remove those too: rm -rf ~/.config/notepadplus"
echo ""
