"""
History Tracking Widget
Provides comprehensive patient history tracking with timeline views and trend analysis
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                            QGroupBox, QSplitter, QHeaderView, QMessageBox,
                            QDateEdit, QComboBox, QCheckBox, QTextEdit, QScrollArea)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QBrush
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

from database.manager import DatabaseManager
from app_utils.config import AppConfig
from app_utils.logger import get_logger, get_medical_logger


class HistoryTrackingWidget(QWidget):
    """Main history tracking interface with timeline and trend analysis"""
    
    def __init__(self, config: AppConfig):
        super().__init__()
        
        self.config = config
        self.logger = get_logger("ui_components.history_tracking")
        self.medical_logger = get_medical_logger()
        
        # Initialize database manager
        self.db_manager = DatabaseManager(config)
        
        # Current patient context
        self.current_patient_id = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the history tracking UI"""
        layout = QVBoxLayout(self)
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section: Patient Selection and Controls
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Patient selection section
        patient_group = QGroupBox("Patient Selection")
        patient_layout = QHBoxLayout()
        
        self.patient_id_input = QComboBox()
        self.patient_id_input.setEditable(True)
        self.patient_id_input.setPlaceholderText("Enter patient ID")
        self.load_recent_patients()
        
        self.select_patient_button = QPushButton("Load History")
        self.select_patient_button.clicked.connect(self.load_patient_history)
        
        self.clear_selection_button = QPushButton("Clear Selection")
        self.clear_selection_button.clicked.connect(self.clear_selection)
        
        patient_layout.addWidget(QLabel("Patient ID:"))
        patient_layout.addWidget(self.patient_id_input, 1)
        patient_layout.addWidget(self.select_patient_button)
        patient_layout.addWidget(self.clear_selection_button)
        
        patient_group.setLayout(patient_layout)
        
        # Analysis controls section
        controls_group = QGroupBox("Analysis Controls")
        controls_layout = QGridLayout()
        
        # Date range selection
        controls_layout.addWidget(QLabel("Start Date:"), 0, 0)
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-12))
        self.start_date.setCalendarPopup(True)
        controls_layout.addWidget(self.start_date, 0, 1)
        
        controls_layout.addWidget(QLabel("End Date:"), 0, 2)
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        controls_layout.addWidget(self.end_date, 0, 3)
        
        # Metrics selection
        controls_layout.addWidget(QLabel("Metrics:"), 1, 0)
        self.metrics_combo = QComboBox()
        self.metrics_combo.addItems([
            "Detection Count", "Average Confidence", "Max Confidence", 
            "Tumor Size", "Processing Time"
        ])
        controls_layout.addWidget(self.metrics_combo, 1, 1)
        
        # Update button
        self.update_analysis_button = QPushButton("Update Analysis")
        self.update_analysis_button.clicked.connect(self.update_analysis)
        controls_layout.addWidget(self.update_analysis_button, 1, 2, 1, 2)
        
        controls_group.setLayout(controls_layout)
        
        # Add sections to top layout
        top_layout.addWidget(patient_group)
        top_layout.addWidget(controls_group)
        
        # Bottom section: History Display
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # Create horizontal splitter for timeline and details
        h_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Timeline and Charts
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Timeline section
        timeline_group = QGroupBox("Patient Timeline")
        timeline_layout = QVBoxLayout()
        
        self.timeline_table = QTableWidget()
        self.timeline_table.setColumnCount(5)
        self.timeline_table.setHorizontalHeaderLabels([
            "Date", "Image Type", "Detections", "Max Confidence", "Actions"
        ])
        self.timeline_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.timeline_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.timeline_table.cellClicked.connect(self.on_timeline_selection)
        
        timeline_layout.addWidget(self.timeline_table)
        timeline_group.setLayout(timeline_layout)
        
        # Charts section
        charts_group = QGroupBox("Trend Analysis")
        charts_layout = QVBoxLayout()
        
        # Create matplotlib figure
        self.figure, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.figure.tight_layout(pad=3.0)
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(400)
        
        charts_layout.addWidget(self.canvas)
        charts_group.setLayout(charts_layout)
        
        left_layout.addWidget(timeline_group)
        left_layout.addWidget(charts_group)
        left_layout.addStretch()
        
        # Right: Detailed Information
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Patient summary section
        summary_group = QGroupBox("Patient Summary")
        summary_layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(150)
        
        summary_layout.addWidget(self.summary_text)
        summary_group.setLayout(summary_layout)
        
        # Detailed results section
        details_group = QGroupBox("Detailed Results")
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        
        details_layout.addWidget(self.details_text)
        details_group.setLayout(details_layout)
        
        right_layout.addWidget(summary_group)
        right_layout.addWidget(details_group)
        
        # Add panels to horizontal splitter
        h_splitter.addWidget(left_panel)
        h_splitter.addWidget(right_panel)
        h_splitter.setSizes([600, 400])
        
        bottom_layout.addWidget(h_splitter)
        
        # Add widgets to main splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([200, 600])
        
        layout.addWidget(splitter)
        
    def load_recent_patients(self):
        """Load recent patients into dropdown"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT patient_id, first_name, last_name, updated_at
                    FROM patients 
                    WHERE is_active = 1 
                    ORDER BY updated_at DESC 
                    LIMIT 20
                """)
                
                patients = cursor.fetchall()
                for patient in patients:
                    display_text = f"{patient['patient_id']} - {patient['first_name']} {patient['last_name']} ({patient['updated_at']})"
                    self.patient_id_input.addItem(display_text, patient['patient_id'])
                    
        except Exception as e:
            self.logger.error(f"Failed to load recent patients: {e}")
            
    def load_patient_history(self):
        """Load patient history and display"""
        patient_id = self.extract_patient_id()
        if not patient_id:
            QMessageBox.warning(self, "Warning", "Please enter a valid patient ID.")
            return
            
        try:
            self.current_patient_id = patient_id
            
            # Load patient data
            patient = self.db_manager.get_patient(patient_id)
            if not patient:
                QMessageBox.warning(self, "Warning", f"Patient {patient_id} not found.")
                return
                
            # Load analysis results
            results = self.db_manager.get_analysis_results(patient_id, limit=100)
            
            # Update UI
            self.update_timeline_table(results)
            self.update_patient_summary(patient)
            self.update_trend_analysis(results)
            
            self.logger.info(f"Loaded history for patient: {patient_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to load patient history: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load patient history: {str(e)}")
            
    def extract_patient_id(self):
        """Extract patient ID from input"""
        current_text = self.patient_id_input.currentText().strip()
        if not current_text:
            return None
            
        # Extract from display text if it contains " - "
        if " - " in current_text:
            return current_text.split(" - ")[0]
        else:
            return current_text
            
    def update_timeline_table(self, results):
        """Update timeline table with analysis results"""
        try:
            self.timeline_table.setRowCount(len(results))
            
            for row, result in enumerate(results):
                # Date
                date_str = result.get('analysis_date', '')
                self.timeline_table.setItem(row, 0, QTableWidgetItem(date_str))
                
                # Image type
                image_type = result.get('image_type', 'Unknown')
                self.timeline_table.setItem(row, 1, QTableWidgetItem(image_type))
                
                # Detections
                detection_count = result.get('detection_count', 0)
                self.timeline_table.setItem(row, 2, QTableWidgetItem(str(detection_count)))
                
                # Max confidence
                max_confidence = result.get('max_confidence', 0)
                confidence_item = QTableWidgetItem(f"{max_confidence:.3f}")
                self.timeline_table.setItem(row, 3, confidence_item)
                
                # Actions
                actions = QPushButton("View Details")
                actions.clicked.connect(lambda _, r=result: self.show_detailed_results(r))
                self.timeline_table.setCellWidget(row, 4, actions)
                
        except Exception as e:
            self.logger.error(f"Failed to update timeline table: {e}")
            
    def update_patient_summary(self, patient):
        """Update patient summary information"""
        try:
            # Get patient statistics
            results = self.db_manager.get_analysis_results(self.current_patient_id, limit=1000)
            
            total_analyses = len(results)
            total_detections = sum(r.get('detection_count', 0) for r in results)
            
            if results:
                avg_confidence = sum(r.get('max_confidence', 0) for r in results) / len(results)
                latest_analysis = max(results, key=lambda x: x.get('analysis_date', ''))
            else:
                avg_confidence = 0
                latest_analysis = None
                
            # Build summary text
            summary = f"""
            <h3>Patient Summary: {patient['patient_id']}</h3>
            <p><b>Name:</b> {patient['first_name']} {patient['last_name']}</p>
            <p><b>Date of Birth:</b> {patient.get('date_of_birth', 'Not specified')}</p>
            <p><b>Gender:</b> {patient.get('gender', 'Not specified')}</p>
            <p><b>Medical Record Number:</b> {patient.get('medical_record_number', 'Not specified')}</p>
            
            <h4>Analysis Statistics</h4>
            <p><b>Total Analyses:</b> {total_analyses}</p>
            <p><b>Total Detections:</b> {total_detections}</p>
            <p><b>Average Max Confidence:</b> {avg_confidence:.3f}</p>
            <p><b>Latest Analysis:</b> {latest_analysis.get('analysis_date', 'None') if latest_analysis else 'None'}</p>
            """
            
            self.summary_text.setHtml(summary)
            
        except Exception as e:
            self.logger.error(f"Failed to update patient summary: {e}")
            
    def update_trend_analysis(self, results):
        """Update trend analysis charts"""
        try:
            if not results:
                self.clear_charts()
                return
                
            # Prepare data for charts
            dates = [datetime.fromisoformat(r['analysis_date']) for r in results]
            detection_counts = [r['detection_count'] for r in results]
            max_confidences = [r['max_confidence'] for r in results]
            processing_times = [r['processing_time_ms'] for r in results]
            
            # Clear previous plots
            for ax in self.axes.flat:
                ax.clear()
                
            # Chart 1: Detection Count Over Time
            self.axes[0, 0].plot(dates, detection_counts, 'bo-', linewidth=2, markersize=6)
            self.axes[0, 0].set_title('Detection Count Over Time', fontsize=12, fontweight='bold')
            self.axes[0, 0].set_ylabel('Detection Count')
            self.axes[0, 0].grid(True, alpha=0.3)
            self.axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Chart 2: Confidence Trend
            self.axes[0, 1].plot(dates, max_confidences, 'go-', linewidth=2, markersize=6)
            self.axes[0, 1].set_title('Max Confidence Trend', fontsize=12, fontweight='bold')
            self.axes[0, 1].set_ylabel('Confidence Score')
            self.axes[0, 1].set_ylim(0, 1)
            self.axes[0, 1].grid(True, alpha=0.3)
            self.axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Chart 3: Processing Time
            self.axes[1, 0].bar(range(len(processing_times)), processing_times, color='skyblue')
            self.axes[1, 0].set_title('Processing Time per Analysis', fontsize=12, fontweight='bold')
            self.axes[1, 0].set_ylabel('Time (ms)')
            self.axes[1, 0].grid(True, alpha=0.3)
            
            # Chart 4: Detection Distribution
            detection_counts_array = np.array(detection_counts)
            unique_counts, counts = np.unique(detection_counts_array, return_counts=True)
            
            self.axes[1, 1].pie(counts, labels=unique_counts, autopct='%1.1f%%', startangle=90)
            self.axes[1, 1].set_title('Detection Count Distribution', fontsize=12, fontweight='bold')
            
            # Update canvas
            self.canvas.draw()
            
        except Exception as e:
            self.logger.error(f"Failed to update trend analysis: {e}")
            self.clear_charts()
            
    def clear_charts(self):
        """Clear all charts"""
        try:
            for ax in self.axes.flat:
                ax.clear()
                ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center',
                       verticalalignment='center', transform=ax.transAxes, fontsize=14)
            self.canvas.draw()
        except Exception as e:
            self.logger.error(f"Failed to clear charts: {e}")
            
    def on_timeline_selection(self, row, column):
        """Handle timeline row selection"""
        try:
            # Get the result data for the selected row
            date_item = self.timeline_table.item(row, 0)
            if date_item:
                # For now, just update the details text
                # In a real implementation, you might want to store the full result data
                self.details_text.setText(f"Selected analysis from: {date_item.text()}")
                
        except Exception as e:
            self.logger.error(f"Failed to handle timeline selection: {e}")
            
    def show_detailed_results(self, result):
        """Show detailed results for a specific analysis"""
        try:
            detections = result.get('detections', [])
            
            details = f"""
            <h3>Detailed Analysis Results</h3>
            <p><b>Date:</b> {result.get('analysis_date', 'Unknown')}</p>
            <p><b>Image Type:</b> {result.get('image_type', 'Unknown')}</p>
            <p><b>Model:</b> {result.get('model_version', 'Unknown')}</p>
            <p><b>Detection Count:</b> {result.get('detection_count', 0)}</p>
            <p><b>Max Confidence:</b> {result.get('max_confidence', 0):.3f}</p>
            <p><b>Processing Time:</b> {result.get('processing_time_ms', 0):.1f} ms</p>
            
            <h4>Detection Details:</h4>
            """
            
            for i, detection in enumerate(detections):
                details += f"""
                <p><b>Detection {i+1}:</b></p>
                <ul>
                <li>Class: {detection.get('class_name', 'Unknown')}</li>
                <li>Confidence: {detection.get('confidence', 0):.3f}</li>
                <li>Bounding Box: [{detection.get('x1', 0):.1f}, {detection.get('y1', 0):.1f}, 
                                   {detection.get('x2', 0):.1f}, {detection.get('y2', 0):.1f}]</li>
                <li>Area: {detection.get('area', 0):.1f}</li>
                </ul>
                """
                
            self.details_text.setHtml(details)
            
        except Exception as e:
            self.logger.error(f"Failed to show detailed results: {e}")
            
    def update_analysis(self):
        """Update analysis with new date range and metrics"""
        if not self.current_patient_id:
            QMessageBox.warning(self, "Warning", "Please select a patient first.")
            return
            
        try:
            # Get date range
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            
            # Reload history with date filtering
            self.load_patient_history()
            
            self.logger.info(f"Updated analysis for patient {self.current_patient_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to update analysis: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update analysis: {str(e)}")
            
    def clear_selection(self):
        """Clear current patient selection"""
        self.current_patient_id = None
        self.timeline_table.setRowCount(0)
        self.summary_text.clear()
        self.details_text.clear()
        self.clear_charts()
        
        self.logger.info("Cleared patient selection")