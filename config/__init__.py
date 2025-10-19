"""
Configuration Package
Centralized settings and hardware configuration
"""

from config.settings import settings
from config.hardware_config import (
    SERVO_PINS,
    ULTRASONIC_PINS,
    I2C_ADDRESSES,
    CAMERA_CONFIG,
    SERVO_LIMITS,
    MOVEMENT_PARAMS,
    SENSOR_CONFIG,
)
from config.yolo_detection_config import (
    YOLOConfig,
    COCO_CLASSES,
    ENHANCED_CLASS_INFO,
    COLOR_MAP,
)

__all__ = [
    'settings',
    'SERVO_PINS',
    'ULTRASONIC_PINS',
    'I2C_ADDRESSES',
    'CAMERA_CONFIG',
    'SERVO_LIMITS',
    'MOVEMENT_PARAMS',
    'SENSOR_CONFIG',
    'YOLOConfig',
    'COCO_CLASSES',
    'ENHANCED_CLASS_INFO',
    'COLOR_MAP',
]