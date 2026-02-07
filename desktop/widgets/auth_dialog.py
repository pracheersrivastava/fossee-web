"""
Authentication Dialogs
CHEM•VIZ - Chemical Equipment Parameter Visualizer

Login and Register dialogs for Desktop application.
Connects to Django backend auth endpoints.
"""

from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QFrame, QMessageBox, QTabWidget,
    QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QSettings

from core.tokens import SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL
from core.api_client import api_client


class AuthDialog(QDialog):
    """
    Combined Login/Register dialog with tabs.
    
    Signals:
        authenticated: Emitted when login/register succeeds, passes user info dict
    """
    
    authenticated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CHEM•VIZ - Login")
        self.setMinimumWidth(400)
        self.setMinimumHeight(350)
        self.setModal(True)
        
        self._settings = QSettings("CHEMVIZ", "Desktop")
        self._current_token: Optional[str] = None
        self._current_user: Optional[Dict[str, Any]] = None
        
        self._setup_ui()
        self._load_saved_username()
    
    def _setup_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_LG, SPACE_LG, SPACE_LG, SPACE_LG)
        layout.setSpacing(SPACE_MD)
        
        # Title
        title_label = QLabel("CHEM•VIZ")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1E2A38;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Chemical Equipment Parameter Visualizer")
        subtitle_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(SPACE_MD)
        
        # Tab widget for Login/Register
        self._tab_widget = QTabWidget()
        self._tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                background: white;
            }
            QTabBar::tab {
                padding: 8px 24px;
                background: #F8FAFC;
                border: 1px solid #E5E7EB;
                border-bottom: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
            }
        """)
        
        # Login tab
        login_widget = self._create_login_tab()
        self._tab_widget.addTab(login_widget, "Login")
        
        # Register tab
        register_widget = self._create_register_tab()
        self._tab_widget.addTab(register_widget, "Register")
        
        layout.addWidget(self._tab_widget)
        
        # Error message area
        self._error_label = QLabel()
        self._error_label.setStyleSheet("""
            color: #DC2626;
            background: #FEE2E2;
            padding: 8px;
            border-radius: 4px;
        """)
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)
        
        # Success message area
        self._success_label = QLabel()
        self._success_label.setStyleSheet("""
            color: #22C55E;
            background: #DCFCE7;
            padding: 8px;
            border-radius: 4px;
        """)
        self._success_label.setWordWrap(True)
        self._success_label.hide()
        layout.addWidget(self._success_label)
    
    def _create_login_tab(self) -> QWidget:
        """Create the login form tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setContentsMargins(SPACE_MD, SPACE_MD, SPACE_MD, SPACE_MD)
        layout.setSpacing(SPACE_MD)
        
        # Username field
        self._login_username = QLineEdit()
        self._login_username.setPlaceholderText("Enter your username")
        self._login_username.setStyleSheet(self._get_input_style())
        layout.addRow("Username:", self._login_username)
        
        # Password field
        self._login_password = QLineEdit()
        self._login_password.setPlaceholderText("Enter your password")
        self._login_password.setEchoMode(QLineEdit.Password)
        self._login_password.setStyleSheet(self._get_input_style())
        self._login_password.returnPressed.connect(self._handle_login)
        layout.addRow("Password:", self._login_password)
        
        # Remember username checkbox would go here
        
        # Login button
        self._login_btn = QPushButton("Login")
        self._login_btn.setStyleSheet(self._get_primary_btn_style())
        self._login_btn.setCursor(Qt.PointingHandCursor)
        self._login_btn.clicked.connect(self._handle_login)
        layout.addRow("", self._login_btn)
        
        return widget
    
    def _create_register_tab(self) -> QWidget:
        """Create the register form tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setContentsMargins(SPACE_MD, SPACE_MD, SPACE_MD, SPACE_MD)
        layout.setSpacing(SPACE_MD)
        
        # Username field
        self._register_username = QLineEdit()
        self._register_username.setPlaceholderText("Choose a username")
        self._register_username.setStyleSheet(self._get_input_style())
        layout.addRow("Username:", self._register_username)
        
        # Email field
        self._register_email = QLineEdit()
        self._register_email.setPlaceholderText("your@email.com (optional)")
        self._register_email.setStyleSheet(self._get_input_style())
        layout.addRow("Email:", self._register_email)
        
        # Password field
        self._register_password = QLineEdit()
        self._register_password.setPlaceholderText("Choose a password")
        self._register_password.setEchoMode(QLineEdit.Password)
        self._register_password.setStyleSheet(self._get_input_style())
        layout.addRow("Password:", self._register_password)
        
        # Confirm password field
        self._register_confirm = QLineEdit()
        self._register_confirm.setPlaceholderText("Confirm your password")
        self._register_confirm.setEchoMode(QLineEdit.Password)
        self._register_confirm.setStyleSheet(self._get_input_style())
        self._register_confirm.returnPressed.connect(self._handle_register)
        layout.addRow("Confirm:", self._register_confirm)
        
        # Register button
        self._register_btn = QPushButton("Register")
        self._register_btn.setStyleSheet(self._get_primary_btn_style())
        self._register_btn.setCursor(Qt.PointingHandCursor)
        self._register_btn.clicked.connect(self._handle_register)
        layout.addRow("", self._register_btn)
        
        return widget
    
    def _get_input_style(self) -> str:
        """Get consistent input field styling."""
        return """
            QLineEdit {
                padding: 10px 12px;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                background: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #2F80ED;
            }
            QLineEdit::placeholder {
                color: #9CA3AF;
            }
        """
    
    def _get_primary_btn_style(self) -> str:
        """Get primary button styling."""
        return """
            QPushButton {
                background: #2F80ED;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #1D6FDB;
            }
            QPushButton:pressed {
                background: #1557B0;
            }
            QPushButton:disabled {
                background: #9CA3AF;
            }
        """
    
    def _load_saved_username(self):
        """Load saved username from settings."""
        saved_username = self._settings.value("auth/username", "")
        if saved_username:
            self._login_username.setText(saved_username)
    
    def _save_username(self, username: str):
        """Save username to settings."""
        self._settings.setValue("auth/username", username)
    
    def _show_error(self, message: str):
        """Display an error message."""
        self._success_label.hide()
        self._error_label.setText(message)
        self._error_label.show()
    
    def _show_success(self, message: str):
        """Display a success message."""
        self._error_label.hide()
        self._success_label.setText(message)
        self._success_label.show()
    
    def _clear_messages(self):
        """Clear all messages."""
        self._error_label.hide()
        self._success_label.hide()
    
    def _handle_login(self):
        """Handle login button click."""
        self._clear_messages()
        
        username = self._login_username.text().strip()
        password = self._login_password.text()
        
        if not username or not password:
            self._show_error("Please enter both username and password.")
            return
        
        # Disable button during request
        self._login_btn.setEnabled(False)
        self._login_btn.setText("Logging in...")
        
        try:
            result = api_client.login(username, password)
            
            if 'error' in result:
                self._show_error(result['error'])
                return
            
            # Success
            self._current_token = result.get('token')
            self._current_user = {
                'user_id': result.get('user_id'),
                'username': result.get('username'),
                'token': self._current_token,
            }
            
            # Save username for next time
            self._save_username(username)
            
            # Emit signal and close
            self.authenticated.emit(self._current_user)
            self.accept()
            
        except Exception as e:
            self._show_error(f"Login failed: {str(e)}")
        finally:
            self._login_btn.setEnabled(True)
            self._login_btn.setText("Login")
    
    def _handle_register(self):
        """Handle register button click."""
        self._clear_messages()
        
        username = self._register_username.text().strip()
        email = self._register_email.text().strip()
        password = self._register_password.text()
        confirm = self._register_confirm.text()
        
        # Validation
        if not username:
            self._show_error("Please enter a username.")
            return
        
        if len(username) < 3:
            self._show_error("Username must be at least 3 characters.")
            return
        
        if not password:
            self._show_error("Please enter a password.")
            return
        
        if len(password) < 6:
            self._show_error("Password must be at least 6 characters.")
            return
        
        if password != confirm:
            self._show_error("Passwords do not match.")
            return
        
        # Disable button during request
        self._register_btn.setEnabled(False)
        self._register_btn.setText("Registering...")
        
        try:
            result = api_client.register(username, password, email)
            
            if 'error' in result:
                self._show_error(result['error'])
                return
            
            # Success - auto-login
            self._current_token = result.get('token')
            self._current_user = {
                'user_id': result.get('user_id'),
                'username': result.get('username'),
                'token': self._current_token,
            }
            
            # Save username
            self._save_username(username)
            
            # Emit signal and close
            self.authenticated.emit(self._current_user)
            self.accept()
            
        except Exception as e:
            self._show_error(f"Registration failed: {str(e)}")
        finally:
            self._register_btn.setEnabled(True)
            self._register_btn.setText("Register")
    
    def get_token(self) -> Optional[str]:
        """Get the current auth token."""
        return self._current_token
    
    def get_user(self) -> Optional[Dict[str, Any]]:
        """Get the current user info."""
        return self._current_user


class UserMenuWidget(QWidget):
    """
    Small user menu widget showing current user and logout button.
    
    Signals:
        logout_clicked: Emitted when logout button is clicked
    """
    
    logout_clicked = pyqtSignal()
    
    def __init__(self, user_info: Dict[str, Any], parent=None):
        super().__init__(parent)
        self._user_info = user_info
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACE_SM, SPACE_SM, SPACE_SM, SPACE_SM)
        layout.setSpacing(SPACE_SM)
        
        # User icon
        icon_label = QLabel("👤")
        layout.addWidget(icon_label)
        
        # Username
        username = self._user_info.get('username', 'User')
        user_label = QLabel(username)
        user_label.setStyleSheet("color: #1E2A38; font-weight: 500;")
        layout.addWidget(user_label)
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #6B7280;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #F3F4F6;
                color: #DC2626;
            }
        """)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout_clicked.emit)
        layout.addWidget(logout_btn)
    
    def update_user(self, user_info: Dict[str, Any]):
        """Update the displayed user info."""
        self._user_info = user_info
        # Would need to rebuild UI or update labels


def show_login_dialog(parent=None) -> Optional[Dict[str, Any]]:
    """
    Show the login dialog and return user info if authenticated.
    
    Returns:
        User info dict if authenticated, None if cancelled
    """
    dialog = AuthDialog(parent)
    result = dialog.exec_()
    
    if result == QDialog.Accepted:
        return dialog.get_user()
    return None
