"""
Main Window UI Component for Breast Cancer Detection Application
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QMenuBar, QMenu, QToolBar, QStatusBar,
                            QLabel, QPushButton, QFrame, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon, QPixmap

from ui_components.patient_management import PatientManagementWidget
from ui_components.image_analysis import ImageAnalysisWidget
from ui_components.history_tracking import HistoryTrackingWidget
from ui_components.analytics_dashboard import AnalyticsDashboardWidget
from app_utils.config import AppConfig


class MainWindow(QMainWindow):
    """Main application window with tabbed interface"""
    
    def __init__(self, config: AppConfig):
        super().__init__()
        
        self.config = config
        self.setWindowTitle("AI Breast Cancer Detection System")
        self.setGeometry(100, 100, 1400, 900)
        
        # Setup UI
        self.setup_ui()
        self.setup_menubar()
        self.setup_toolbar()
        self.setup_statusbar()
        
        # Initialize components
        self.init_components()
        
    def setup_ui(self):
        """Setup the main window UI layout"""
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create header
        self.create_header()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMovable(True)
        
        self.main_layout.addWidget(self.tab_widget)
        
    def create_header(self):
        """Create the application header"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3e3e42;
                min-height: 60px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo and title
        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.logo_label = QLabel()
        self.logo_label.setText("🩺")
        self.logo_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_layout.addWidget(self.logo_label)
        
        self.title_label = QLabel("AI Breast Cancer Detection System")
        self.title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            margin-left: 10px;
        """)
        title_layout.addWidget(self.title_label)
        
        header_layout.addLayout(title_layout)
        
        # Status indicators
        status_layout = QHBoxLayout()
        status_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.model_status = QLabel("Model: Not Loaded")
        self.model_status.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        status_layout.addWidget(self.model_status)
        
        self.db_status = QLabel("Database: Connected")
        self.db_status.setStyleSheet("color: #51cf66; font-weight: bold;")
        status_layout.addWidget(self.db_status)
        
        header_layout.addLayout(status_layout)
        
        self.main_layout.addWidget(header_frame)
        
    def setup_menubar(self):
        """Setup the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_toolbar(self):
        """Setup the application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(self.config.get_icon_size())
        
        # Add actions to toolbar
        new_patient_action = QAction("New Patient", self)
        new_patient_action.triggered.connect(self.new_patient)
        toolbar.addAction(new_patient_action)
        
        analyze_action = QAction("Analyze Image", self)
        analyze_action.triggered.connect(self.analyze_image)
        toolbar.addAction(analyze_action)
        
        self.addToolBar(toolbar)
        
    def setup_statusbar(self):
        """Setup the application status bar"""
        self.statusBar().showMessage("Ready")
        
    def init_components(self):
        """Initialize all UI components"""
        # Patient Management Tab
        self.patient_widget = PatientManagementWidget(self.config)
        self.tab_widget.addTab(self.patient_widget, "Patient Management")
        
        # Image Analysis Tab
        self.image_widget = ImageAnalysisWidget(self.config)
        self.tab_widget.addTab(self.image_widget, "Image Analysis")
        
        # History Tracking Tab
        self.history_widget = HistoryTrackingWidget(self.config)
        self.tab_widget.addTab(self.history_widget, "History Tracking")
        
        # Analytics Dashboard Tab
        self.analytics_widget = AnalyticsDashboardWidget(self.config)
        self.tab_widget.addTab(self.analytics_widget, "Analytics Dashboard")
        
        # Connect signals
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
    def on_tab_changed(self, index):
        """Handle tab changes"""
        tab_text = self.tab_widget.tabText(index)
        self.statusBar().showMessage(f"Active: {tab_text}")
        
        # Update model status
        if hasattr(self.image_widget, 'model_manager'):
            if self.image_widget.model_manager.is_loaded:
                self.model_status.setText("Model: Loaded")
                self.model_status.setStyleSheet("color: #51cf66; font-weight: bold;")
            else:
                self.model_status.setText("Model: Not Loaded")
                self.model_status.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        
    def new_patient(self):
        """Open new patient dialog"""
        self.tab_widget.setCurrentWidget(self.patient_widget)
        self.patient_widget.open_new_patient_dialog()
        
    def analyze_image(self):
        """Open image analysis tab"""
        self.tab_widget.setCurrentWidget(self.image_widget)
        self.image_widget.open_image_upload()
        
    def open_settings(self):
        """Open settings dialog"""
        # TODO: Implement settings dialog
        pass
        
    def show_about(self):
        """Show about dialog"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(self, "About", 
                         "AI Breast Cancer Detection System\n\n"
                         "Version: 1.0.0\n"
                         "Framework: PyQt6 + YOLOv5\n"
                         "Purpose: Medical imaging analysis for breast cancer detection")