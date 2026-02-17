"""
YOLOv5 Model Manager
Handles model loading, validation, and inference for breast cancer detection
"""

# Fix DLL error
import os
import platform
if platform.system() == "Windows":
    import ctypes
    from importlib.util import find_spec
    try:
        if (spec := find_spec("torch")) and spec.origin and os.path.exists(
            dll_path := os.path.join(os.path.dirname(spec.origin), "lib", "c10.dll")
        ):
            ctypes.CDLL(os.path.normpath(dll_path))
    except Exception:
        pass

import os
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import logging
from datetime import datetime

from app_utils.config import AppConfig
from app_utils.logger import get_logger, get_medical_logger

os.environ["CUDA_VISIBLE_DEVICES"] = ""

class ModelManager:
    """Manager for YOLOv5 model operations"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger("models.model_manager")
        self.medical_logger = get_medical_logger()
        
        # Model attributes
        self.model = None
        self.model_path = None
        self.device = None
        self.is_loaded = False
        self.model_info = {}
        
        # Initialize model
        self._setup_device()
        
    def _setup_device(self):
        """Setup computation device (CPU/GPU)"""
        device_config = self.config.get_device()
        
        # Use ultralytics device selection
        import ultralytics
        self.device = ultralytics.utils.torch_utils.select_device(device_config)
        self.logger.info(f"Using device: {self.device}")
            
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Load YOLOv5 model from file
        
        Args:
            model_path: Path to model file (optional, uses config default if not provided)
            
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            if model_path is None:
                model_path = self.config.get_model_path()
                
            self.model_path = Path(model_path)
            
            # Validate model file exists
            if not self.model_path.exists():
                self.logger.error(f"Model file not found: {self.model_path}")
                return False
                
            # Load model
            self.logger.info(f"Loading model from: {self.model_path}")
            
            # Load YOLOv5 model using ultralytics API
            from ultralytics import YOLO
            self.model = YOLO(str(self.model_path))
            
            # Set model to evaluation mode
            self.model.eval()
            
            # Get model information
            self._extract_model_info()
            
            self.is_loaded = True
            
            # Log successful model loading
            self.medical_logger.log_model_inference(
                model_path=str(self.model_path),
                confidence=0.0,  # Not applicable for loading
                processing_time=0.0,  # Not applicable for loading
                image_path="model_loading"
            )
            
            self.logger.info(f"Model loaded successfully: {self.model_info}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            self.medical_logger.log_error(
                f"Model loading failed: {str(e)}",
                {"model_path": str(model_path)},
                e
            )
            return False
            
    def _extract_model_info(self):
        """Extract information about the loaded model"""
        try:
            # Get model architecture info
            self.model_info = {
                "model_type": "YOLOv5",
                "model_path": str(self.model_path),
                "device": str(self.device),
                "input_shape": [640, 640],  # Standard YOLOv5 input size
                "confidence_threshold": self.config.get_confidence_threshold(),
                "iou_threshold": self.config.get_iou_threshold(),
                "loaded_at": datetime.now().isoformat()
            }
            
            # Try to get model class names if available
            if hasattr(self.model, 'names'):
                self.model_info["classes"] = self.model.names
                
        except Exception as e:
            self.logger.warning(f"Could not extract full model info: {e}")
            self.model_info["error"] = str(e)
            
    def predict(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Run inference on an image
        
        Args:
            image: Input image as numpy array (H, W, C)
            
        Returns:
            Dict containing detection results
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        start_time = datetime.now()
        
        try:
            # Run inference directly with ultralytics (handles preprocessing internally)
            results = self.model(image, 
                               conf=self.config.get_confidence_threshold(),
                               iou=self.config.get_iou_threshold())
                
            # Process results
            detections = self._process_results(results)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Log inference
            self.medical_logger.log_model_inference(
                model_path=str(self.model_path),
                confidence=detections.get("max_confidence", 0.0),
                processing_time=processing_time,
                image_path="inference"
            )
            
            self.logger.info(f"Inference completed in {processing_time:.3f}s")
            
            return {
                "detections": detections,
                "processing_time": processing_time,
                "model_info": self.model_info
            }
            
        except Exception as e:
            self.logger.error(f"Inference failed: {e}")
            self.medical_logger.log_error(
                f"Inference failed: {str(e)}",
                {"image_shape": image.shape if image is not None else None},
                e
            )
            raise
            
    def _process_results(self, results) -> Dict[str, Any]:
        """
        Process ultralytics results into structured format
        
        Args:
            results: ultralytics results object
            
        Returns:
            Structured detection results
        """
        try:
            # Get boxes from results
            boxes = results[0].boxes  # First result in batch
            
            # Extract detection information
            detections = []
            max_confidence = 0.0
            
            # Process each detection
            for box in boxes:
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                # Get confidence and class
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                
                # Apply confidence threshold
                if conf >= self.config.get_confidence_threshold():
                    detection = {
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "confidence": float(conf),
                        "class_id": int(cls_id),
                        "class_name": self.model.names[int(cls_id)] if hasattr(self.model, 'names') else f"Class_{int(cls_id)}"
                    }
                    detections.append(detection)
                    
                    if conf > max_confidence:
                        max_confidence = float(conf)
                        
            return {
                "detections": detections,
                "count": len(detections),
                "max_confidence": max_confidence,
                "confidence_threshold": self.config.get_confidence_threshold()
            }
            
        except Exception as e:
            self.logger.error(f"Result processing failed: {e}")
            raise
            
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and information"""
        return {
            "is_loaded": self.is_loaded,
            "model_path": str(self.model_path) if self.model_path else None,
            "device": str(self.device) if self.device else None,
            "model_info": self.model_info,
            "confidence_threshold": self.config.get_confidence_threshold(),
            "iou_threshold": self.config.get_iou_threshold()
        }
        
    def unload_model(self):
        """Unload the model to free memory"""
        if self.model is not None:
            del self.model
            self.model = None
            
        self.is_loaded = False
        self.model_path = None
        self.model_info = {}
        
        self.logger.info("Model unloaded successfully")
        
    def update_thresholds(self, confidence_threshold: float = None, 
                         iou_threshold: float = None):
        """
        Update model inference thresholds
        
        Args:
            confidence_threshold: New confidence threshold
            iou_threshold: New IoU threshold for NMS
        """
        if confidence_threshold is not None:
            self.config.set("model.confidence_threshold", confidence_threshold)
            
        if iou_threshold is not None:
            self.config.set("model.iou_threshold", iou_threshold)
            
        self.logger.info(f"Updated thresholds: confidence={self.config.get_confidence_threshold()}, "
                        f"iou={self.config.get_iou_threshold()}")
                        
    def validate_model_compatibility(self) -> bool:
        """
        Validate that the loaded model is compatible with the application
        
        Returns:
            bool: True if compatible, False otherwise
        """
        if not self.is_loaded:
            return False
            
        try:
            # Check if model has required attributes
            required_attrs = ['names', 'stride', 'model']
            for attr in required_attrs:
                if not hasattr(self.model, attr):
                    self.logger.error(f"Model missing required attribute: {attr}")
                    return False
                    
            # Check if model can process a dummy image
            dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            test_result = self.predict(dummy_image)
            
            if test_result is None:
                self.logger.error("Model failed to process test image")
                return False
                
            self.logger.info("Model compatibility validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Model compatibility validation failed: {e}")
            return False