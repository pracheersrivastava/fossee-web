"""
Header Widget
CHEM•VIZ - Chemical Equipment Parameter Visualizer

Persistent header with app title and user menu.
Height: 56px, Background: Deep Indigo (#1E2A38)

Per design.md tokens:
- Deep Indigo: #1E2A38 (header bg)
- Academic Blue: #2F80ED (logo)
- Font: Source Sans 3, 18px/600 for title
"""

from typing import Optional, Dict, Any

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

from core.tokens import SPACE_LG, SPACE_SM


class Header(QWidget):
    """Application header with logo, title, and user menu."""
    
    # Signals
    login_clicked = pyqtSignal()
    logout_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("header")
        self._user_info: Optional[Dict[str, Any]] = None
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the header UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACE_LG, 0, SPACE_LG, 0)
        layout.setSpacing(SPACE_SM)

        # Brand section
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(SPACE_SM)

        # Logo - Academic Blue per design.md
        logo_label = QLabel("⬡")
        logo_label.setObjectName("headerLogo")
        logo_label.setStyleSheet("""
            color: #2F80ED;
            font-size: 24px;
        """)
        brand_layout.addWidget(logo_label)

        # Title - 18px/600 per design.md
        title_label = QLabel("CHEM•VIZ")
        title_label.setObjectName("headerTitle")
        title_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 18px;
            font-weight: 600;
            letter-spacing: 0.5px;
        """)
        brand_layout.addWidget(title_label)

        layout.addLayout(brand_layout)

        # Spacer
        layout.addStretch()

        # User section (login button or user menu)
        self._user_section = QHBoxLayout()
        self._user_section.setSpacing(SPACE_SM)
        
        # Login button (shown when not logged in)
        self._login_btn = QPushButton("Login")
        self._login_btn.setObjectName("headerLoginBtn")
        self._login_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: 500;
                min-height: 32px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        self._login_btn.setCursor(Qt.PointingHandCursor)
        self._login_btn.clicked.connect(self.login_clicked.emit)
        self._user_section.addWidget(self._login_btn)
        
        # User label (shown when logged in)
        self._user_label = QLabel()
        self._user_label.setObjectName("headerUserLabel")
        self._user_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 13px;
            font-weight: 500;
        """)
        self._user_label.hide()
        self._user_section.addWidget(self._user_label)
        
        # Logout button (shown when logged in)
        self._logout_btn = QPushButton("Logout")
        self._logout_btn.setObjectName("headerLogoutBtn")
        self._logout_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(255, 255, 255, 0.7);
                border: none;
                padding: 6px 12px;
                font-size: 12px;
                min-height: 32px;
            }
            QPushButton:hover {
                color: #F87171;
            }
        """)
        self._logout_btn.setCursor(Qt.PointingHandCursor)
        self._logout_btn.clicked.connect(self.logout_clicked.emit)
        self._logout_btn.hide()
        self._user_section.addWidget(self._logout_btn)
        
        layout.addLayout(self._user_section)

    def set_user(self, user_info: Optional[Dict[str, Any]]):
        """
        Set the current user info.
        
        Args:
            user_info: User dict or None to clear
        """
        self._user_info = user_info
        
        if user_info:
            username = user_info.get('username', 'User')
            self._user_label.setText(f"👤 {username}")
            self._user_label.show()
            self._logout_btn.show()
            self._login_btn.hide()
        else:
            self._user_label.hide()
            self._logout_btn.hide()
            self._login_btn.show()
    
    def get_user(self) -> Optional[Dict[str, Any]]:
        """Get the current user info."""
        return self._user_info
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in."""
        return self._user_info is not None
