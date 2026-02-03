"""
CHEM•VIZ Desktop Package
FOSSEE Scientific Analytics UI
"""

from .main_window import MainWindow
from .widgets import Header, Sidebar, MainContent, ScreenPlaceholder
from .core import tokens

__version__ = "1.0.0"
__all__ = [
    "MainWindow",
    "Header",
    "Sidebar",
    "MainContent",
    "ScreenPlaceholder",
    "tokens",
]
