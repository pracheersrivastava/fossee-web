"""
Main Window
FOSSEE Scientific Analytics UI - CHEM•VIZ

Main application window with Header, Sidebar, and MainContent.
Follows design.md specifications exactly.
"""

from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt

from .widgets import (
    Header, Sidebar, MainContent, ScreenPlaceholder,
    CSVUpload, SummaryScreen
)
from .charts import AnalysisCharts
from .core.tokens import LAYOUT_MIN_CONTENT_WIDTH, LAYOUT_HEADER_HEIGHT


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
    """Main application window."""

    def __init__(self):
        super().__init__()
        self._current_screen = "upload"
        self._uploaded_data: Optional[Dict[str, Any]] = None
        self._csv_upload: Optional[CSVUpload] = None
        self._summary_screen: Optional[SummaryScreen] = None
        self._analysis_charts: Optional[AnalysisCharts] = None
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
        self._navigate_to("upload")

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("CHEM•VIZ | FOSSEE Scientific Analytics")
        self.setMinimumWidth(LAYOUT_MIN_CONTENT_WIDTH)
        self.setMinimumHeight(600)

        # Set initial size
        self.resize(1200, 800)

    def _setup_ui(self):
        """Initialize the main UI layout."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout (header + body)
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
        body_layout.addWidget(self._main_content, 1)  # Stretch factor 1

        main_layout.addWidget(body_widget, 1)  # Stretch factor 1

    def _connect_signals(self):
        """Connect widget signals."""
        self._sidebar.navigation_changed.connect(self._navigate_to)

    def _navigate_to(self, screen_id: str):
        """Navigate to a specific screen."""
        self._current_screen = screen_id
        self._sidebar.set_active_item(screen_id)
        
        # Update title
        title = PAGE_TITLES.get(screen_id, "")
        self._main_content.set_title(title)

        # Render screen content
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
        """Render the summary screen."""
        self._summary_screen = SummaryScreen()
        self._summary_screen.viewChartsClicked.connect(
            lambda: self._navigate_to("analysis")
        )
        self._summary_screen.uploadNewClicked.connect(
            lambda: self._navigate_to("upload")
        )
        
        # Set data if available
        if self._uploaded_data:
            self._summary_screen.set_data(self._uploaded_data)
        
        self._main_content.set_content(self._summary_screen)

    def _render_analysis_screen(self):
        """Render the analysis charts screen."""
        self._analysis_charts = AnalysisCharts()
        
        # Set data if available
        if self._uploaded_data:
            self._analysis_charts.set_data(self._uploaded_data)
        
        self._main_content.set_content(self._analysis_charts)

    def _on_upload_complete(self, data: Dict[str, Any]):
        """Handle successful CSV upload."""
        self._uploaded_data = data
        # Auto-navigate to summary
        self._navigate_to("summary")

    def _on_upload_cleared(self):
        """Handle upload cleared."""
        self._uploaded_data = None

    def get_current_screen(self) -> str:
        """Get the current screen ID."""
        return self._current_screen

    def get_uploaded_data(self) -> Optional[Dict[str, Any]]:
        """Get the current uploaded data."""
        return self._uploaded_data
