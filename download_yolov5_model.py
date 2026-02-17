#!/usr/bin/env python3
"""
YOLOv5 Model Download Script (Modern Ultralytics Version)
Safe for PyTorch 2.6+ and Python 3.12+
"""

import sys
import logging
from pathlib import Path
from typing import Optional

from ultralytics import YOLO

# Absolute imports (recommended project structure)
from app_utils.config import AppConfig
from app_utils.logger import get_logger


class YOLOv5Downloader:
    """Handles downloading and setup of YOLOv5 models using Ultralytics API"""

    def __init__(self):
        self.config = AppConfig()
        self.logger = get_logger("download_yolov5_model")

        # Model configuration
        self.model_variant = "yolov5s.pt"
        self.models_dir = self.config.models_dir
        self.target_model_path = self.models_dir / self.model_variant

        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.config.logs_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.config.logs_dir / "model_download.log"),
                logging.StreamHandler(),
            ],
        )

    def check_existing_model(self) -> bool:
        """Check if the model already exists"""
        if self.target_model_path.exists():
            self.logger.info(f"Model already exists at: {self.target_model_path}")
            return True
        return False

    def download_model(self) -> bool:
        """
        Download YOLOv5 model using official Ultralytics API
        """
        try:
            self.logger.info("Starting model download using Ultralytics API...")

            # This automatically downloads yolov5s.pt if not present
            model = YOLO(self.model_variant)

            # Save explicitly to your project directory
            model.save(str(self.target_model_path))

            self.logger.info(f"Model downloaded successfully to: {self.target_model_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to download model: {e}")
            return False

    def validate_model(self) -> bool:
        """Validate the downloaded model"""
        try:
            self.logger.info("Validating model...")

            model = YOLO(str(self.target_model_path))

            # Basic validation: check model names/classes
            if not hasattr(model.model, "names"):
                self.logger.error("Model validation failed: no class names found.")
                return False

            self.logger.info("Model validation successful.")
            return True

        except Exception as e:
            self.logger.error(f"Model validation failed: {e}")
            return False

    def update_configuration(self) -> bool:
        """Update application configuration"""
        try:
            self.config.set("model.path", str(self.target_model_path))
            self.config.set("model.device", "cpu")
            self.config.set("model.confidence_threshold", 0.3)
            self.config.set("model.iou_threshold", 0.45)

            self.logger.info("Configuration updated successfully.")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            return False

    def run(self) -> bool:
        """Main execution flow"""
        self.logger.info("=" * 60)
        self.logger.info("YOLOv5 Model Download and Setup")
        self.logger.info("=" * 60)

        if not self.check_existing_model():
            if not self.download_model():
                return False

        if not self.validate_model():
            return False

        if not self.update_configuration():
            return False

        self.logger.info("Setup completed successfully.")
        self.logger.info(f"Model location: {self.target_model_path}")
        self.logger.info("=" * 60)

        return True


def main():
    downloader = YOLOv5Downloader()

    try:
        success = downloader.run()
        if success:
            print("\n✅ YOLOv5 model setup completed successfully!")
            print(f"📍 Model saved to: {downloader.target_model_path}")
            print("🔧 Configuration updated automatically")
        else:
            print("\n Setup failed. Check logs for details.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user.")
        sys.exit(1)

    except Exception as e:
        print(f"\n Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
