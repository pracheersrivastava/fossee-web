"""
Main Window
CHEM•VIZ - Chemical Equipment Parameter Visualizer

Main application window with Header, Sidebar, and MainContent.
Follows design.md specifications exactly.

Features:
- Backend API integration for all data operations
- User authentication via login/register dialogs
- PDF export functionality
"""

from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QSettings

from widgets import (
    Header, Sidebar, MainContent, ScreenPlaceholder,
    CSVUpload, SummaryScreen, AuthDialog
)
from charts import AnalysisCharts
from core.tokens import LAYOUT_MIN_CONTENT_WIDTH, LAYOUT_HEADER_HEIGHT
from core.api_client import api_client


PAGE_TITLES = {
    "upload": "Upload Equipment Data",
    "summary": "Data Summary",
    "analysis": "Parameter Analysis",
    "history": "Analysis History",
}

SCREEN_PLACEHOLDERS = {
    "history": "Analysis history table will appear here.",
}


class MainWindow(QMainWindow):
    """Main application window with backend integration and authentication."""

    def __init__(self):
        super().__init__()
        self._settings = QSettings("CHEMVIZ", "Desktop")
        self._current_screen = "upload"
        self._current_dataset_id: Optional[str] = None
        self._uploaded_data: Optional[Dict[str, Any]] = None
        self._current_user: Optional[Dict[str, Any]] = None
        self._pending_claim_dataset_id: Optional[str] = None  # Dataset to claim after login
        self._csv_upload: Optional[CSVUpload] = None
        self._summary_screen: Optional[SummaryScreen] = None
        self._analysis_charts: Optional[AnalysisCharts] = None
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
        self._navigate_to("upload")
        
        # Check backend connectivity on startup
        self._check_backend()
        
        # Restore saved auth token if available
        self._restore_auth_state()

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("CHEM•VIZ | Chemical Equipment Parameter Visualizer")
        self.setMinimumWidth(LAYOUT_MIN_CONTENT_WIDTH)
        self.setMinimumHeight(600)
        self.resize(1200, 800)

    def _setup_ui(self):
        """Initialize the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self._header = Header()
        self._header.setFixedHeight(LAYOUT_HEADER_HEIGHT)
        main_layout.addWidget(self._header)

        # Body (sidebar + main content)
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar()
        body_layout.addWidget(self._sidebar)

        # Main content
        self._main_content = MainContent()
        body_layout.addWidget(self._main_content, 1)

        main_layout.addWidget(body_widget, 1)

    def _connect_signals(self):
        """Connect widget signals."""
        self._sidebar.navigation_changed.connect(self._navigate_to)
        
        # Connect history signals
        history_widget = self._sidebar.get_history_widget()
        if history_widget:
            history_widget.dataset_selected.connect(self._on_history_dataset_selected)
            history_widget.reanalyze_clicked.connect(self._on_history_reanalyze)
        
        # Connect header auth signals
        self._header.login_clicked.connect(self._show_login_dialog)
        self._header.logout_clicked.connect(self._handle_logout)

    def _check_backend(self):
        """
        Check if backend is available.
        
        NOTE: Only checks connectivity. Does NOT fetch user data yet.
        User data is fetched in _restore_auth_state after token is validated.
        """
        if not api_client.health_check():
            QMessageBox.warning(
                self,
                "Backend Not Available",
                "Cannot connect to the backend server.\n\n"
                "Please ensure the Django server is running:\n"
                "cd backend && python manage.py runserver 8000"
            )
    
    def _restore_auth_state(self):
        """
        Try to restore authentication state from saved token.
        
        Called on app startup to restore previous session.
        If token is valid, also refresh user's data.
        """
        saved_token = self._settings.value("auth/token", "")
        
        # Update history widget auth state
        history_widget = self._sidebar.get_history_widget()
        
        if saved_token:
            # Set token first so API calls work
            api_client.set_token(saved_token)
            
            # Verify token is still valid
            user_info = api_client.get_user()
            if user_info and 'error' not in user_info:
                self._current_user = {
                    'username': user_info.get('username'),
                    'user_id': user_info.get('user_id'),
                    'token': saved_token,
                }
                self._header.set_user(self._current_user)
                
                # Set history widget as authenticated
                if history_widget:
                    history_widget.set_authenticated(True)
                
                # Refresh user's data (history, active dataset)
                self._refresh_user_data_after_login()
            else:
                # Token invalid, clear it
                api_client.set_token(None)
                self._settings.remove("auth/token")
                
                # Set history widget as not authenticated
                if history_widget:
                    history_widget.set_authenticated(False)
        else:
            # No saved token, set as not authenticated
            if history_widget:
                history_widget.set_authenticated(False)
    
    def _show_login_dialog(self):
        """Show the login/register dialog."""
        dialog = AuthDialog(self)
        dialog.authenticated.connect(self._on_auth_success)
        dialog.exec_()
    
    def _on_auth_success(self, user_info: Dict[str, Any]):
        """
        Handle successful authentication.
        
        CRITICAL DATA FLOW:
        1. Store user info and token
        2. Set token in api_client (MUST happen before any API calls)
        3. Update header UI
        4. Set history widget as authenticated
        5. Claim any pending anonymous dataset
        6. Fetch user's history from backend
        7. If history non-empty, set most recent dataset as active
        8. Fetch summary + analysis for active dataset
        """
        self._current_user = user_info
        
        # Save token for next session
        token = user_info.get('token', '')
        self._settings.setValue("auth/token", token)
        
        # CRITICAL: Set token in api_client BEFORE any other API calls
        api_client.set_token(token)
        
        # Update header to show logged-in user
        self._header.set_user(user_info)
        
        # Set history widget as authenticated (this will trigger refresh)
        history_widget = self._sidebar.get_history_widget()
        if history_widget:
            history_widget.set_authenticated(True)
        
        # Claim any pending anonymous dataset
        self._claim_pending_dataset()
        
        # Fetch user's history from backend
        self._refresh_user_data_after_login()
    
    def _claim_pending_dataset(self):
        """
        Claim the pending anonymous dataset after login.
        This syncs anonymous uploads to the user's history.
        """
        if not self._pending_claim_dataset_id:
            return
        
        dataset_id = self._pending_claim_dataset_id
        self._pending_claim_dataset_id = None  # Clear to prevent double claim
        
        try:
            result = api_client.claim_dataset(dataset_id)
            print(f"Dataset {dataset_id} claimed successfully")
            
            # Update current dataset to the claimed one
            self._current_dataset_id = dataset_id
        except Exception as e:
            print(f"Failed to claim dataset {dataset_id}: {e}")
            # Non-fatal - user can still use the app
    
    def _refresh_user_data_after_login(self):
        """
        Refresh all user-scoped data after successful login.
        
        This ensures desktop app behaves identically to web app:
        1. Fetch history (backend filters by request.user)
        2. If history not empty, set most recent dataset as active
        3. Navigate to summary to show the active dataset
        """
        try:
            # Step 1: Refresh history widget (shows user's datasets)
            history_widget = self._sidebar.get_history_widget()
            if history_widget:
                history_widget.refresh_from_backend()
            
            # Step 2: Fetch history to get most recent dataset
            history_result = api_client.get_history()
            datasets = history_result.get('datasets', [])
            
            if datasets:
                # Set most recent dataset as active
                most_recent = datasets[0]  # Backend returns sorted by upload_time desc
                dataset_id = most_recent.get('id') or most_recent.get('dataset_id')
                
                if dataset_id:
                    self._current_dataset_id = str(dataset_id)
                    self._uploaded_data = {
                        'dataset_id': self._current_dataset_id,
                        'fileName': most_recent.get('filename', most_recent.get('name', 'Unknown')),
                        'rowCount': most_recent.get('row_count', 0),
                    }
                    
                    # Navigate to summary to show the data
                    self._navigate_to("summary")
            else:
                # No datasets yet, stay on upload screen
                self._navigate_to("upload")
                
        except Exception as e:
            # Log error but don't crash - user can still upload new data
            print(f"Warning: Failed to refresh user data after login: {e}")
            self._navigate_to("upload")

    def _handle_logout(self):
        """
        Handle logout action.
        
        Clears all user state and navigates to upload screen.
        """
        if self._current_user:
            # Call logout API
            token = self._current_user.get('token')
            if token:
                api_client.logout(token)
        
        # Clear all user-specific state
        self._current_user = None
        self._current_dataset_id = None
        self._uploaded_data = None
        self._settings.remove("auth/token")
        api_client.set_token(None)
        
        # Update header to show logged-out state
        self._header.set_user(None)
        
        # Set history widget as not authenticated (this clears and shows login prompt)
        history_widget = self._sidebar.get_history_widget()
        if history_widget:
            history_widget.set_authenticated(False)
        
        # Navigate to upload screen
        self._navigate_to("upload")

    def _navigate_to(self, screen_id: str):
        """Navigate to a specific screen."""
        self._current_screen = screen_id
        self._sidebar.set_active_item(screen_id)
        
        title = PAGE_TITLES.get(screen_id, "")
        self._main_content.set_title(title)

        if screen_id == "upload":
            self._render_upload_screen()
        elif screen_id == "summary":
            self._render_summary_screen()
        elif screen_id == "analysis":
            self._render_analysis_screen()
        else:
            placeholder_text = SCREEN_PLACEHOLDERS.get(screen_id, "")
            placeholder = ScreenPlaceholder(placeholder_text)
            self._main_content.set_content(placeholder)

    def _render_upload_screen(self):
        """Render the CSV upload screen."""
        self._csv_upload = CSVUpload()
        self._csv_upload.upload_complete.connect(self._on_upload_complete)
        self._csv_upload.upload_cleared.connect(self._on_upload_cleared)
        self._main_content.set_content(self._csv_upload)

    def _render_summary_screen(self):
        """
        Render the summary screen.
        
        Always fetches data from backend via load_from_backend().
        Backend is the source of truth for all analytics data.
        """
        self._summary_screen = SummaryScreen()
        self._summary_screen.viewChartsClicked.connect(
            lambda: self._navigate_to("analysis")
        )
        self._summary_screen.uploadNewClicked.connect(
            lambda: self._navigate_to("upload")
        )
        self._summary_screen.exportClicked.connect(self._on_export_pdf)
        
        # Load from backend if we have a dataset_id
        if self._current_dataset_id:
            # Build file_info from whatever metadata we have
            file_info = {}
            if self._uploaded_data:
                file_info = {
                    'fileName': self._uploaded_data.get('fileName', 
                               self._uploaded_data.get('name', 'Unknown')),
                    'rowCount': self._uploaded_data.get('rowCount', 
                               self._uploaded_data.get('row_count', 0)),
                    'fileSize': self._uploaded_data.get('fileSize', 
                               self._uploaded_data.get('file_size', 0)),
                    'columnCount': self._uploaded_data.get('columnCount', 
                                  self._uploaded_data.get('column_count', 0)),
                    'hasIssues': len(self._uploaded_data.get('issues', [])) > 0,
                }
            
            # Fetch summary from backend
            self._summary_screen.load_from_backend(
                self._current_dataset_id,
                file_info=file_info
            )
        
        self._main_content.set_content(self._summary_screen)

    def _render_analysis_screen(self):
        """Render the analysis charts screen."""
        self._analysis_charts = AnalysisCharts()
        
        # Load from backend if we have a dataset_id
        if self._current_dataset_id:
            self._analysis_charts.load_from_backend(self._current_dataset_id)
        
        self._main_content.set_content(self._analysis_charts)

    def _on_upload_complete(self, data: Dict[str, Any]):
        """
        Handle successful CSV upload from backend.
        
        CRITICAL DATA FLOW:
        1. Store dataset_id from backend response
        2. Store upload metadata (fileName, rowCount, etc)
        3. If not authenticated, mark dataset for claiming after login
        4. Refresh history to show new dataset (if authenticated)
        5. Navigate to summary (which will fetch summary data from backend)
        """
        # Get dataset_id from response (backend may use 'dataset_id' or 'id')
        dataset_id = data.get('dataset_id') or data.get('id')
        if dataset_id:
            self._current_dataset_id = str(dataset_id)
        else:
            print("Warning: Upload response missing dataset_id!")
            return
        
        # Store upload metadata for display
        self._uploaded_data = {
            'dataset_id': self._current_dataset_id,
            'fileName': data.get('name', data.get('filename', 'Unknown')),
            'rowCount': data.get('row_count', 0),
            'columnCount': data.get('column_count', 0),
            'fileSize': data.get('file_size', 0),
            'issues': data.get('validation', {}).get('issues', []),
        }
        
        # If not authenticated, mark this dataset for claiming after login
        if not self._current_user:
            self._pending_claim_dataset_id = self._current_dataset_id
            print(f"Anonymous upload - dataset {self._current_dataset_id} pending claim after login")
        
        # Refresh history to show the new dataset (only if authenticated)
        if self._current_user:
            history_widget = self._sidebar.get_history_widget()
            if history_widget:
                history_widget.refresh_from_backend()
        
        # Auto-navigate to summary (will fetch summary data from backend)
        self._navigate_to("summary")

    def _on_upload_cleared(self):
        """Handle upload cleared."""
        self._uploaded_data = None
        self._current_dataset_id = None

    def _on_history_dataset_selected(self, dataset_id: str):
        """Handle dataset selection from history."""
        self._current_dataset_id = dataset_id
        
        # Fetch dataset details from backend to get filename, row_count, etc.
        try:
            dataset_info = api_client.get_dataset(dataset_id)
            self._uploaded_data = {
                'dataset_id': dataset_id,
                'fileName': dataset_info.get('original_filename', dataset_info.get('name', 'Unknown')),
                'rowCount': dataset_info.get('row_count', 0),
                'columnCount': dataset_info.get('column_count', 0),
                'fileSize': dataset_info.get('file_size', 0),
            }
        except Exception as e:
            print(f"Warning: Could not fetch dataset details: {e}")
            self._uploaded_data = {'dataset_id': dataset_id}
        
        self._navigate_to("summary")

    def _on_history_reanalyze(self, dataset_id: str):
        """Handle re-analyze action from history."""
        self._current_dataset_id = dataset_id
        self._uploaded_data = {'dataset_id': dataset_id}
        self._navigate_to("analysis")

    def _on_export_pdf(self):
        """Handle PDF export request."""
        if not self._current_dataset_id:
            QMessageBox.warning(self, "No Data", "Please upload a dataset first.")
            return
        
        # Import PDF generator
        try:
            from config.pdf_generator import generate_pdf_report
            generate_pdf_report(self._current_dataset_id, self)
        except ImportError as e:
            QMessageBox.information(
                self,
                "Export PDF",
                f"PDF export requires ReportLab.\n\n"
                f"Install with: pip install reportlab\n\n"
                f"Error: {str(e)}"
            )

    def get_current_screen(self) -> str:
        """Get the current screen ID."""
        return self._current_screen

    def get_current_dataset_id(self) -> Optional[str]:
        """Get the current dataset ID."""
        return self._current_dataset_id

    def get_uploaded_data(self) -> Optional[Dict[str, Any]]:
        """Get the current uploaded data."""
        return self._uploaded_data
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get the current user info."""
        return self._current_user
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self._current_user is not None
