"""
Header Widget
FOSSEE Scientific Analytics UI

Persistent header with app title and FOSSEE branding.
Height: 56px, Background: Deep Indigo (#1E2A38)
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt

from ..core.tokens import SPACE_LG, SPACE_SM


class Header(QWidget):
    """Application header with logo and title."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("header")
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the header UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACE_LG, 0, SPACE_LG, 0)
        layout.setSpacing(SPACE_SM)

        # Brand section
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(SPACE_SM)

        # Logo
        logo_label = QLabel("⬡")
        logo_label.setObjectName("headerLogo")
        brand_layout.addWidget(logo_label)

        # Title
        title_label = QLabel("CHEM•VIZ")
        title_label.setObjectName("headerTitle")
        brand_layout.addWidget(title_label)

        layout.addLayout(brand_layout)

        # Spacer
        layout.addStretch()

        # FOSSEE branding
        fossee_label = QLabel("FOSSEE")
        fossee_label.setObjectName("headerFossee")
        layout.addWidget(fossee_label)
