"""
MainContent Widget
FOSSEE Scientific Analytics UI

Main content area with proper spacing and scroll support.
Padding: 24px (lg)
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame
)
from PyQt5.QtCore import Qt

from ..core.tokens import SPACE_LG, LAYOUT_MAX_WIDTH, LAYOUT_SIDEBAR_WIDTH


class MainContent(QWidget):
    """Main content area with scroll support."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mainContent")
        self._title_label = None
        self._content_widget = None
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the main content UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setObjectName("mainScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Inner content widget
        inner_widget = QWidget()
        inner_widget.setObjectName("mainContentInner")
        inner_widget.setMaximumWidth(LAYOUT_MAX_WIDTH - LAYOUT_SIDEBAR_WIDTH)

        inner_layout = QVBoxLayout(inner_widget)
        inner_layout.setContentsMargins(SPACE_LG, SPACE_LG, SPACE_LG, SPACE_LG)
        inner_layout.setSpacing(0)

        # Page title
        self._title_label = QLabel()
        self._title_label.setProperty("class", "h1")
        inner_layout.addWidget(self._title_label)

        # Content container
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(SPACE_LG)
        inner_layout.addWidget(self._content_widget)

        # Stretch at bottom
        inner_layout.addStretch()

        scroll_area.setWidget(inner_widget)
        layout.addWidget(scroll_area)

    def set_title(self, title: str):
        """Set the page title."""
        self._title_label.setText(title)

    def set_content(self, widget: QWidget):
        """Set the main content widget."""
        # Clear existing content
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new content
        if widget:
            self._content_layout.addWidget(widget)

    def add_content(self, widget: QWidget):
        """Add a widget to the content area."""
        self._content_layout.addWidget(widget)

    def clear_content(self):
        """Clear all content widgets."""
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class ScreenPlaceholder(QFrame):
    """Placeholder widget for screen content."""

    def __init__(self, message: str, parent=None):
        super().__init__(parent)
        self.setProperty("class", "placeholder")
        self.setMinimumHeight(200)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel(message)
        label.setProperty("class", "textSecondary")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
