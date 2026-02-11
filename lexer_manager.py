"""Syntax highlighting lexer configuration for NotepadPlus."""

import os
from PyQt5.Qsci import (
    QsciLexerPython,
    QsciLexerCPP,
    QsciLexerJavaScript,
    QsciLexerHTML,
    QsciLexerCSS,
    QsciLexerSQL,
    QsciLexerBash,
    QsciLexerJSON,
    QsciLexerXML,
    QsciLexerMarkdown,
    QsciLexerYAML,
    QsciLexerLua,
    QsciLexerMakefile,
    QsciLexerPerl,
    QsciLexerRuby,
    QsciLexerBatch,
    QsciLexerDiff,
    QsciLexerProperties,
    QsciLexerCMake,
)

# Extension to (LexerClass, LanguageName) mapping
EXTENSION_MAP = {
    # Python
    ".py": (QsciLexerPython, "Python"),
    ".pyw": (QsciLexerPython, "Python"),
    ".pyi": (QsciLexerPython, "Python"),
    # C/C++
    ".c": (QsciLexerCPP, "C"),
    ".h": (QsciLexerCPP, "C"),
    ".cpp": (QsciLexerCPP, "C++"),
    ".cxx": (QsciLexerCPP, "C++"),
    ".cc": (QsciLexerCPP, "C++"),
    ".hpp": (QsciLexerCPP, "C++"),
    ".hxx": (QsciLexerCPP, "C++"),
    # Java/C#
    ".java": (QsciLexerCPP, "Java"),
    ".cs": (QsciLexerCPP, "C#"),
    # JavaScript/TypeScript
    ".js": (QsciLexerJavaScript, "JavaScript"),
    ".jsx": (QsciLexerJavaScript, "JavaScript"),
    ".ts": (QsciLexerJavaScript, "TypeScript"),
    ".tsx": (QsciLexerJavaScript, "TypeScript"),
    ".mjs": (QsciLexerJavaScript, "JavaScript"),
    # Web
    ".html": (QsciLexerHTML, "HTML"),
    ".htm": (QsciLexerHTML, "HTML"),
    ".xhtml": (QsciLexerHTML, "HTML"),
    ".php": (QsciLexerHTML, "PHP"),
    ".css": (QsciLexerCSS, "CSS"),
    ".scss": (QsciLexerCSS, "SCSS"),
    ".less": (QsciLexerCSS, "LESS"),
    # Data/Config
    ".json": (QsciLexerJSON, "JSON"),
    ".xml": (QsciLexerXML, "XML"),
    ".svg": (QsciLexerXML, "SVG"),
    ".yaml": (QsciLexerYAML, "YAML"),
    ".yml": (QsciLexerYAML, "YAML"),
    ".toml": (QsciLexerProperties, "TOML"),
    ".ini": (QsciLexerProperties, "INI"),
    ".cfg": (QsciLexerProperties, "Config"),
    ".conf": (QsciLexerProperties, "Config"),
    ".properties": (QsciLexerProperties, "Properties"),
    # Shell
    ".sh": (QsciLexerBash, "Bash"),
    ".bash": (QsciLexerBash, "Bash"),
    ".zsh": (QsciLexerBash, "Zsh"),
    ".fish": (QsciLexerBash, "Fish"),
    ".bat": (QsciLexerBatch, "Batch"),
    ".cmd": (QsciLexerBatch, "Batch"),
    # Database
    ".sql": (QsciLexerSQL, "SQL"),
    # Markup
    ".md": (QsciLexerMarkdown, "Markdown"),
    ".markdown": (QsciLexerMarkdown, "Markdown"),
    ".rst": (QsciLexerMarkdown, "reStructuredText"),
    # Other languages
    ".lua": (QsciLexerLua, "Lua"),
    ".pl": (QsciLexerPerl, "Perl"),
    ".pm": (QsciLexerPerl, "Perl"),
    ".rb": (QsciLexerRuby, "Ruby"),
    ".rake": (QsciLexerRuby, "Ruby"),
    ".diff": (QsciLexerDiff, "Diff"),
    ".patch": (QsciLexerDiff, "Diff"),
    # Build systems
    ".cmake": (QsciLexerCMake, "CMake"),
}

# Filename-based detection (no extension)
FILENAME_MAP = {
    "Makefile": (QsciLexerMakefile, "Makefile"),
    "makefile": (QsciLexerMakefile, "Makefile"),
    "GNUmakefile": (QsciLexerMakefile, "Makefile"),
    "Dockerfile": (QsciLexerBash, "Dockerfile"),
    "CMakeLists.txt": (QsciLexerCMake, "CMake"),
    ".bashrc": (QsciLexerBash, "Bash"),
    ".bash_profile": (QsciLexerBash, "Bash"),
    ".zshrc": (QsciLexerBash, "Zsh"),
    ".profile": (QsciLexerBash, "Bash"),
    ".gitignore": (QsciLexerProperties, "Git Ignore"),
    ".editorconfig": (QsciLexerProperties, "EditorConfig"),
}

# Language name to lexer class (for manual selection)
LANGUAGE_LEXER_MAP = {
    "Plain Text": None,
    "Python": QsciLexerPython,
    "C": QsciLexerCPP,
    "C++": QsciLexerCPP,
    "Java": QsciLexerCPP,
    "C#": QsciLexerCPP,
    "JavaScript": QsciLexerJavaScript,
    "TypeScript": QsciLexerJavaScript,
    "HTML": QsciLexerHTML,
    "CSS": QsciLexerCSS,
    "SQL": QsciLexerSQL,
    "Bash": QsciLexerBash,
    "JSON": QsciLexerJSON,
    "XML": QsciLexerXML,
    "Markdown": QsciLexerMarkdown,
    "YAML": QsciLexerYAML,
    "Lua": QsciLexerLua,
    "Makefile": QsciLexerMakefile,
    "Perl": QsciLexerPerl,
    "Ruby": QsciLexerRuby,
    "Batch": QsciLexerBatch,
    "Diff": QsciLexerDiff,
    "Properties": QsciLexerProperties,
    "CMake": QsciLexerCMake,
}


def get_lexer_for_file(filename, parent=None):
    """Return an appropriate QScintilla lexer instance for the given filename."""
    if not filename:
        return None

    basename = os.path.basename(filename)

    # Check exact filename match first
    if basename in FILENAME_MAP:
        lexer_cls, _ = FILENAME_MAP[basename]
        return lexer_cls(parent) if lexer_cls else None

    # Check extension
    _, ext = os.path.splitext(basename)
    ext = ext.lower()
    if ext in EXTENSION_MAP:
        lexer_cls, _ = EXTENSION_MAP[ext]
        return lexer_cls(parent) if lexer_cls else None

    return None


def get_language_name(filename):
    """Return the language name for the given filename."""
    if not filename:
        return "Plain Text"

    basename = os.path.basename(filename)

    if basename in FILENAME_MAP:
        _, name = FILENAME_MAP[basename]
        return name

    _, ext = os.path.splitext(basename)
    ext = ext.lower()
    if ext in EXTENSION_MAP:
        _, name = EXTENSION_MAP[ext]
        return name

    return "Plain Text"


def get_lexer_for_language(language_name, parent=None):
    """Return a lexer instance for a language name (for manual selection)."""
    lexer_cls = LANGUAGE_LEXER_MAP.get(language_name)
    if lexer_cls:
        return lexer_cls(parent)
    return None


def get_available_languages():
    """Return sorted list of available language names."""
    return sorted(LANGUAGE_LEXER_MAP.keys())
