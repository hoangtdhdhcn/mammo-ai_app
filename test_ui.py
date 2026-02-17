#!/usr/bin/env python3
"""
Test script to verify the UI displays images correctly
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from ui_components.main_window import MainWindow
from app_utils.config import AppConfig

def main():
    """Test the UI with a sample image"""
    app = QApplication(sys.argv)
    
    # Create config
    config = AppConfig()
    
    # Create main window
    window = MainWindow(config)
    window.show()
    
    # Try to load a test image if it exists
    test_image_path = project_root / "images" / "test_image.jpg"
    if test_image_path.exists():
        print(f"Loading test image: {test_image_path}")
        # Switch to Image Analysis tab
        window.tab_widget.setCurrentWidget(window.image_widget)
        # Load the image
        window.image_widget.load_image(str(test_image_path))
        print("Image loaded successfully")
    else:
        print(f"Test image not found at: {test_image_path}")
        print("Please ensure test_image.jpg exists in the images/ directory")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()