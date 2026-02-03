"""
Sidebar Widget
FOSSEE Scientific Analytics UI

Navigation sidebar with dataset history.
Width: 240px, Background: Pure White (#FFFFFF)
"""

from typing import List, Dict, Any, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QButtonGroup
)
from PyQt5.QtCore import Qt, pyqtSignal

from ..core.tokens import SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG
from .dataset_history import DatasetHistory


class NavItem(QPushButton):
    """Navigation item button."""

    def __init__(self, icon: str, label: str, item_id: str, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.setText(f"  {icon}    {label}")
        self.setProperty("class", "navItem")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)


class Sidebar(QWidget):
    """Application sidebar with navigation and history."""

    # Signal emitted when navigation item is clicked
    navigation_changed = pyqtSignal(str)
    # Dataset history signals
    reanalyze_clicked = pyqtSignal(str)
    compare_clicked = pyqtSignal(str)
    clear_history_clicked = pyqtSignal()

    NAV_ITEMS = [
        ("↑", "Upload", "upload"),
        ("▤", "Summary", "summary"),
        ("◩", "Analysis", "analysis"),
        ("◷", "History", "history"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._nav_buttons = {}
        self._setup_ui()
        self.set_active_item("upload")

    def _setup_ui(self):
        """Initialize the sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, SPACE_MD, 0, 0)
        layout.setSpacing(0)

        # Navigation section
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        for icon, label, item_id in self.NAV_ITEMS:
            btn = NavItem(icon, label, item_id)
            self._nav_buttons[item_id] = btn
            self._nav_group.addButton(btn)
            layout.addWidget(btn)
            btn.clicked.connect(lambda checked, id=item_id: self._on_nav_click(id))

        # Spacer before history
        layout.addSpacing(SPACE_MD)

        # History section separator
        history_separator = QFrame()
        history_separator.setFrameShape(QFrame.HLine)
        history_separator.setStyleSheet("background-color: #CBD5E1; max-height: 1px;")
        layout.addWidget(history_separator)

        # Dataset History widget
        self._dataset_history = DatasetHistory(max_items=5)
        self._dataset_history.reanalyze_clicked.connect(self.reanalyze_clicked.emit)
        self._dataset_history.compare_clicked.connect(self.compare_clicked.emit)
        self._dataset_history.clear_history_clicked.connect(self.clear_history_clicked.emit)
        layout.addWidget(self._dataset_history, 1)

        # Footer separator
        footer_separator = QFrame()
        footer_separator.setFrameShape(QFrame.HLine)
        footer_separator.setStyleSheet("background-color: #CBD5E1; max-height: 1px;")
        layout.addWidget(footer_separator)

        # Footer
        footer_widget = QWidget()
        footer_widget.setObjectName("sidebarFooter")
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(SPACE_LG, SPACE_MD, SPACE_LG, SPACE_MD)
        footer_layout.setSpacing(SPACE_XS)

        fossee_label = QLabel("FOSSEE Project")
        fossee_label.setProperty("class", "sidebarFooterText")
        footer_layout.addWidget(fossee_label)

        iit_label = QLabel("IIT Bombay")
        iit_label.setProperty("class", "sidebarFooterText")
        footer_layout.addWidget(iit_label)

        layout.addWidget(footer_widget)

    def _on_nav_click(self, item_id: str):
        """Handle navigation item click."""
        self.navigation_changed.emit(item_id)

    def set_active_item(self, item_id: str):
        """Set the active navigation item."""
        if item_id in self._nav_buttons:
            self._nav_buttons[item_id].setChecked(True)

    def set_datasets(self, datasets: List[Dict[str, Any]]):
        """Set the dataset history."""
        self._dataset_history.set_datasets(datasets)

    def set_selected_dataset(self, dataset_id: Optional[str]):
        """Set the selected dataset in history."""
        self._dataset_history.set_selected(dataset_id)

    def add_dataset(self, dataset: Dict[str, Any]):
        """Add a new dataset to history."""
        self._dataset_history.add_dataset(dataset)

    def clear_history(self):
        """Clear dataset history."""
        self._dataset_history.clear()
