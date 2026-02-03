"""
CHEM•VIZ Desktop Application
FOSSEE Scientific Analytics UI

Entry point for the PyQt5 desktop application.
"""

import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import Qt

from main_window import MainWindow


def load_stylesheet() -> str:
    """Load the QSS stylesheet."""
    style_path = Path(__file__).parent / "styles" / "theme.qss"
    
    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            return f.read()
    
    print(f"Warning: Stylesheet not found at {style_path}")
    return ""


def setup_fonts():
    """Load and configure application fonts."""
    # Try to load Source Sans 3 if available
    # Falls back to system fonts as defined in QSS
    
    # Set default application font
    font = QFont("Source Sans 3", 14)
    font.setStyleHint(QFont.SansSerif)
    QApplication.setFont(font)


def main():
    """Main entry point."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("CHEM•VIZ")
    app.setOrganizationName("FOSSEE")
    app.setOrganizationDomain("fossee.in")

    # Setup fonts
    setup_fonts()

    # Load and apply stylesheet
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
