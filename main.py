#!/usr/bin/env python3
"""
AI-Powered Breast Cancer Detection Desktop Application
Main application entry point
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPalette, QColor

from ui_components.main_window import MainWindow
from app_utils.config import AppConfig
from app_utils.logger import setup_logging


class BreastCancerDetectionApp(QApplication):
    """Main application class for the breast cancer detection system"""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Setup logging
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = AppConfig()
        
        # Set application properties
        self.setApplicationName("AI Breast Cancer Detection")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Medical AI Solutions")
        self.setOrganizationDomain("medicalai.example.com")
        
        # Setup application style
        self.setup_style()
        
        # Initialize main window
        self.main_window = MainWindow(self.config)
        self.main_window.show()
        
        self.logger.info("Application started successfully")
    
    def setup_style(self):
        """Setup application-wide styling"""
        # Set dark theme for medical environment
        self.setStyle('Fusion')
        
        # Custom palette for medical-grade appearance
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 48))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 48))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(45, 45, 48))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 48))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        
        self.setPalette(palette)
        
        # Set stylesheet for medical-grade appearance
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d30;
            }
            QLabel {
                color: #dcdcdc;
                font-size: 12px;
            }
            QPushButton {
                background-color: #2a7ae2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e5bb0;
            }
            QPushButton:pressed {
                background-color: #164485;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 4px;
                color: #dcdcdc;
            }
            QGroupBox {
                border: 1px solid #5a5a5a;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0 3px 0 3px;
            }
            QProgressBar {
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2a7ae2;
            }
        """)


def main():
    """Main entry point for the application"""
    try:
        app = BreastCancerDetectionApp(sys.argv)
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Application failed to start: {e}")
        QMessageBox.critical(None, "Application Error", 
                           f"Failed to start application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()