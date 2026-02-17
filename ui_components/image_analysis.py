"""
Image Analysis Widget
Handles image upload, preprocessing, YOLOv5 inference, and results visualization
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QPushButton, QProgressBar, QGroupBox,
                            QScrollArea, QFrame, QMessageBox, QFileDialog,
                            QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont
import numpy as np
import cv2
import os
from pathlib import Path
from datetime import datetime
import logging

from models.model_manager import ModelManager
from database.manager import DatabaseManager
from app_utils.config import AppConfig
from app_utils.logger import get_logger, get_medical_logger


class ImageAnalysisWidget(QWidget):
    """Main image analysis interface with YOLOv5 integration"""
    
    def __init__(self, config: AppConfig):
        super().__init__()
        
        self.config = config
        self.logger = get_logger("ui_components.image_analysis")
        self.medical_logger = get_medical_logger()
        
        # Initialize managers
        self.db_manager = DatabaseManager(config)
        self.model_manager = ModelManager(config)
        
        # Current state
        self.current_image_path = None
        self.current_image = None
        self.current_patient_id = None
        self.analysis_result = None
        
        # Setup UI
        self.setup_ui()
        self.setup_model()
        
    def setup_ui(self):
        """Setup the image analysis UI"""
        layout = QVBoxLayout(self)
        
        # Create main splitter
        from PyQt6.QtWidgets import QSplitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Controls and Settings
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Image upload section
        upload_group = QGroupBox("Image Upload")
        upload_layout = QVBoxLayout()
        
        self.upload_button = QPushButton("Upload Image")
        self.upload_button.clicked.connect(self.open_image_upload)
        self.upload_button.setStyleSheet("background-color: #2a7ae2; color: white; font-weight: bold;")
        
        self.image_info_label = QLabel("No image selected")
        self.image_info_label.setWordWrap(True)
        
        upload_layout.addWidget(self.upload_button)
        upload_layout.addWidget(self.image_info_label)
        upload_group.setLayout(upload_layout)
        
        # Patient selection section
        patient_group = QGroupBox("Patient Information")
        patient_layout = QVBoxLayout()
        
        self.patient_id_input = QComboBox()
        self.patient_id_input.setEditable(True)
        self.patient_id_input.setPlaceholderText("Select or enter patient ID")
        self.load_patient_ids()
        
        self.select_patient_button = QPushButton("Select Patient")
        self.select_patient_button.clicked.connect(self.select_current_patient)
        
        patient_layout.addWidget(QLabel("Patient ID:"))
        patient_layout.addWidget(self.patient_id_input)
        patient_layout.addWidget(self.select_patient_button)
        patient_group.setLayout(patient_layout)
        
        # Analysis settings section
        settings_group = QGroupBox("Analysis Settings")
        settings_layout = QGridLayout()
        
        settings_layout.addWidget(QLabel("Confidence Threshold:"), 0, 0)
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.0, 1.0)
        self.confidence_spin.setValue(self.config.get_confidence_threshold())
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.valueChanged.connect(self.update_confidence_threshold)
        settings_layout.addWidget(self.confidence_spin, 0, 1)
        
        settings_layout.addWidget(QLabel("IoU Threshold:"), 1, 0)
        self.iou_spin = QDoubleSpinBox()
        self.iou_spin.setRange(0.0, 1.0)
        self.iou_spin.setValue(self.config.get_iou_threshold())
        self.iou_spin.setSingleStep(0.05)
        self.iou_spin.valueChanged.connect(self.update_iou_threshold)
        settings_layout.addWidget(self.iou_spin, 1, 1)
        
        settings_layout.addWidget(QLabel("Image Type:"), 2, 0)
        self.image_type_combo = QComboBox()
        self.image_type_combo.addItems(["Mammogram", "Ultrasound", "MRI", "Other"])
        settings_layout.addWidget(self.image_type_combo, 2, 1)
        
        settings_group.setLayout(settings_layout)
        
        # Analysis control section
        control_group = QGroupBox("Analysis Control")
        control_layout = QVBoxLayout()
        
        self.analyze_button = QPushButton("Start Analysis")
        self.analyze_button.clicked.connect(self.start_analysis)
        self.analyze_button.setEnabled(False)
        self.analyze_button.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
        
        control_layout.addWidget(self.analyze_button)
        control_layout.addWidget(self.progress_bar)
        control_layout.addWidget(self.status_label)
        control_group.setLayout(control_layout)
        
        # Results summary section
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(150)
        
        results_layout.addWidget(self.results_text)
        results_group.setLayout(results_layout)
        
        # Add all sections to left panel
        left_layout.addWidget(upload_group)
        left_layout.addWidget(patient_group)
        left_layout.addWidget(settings_group)
        left_layout.addWidget(control_group)
        left_layout.addWidget(results_group)
        left_layout.addStretch()
        
        # Right panel: Image Display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        display_group = QGroupBox("Image Display")
        display_layout = QVBoxLayout()
        
        # Image container with scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: 1px solid #5a5a5a; }")
        
        self.image_container = QLabel()
        self.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_container.setMinimumSize(400, 400)
        scroll_area.setWidget(self.image_container)
        
        display_layout.addWidget(scroll_area)
        display_group.setLayout(display_layout)
        
        right_layout.addWidget(display_group)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        layout.addWidget(splitter)
        
    def setup_model(self):
        """Setup YOLOv5 model"""
        try:
            # Load model in background thread
            self.model_thread = ModelLoadingThread(self.model_manager)
            self.model_thread.finished.connect(self.on_model_loaded)
            self.model_thread.error.connect(self.on_model_error)
            self.model_thread.start()
            
            self.status_label.setText("Loading model...")
            self.status_label.setStyleSheet("color: #ffc107; font-weight: bold;")
            
        except Exception as e:
            self.logger.error(f"Failed to setup model: {e}")
            self.status_label.setText(f"Model setup failed: {e}")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            
    def load_patient_ids(self):
        """Load patient IDs into dropdown"""
        try:
            # Get recent patients
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT patient_id, first_name, last_name 
                    FROM patients 
                    WHERE is_active = 1 
                    ORDER BY updated_at DESC 
                    LIMIT 20
                """)
                
                patients = cursor.fetchall()
                for patient in patients:
                    display_text = f"{patient['patient_id']} - {patient['first_name']} {patient['last_name']}"
                    self.patient_id_input.addItem(display_text, patient['patient_id'])
                    
        except Exception as e:
            self.logger.error(f"Failed to load patient IDs: {e}")
            
    def select_current_patient(self):
        """Select current patient from dropdown"""
        current_text = self.patient_id_input.currentText()
        if current_text:
            # Extract patient ID from display text
            if " - " in current_text:
                self.current_patient_id = current_text.split(" - ")[0]
            else:
                self.current_patient_id = current_text
                
            self.status_label.setText(f"Selected patient: {self.current_patient_id}")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            
    def open_image_upload(self):
        """Open file dialog for image upload"""
        try:
            supported_formats = self.config.get_supported_formats()
            filter_str = f"Images ({' '.join('*' + fmt for fmt in supported_formats)})" + \
                        ";;All Files (*.*)"
            
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Medical Image", "", filter_str
            )
            
            if file_path:
                self.load_image(file_path)
                
        except Exception as e:
            self.logger.error(f"Failed to open image upload: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open image: {str(e)}")
            
    def load_image(self, file_path):
        """Load and display image"""
        try:
            self.current_image_path = file_path
            self.current_image = cv2.imread(file_path)
            
            if self.current_image is None:
                raise ValueError("Failed to load image")
                
            # Convert BGR to RGB for display
            rgb_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
            
            # Update image display
            self.display_image(rgb_image)
            
            # Update image info
            height, width, channels = self.current_image.shape
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            
            info_text = f"""
            <b>Image Information:</b>
            <ul>
            <li>File: {os.path.basename(file_path)}</li>
            <li>Size: {width} x {height} pixels</li>
            <li>Channels: {channels}</li>
            <li>File Size: {file_size:.2f} MB</li>
            <li>Path: {file_path}</li>
            </ul>
            """
            self.image_info_label.setText(info_text)
            
            # Enable analysis button
            self.analyze_button.setEnabled(True)
            self.status_label.setText("Image loaded successfully")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            
            self.logger.info(f"Image loaded: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load image: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
            
    def display_image(self, image_array):
        """Display image in the container"""
        try:
            height, width, channels = image_array.shape
            bytes_per_line = channels * width
            
            q_image = QImage(image_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            # Scale pixmap to fit container while maintaining aspect ratio
            max_size = self.image_container.maximumSize()
            scaled_pixmap = pixmap.scaled(
                max_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            
            self.image_container.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.logger.error(f"Failed to display image: {e}")
            
    def start_analysis(self):
        """Start YOLOv5 analysis"""
        if not self.current_image.any():
            QMessageBox.warning(self, "Warning", "Please load an image first.")
            return
            
        if not self.current_patient_id:
            QMessageBox.warning(self, "Warning", "Please select a patient first.")
            return
            
        if not self.model_manager.is_loaded:
            QMessageBox.warning(self, "Warning", "Model not loaded yet. Please wait.")
            return
            
        try:
            # Start analysis in background thread
            self.analysis_thread = AnalysisThread(self.model_manager, self.current_image)
            self.analysis_thread.started.connect(self.on_analysis_started)
            self.analysis_thread.finished.connect(self.on_analysis_finished)
            self.analysis_thread.error.connect(self.on_analysis_error)
            self.analysis_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start analysis: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start analysis: {str(e)}")
            
    def on_analysis_started(self):
        """Handle analysis start"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.analyze_button.setEnabled(False)
        self.status_label.setText("Analyzing image...")
        self.status_label.setStyleSheet("color: #ffc107; font-weight: bold;")
        
    def on_analysis_finished(self, result):
        """Handle analysis completion"""
        self.analysis_result = result
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.analyze_button.setEnabled(True)
        
        if result:
            # Display results
            self.display_analysis_results(result)
            
            # Save to database
            self.save_analysis_to_database(result)
            
            self.status_label.setText("Analysis completed successfully")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
        else:
            self.status_label.setText("Analysis failed")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            
    def on_analysis_error(self, error_msg):
        """Handle analysis error"""
        self.progress_bar.setVisible(False)
        self.analyze_button.setEnabled(True)
        self.status_label.setText(f"Analysis error: {error_msg}")
        self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        
        self.logger.error(f"Analysis error: {error_msg}")
        QMessageBox.critical(self, "Analysis Error", f"Analysis failed: {error_msg}")
        
    def display_analysis_results(self, result):
        """Display analysis results"""
        try:
            # Draw bounding boxes on image
            image_with_boxes = self.draw_detections(self.current_image.copy(), result['detections'])
            rgb_image = cv2.cvtColor(image_with_boxes, cv2.COLOR_BGR2RGB)
            self.display_image(rgb_image)
            
            # Update results text
            detections = result['detections']
            processing_time = result['processing_time']
            
            results_text = f"""
            <b>Analysis Results:</b>
            <ul>
            <li>Detections: {detections['count']}</li>
            <li>Max Confidence: {detections['max_confidence']:.3f}</li>
            <li>Processing Time: {processing_time*1000:.1f} ms</li>
            <li>Model: {result['model_info'].get('model_type', 'Unknown')}</li>
            </ul>
            
            <b>Detection Details:</b>
            """
            
            for i, detection in enumerate(detections['detections']):
                results_text += f"""
                <li><b>Detection {i+1}:</b> 
                Class: {detection['class_name']}, 
                Confidence: {detection['confidence']:.3f}, 
                BBox: [{detection['bbox'][0]:.1f}, {detection['bbox'][1]:.1f}, 
                       {detection['bbox'][2]:.1f}, {detection['bbox'][3]:.1f}]
                </li>
                """
                
            self.results_text.setHtml(results_text)
            
        except Exception as e:
            self.logger.error(f"Failed to display analysis results: {e}")
            
    def draw_detections(self, image, detections):
        """Draw detection bounding boxes on image"""
        try:
            for detection in detections['detections']:
                bbox = detection['bbox']
                confidence = detection['confidence']
                class_name = detection['class_name']
                
                # Draw rectangle
                cv2.rectangle(image, (int(bbox[0]), int(bbox[1])), 
                             (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
                
                # Draw label
                label = f"{class_name}: {confidence:.2f}"
                cv2.putText(image, label, (int(bbox[0]), int(bbox[1])-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                           
            return image
            
        except Exception as e:
            self.logger.error(f"Failed to draw detections: {e}")
            return image
            
    def save_analysis_to_database(self, result):
        """Save analysis results to database"""
        try:
            # Add image record
            image_data = {
                'image_path': self.current_image_path,
                'image_type': self.image_type_combo.currentText(),
                'image_format': os.path.splitext(self.current_image_path)[1],
                'image_size_mb': os.path.getsize(self.current_image_path) / (1024 * 1024),
                'quality_score': 1.0  # TODO: Implement quality scoring
            }
            
            image_id = self.db_manager.add_image(self.current_patient_id, image_data)
            
            if image_id:
                # Add analysis result
                result_data = {
                    'model_version': result['model_info'].get('model_type', 'YOLOv5'),
                    'confidence_threshold': self.config.get_confidence_threshold(),
                    'iou_threshold': self.config.get_iou_threshold(),
                    'detection_count': result['detections']['count'],
                    'max_confidence': result['detections']['max_confidence'],
                    'processing_time_ms': result['processing_time'] * 1000,
                    'result_status': 'completed',
                    'detections': result['detections']['detections']
                }
                
                self.db_manager.add_analysis_result(image_id, result_data)
                
                # Add analytics data
                self.db_manager.add_analytics_data(
                    self.current_patient_id,
                    'detection_count',
                    result['detections']['count']
                )
                
                self.db_manager.add_analytics_data(
                    self.current_patient_id,
                    'max_confidence',
                    result['detections']['max_confidence']
                )
                
                self.logger.info(f"Analysis saved to database for patient {self.current_patient_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to save analysis to database: {e}")
            
    def update_confidence_threshold(self, value):
        """Update confidence threshold"""
        self.config.set("model.confidence_threshold", value)
        self.model_manager.update_thresholds(confidence_threshold=value)
        
    def update_iou_threshold(self, value):
        """Update IoU threshold"""
        self.config.set("model.iou_threshold", value)
        self.model_manager.update_thresholds(iou_threshold=value)
        
    def on_model_loaded(self):
        """Handle model loading completion"""
        self.status_label.setText("Model loaded successfully")
        self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
        
    def on_model_error(self, error_msg):
        """Handle model loading error"""
        self.status_label.setText(f"Model loading failed: {error_msg}")
        self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        
        self.logger.error(f"Model loading error: {error_msg}")
        QMessageBox.critical(self, "Model Error", f"Failed to load model: {error_msg}")


class ModelLoadingThread(QThread):
    """Thread for loading YOLOv5 model"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, model_manager):
        super().__init__()
        self.model_manager = model_manager
        
    def run(self):
        """Run model loading in background"""
        try:
            success = self.model_manager.load_model()
            if success:
                self.finished.emit()
            else:
                self.error.emit("Failed to load model")
        except Exception as e:
            self.error.emit(str(e))


class AnalysisThread(QThread):
    """Thread for running YOLOv5 analysis"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, model_manager, image):
        super().__init__()
        self.model_manager = model_manager
        self.image = image
        
    def run(self):
        """Run analysis in background"""
        try:
            result = self.model_manager.predict(self.image)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))