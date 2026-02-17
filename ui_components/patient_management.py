"""
Patient Management Widget
Handles patient registration, search, and profile management
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QGroupBox, QSplitter, QHeaderView, QMessageBox,
                            QDialog, QDialogButtonBox, QFormLayout)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QIntValidator, QDoubleValidator
import json
from datetime import datetime

from database.manager import DatabaseManager
from app_utils.logger import get_logger, get_medical_logger


class PatientManagementWidget(QWidget):
    """Main patient management interface"""
    
    patient_selected = pyqtSignal(str)
    
    def __init__(self, config):
        super().__init__()
        
        self.config = config
        self.logger = get_logger("ui_components.patient_management")
        self.medical_logger = get_medical_logger()
        
        # Initialize database manager
        self.db_manager = DatabaseManager(config)
        
        # Current patient context
        self.current_patient_id = None
        
        # Setup UI
        self.setup_ui()
        self.load_patient_list()
        
    def setup_ui(self):
        """Setup the patient management UI"""
        layout = QVBoxLayout(self)
        
        # Create splitter for search/form and patient list
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section: Search and Form
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Search section
        search_group = QGroupBox("Patient Search")
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or patient ID...")
        self.search_input.textChanged.connect(self.on_search_changed)
        
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.on_search_clicked)
        
        new_patient_button = QPushButton("New Patient")
        new_patient_button.clicked.connect(self.open_new_patient_dialog)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(new_patient_button)
        
        search_group.setLayout(search_layout)
        
        # Patient form section
        self.form_group = QGroupBox("Patient Information")
        self.form_layout = QGridLayout()
        
        # Form fields
        self.patient_id_input = QLineEdit()
        self.patient_id_input.setReadOnly(True)
        
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate())
        
        self.gender_input = QComboBox()
        self.gender_input.addItems(["", "Male", "Female", "Other"])
        
        self.mrn_input = QLineEdit()  # Medical Record Number
        
        self.contact_info_input = QTextEdit()
        self.contact_info_input.setPlaceholderText("Contact information (JSON format)")
        
        self.medical_history_input = QTextEdit()
        self.medical_history_input.setPlaceholderText("Medical history (JSON format)")
        
        self.risk_factors_input = QTextEdit()
        self.risk_factors_input.setPlaceholderText("Risk factors (JSON format)")
        
        # Form layout
        self.form_layout.addWidget(QLabel("Patient ID:"), 0, 0)
        self.form_layout.addWidget(self.patient_id_input, 0, 1, 1, 2)
        
        self.form_layout.addWidget(QLabel("First Name:"), 1, 0)
        self.form_layout.addWidget(self.first_name_input, 1, 1, 1, 2)
        
        self.form_layout.addWidget(QLabel("Last Name:"), 2, 0)
        self.form_layout.addWidget(self.last_name_input, 2, 1, 1, 2)
        
        self.form_layout.addWidget(QLabel("Date of Birth:"), 3, 0)
        self.form_layout.addWidget(self.dob_input, 3, 1)
        
        self.form_layout.addWidget(QLabel("Gender:"), 3, 2)
        self.form_layout.addWidget(self.gender_input, 3, 3)
        
        self.form_layout.addWidget(QLabel("Medical Record Number:"), 4, 0)
        self.form_layout.addWidget(self.mrn_input, 4, 1, 1, 2)
        
        self.form_layout.addWidget(QLabel("Contact Information:"), 5, 0)
        self.form_layout.addWidget(self.contact_info_input, 5, 1, 1, 3)
        
        self.form_layout.addWidget(QLabel("Medical History:"), 6, 0)
        self.form_layout.addWidget(self.medical_history_input, 6, 1, 1, 3)
        
        self.form_layout.addWidget(QLabel("Risk Factors:"), 7, 0)
        self.form_layout.addWidget(self.risk_factors_input, 7, 1, 1, 3)
        
        # Form buttons
        form_buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Patient")
        self.save_button.clicked.connect(self.save_patient)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.clear_form)
        
        self.delete_button = QPushButton("Delete Patient")
        self.delete_button.clicked.connect(self.delete_patient)
        self.delete_button.setStyleSheet("background-color: #d9534f; color: white;")
        
        form_buttons_layout.addStretch()
        form_buttons_layout.addWidget(self.save_button)
        form_buttons_layout.addWidget(self.cancel_button)
        form_buttons_layout.addWidget(self.delete_button)
        
        self.form_layout.addLayout(form_buttons_layout, 8, 0, 1, 4)
        
        self.form_group.setLayout(self.form_layout)
        
        top_layout.addWidget(search_group)
        top_layout.addWidget(self.form_group)
        top_layout.addStretch()
        
        # Bottom section: Patient List
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        list_group = QGroupBox("Patient List")
        list_layout = QVBoxLayout()
        
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(6)
        self.patient_table.setHorizontalHeaderLabels([
            "Patient ID", "Name", "DOB", "Gender", "MRN", "Last Updated"
        ])
        self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.patient_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.patient_table.cellClicked.connect(self.on_patient_selected)
        
        list_layout.addWidget(self.patient_table)
        list_group.setLayout(list_layout)
        
        bottom_layout.addWidget(list_group)
        
        # Add widgets to splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([400, 400])
        
        layout.addWidget(splitter)
        
        # Set initial state
        self.clear_form()
        
    def load_patient_list(self, search_term=""):
        """Load patient list from database"""
        try:
            patients = self.db_manager.search_patients(search_term, limit=100)
            
            self.patient_table.setRowCount(len(patients))
            
            for row, patient in enumerate(patients):
                # Patient ID
                self.patient_table.setItem(row, 0, QTableWidgetItem(patient['patient_id']))
                
                # Full name
                name = f"{patient['first_name']} {patient['last_name']}"
                self.patient_table.setItem(row, 1, QTableWidgetItem(name))
                
                # Date of birth
                dob = patient.get('date_of_birth', '')
                self.patient_table.setItem(row, 2, QTableWidgetItem(dob))
                
                # Gender
                gender = patient.get('gender', '')
                self.patient_table.setItem(row, 3, QTableWidgetItem(gender))
                
                # Medical Record Number
                mrn = patient.get('medical_record_number', '')
                self.patient_table.setItem(row, 4, QTableWidgetItem(mrn))
                
                # Last updated
                updated = patient.get('updated_at', '')
                self.patient_table.setItem(row, 5, QTableWidgetItem(updated))
                
            self.logger.info(f"Loaded {len(patients)} patients")
            
        except Exception as e:
            self.logger.error(f"Failed to load patient list: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to load patient list: {str(e)}")
            
    def on_search_changed(self, text):
        """Handle search input changes"""
        self.load_patient_list(text)
        
    def on_search_clicked(self):
        """Handle search button click"""
        search_term = self.search_input.text().strip()
        self.load_patient_list(search_term)
        
    def on_patient_selected(self, row, column):
        """Handle patient selection from table"""
        try:
            patient_id_item = self.patient_table.item(row, 0)
            if patient_id_item:
                patient_id = patient_id_item.text()
                self.load_patient_data(patient_id)
                
        except Exception as e:
            self.logger.error(f"Failed to select patient: {e}")
            
    def load_patient_data(self, patient_id):
        """Load patient data into form"""
        try:
            patient = self.db_manager.get_patient(patient_id)
            if patient:
                self.current_patient_id = patient_id
                
                # Fill form fields
                self.patient_id_input.setText(patient['patient_id'])
                self.first_name_input.setText(patient['first_name'])
                self.last_name_input.setText(patient['last_name'])
                
                # Date of birth
                if patient['date_of_birth']:
                    dob = QDate.fromString(patient['date_of_birth'], "yyyy-MM-dd")
                    self.dob_input.setDate(dob)
                else:
                    self.dob_input.setDate(QDate.currentDate())
                
                # Gender
                gender = patient.get('gender', '')
                index = self.gender_input.findText(gender)
                self.gender_input.setCurrentIndex(index if index >= 0 else 0)
                
                # Medical Record Number
                self.mrn_input.setText(patient.get('medical_record_number', ''))
                
                # Contact information
                contact_info = patient.get('contact_info', '{}')
                if isinstance(contact_info, str):
                    try:
                        contact_info = json.loads(contact_info)
                    except:
                        contact_info = {}
                self.contact_info_input.setText(json.dumps(contact_info, indent=2))
                
                # Medical history
                medical_history = patient.get('medical_history', '{}')
                if isinstance(medical_history, str):
                    try:
                        medical_history = json.loads(medical_history)
                    except:
                        medical_history = {}
                self.medical_history_input.setText(json.dumps(medical_history, indent=2))
                
                # Risk factors
                risk_factors = patient.get('risk_factors', '{}')
                if isinstance(risk_factors, str):
                    try:
                        risk_factors = json.loads(risk_factors)
                    except:
                        risk_factors = {}
                self.risk_factors_input.setText(json.dumps(risk_factors, indent=2))
                
                # Enable buttons
                self.save_button.setEnabled(True)
                self.delete_button.setEnabled(True)
                
                # Emit signal
                self.patient_selected.emit(patient_id)
                
                self.logger.info(f"Loaded patient data: {patient_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to load patient data: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to load patient data: {str(e)}")
            
    def save_patient(self):
        """Save patient data"""
        try:
            # Collect form data
            patient_data = {
                'patient_id': self.patient_id_input.text().strip(),
                'first_name': self.first_name_input.text().strip(),
                'last_name': self.last_name_input.text().strip(),
                'date_of_birth': self.dob_input.date().toString("yyyy-MM-dd"),
                'gender': self.gender_input.currentText(),
                'medical_record_number': self.mrn_input.text().strip(),
                'contact_info': self._parse_json_field(self.contact_info_input.toPlainText()),
                'medical_history': self._parse_json_field(self.medical_history_input.toPlainText()),
                'risk_factors': self._parse_json_field(self.risk_factors_input.toPlainText())
            }
            
            # Validate required fields
            if not patient_data['first_name'] or not patient_data['last_name']:
                QMessageBox.warning(self, "Validation Error", "First name and last name are required.")
                return
                
            # Save to database
            if self.current_patient_id:
                # Update existing patient
                success = self.db_manager.update_patient(self.current_patient_id, patient_data)
                action = "updated"
            else:
                # Add new patient
                patient_id = self.db_manager.add_patient(patient_data)
                if patient_id:
                    self.current_patient_id = patient_data['patient_id']
                    success = True
                    action = "created"
                else:
                    success = False
                    action = "created"
            
            if success:
                QMessageBox.information(self, "Success", f"Patient {action} successfully.")
                self.load_patient_list()
                self.clear_form()
            else:
                QMessageBox.warning(self, "Error", f"Failed to {action} patient.")
                
        except Exception as e:
            self.logger.error(f"Failed to save patient: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save patient: {str(e)}")
            
    def delete_patient(self):
        """Delete current patient"""
        if not self.current_patient_id:
            return
            
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete patient {self.current_patient_id}?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.db_manager.delete_patient(self.current_patient_id)
                if success:
                    QMessageBox.information(self, "Success", "Patient deleted successfully.")
                    self.load_patient_list()
                    self.clear_form()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete patient.")
                    
            except Exception as e:
                self.logger.error(f"Failed to delete patient: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete patient: {str(e)}")
                
    def clear_form(self):
        """Clear form fields"""
        self.current_patient_id = None
        self.patient_id_input.clear()
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.dob_input.setDate(QDate.currentDate())
        self.gender_input.setCurrentIndex(0)
        self.mrn_input.clear()
        self.contact_info_input.clear()
        self.medical_history_input.clear()
        self.risk_factors_input.clear()
        
        self.save_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
    def _parse_json_field(self, text):
        """Parse JSON field with fallback to string"""
        if not text.strip():
            return {}
            
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # If not valid JSON, return as string in a dict
            return {"text": text}
            
    def open_new_patient_dialog(self):
        """Open dialog for creating a new patient"""
        dialog = NewPatientDialog(self)
        if dialog.exec():
            patient_data = dialog.get_patient_data()
            if patient_data:
                patient_id = self.db_manager.add_patient(patient_data)
                if patient_id:
                    self.load_patient_list()
                    self.logger.info(f"New patient created: {patient_data['patient_id']}")


class NewPatientDialog(QDialog):
    """Dialog for creating new patients"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("New Patient Registration")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate())
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Other"])
        self.mrn_input = QLineEdit()
        
        form_layout.addRow("First Name:", self.first_name_input)
        form_layout.addRow("Last Name:", self.last_name_input)
        form_layout.addRow("Date of Birth:", self.dob_input)
        form_layout.addRow("Gender:", self.gender_input)
        form_layout.addRow("Medical Record Number:", self.mrn_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        
    def get_patient_data(self):
        """Get patient data from form"""
        if not self.first_name_input.text().strip() or not self.last_name_input.text().strip():
            return None
            
        return {
            'first_name': self.first_name_input.text().strip(),
            'last_name': self.last_name_input.text().strip(),
            'date_of_birth': self.dob_input.date().toString("yyyy-MM-dd"),
            'gender': self.gender_input.currentText(),
            'medical_record_number': self.mrn_input.text().strip(),
            'contact_info': {},
            'medical_history': {},
            'risk_factors': {}
        }