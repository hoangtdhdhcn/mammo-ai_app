# AI-Powered Breast Cancer Detection Desktop Application

A comprehensive medical-grade desktop application for AI-powered breast cancer detection using YOLOv5 and PyQt6.

## Features

### 🏥 **Patient Management**
- Complete patient registration and profile management
- Secure medical record storage with encryption
- Patient search and history tracking
- Medical history and risk factor documentation

### 🔍 **Image Analysis**
- Support for multiple medical imaging formats (PNG, JPG, DICOM, etc.)
- Real-time YOLOv5 inference with bounding box visualization
- Configurable confidence and IoU thresholds
- Image quality assessment and preprocessing
- Batch processing capabilities

### 📊 **Advanced Analytics**
- Comprehensive history tracking with timeline views
- Interactive charts and trend analysis
- Patient engagement and performance metrics
- Comparative analysis tools
- System health monitoring

### 📈 **Professional Dashboard**
- Medical-grade UI with dark theme
- Real-time system statistics
- Performance benchmarks and KPIs
- Export capabilities (PDF, Excel, CSV)
- Compliance reporting (HIPAA, GDPR)

### 🔒 **Security & Compliance**
- Encrypted patient data storage
- Audit trail for all operations
- Data backup and retention policies
- Medical-grade security features

## Technology Stack

### Frontend
- **PyQt6** - Modern, professional UI framework
- **Matplotlib** - Advanced charting and visualization
- **OpenCV** - Image processing and computer vision

### Backend
- **Python 3.8+** - Core application logic
- **SQLite** - Local database with encryption
- **PyTorch/YOLOv5** - AI model inference
- **NumPy/Pandas** - Data analysis and manipulation

### Utilities
- **ReportLab** - PDF report generation
- **XlsxWriter** - Excel export functionality
- **Logging** - Comprehensive application logging

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11, macOS, or Linux

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd breast_cancer_detection_app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download YOLOv5 Model:**
   - Place your trained YOLOv5 model file in the `models/` directory
   - Update the model path in `config.json` if needed

4. **Run the application:**
   ```bash
   python main.py
   ```

## Project Structure

```
breast_cancer_detection_app/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── config.json               # Application configuration
├── models/                   # YOLOv5 model files
│   ├── __init__.py
│   └── model_manager.py      # Model loading and inference
├── database/                 # Database schema and management
│   ├── __init__.py
│   ├── schema.sql           # Database schema
│   └── manager.py           # Database operations
├── ui_components/           # PyQt6 UI components
│   ├── __init__.py
│   ├── main_window.py       # Main application window
│   ├── patient_management.py # Patient management interface
│   ├── image_analysis.py    # Image analysis interface
│   ├── history_tracking.py  # History tracking interface
│   └── analytics_dashboard.py # Analytics dashboard
├── utils/                   # Utility modules
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   └── logger.py           # Logging utilities
└── tests/                  # Test files
    └── __init__.py
```

## Usage

### Getting Started

1. **Launch the Application:**
   ```bash
   python main.py
   ```

2. **Configure Model:**
   - Go to Settings (if implemented)
   - Specify the path to your YOLOv5 model file
   - Set confidence and IoU thresholds

3. **Add Patients:**
   - Use the Patient Management tab
   - Register new patients or search existing ones
   - Add medical history and risk factors

4. **Analyze Images:**
   - Upload medical images (PNG, JPG, DICOM)
   - Select patient and image type
   - Configure analysis parameters
   - View results with bounding box visualization

5. **Review Analytics:**
   - Access history tracking for patient trends
   - Use analytics dashboard for system insights
   - Export reports in various formats

### Key Workflows

#### Patient Registration
1. Navigate to "Patient Management"
2. Click "New Patient"
3. Fill in patient information
4. Save to database

#### Image Analysis
1. Go to "Image Analysis"
2. Upload medical image
3. Select patient from dropdown
4. Configure analysis settings
5. Click "Start Analysis"
6. View results and save to patient record

#### History Review
1. Navigate to "History Tracking"
2. Select patient
3. View timeline of analyses
4. Examine trend charts
5. Access detailed results

#### Analytics Dashboard
1. Go to "Analytics Dashboard"
2. Select analysis type
3. View system statistics
4. Generate reports
5. Export data

## Configuration

### Application Settings

The application uses a JSON configuration file (`config.json`) with the following structure:

```json
{
  "model": {
    "path": "models/yolov5_model.pt",
    "confidence_threshold": 0.5,
    "iou_threshold": 0.45,
    "device": "cpu"
  },
  "database": {
    "path": "database/patients.db",
    "backup_enabled": true,
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
    "quality_enhancement": true
  },
  "analytics": {
    "enable_trend_analysis": true,
    "history_retention_days": 365,
    "export_formats": ["pdf", "excel", "csv"],
    "chart_theme": "medical"
  }
}
```

### Model Configuration

To use your own YOLOv5 model:

1. Place your `.pt` model file in the `models/` directory
2. Update the `model.path` in `config.json`
3. Adjust confidence and IoU thresholds as needed
4. Ensure your model classes match the expected output format

## Security Features

### Data Protection
- **Encryption**: Patient data is encrypted at rest
- **Access Control**: Audit trail for all data access
- **Backup**: Automatic encrypted backups
- **Retention**: Configurable data retention policies

### Compliance
- **HIPAA**: Medical data handling compliance
- **GDPR**: Data protection regulation compliance
- **Audit Logging**: Complete operation logging
- **Secure Storage**: Encrypted database storage

## Performance Optimization

### System Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space for images and database
- **GPU**: Optional for faster inference (CUDA support)

### Optimization Tips
- Use GPU acceleration when available
- Configure appropriate image resize dimensions
- Set optimal confidence thresholds
- Enable batch processing for multiple images

## Troubleshooting

### Common Issues

**Model Loading Failed:**
- Check model file path in configuration
- Ensure PyTorch and torchvision are installed
- Verify model compatibility with YOLOv5

**Database Connection Error:**
- Check database file permissions
- Verify database directory exists
- Ensure no other processes are using the database

**Image Processing Error:**
- Check image format support
- Verify image file integrity
- Ensure sufficient memory for large images

### Logs and Debugging

Application logs are stored in the `logs/` directory:
- `app_YYYYMMDD_HHMMSS.log` - Main application logs
- Error logs with detailed stack traces
- Performance and security event logs

## Development

### Adding New Features

1. **UI Components**: Add new widgets to `ui_components/`
2. **Database**: Update schema in `database/schema.sql`
3. **Models**: Extend `models/model_manager.py`
4. **Utilities**: Add utilities to `utils/`

### Testing

Unit tests should be added to the `tests/` directory:
- Mock database operations for testing
- Test UI components with PyQt test framework
- Validate model inference accuracy

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit pull request

## Support

### Documentation
- Code comments for complex algorithms
- API documentation in docstrings
- Configuration examples

### Community
- Issue tracking for bug reports
- Feature requests and discussions
- Code review and collaboration

## License

This project is licensed for educational and research purposes. Ensure compliance with medical regulations and data protection laws in your jurisdiction.

## Disclaimer

This application is intended for research and educational purposes. It should not be used as the sole basis for medical diagnosis or treatment decisions. Always consult with qualified medical professionals for patient care.

## Contact

For questions, support, or collaboration opportunities, please contact the development team.

---

**Note**: This application handles sensitive medical data. Ensure proper security measures and compliance with applicable regulations in your deployment environment.