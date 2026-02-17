"""
Application Logging Module
Provides centralized logging configuration for the medical application
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(level: int = logging.INFO, 
                 log_file: Optional[str] = None,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
    """
    Setup centralized logging for the application
    
    Args:
        level: Logging level (default: INFO)
        log_file: Path to log file (default: logs/app.log)
        max_file_size: Maximum size of log file before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
    """
    
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Set up log file path
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"app_{timestamp}.log"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Create specific loggers for different components
    setup_component_loggers()
    
    # Log application startup
    root_logger.info("=" * 60)
    root_logger.info("AI Breast Cancer Detection Application Started")
    root_logger.info(f"Log file: {log_file}")
    root_logger.info(f"Log level: {logging.getLevelName(level)}")
    root_logger.info("=" * 60)


def setup_component_loggers():
    """Setup specific loggers for different application components"""
    
    # Model manager logger
    model_logger = logging.getLogger("models.model_manager")
    model_logger.setLevel(logging.INFO)
    
    # Database logger
    db_logger = logging.getLogger("database.manager")
    db_logger.setLevel(logging.INFO)
    
    # Image processing logger
    image_logger = logging.getLogger("utils.image_processor")
    image_logger.setLevel(logging.INFO)
    
    # UI logger
    ui_logger = logging.getLogger("ui_components")
    ui_logger.setLevel(logging.INFO)
    
    # Analytics logger
    analytics_logger = logging.getLogger("analytics")
    analytics_logger.setLevel(logging.INFO)


class MedicalLogger:
    """Enhanced logger for medical application with structured logging"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        
    def log_patient_action(self, patient_id: str, action: str, details: dict = None):
        """Log patient-related actions with structured format"""
        log_data = {
            "type": "patient_action",
            "patient_id": patient_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.logger.info(f"PATIENT_ACTION: {log_data}")
        
    def log_model_inference(self, model_path: str, confidence: float, 
                           processing_time: float, image_path: str = None):
        """Log model inference with performance metrics"""
        log_data = {
            "type": "model_inference",
            "model_path": model_path,
            "confidence": confidence,
            "processing_time_ms": processing_time * 1000,
            "image_path": image_path,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(f"MODEL_INFERENCE: {log_data}")
        
    def log_security_event(self, event_type: str, description: str, 
                          user_id: str = None, severity: str = "INFO"):
        """Log security-related events"""
        log_data = {
            "type": "security_event",
            "event_type": event_type,
            "description": description,
            "user_id": user_id,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.warning(f"SECURITY_EVENT: {log_data}")
        
    def log_analytics_export(self, export_type: str, format: str, 
                           patient_count: int, file_path: str):
        """Log analytics export operations"""
        log_data = {
            "type": "analytics_export",
            "export_type": export_type,
            "format": format,
            "patient_count": patient_count,
            "file_path": file_path,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(f"ANALYTICS_EXPORT: {log_data}")
        
    def log_error(self, error_message: str, context: dict = None, 
                 exception: Exception = None):
        """Log errors with context and optional exception"""
        log_data = {
            "type": "error",
            "message": error_message,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        if exception:
            log_data["exception"] = str(exception)
            log_data["exception_type"] = type(exception).__name__
            
        self.logger.error(f"ERROR: {log_data}")


# Create a global medical logger instance
medical_logger = MedicalLogger("medical_app")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name"""
    return logging.getLogger(name)


def get_medical_logger() -> MedicalLogger:
    """Get the medical logger instance"""
    return medical_logger