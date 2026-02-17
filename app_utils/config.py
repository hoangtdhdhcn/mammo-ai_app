"""
Application Configuration Module
Handles application settings, paths, and configuration management
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class AppConfig:
    """Application configuration manager"""
    
    def __init__(self):
        self.app_name = "AI Breast Cancer Detection"
        self.version = "1.0.0"
        
        # Application paths
        self.app_dir = Path(__file__).parent.parent
        self.data_dir = self.app_dir / "data"
        self.models_dir = self.app_dir / "models"
        self.database_dir = self.app_dir / "database"
        self.logs_dir = self.app_dir / "logs"
        self.temp_dir = self.app_dir / "temp"
        
        # Create directories
        self._create_directories()
        
        # Configuration file path
        self.config_file = self.data_dir / "config.json"
        
        # Default configuration
        self.default_config = {
            "model": {
                "path": str(self.models_dir / "yolov5_model.pt"),
                "confidence_threshold": 0.5,
                "iou_threshold": 0.45,
                "device": "cpu"
            },
            "database": {
                "path": str(self.database_dir / "patients.db"),
                "backup_enabled": True,
                "backup_interval_hours": 24
            },
            "ui": {
                "theme": "dark",
                "font_size": 12,
                "icon_size": 24,
                "window_width": 1400,
                "window_height": 900
            },
            "image_processing": {
                "supported_formats": [".png", ".jpg", ".jpeg", ".dcm", ".tiff"],
                "max_image_size_mb": 50,
                "resize_width": 1024,
                "resize_height": 1024,
                "quality_enhancement": True
            },
            "analytics": {
                "enable_trend_analysis": True,
                "history_retention_days": 365,
                "export_formats": ["pdf", "excel", "csv"],
                "chart_theme": "medical"
            }
        }
        
        # Load or create configuration
        self.config = self._load_config()
        
    def _create_directories(self):
        """Create necessary application directories"""
        directories = [
            self.data_dir,
            self.models_dir,
            self.database_dir,
            self.logs_dir,
            self.temp_dir
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_config(self.default_config, config)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_config
        else:
            # Create default config file
            self._save_config(self.default_config)
            return self.default_config
            
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with defaults"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
        
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot notation path"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
        
    def set(self, key_path: str, value: Any):
        """Set configuration value by dot notation path"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
            
        config[keys[-1]] = value
        self._save_config(self.config)
        
    def get_model_path(self) -> str:
        """Get the path to the YOLOv5 model"""
        return self.get("model.path", str(self.models_dir / "yolov5_model.pt"))
        
    def get_confidence_threshold(self) -> float:
        """Get the confidence threshold for detection"""
        return self.get("model.confidence_threshold", 0.5)
        
    def get_database_path(self) -> str:
        """Get the path to the database file"""
        return self.get("database.path", str(self.database_dir / "patients.db"))
        
    def get_icon_size(self):
        """Get the icon size for UI elements"""
        from PyQt6.QtCore import QSize
        size = self.get("ui.icon_size", 24)
        return QSize(size, size)
        
    def get_supported_formats(self) -> list:
        """Get list of supported image formats"""
        return self.get("image_processing.supported_formats", [".png", ".jpg", ".jpeg"])
        
    def get_max_image_size(self) -> int:
        """Get maximum allowed image size in MB"""
        return self.get("image_processing.max_image_size_mb", 50)
        
    def get_resize_dimensions(self) -> tuple:
        """Get image resize dimensions"""
        width = self.get("image_processing.resize_width", 1024)
        height = self.get("image_processing.resize_height", 1024)
        return (width, height)
        
    def is_quality_enhancement_enabled(self) -> bool:
        """Check if image quality enhancement is enabled"""
        return self.get("image_processing.quality_enhancement", True)
        
    def get_export_formats(self) -> list:
        """Get list of supported export formats"""
        return self.get("analytics.export_formats", ["pdf", "excel", "csv"])
        
    def get_history_retention_days(self) -> int:
        """Get history retention period in days"""
        return self.get("analytics.history_retention_days", 365)
        
    def get_chart_theme(self) -> str:
        """Get the chart theme for analytics"""
        return self.get("analytics.chart_theme", "medical")
        
    def get_window_size(self) -> tuple:
        """Get default window size"""
        width = self.get("ui.window_width", 1400)
        height = self.get("ui.window_height", 900)
        return (width, height)
        
    def get_device(self) -> str:
        """Get the device for model inference"""
        return self.get("model.device", "cpu")
        
    def get_iou_threshold(self) -> float:
        """Get the IoU threshold for non-maximum suppression"""
        return self.get("model.iou_threshold", 0.45)
        
    def is_trend_analysis_enabled(self) -> bool:
        """Check if trend analysis is enabled"""
        return self.get("analytics.enable_trend_analysis", True)
        
    def is_backup_enabled(self) -> bool:
        """Check if database backup is enabled"""
        return self.get("database.backup_enabled", True)
        
    def get_backup_interval(self) -> int:
        """Get backup interval in hours"""
        return self.get("database.backup_interval_hours", 24)